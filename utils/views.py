import asyncio
import datetime as dt
import typing
import discord
import humanize
import importlib
import numpy as np
from io import StringIO, BytesIO
from requests import options
from tabulate import tabulate
from bs4 import BeautifulSoup
from jishaku.functools import executor_function
from PIL import Image, ImageDraw, ImageFont
from arsenic import stop_session, Session
from discord.ext import commands

from utils import pour_puzzle, sounder
importlib.reload(pour_puzzle)
importlib.reload(sounder)

from utils.pour_puzzle import Liquid, Bottle, levels
from utils.sounder import Sounder, audios

# Base
class BaseView(discord.ui.View):
	def __init__(self, ctx, *, timeout=180):
		self.ctx = ctx
		super().__init__(timeout=timeout)

	async def interaction_check(self, interaction):
		if interaction.user != self.ctx.author:
			await interaction.response.send_message(f'Only **{self.ctx.author}** can use this button!', ephemeral=True)
			return False

		return True

class DelView(BaseView):
	def __init__(self, ctx, *, timeout=180):
		super().__init__(ctx, timeout=timeout)

	@discord.ui.button(emoji="<:redx:827600701768597554>", style=discord.ButtonStyle.red)
	async def delete(self, button, interaction):
		await interaction.response.defer()
		await interaction.delete_original_message()

# Bot cog
class HelpView(discord.ui.View):
	def __init__(self, ctx, mapping, help_command, *, timeout = None):
		super().__init__(timeout=timeout)
		self.ctx = ctx
		self.mapping = mapping
		self.help = help_command
		self.embed_mapping = {}
		self.embeds = []
		self.length = 0
		self.index = 0
		self.button_first = None
		self.button_previous = None
		self.button_index = None
		self.button_next = None
		self.button_last = None
		self.message = None
		self.menu = HelpMenu(self)

	async def interaction_check(self, interaction):
		if interaction.user != self.ctx.author:
			await interaction.response.send_message("This is not your interaction!", ephemeral=True)
			return False
		
		return True

	async def start_help(self):
		for cog, commands in self.mapping.items():
			commands = await self.help.filter_commands(commands, sort=True)
			if getattr(cog, 'hidden', False) or not cog or cog.qualified_name == 'Jishaku':
				continue

			self.embed_mapping[cog] = self.create_cog_embeds(cog, commands)
			self.menu.append_option(discord.SelectOption(label=cog.qualified_name, description=cog.description))
		
		self.add_item(self.menu)
		self.message = await self.ctx.reply(embed=self.create_home_embed(), view=self, allowed_mentions=discord.AllowedMentions.none())

	def create_home_embed(self):
		embed = discord.Embed(title="Help", description="List of commands available", color=self.ctx.bot.c)
		embed.set_author(name=self.ctx.author.name, icon_url=self.ctx.author.display_avatar.url)
		embed.add_field(name="Categories:", value="\n".join(f"\U000025ab\U0000fe0f {cog.qualified_name}" for cog in self.ctx.bot.cogs.values() if not (getattr(cog, 'hidden', False) or not cog or cog.qualified_name == 'Jishaku')), inline=False)
		return embed

	def create_cog_embeds(self, cog, commands):
		embeds = []
		chunks = self.ctx.chunk(commands, per=9)

		for chunk in chunks:
			embed = discord.Embed(title="Help", description="List of commands available", color=self.ctx.bot.c)
			embed.set_author(name=self.ctx.author.name, icon_url=self.ctx.author.display_avatar.url)
			embed.set_thumbnail(url=getattr(cog, 'thumbnail', discord.Embed.Empty))
			embed.add_field(name=f"-=: {cog.qualified_name} :=-", value=cog.description, inline=False)

			for command in chunk:
				embed.add_field(name=f"`{command.name}`", value=command.short_doc or "-", inline=True)

			if len(chunk) % 3 != 0:
				for _ in range(3 - len(chunk) % 3):
					embed.add_field(name="\u200b", value="\u200b", inline=True)

			embed.add_field(name="\u200b", value=f"Use `{self.ctx.clean_prefix}help [command]` for more info on a command.", inline=False)
			embeds.append(embed)

		return embeds
		
	async def change_cog_to(self, cog):
		self.embeds = self.embed_mapping[cog]

		for child in self.children[:]:
			if isinstance(child, discord.ui.Button):
				self.remove_item(child)

		self.length = len(self.embeds)
		self.index = 0
		
		self.button_first = discord.ui.Button(style=discord.ButtonStyle.secondary, label="\u00AB")
		self.button_previous = discord.ui.Button(style=discord.ButtonStyle.secondary, label="\u2039")
		self.button_index = discord.ui.Button(style=discord.ButtonStyle.red, emoji="\U0001f6d1", label=f"Page 1 of {self.length}")
		self.button_next = discord.ui.Button(style=discord.ButtonStyle.secondary, label="\u203A")
		self.button_last = discord.ui.Button(style=discord.ButtonStyle.secondary, label="\u00BB")

		self.button_first.callback = self.button_first_callback
		self.button_previous.callback = self.button_previous_callback
		self.button_index.callback = self.button_index_callback
		self.button_next.callback = self.button_next_callback
		self.button_last.callback = self.button_last_callback
		
		self.button_next.disabled = False
		self.button_last.disabled = False
		self.button_previous.disabled = False
		self.button_first.disabled = False

		if self.index == self.length-1:
			self.button_next.disabled = True
			self.button_last.disabled = True

		if self.index == 0:
			self.button_previous.disabled = True
			self.button_first.disabled = True

		self.add_item(self.button_first)
		self.add_item(self.button_previous)
		self.add_item(self.button_index)
		self.add_item(self.button_next)
		self.add_item(self.button_last)

		if self.message is None:
			self.message = await self.ctx.reply(embed=self.embeds[0], view=self)
		else:
			await self.message.edit(embed=self.embeds[0], view=self)

	async def button_first_callback(self, interaction):
		if self.index == 0:
			return

		self.index = 0
		await self.update()

	async def button_previous_callback(self, interaction):
		if self.index == 0:
			return

		self.index -= 1
		await self.update()

	async def button_index_callback(self, interaction):
		await self.message.delete()
		self.stop()

	async def button_next_callback(self, interaction):
		if self.index == self.length-1:
			return

		self.index += 1
		await self.update()

	async def button_last_callback(self, interaction):
		if self.index == self.length-1:
			return

		self.index = self.length-1
		await self.update()
		
	async def update(self):
		self.button_index.label = f"Page {self.index+1} of {self.length}"

		self.button_next.disabled = False
		self.button_last.disabled = False
		self.button_previous.disabled = False
		self.button_first.disabled = False

		if self.index == self.length-1:
			self.button_next.disabled = True
			self.button_last.disabled = True

		if self.index == 0:
			self.button_previous.disabled = True
			self.button_first.disabled = True

		await self.message.edit(embed=self.embeds[self.index], view=self)

class HelpMenu(discord.ui.Select):
	def __init__(self, view):
		super().__init__(placeholder='Select Category')
		self.parent_view = view
		self.previous = None

	async def callback(self, interaction: discord.Interaction):
		if self.previous == self.values[0]:
			return
		self.previous = self.values[0]

		cog = discord.utils.get(self.parent_view.mapping, qualified_name=self.values[0])
		
		await self.parent_view.change_cog_to(cog)

# class HelpMenu(discord.ui.S)

class EndpointView(discord.ui.View):
	def __init__(self, msg, results):
		super().__init__()
		self.msg = msg
		self.results = results

	@discord.ui.button(label='Show result', style=discord.ButtonStyle.primary)
	async def show(self, button, interaction):
		button.label = 'Result sent!'
		button.disabled = True
		await self.msg.edit(view=self)
		await interaction.response.send_message(self.results)

class ApiKeyView(discord.ui.View):
	def __init__(self, ctx: commands.Context):
		super().__init__()
		self.ctx = ctx


# Isometric cog
class Switch(discord.ui.View):
	def __init__(self, ctx):
		super().__init__()
		self.ctx = ctx
		self.text1 = None
		self.text2 = None
		self.state = 0
		self.button = None
		self.message = None

	async def switch(self, text1, text2):
		self.text1 = text1
		self.text2 = text2

		self.button = discord.ui.Button(emoji="<:lever:843768316002172958>", style=discord.ButtonStyle.red)
		self.button.callback = self.callback

		self.add_item(self.button)
		self.message = await self.ctx.reply(self.text1, view=self, allowed_mentions=discord.AllowedMentions.none())

	async def callback(self, interaction):
		if interaction.user != self.ctx.author:
			return await interaction.response.send_message("This is not your interaction!", ephemeral=True)

		if not self.state:
			self.state = 1
			self.button.style = discord.ButtonStyle.green
			await self.message.edit(content=self.text2, view=self, allowed_mentions=discord.AllowedMentions.none())
		else:
			self.state = 0
			self.button.style = discord.ButtonStyle.red
			await self.message.edit(content=self.text1, view=self, allowed_mentions=discord.AllowedMentions.none())

	async def on_timeout(self):
		self.clear_items()
		await self.message.edit(view=self)

class BuildView(discord.ui.View):
	def __init__(self, ctx, build_search):
		super().__init__()
		self.ctx = ctx
		self.build_search = build_search
		self.message = None
		self.render_button = None
		self.gif_button = None
		self.star_button = None
		self.info_button = None
	
	async def start(self):
		self.render_button = discord.ui.Button(label="Render", style=discord.ButtonStyle.primary)
		self.render_button.callback = self.render_callback
		self.add_item(self.render_button)

		if any([lever in self.build_search['build'] for lever in ['e', '#']]):
			self.gif_button = discord.ui.Button(label="Render as gif", style=discord.ButtonStyle.primary)
			self.gif_button.callback = self.gif_callback
			self.add_item(self.gif_button)

		self.info_button = discord.ui.Button(label="Build info", style=discord.ButtonStyle.grey)
		self.info_button.callback = self.info_callback
		self.add_item(self.info_button)

		left = await self.cooldown_left()
		if left:
			self.star_button = discord.ui.Button(label=f"Build star on cooldown.. {left}", disabled=True, emoji="<:nostar:596577059673866260>", style=discord.ButtonStyle.grey)
		else:
			self.star_button = discord.ui.Button(label="Star this build", emoji="\U00002b50", style=discord.ButtonStyle.grey)
		
		self.star_button.callback = self.star_callback
		self.add_item(self.star_button)

		content = f"`build: {self.build_search['build_name']}`\n```\nj;isometric {self.build_search['build']}```"
		self.message = await self.ctx.reply(content, view=self, allowed_mentions=discord.AllowedMentions.none())

		await self.ctx.bot.db.execute("UPDATE builds SET uses = uses + 1 WHERE build_name = $1", self.build_search['build_name'])

	async def cooldown_left(self):
		triggered = await self.ctx.bot.db.fetchval("SELECT triggered FROM star_cooldown WHERE user_id = $1", self.ctx.author.id)
		if triggered:
			delta = dt.datetime.now() - triggered
			if delta.total_seconds() <= 3600:
				left = humanize.precisedelta(dt.timedelta(hours=1) - delta)
				return left
			else:
				await self.ctx.bot.db.execute("DELETE FROM star_cooldown WHERE user_id = $1", self.ctx.author.id)
				return None
		else:
			return None

	async def interaction_check(self, interaction):
		if interaction.user != self.ctx.author:
			await interaction.response.send_message("This is not your interaction!", ephemeral=True)
			return False

		return True

	async def update_view(self):
		await self.message.edit(view=self)

	async def on_timeout(self):
		self.clear_items()
		await self.update_view()

	async def render_callback(self, interaction):
		self.render_button.disabled = True
		self.render_button.label = "Rendered!"
		self.render_button.style = discord.ButtonStyle.grey

		if self.gif_button:
			self.remove_item(self.gif_button)

		await self.update_view()

		cmd = self.ctx.bot.get_command("isometric")
		await cmd(self.ctx, blocks=self.build_search["build"])

	async def gif_callback(self, interaction):
		self.render_button.disabled = True
		self.render_button.label = "Rendered!"
		self.render_button.style = discord.ButtonStyle.grey
		self.remove_item(self.gif_button)

		await self.update_view()

		cmd = self.ctx.bot.get_command("isometric")
		await cmd(self.ctx, blocks=self.build_search["build"]+' gif')

	async def info_callback(self, interaction):
		self.info_button.disabled = True
		self.info_button.label = "Info sent!"

		await self.update_view()

		cmd = self.ctx.bot.get_command("build info")
		await cmd(self.ctx, build_name=self.build_search["build_name"])

	async def star_callback(self, interaction):
		left = await self.cooldown_left()

		if left:
			await interaction.response.send_message(label := f"Build star on cooldown.. {left}", ephemeral=True)
			self.star_button.label = label
		else:
			await self.ctx.bot.db.execute("UPDATE builds SET stars = stars + 1 WHERE build_name = $1", self.build_search['build_name'])
			await self.ctx.bot.db.execute("INSERT INTO star_cooldown (user_id, triggered) VALUES ($1, $2)", self.ctx.author.id, dt.datetime.now())
			await interaction.response.send_message(f'You starred \"{self.build_search["build_name"]}\" \U00002b50 !', ephemeral=True)
			self.star_button.label = f"Build star on cooldown.. 1 hour"

		self.star_button.emoji = "<:nostar:596577059673866260>"
		self.star_button.disabled = True

		await self.update_view()

class NonoButton(discord.ui.Button):
	def __init__(self, idx, kind):
		super().__init__(label='\u200b', style=discord.ButtonStyle.secondary)
		self.idx = idx
		self.kind = kind

	async def callback(self, interaction):
		await self.view.pressed(self, interaction)

class NonoView(discord.ui.View):
	font = ImageFont.truetype('./image/GothamMedium.ttf', 40)
	def __init__(self, ctx, ans_map):
		super().__init__(timeout=None)
		self.ctx = ctx
		self.ans_map = ans_map
		self.buttons = [NonoButton(i, t) for i, t in enumerate(sum(ans_map, []))]
		self.board = [[0]*5 for _ in range(5)]
		self.msg = None
		for button in self.buttons:
			self.add_item(button)

	def get_ans_amount(self, ans_map):
		side_ans = []
		for row in ans_map:
			row_ans = [0, 0, 0, 0, 0, 0]
			i = 0
			amount = 0
			for t in row:
				if t:
					amount += 1
				else:
					amount = 0
					i += 1
				row_ans[i] = amount
			row_ans = [a for a in row_ans if a]
			side_ans.append(row_ans if row_ans else [0])

		return side_ans

	@executor_function
	def draw_board(self):
		side_ans, top_ans = self.get_ans_amount(self.ans_map), self.get_ans_amount(np.array(self.ans_map).T)

		img = Image.new('RGBA', (500, 500), 'white')
		draw = ImageDraw.Draw(img)
		for j, row in enumerate(self.board, start=1):
			for i, cell in enumerate(row, start=1):
				draw.rectangle([(100+i*70, 100+j*70), (i*70+30, j*70+20)], 'black' if cell else 'white', 'grey', 5)

		for i, row_ans in enumerate(side_ans):
			draw.text((90, 115+i*70), ' '.join(str(c) for c in row_ans), 'black', self.font, 'ra')

		for i, col_ans in enumerate(top_ans):
			draw.text((130+i*70, 90), '\n'.join(str(c) for c in col_ans), 'black', self.font, 'md', align='center')
				

		buf = BytesIO()
		img.save(buf, 'PNG')
		buf.seek(0)
		
		return buf

	async def pressed(self, button, interaction):
		if interaction.user != self.ctx.author:
			return await interaction.response.send_message('You can\'t use this button!', ephemeral=True)

		if button.kind:
			for child in self.children:
				if child == button:
					child.disabled = True
					child.style = discord.ButtonStyle.primary

			self.board[button.idx//5][button.idx%5] = 1

			buf = await self.draw_board()
			url = await self.ctx.upload_bytes(buf.getvalue(), 'image/png', 'nonogram')

			embed = self.msg.embeds[0]
			embed.set_image(url=url)

			if self.board == self.ans_map:
				embed.description = 'You\'ve won!'
				# for child in self.children:
				# 	child.disabled = True
				self.clear_items()
			await self.msg.edit(embed=embed, allowed_mentions=discord.AllowedMentions.none(), view=self)
		else:
			for child in self.children:
				if child.kind:
					child.style = discord.ButtonStyle.primary
				else:
					child.style = discord.ButtonStyle.danger
				child.disabled = True
			await interaction.message.edit(view=self)

class BottleButton(discord.ui.Button):
	def __init__(self, bottle: Bottle, **kwargs):
		super().__init__(**kwargs)
		self.bottle = bottle

	async def callback(self, interaction: discord.Interaction):
		if self.view.state == 0:
			self.disabled = True
			self.style = discord.ButtonStyle.primary
			self.view.selected = self
			for btn in self.view.children:
				if btn.custom_id == 'cancel_btn':
					btn.disabled = False
					continue
				if isinstance(btn, BottleButton) and btn != self:
					try:
						if btn.bottle.is_full() or self.bottle.liquids[-1].color != btn.bottle.liquids[-1].color:
							btn.disabled = True
						else:
							btn.disabled = False
					except IndexError:
						btn.disabled = False
			self.view.state = 1
			await interaction.message.edit(view=self.view)
		elif self.view.state == 1:
			await self.view.selected.bottle.pour(self.bottle)

			for btn in self.view.children:
				if btn.custom_id == 'cancel_btn':
					btn.disabled = True
					continue
				if isinstance(btn, BottleButton):
					btn.disabled = True if btn.bottle.is_empty() else False
					if btn == self.view.selected:
						btn.style = discord.ButtonStyle.secondary
					if btn.bottle.is_completed():
						btn.style = discord.ButtonStyle.success
						btn.disabled = True
			
			self.view.state = 0
			embed = self.view.msg.embeds[0]
			img_buf = await self.view.draw_image()
			url = await self.view.ctx.upload_bytes(img_buf.getvalue(), 'image/png', 'pour game')
			embed.set_image(url=url)

			if self.view.win_check():
				embed.description = f'Level : {self.view.level}\nYou\'ve completed this level!'
				for btn in self.view.children:
					if btn.custom_id != 'exit_btn':
						btn.disabled = True
				
				highest_level = await self.view.ctx.db.fetchval('SELECT level FROM pour_level WHERE user_id = $1', self.view.ctx.author.id)
				if highest_level == self.view.level:
					await self.view.ctx.db.execute('UPDATE pour_level SET level = level + 1 WHERE user_id = $1', self.view.ctx.author.id)
				self.view.level += 1
				if self.view.level <= len(levels):
					next_button = discord.ui.Button(label=f'Level {self.view.level} >', style=discord.ButtonStyle.success, row=0, custom_id='next_lvl_btn')
					next_button.callback = self.view.next_button_callback

					self.view.add_item(next_button)

			await interaction.message.edit(embed=embed, view=self.view)

class PourView(discord.ui.View):
	font = ImageFont.truetype('./image/GothamMedium.ttf', 30)
	def __init__(self, ctx, level):
		super().__init__(timeout=None)
		self.ctx = ctx
		self.level = level
		self.state = 0
		self.selected = None
		self.msg = None
		self.next_btn = None
		
		for i, bottle_data in enumerate(levels[self.level], start=1):
			bottle = Bottle(i, [Liquid(color) for color in bottle_data])
			self.add_item(BottleButton(bottle, label=i, style=discord.ButtonStyle.secondary, row=1+(i-1)//5, disabled=True if bottle.is_empty() else False))

	@executor_function
	def draw_image(self):
		n_bottle = len(levels[self.level])
		img = Image.new('RGBA', (50+50*n_bottle, 200), (255, 242, 161))
		draw = ImageDraw.Draw(img)

		for btn in self.children:
			if isinstance(btn, BottleButton):
				for i, liquid in enumerate(btn.bottle.liquids):
					draw.rectangle((btn.bottle.num*50-20, 150-i*20, 16+btn.bottle.num*50, 130-i*20), liquid.color)
				draw.rectangle((btn.bottle.num*50-20, 50, 16+btn.bottle.num*50, 150), None, 'black', 5)
				draw.text((btn.bottle.num*50, 160), str(btn.bottle.num), 'black', self.font, 'mt')
		draw.rectangle((0, 50, 1000, 55), (255, 242, 161))
		
		buf = BytesIO()
		img.save(buf, 'PNG')
		buf.seek(0)

		return buf

	def win_check(self):
		checks = []
		for btn in self.children:
			if isinstance(btn, BottleButton):
				checks.append(btn.bottle.is_completed() or btn.bottle.is_empty())

		for btn in self.children:
			if isinstance(btn, BottleButton):
				checks.append(btn.bottle.is_completed() or btn.bottle.is_empty())
		
		return all(checks)

	async def interaction_check(self, interaction):
		if interaction.user != self.ctx.author:
			await interaction.response.send_message('You can\'t use this button!', ephemeral=True)
			return False
		return True

	@discord.ui.button(label='Exit', style=discord.ButtonStyle.danger, custom_id='exit_btn', row=0)
	async def exit_button(self, button: discord.Button, interaction: discord.Interaction):
		for btn in self.children:
			btn.disabled = True
		
		button.label = 'Exited'
		await interaction.message.edit(view=self)
		self.stop()

	@discord.ui.button(label='Reset', style=discord.ButtonStyle.danger, custom_id='reset_btn', row=0)
	async def reset_button(self, button: discord.Button, interaction: discord.Interaction):
		self.state = 0
		self.selected = None

		for btn in self.children:
			if btn.custom_id == 'cancel_btn':
				btn.disabled = True
				continue
			if isinstance(btn, BottleButton):
				self.remove_item(btn)


		for btn in self.children[:]:
			if isinstance(btn, BottleButton):
				self.remove_item(btn)

		for i, bottle_data in enumerate(levels[self.level], start=1):
			bottle = Bottle(i, [Liquid(color) for color in bottle_data])
			self.add_item(BottleButton(bottle, label=i, style=discord.ButtonStyle.secondary, row=1+(i-1)//5, disabled=True if bottle.is_empty() else False))
		
		embed = self.msg.embeds[0]
		img_buf = await self.draw_image()
		url = await self.ctx.upload_bytes(img_buf.getvalue(), 'image/png', 'pour game')
		embed.set_image(url=url)
		await interaction.message.edit(embed=embed, view=self)

	@discord.ui.button(label='Cancel', style=discord.ButtonStyle.primary, custom_id='cancel_btn', disabled=True, row=0)
	async def cancel_button(self, button: discord.Button, interaction: discord.Interaction):
		if self.state == 1:
			for btn in self.children:
				if isinstance(btn, BottleButton):
					btn.disabled = True if btn.bottle.is_empty() else False
					if btn == self.selected:
						btn.style = discord.ButtonStyle.secondary
					if btn.bottle.is_completed():
						btn.disabled = True

			button.disabled = True
			self.selected = None
			self.state = 0
			await interaction.message.edit(view=self)

	async def next_button_callback(self, interaction):
		self.state = 0
		self.selected = None

		for btn in self.children[:]:
			if isinstance(btn, BottleButton) or btn.custom_id == 'next_lvl_btn':
				self.remove_item(btn)
			elif btn.custom_id == 'cancel_btn':
				btn.disabled = True
				continue
			elif btn.custom_id == 'reset_btn' or btn.custom_id == 'exit_btn':
				btn.disabled = False
				continue

		for i, bottle_data in enumerate(levels[self.level], start=1):
			bottle = Bottle(i, [Liquid(color) for color in bottle_data])
			self.add_item(BottleButton(bottle, label=i, style=discord.ButtonStyle.secondary, row=1+(i-1)//5, disabled=True if bottle.is_empty() else False))

		embed = self.msg.embeds[0]
		embed.description = f'Level : {self.level}'
		img_buf = await self.draw_image()
		url = await self.ctx.upload_bytes(img_buf.getvalue(), 'image/png', 'pour game')
		embed.set_image(url=url)
		await interaction.message.edit(embed=embed, view=self)

# Utility cog
class FileView(discord.ui.View):
	def __init__(self, ctx, full):
		super().__init__()
		self.ctx = ctx
		self.full = full
		self.add = discord.ui.Button(label="Add file", style=discord.ButtonStyle.primary)
		self.done = discord.ui.Button(label="Done", style=discord.ButtonStyle.green)
		self.cancel = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.red)
		self.value = None
		if self.full:
			self.add.disabled = True
		
	def start(self):

		self.add.callback = self.add_callback
		self.done.callback = self.done_callback
		self.cancel.callback = self.cancel_callback

		self.add_item(self.add)
		self.add_item(self.done)
		self.add_item(self.cancel)

	async def interaction_check(self, interaction):
		if interaction.user != self.ctx.author:
			await interaction.response.send_message('This is not your interaction!', ephemeral=True)
			return False

		return True

	async def add_callback(self, interaction):
		self.value = 1
		self.stop()

	async def done_callback(self, interaction):
		self.value = 2
		self.stop()
	
	async def cancel_callback(self, interaction):
		self.value = 3
		self.stop()

class EmbedBuilder(discord.ui.View):
	def __init__(self, ctx):
		super().__init__()
		self.ctx = ctx
		self.msg = None
		self.embed = None

	def check_msg(self, message):
		return message.author == self.ctx.author and message.channel == self.ctx.channel

	@discord.ui.button(emoji='Set title', style=discord.ButtonStyle.primary)
	async def set_title(self, button: discord.ui.Button, interaction: discord.Interaction):
		askm = await self.ctx.send("Type below your embed title")

		while True:
			try:
				message = await self.ctx.bot.wait_for('message', check=self.check_msg, timeout=60)
			except asyncio.TimeoutError:
				await interaction.response.send_message("Timed out.")
				self.stop()
				return

			if len(message.content) > 256:
				await interaction.response.send_message("Embed title can not be more than 256 characters long!")
				continue
			else:
				break

class AnsiMaker(discord.ui.View):
	def __init__(self, ctx, text):
		super().__init__(timeout=None)
		self.ctx = ctx
		self.msg = None
		self.text = text
		self.code = ''
		self.state = {
			'format': {
				'bold': False,
				'underline': False,
			},
			'color': None,
			'bgcolor': None
		}
	
	async def update(self, button: discord.Button | None = None, identifier: str | None = None):
		if identifier:
			for child in self.children:
				if child != button and child.label.startswith(identifier):
					child.style = discord.ButtonStyle.primary

		ansis = ['0']

		state = self.state
		fmt = state['format']

		if fmt['bold'] and fmt['underline']:
			ansis.append('1')
			ansis.append('4')
		elif fmt['bold']:
			ansis.append('1')
		elif fmt['underline']:
			ansis.append('4')

		if state['color']:
			ansis.append(state['color'])
		if state['bgcolor']:
			ansis.append(state['bgcolor'])

		if any([fmt['bold'], fmt['underline'], state['color'], state['bgcolor']]):
			self.code = f"\u001b[{';'.join(ansis)}m"
			await self.msg.edit(f'```ansi\n{self.code}{self.text}\u001b[0m\n```', view=self, allowed_mentions=discord.AllowedMentions.none())
		else:
			self.code = ''
			await self.msg.edit(f'```ansi\n{self.text}\n```', view=self, allowed_mentions=discord.AllowedMentions.none())

	async def interaction_check(self, interaction: discord.Interaction):
		if interaction.user != self.ctx.author:
			await interaction.response.send_message('This is not your interaction!', ephemeral=True)
			return False

		return True

	@discord.ui.button(label='Finish', style=discord.ButtonStyle.success)
	async def finish(self, button: discord.ui.Button, interaction: discord.Interaction):
		await self.ctx.message.reply(f'\`\`\`ansi\n{self.code}{self.text}\u001b[0m\n\`\`\`')

	@discord.ui.button(label='Delete', style=discord.ButtonStyle.danger)
	async def delete(self, button: discord.ui.Button, interaction: discord.Interaction):
		await self.msg.delete()

	@discord.ui.button(label='Bold', style=discord.ButtonStyle.primary)
	async def bolder(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.state['format']['bold']:
			self.state['format']['bold'] = False
			button.style = discord.ButtonStyle.primary
		else:
			self.state['format']['bold'] = True
			button.style = discord.ButtonStyle.danger

		await self.update()

	@discord.ui.button(label='Underline', style=discord.ButtonStyle.primary)
	async def underliner(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.state['format']['underline']:
			self.state['format']['underline'] = False
			button.style = discord.ButtonStyle.primary
		else:
			self.state['format']['underline'] = True
			button.style = discord.ButtonStyle.danger

		await self.update()

	@discord.ui.button(label='T Gray', style=discord.ButtonStyle.primary)
	async def t_gray(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.state['color'] == '30':
			self.state['color'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['color'] = '30'
			button.style = discord.ButtonStyle.danger

		await self.update(button, 'T')

	@discord.ui.button(label='T Red', style=discord.ButtonStyle.primary)
	async def t_red(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.state['color'] == '31':
			self.state['color'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['color'] = '31'
			button.style = discord.ButtonStyle.danger

		await self.update(button, 'T')

	@discord.ui.button(label='T Green', style=discord.ButtonStyle.primary)
	async def t_green(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.state['color'] == '32':
			self.state['color'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['color'] = '32'
			button.style = discord.ButtonStyle.danger

		await self.update(button, 'T')

	@discord.ui.button(label='T Yellow', style=discord.ButtonStyle.primary)
	async def t_yellow(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.state['color'] == '33':
			self.state['color'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['color'] = '33'
			button.style = discord.ButtonStyle.danger

		await self.update(button, 'T')

	@discord.ui.button(label='T Blue', style=discord.ButtonStyle.primary)
	async def t_blue(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.state['color'] == '34':
			self.state['color'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['color'] = '34'
			button.style = discord.ButtonStyle.danger

		await self.update(button, 'T')

	@discord.ui.button(label='T Pink', style=discord.ButtonStyle.primary)
	async def t_pink(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.state['color'] == '35':
			self.state['color'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['color'] = '35'
			button.style = discord.ButtonStyle.danger

		await self.update(button, 'T')

	@discord.ui.button(label='T Cyan', style=discord.ButtonStyle.primary)
	async def t_cyan(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.state['color'] == '36':
			self.state['color'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['color'] = '36'
			button.style = discord.ButtonStyle.danger

		await self.update(button, 'T')

	@discord.ui.button(label='T White', style=discord.ButtonStyle.primary)
	async def t_white(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.state['color'] == '37':
			self.state['color'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['color'] = '37'
			button.style = discord.ButtonStyle.danger

		await self.update(button, 'T')

	@discord.ui.button(label='BG D Blue', style=discord.ButtonStyle.primary)
	async def bg_d_blue(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.state['bgcolor'] == '40':
			self.state['bgcolor'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['bgcolor'] = '40'
			button.style = discord.ButtonStyle.danger

		await self.update(button, 'BG')

	@discord.ui.button(label='BG Orange', style=discord.ButtonStyle.primary)
	async def bg_orange(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.state['bgcolor'] == '41':
			self.state['bgcolor'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['bgcolor'] = '41'
			button.style = discord.ButtonStyle.danger

		await self.update(button, 'BG')

	@discord.ui.button(label='BG Gray 1', style=discord.ButtonStyle.primary)
	async def bg_gray_1(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.state['bgcolor'] == '42':
			self.state['bgcolor'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['bgcolor'] = '42'
			button.style = discord.ButtonStyle.danger

		await self.update(button, 'BG')

	@discord.ui.button(label='BG Gray 2', style=discord.ButtonStyle.primary)
	async def bg_gray_2(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.state['bgcolor'] == '43':
			self.state['bgcolor'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['bgcolor'] = '43'
			button.style = discord.ButtonStyle.danger

		await self.update(button, 'BG')

	@discord.ui.button(label='BG Gray 3', style=discord.ButtonStyle.primary)
	async def bg_gray_3(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.state['bgcolor'] == '44':
			self.state['bgcolor'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['bgcolor'] = '44'
			button.style = discord.ButtonStyle.danger

		await self.update(button, 'BG')

	@discord.ui.button(label='BG Gray 4', style=discord.ButtonStyle.primary)
	async def bg_gray_4(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.state['bgcolor'] == '46':
			self.state['bgcolor'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['bgcolor'] = '46'
			button.style = discord.ButtonStyle.danger

		await self.update(button, 'BG')

	@discord.ui.button(label='BG Indigo', style=discord.ButtonStyle.primary)
	async def bg_indigo(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.state['bgcolor'] == '45':
			self.state['bgcolor'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['bgcolor'] = '45'
			button.style = discord.ButtonStyle.danger

		await self.update(button, 'BG')

	@discord.ui.button(label='BG White', style=discord.ButtonStyle.primary)
	async def bg_white(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.state['bgcolor'] == '47':
			self.state['bgcolor'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['bgcolor'] = '47'
			button.style = discord.ButtonStyle.danger

		await self.update(button, 'BG')

class SounderView(discord.ui.View):
	def __init__(self, ctx, sounder, *, timeout=None):
		super().__init__(timeout=timeout)
		self.ctx = ctx
		self.sounder: Sounder = sounder
		self.msg = None
		for audio in audios:
			btn = discord.ui.Button(label=audio, style=discord.ButtonStyle.secondary)
			btn.callback = self.create_callback(audio)
			self.add_item(btn)

	async def interaction_check(self, interaction: discord.Interaction):
		if interaction.user != self.ctx.author:
			await interaction.response.send_message('This is not your interaction!', ephemeral=True)
			return False

		return True

	@discord.ui.button(label='Finish', style=discord.ButtonStyle.success, disabled=True)
	async def finish(self, button: discord.ui.Button, interaction: discord.Interaction):
		await interaction.response.defer()
		buf = await self.sounder.export()

		view = DeleteView(self.ctx)
		view.message = await self.ctx.message.reply(', '.join(self.sounder.sounds), file=discord.File(buf, 'sounder.mp3'), view=view, mention_author=False)

	@discord.ui.button(label='Clear', style=discord.ButtonStyle.primary, disabled=True)
	async def clear(self, button: discord.ui.Button, interaction: discord.Interaction):
		await self.sounder.init()
		self.sounder.count_sound = 0
		self.sounder.position = 0
		self.sounder.sounds = []
		
		for btn in self.children:
			if btn.label in ['Finished', 'Clear']:
				btn.disabled = True
			else:
				btn.disabled = False

		await self.msg.edit(content=', '.join(self.sounder.sounds), view=self, allowed_mentions=discord.AllowedMentions.none())

	@discord.ui.button(label='Delete', style=discord.ButtonStyle.danger)
	async def delete(self, button: discord.ui.Button, interaction: discord.Interaction):
		await self.msg.delete()

	def create_callback(self, sound):

		async def callback(interaction):
			await interaction.response.defer()
			await self.sounder.append_sound(sound)
			for btn in self.children:
				if btn.label in ['Finish', 'Clear']:
					btn.disabled = False
				else:
					if self.sounder.position > 15:
						btn.disabled = True
			
			return await self.msg.edit(content=', '.join(self.sounder.sounds), view=self, allowed_mentions=discord.AllowedMentions.none())

		return callback

class PollButton(discord.ui.Button):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.count = 0

class PollView(discord.ui.View):
	nums = [f'{num}\U0000fe0f\U000020e3' for num in (
		"\U00000031", "\U00000032", "\U00000033", "\U00000034", "\U00000035", 
		"\U00000036", "\U00000037", "\U00000038", "\U00000039")] + ["\U0001f51f"
	]
	def __init__(self, ctx, title, timeout, args):
		super().__init__(timeout=None)
		self.created_at = dt.datetime.now()
		self.ctx = ctx
		self.title = title
		self.timeout = timeout
		self.args = {arg: set() for arg in args}
		self.btns = {}
		self.ended = False
		self.message = None
		self.c = None
		self.cd = commands.CooldownMapping.from_cooldown(1, 3, lambda i: i.user)
		self.ping_result = []
		
		for arg in args:
			btn = PollButton(label=f'{arg} (0)', style=discord.ButtonStyle.primary)
			btn.callback = self.create_callback(arg)
			self.btns[arg] = btn
			self.add_item(btn)

		cancel_btn = discord.ui.Button(emoji="<:redx:827600701768597554>", style=discord.ButtonStyle.red, row=4)
		cancel_btn.callback = self.cancel
		self.add_item(cancel_btn)

		ping_btn = discord.ui.Button(label='Ping me the result', emoji='\U0001f4cc', style=discord.ButtonStyle.secondary, row=4)
		ping_btn.callback = self.ping
		self.add_item(ping_btn)

	async def interaction_check(self, interaction):
		retry_after = self.cd.update_rate_limit(interaction)
		if retry_after:
			await interaction.response.send_message(f'Slow down! You\'re on cooldown. Retry after {int(retry_after)}s', ephemeral=True)
			return False
		return True

	async def start(self):
		self.c = self.ctx.bot.c
		self.message = await self.ctx.reply(embed=self.create_embed(), view=self, mention_author=False)

		await asyncio.sleep(self.timeout)
		if not self.ended:
			await self.end()

	def create_embed(self):
		text = '\n'.join(f'{self.nums[i]} `{choice}`: [`{len(choosers)}`] {", ".join(u.display_name for u in list(choosers)[:3]) + (f", and **{len(choosers)-3}** more" if len(choosers) > 3 else "")}' for i, (choice, choosers) in enumerate(self.args.items()))
		
		ends = self.created_at + dt.timedelta(seconds=self.timeout)
		text += f'\n\n*Poll ends on {discord.utils.format_dt(ends, "F")} ({discord.utils.format_dt(ends, "R")})*'

		embed = discord.Embed(title=self.title, description=text, color=self.c)
		embed.set_author(name=f"{self.ctx.author} has created a poll", icon_url=self.ctx.author.display_avatar.url)
		embed.set_footer(text=f'Configured timeout: {humanize.naturaldelta(dt.timedelta(seconds=self.timeout))}')

		return embed

	def create_callback(self, arg):
		async def callback(interaction):
			for choice, choosers in self.args.items():
				if interaction.user in choosers and choice == arg:
					for choice in self.args:
						if interaction.user in self.args[choice]:
							self.args[choice].remove(interaction.user)
							btn = self.btns.get(arg)
							btn.count -= 1
							btn.label = f"{arg} ({btn.count})"
							break
					break
			else:
				for choice, choosers in self.args.items():
					try:
						choosers.remove(interaction.user)
						btn = self.btns.get(choice)
						btn.count -= 1
						btn.label = f"{arg} ({btn.count})"
					except KeyError:
						...
				self.args[arg].add(interaction.user)

				btn = self.btns.get(arg)
				btn.count += 1
				btn.label = f"{arg} ({btn.count})"

			await self.message.edit(embed=self.create_embed(), view=self, allowed_mentions=discord.AllowedMentions.none())
			
		return callback

	async def cancel(self, interaction):
		if interaction.user == self.ctx.author:
			await self.end()
		else:
			await interaction.response.send_message('Only poll creator can stop this poll.', ephemeral=True)

	async def ping(self, interaction):
		if interaction.user not in self.ping_result:
			self.ping_result.append(interaction.user)
			await interaction.response.send_message(f'Okay {interaction.user.mention}, you will be dmed when the poll ends.', ephemeral=True)
		else:
			self.ping_result.remove(interaction.user)
			await interaction.response.send_message(f'Okay {interaction.user.mention}, you won\'t be dmed when the poll ends.', ephemeral=True)
	
	async def end(self):
		self.ended = True
		self.stop()

		winners = [choice for choice, choosers in self.args.items() if len(choosers) == len(max(self.args.values(), key=lambda c: len(c)))]
		text = '\n'.join(f'{self.nums[i]} `{choice}`: [`{len(choosers)}`] {", ".join(u.display_name for u in list(choosers)[:3]) + (f", and `{len(choosers)-3}` more" if len(choosers) > 3 else "")}' for i, (choice, choosers) in enumerate(self.args.items()))

		embed = discord.Embed(title=self.title, description=text, color=self.c)
		embed.add_field(name=f'The winner{[" is", "s are"][len(winners)>1]} **{", ".join(winners)}**', value=f'\n\n*Poll ended on {discord.utils.format_dt(dt.datetime.now(), "F")} ({discord.utils.format_dt(dt.datetime.now(), "R")})*')
		embed.set_author(name=f"{self.ctx.author} has created a poll", icon_url=self.ctx.author.display_avatar.url)

		for child in self.children[-2:]:
			child.disabled = True

		for choice, btn in self.btns.items():
			btn.disabled = True
			if choice in winners:
				btn.style = discord.ButtonStyle.success
			else:
				btn.style = discord.ButtonStyle.secondary
		
		reference_view = discord.ui.View(timeout=None)
		reference_view.add_item(discord.ui.Button(label='Jump to message', url=self.message.jump_url))

		for user in self.ping_result:
			try:
				await user.send(f'{user.mention}, poll `{self.title}` is ended.', view=reference_view)
			except:
				...
				
		await self.message.edit(embed=embed, view=self)
		
class CariResults(discord.ui.View):
	def __init__(self, ctx, msg, data):
		super().__init__()
		self.ctx = ctx
		self.msg = msg
		self.table_1_title = data[0][0]
		self.table_1_data = data[0][1]
		self.table_2_title = data[1][0]
		self.table_2_data = data[1][1]
		self.button_1 = discord.ui.Button(style=discord.ButtonStyle.primary, label=self.table_1_title)
		self.button_2 = discord.ui.Button(style=discord.ButtonStyle.primary, label=self.table_2_title)
		self.button_1.callback = self.button_1_callback
		self.button_2.callback = self.button_2_callback
		self.add_item(self.button_1)
		self.add_item(self.button_2)

	async def button_1_callback(self, interaction: discord.Interaction):
		table = tabulate(self.table_1_data, headers='firstrow', tablefmt='pretty')
		s = StringIO()
		s.write(self.table_1_title + '\n')
		s.write(table)
		s.seek(0)

		self.button_1.disabled = True
		await self.msg.edit(view=self)
		await self.msg.reply(file=discord.File(s, f'{self.table_1_title}.txt'))

	async def button_2_callback(self, interaction: discord.Interaction):
		table = tabulate(self.table_2_data, headers='firstrow', tablefmt='pretty')
		s = StringIO()
		s.write(self.table_2_title + '\n')
		s.write(table)
		s.seek(0)

		self.button_2.disabled = True
		await self.msg.edit(view=self)
		await self.msg.reply(file=discord.File(s, f'{self.table_2_title}.txt'))

class CariMenu(discord.ui.Select):
	def __init__(self, ctx, session: Session, mapping, tipe, **kwargs):
		super().__init__(placeholder=f"Hasil pencarian {tipe}", **kwargs)
		self.ctx = ctx
		self.session = session
		self.mapping = mapping
		self.tipe = tipe
		if not mapping:
			self.disabled = True
			self.placeholder = f"Tidak ada {tipe}"
			self.options.append(discord.SelectOption(label="Tidak ada hasil."))
		for i, item in enumerate(mapping[:25]):
			self.options.append(
				discord.SelectOption(label=item[0], value=i, description=item[1])
			)
	
	@executor_function
	def parse_source(self, source):
		soup = BeautifulSoup(source, 'html.parser')

		biodata_rows = soup.find('div', attrs={'class': 'single-blog-box'}).find_all('tr')
		biodata_table = []
		for row in biodata_rows:
			biodata_row = []
			for i, cell in enumerate(row.find_all('td')):
				if i == 0:
					text = f'`{cell.get_text().strip():>25}'
				elif i == 1:
					text = cell.get_text().strip()
				elif i == 2:
					text = f'{cell.get_text().strip():<25}`'
				biodata_row.append(text)
			if len(biodata_row) == 3:
				biodata_table.append(' '.join(biodata_row))

		table_1 = soup.find('div', attrs={'id': 'home'})
		table_1_title = table_1.find('h3').get_text()
		table_1_rows = table_1.find_all('tr')
		
		table_1_data = [[th.get_text() for th in table_1.find_all('th')]]
		for row in table_1_rows:
			row_data = []
			for cell in row.find_all('td'):
				row_data.append(cell.get_text())
			if row_data:
				table_1_data.append(row_data)

		table_2 = soup.find('div', attrs={'id': 'menu1'})
		table_2_title = table_2.find('h3').get_text()
		table_2_rows = table_2.find_all('tr')
		
		table_2_data = [[th.get_text() for th in table_2.find_all('th')]]
		for row in table_2_rows:
			row_data = []
			for cell in row.find_all('td'):
				row_data.append(cell.get_text())
			if row_data:
				table_2_data.append(row_data)

		return biodata_table, [
			[table_1_title, table_1_data],
			[table_2_title, table_2_data],
		]

	async def callback(self, interaction: discord.Interaction):
		chosen = self.mapping[int(self.values[0])]
		await interaction.response.edit_message(content=f'Mengambil data {self.tipe} {chosen[0]}...', view=None)

		await chosen[2].click()
		await asyncio.sleep(3)

		# buf = await self.session.get_screenshot()
		source = await self.session.get_page_source()

		biodata, data = await self.parse_source(source)

		embed = discord.Embed(title=f'Biodata {self.tipe.capitalize()}', description='\n'.join(biodata), color=self.ctx.bot.c)

		result_view = CariResults(self.ctx, self.view.msg, data)
		await self.view.msg.edit(content=None, embed=embed, view=result_view, allowed_mentions=discord.AllowedMentions.none())

		await stop_session(self.session)

# Api cog
class ConfirmView(discord.ui.View):

	def __init__(self, ctx):
		super().__init__()
		self.message = None
		self.value = None
		self.ctx = ctx

	@discord.ui.button(emoji="<:check:827600687926870046>", style=discord.ButtonStyle.green)
	async def confirm(self, button, interaction):
		self.value = True
		await self.message.delete()
		self.stop()

	@discord.ui.button(emoji="<:redx:827600701768597554>", style=discord.ButtonStyle.red)
	async def cancel(self, button, interaction):
		self.value = False
		await self.message.delete()
		self.stop()

	async def interaction_check(self, interaction):
		if interaction.user != self.ctx.author:
			await interaction.response.send_message("This is not your interaction!", ephemeral=True)
			return False
		
		return True

class ConfirmationView(discord.ui.View):
	def __init__(self, ctx):
		super().__init__()
		self.ctx = ctx
		self.message = None
		self.value = None

	async def ask(self, message="\u200b", embeds=None):
		yes_button = discord.ui.Button(emoji="<:check:827600687926870046>", style=discord.ButtonStyle.green)
		no_button = discord.ui.Button(emoji="<:redx:827600701768597554>", style=discord.ButtonStyle.red)
		yes_button.callback = self.yes_callback
		no_button.callback = self.no_callback

		self.add_item(yes_button)
		self.add_item(no_button)

		self.message = await self.ctx.reply(message, embeds=embeds, view=self, mention_author=False)
		await self.wait()
		await self.message.delete()
		return self.value

	async def interaction_check(self, interaction):
		if interaction.user != self.ctx.author:
			await interaction.response.send_message("This is not your interaction!", ephemeral=True)
			return False
		
		return True

	async def yes_callback(self, interaction):
		self.value = True
		self.stop()

	async def no_callback(self, interaction):
		self.value = False
		self.stop()

class DeleteView(discord.ui.View):
	def __init__(self, ctx):
		super().__init__()
		self.message = None
		self.ctx = ctx

	@discord.ui.button(emoji="<:redx:827600701768597554>", style=discord.ButtonStyle.red)
	async def cancel(self, button, interaction):
		await self.message.delete()
		self.stop()

	async def interaction_check(self, interaction):
		if interaction.user != self.ctx.author:
			await interaction.response.send_message("This is not your interaction!", ephemeral=True)
			return False
		
		return True

class AkiView(discord.ui.View):
	def __init__(self, ctx):
		super().__init__()
		self.ctx = ctx
		self.result = None

	@discord.ui.button(emoji='\U0001f1fe', style=discord.ButtonStyle.primary)
	async def yes(self, button: discord.ui.Button, interaction: discord.Interaction):
		self.result = 'yes'
		self.stop()

	@discord.ui.button(emoji='\U0001f1f3', style=discord.ButtonStyle.primary)
	async def no(self, button: discord.ui.Button, interaction: discord.Interaction):
		self.result = 'no'
		self.stop()

	@discord.ui.button(emoji='\U0001f937', style=discord.ButtonStyle.primary)
	async def idk(self, button: discord.ui.Button, interaction: discord.Interaction):
		self.result = 'idk'
		self.stop()

	@discord.ui.button(emoji='\U0001f4ad', style=discord.ButtonStyle.primary)
	async def p(self, button: discord.ui.Button, interaction: discord.Interaction):
		self.result = 'p'
		self.stop()
	
	@discord.ui.button(emoji='\U0001f5ef', style=discord.ButtonStyle.primary)
	async def pn(self, button: discord.ui.Button, interaction: discord.Interaction):
		self.result = 'pn'
		self.stop()
	
	@discord.ui.button(emoji='\U0001f6d1', style=discord.ButtonStyle.red)
	async def exit(self, button: discord.ui.Button, interaction: discord.Interaction):
		self.result = 'exit'
		self.stop()

	async def interaction_check(self, interaction):
		if interaction.user != self.ctx.author:
			await interaction.response.send_message('This is not your interaction!', ephemeral=True)
			return False

		return True
