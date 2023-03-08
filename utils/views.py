import asyncio
import datetime as dt
import discord
import humanize
import importlib
import numpy as np
from io import StringIO, BytesIO
from tabulate import tabulate
from bs4 import BeautifulSoup
from jishaku.functools import executor_function
from PIL import Image, ImageDraw, ImageFont
from arsenic import stop_session, Session
from discord.ext import commands

from utils import pour_puzzle, sounder
from utils.imaging import isometric_func, liquid

importlib.reload(pour_puzzle)
importlib.reload(sounder)

from utils.pour_puzzle import Liquid, Bottle, levels
from utils.sounder import Sounder, audios
from utils.imaging import roomy_func

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
			embed.set_thumbnail(url=getattr(cog, 'thumbnail', None))
			embed.add_field(name=f"-=: {cog.qualified_name} :=-", value=cog.description, inline=False)

			for command in chunk:
				embed.add_field(name=f"`{command.name}`", value=command.short_doc or "-", inline=True)

			if len(chunk) % 3 != 0:
				for _ in range(3 - len(chunk) % 3):
					embed.add_field(name="\u200b", value="\u200b", inline=True)

			embed.add_field(name="\u200b", value=f"Use `{self.ctx.clean_prefix}help [command]` for more info on a command.", inline=False)
			embeds.append(embed)

		return embeds
		
	async def change_cog_to(self, cog, interaction=None):
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

		if not self.message:
			self.message = await self.ctx.reply(embed=self.embeds[0], view=self)
		else:
			await interaction.response.edit_message(embed=self.embeds[0], view=self)

	async def button_first_callback(self, interaction):
		if self.index == 0:
			return

		self.index = 0
		await self.update(interaction)

	async def button_previous_callback(self, interaction):
		if self.index == 0:
			return

		self.index -= 1
		await self.update(interaction)

	async def button_index_callback(self, interaction):
		await self.message.delete()
		self.stop()

	async def button_next_callback(self, interaction):
		if self.index == self.length-1:
			return

		self.index += 1
		await self.update(interaction)

	async def button_last_callback(self, interaction):
		if self.index == self.length-1:
			return

		self.index = self.length-1
		await self.update(interaction)
		
	async def update(self, interaction):
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

		await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

class HelpMenu(discord.ui.Select):
	def __init__(self, view):
		super().__init__(placeholder='Select Category')
		self.parent_view = view
		self.previous = None

	async def callback(self, interaction: discord.Interaction):
		if self.previous == self.values[0]:
			return
		
		for option in self.options:
			option.default = False
			if option.value == self.values[0]:
				option.default = True
		
		self.previous = self.values[0]

		cog = discord.utils.get(self.parent_view.mapping, qualified_name=self.values[0])
		
		await self.parent_view.change_cog_to(cog, interaction)

class EndpointView(discord.ui.View):
	def __init__(self, results):
		super().__init__()
		self.results = results

	@discord.ui.button(label='Show result', style=discord.ButtonStyle.primary)
	async def show(self, interaction, button):
		button.label = 'Result sent!'
		button.disabled = True
		
		await interaction.response.edit_message(view=self)
		await interaction.followup.send(self.results)

class ApiKeyView(discord.ui.View):
	def __init__(self, ctx: commands.Context):
		super().__init__()
		self.ctx = ctx

class SupportServerView(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Support Server', url='https://discord.gg/uwKsfMzGJA'))
		self.add_item(discord.ui.Button(label='Try API', url='https://jeyy.xyz/try'))

# Isometric cog
class Switch(discord.ui.View):
	def __init__(self, ctx):
		super().__init__()
		self.ctx = ctx
		self.file_1 = None
		self.file_2 = None
		self.text = None
		self.state = 0
		self.button = None
		self.message = None

	async def switch(self, file_1, file_2, text=None):
		self.file_1 = file_1
		self.file_2 = file_2
		self.text = text

		self.button = discord.ui.Button(emoji="<:lever:843768316002172958>", style=discord.ButtonStyle.red)
		self.button.callback = self.callback

		self.add_item(self.button)
		self.message = await self.ctx.reply(self.text, file=file_1, view=self, allowed_mentions=discord.AllowedMentions.none())

	async def callback(self, interaction):
		if interaction.user != self.ctx.author:
			return await interaction.response.send_message("This is not your interaction!", ephemeral=True)

		if not self.state:
			self.state = 1
			self.button.style = discord.ButtonStyle.green
			self.file_2.fp.seek(0)
			await interaction.response.edit_message(content=self.text, attachments=[self.file_2], view=self)
		else:
			self.state = 0
			self.button.style = discord.ButtonStyle.red
			self.file_1.fp.seek(0)
			await interaction.response.edit_message(content=self.text, attachments=[self.file_1], view=self)

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

	async def update_view(self, interaction):
		await interaction.response.edit_message(view=self)

	async def on_timeout(self):
		self.clear_items()
		await self.message.edit(view=self)

	async def render_callback(self, interaction):
		self.render_button.disabled = True
		self.render_button.label = "Rendered!"
		self.render_button.style = discord.ButtonStyle.grey

		if self.gif_button:
			self.remove_item(self.gif_button)

		await self.update_view(interaction)

		cmd = self.ctx.bot.get_command("isometric")
		await cmd(self.ctx, blocks=self.build_search["build"])

	async def gif_callback(self, interaction):
		self.render_button.disabled = True
		self.render_button.label = "Rendered!"
		self.render_button.style = discord.ButtonStyle.grey
		self.remove_item(self.gif_button)

		await self.update_view(interaction)

		cmd = self.ctx.bot.get_command("isometric")
		await cmd(self.ctx, blocks=self.build_search["build"]+' gif')

	async def info_callback(self, interaction):
		self.info_button.disabled = True
		self.info_button.label = "Info sent!"

		await self.update_view(interaction)

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

		await self.update_view(interaction)

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

	async def pressed(self, interaction, button):
		if interaction.user != self.ctx.author:
			return await interaction.response.send_message('You can\'t use this button!', ephemeral=True)

		if button.kind:
			for child in self.children:
				if child == button:
					child.disabled = True
					child.style = discord.ButtonStyle.primary

			self.board[button.idx//5][button.idx%5] = 1

			buf = await self.draw_board()
			board_file = discord.File(buf, 'board.png')

			embed = self.msg.embeds[0]
			embed.set_image(url='attachment://board.png')

			if self.board == self.ans_map:
				embed.description = 'You\'ve won!'
				self.clear_items()
			await interaction.response.edit_message(attachments=[board_file], embed=embed, view=self)
		else:
			for child in self.children:
				if child.kind:
					child.style = discord.ButtonStyle.primary
				else:
					child.style = discord.ButtonStyle.danger
				child.disabled = True
			await interaction.response.edit_message(view=self)

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
			await interaction.response.edit_message(view=self.view)

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

			img_file = discord.File(img_buf, 'pour_game.png')
			embed.set_image(url='attachment://pour_game.png')

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

			await interaction.response.edit_message(embed=embed, attachments=[img_file], view=self.view)

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
				draw.rectangle((btn.bottle.num*50-20, 50, 16+btn.bottle.num*50, 150), None, 'black', 3)
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
	async def exit_button(self, interaction: discord.Interaction, button: discord.Button):
		for btn in self.children:
			btn.disabled = True
		
		button.label = 'Exited'
		await interaction.response.edit_message(view=self)

		self.stop()

	@discord.ui.button(label='Reset', style=discord.ButtonStyle.danger, custom_id='reset_btn', row=0)
	async def reset_button(self, interaction: discord.Interaction, button: discord.Button):
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

		img_file = discord.File(img_buf, 'pour_game.png')
		embed.set_image(url='attachment://pour_game.png')

		await interaction.response.edit_message(embed=embed, attachments=[img_file], view=self)

	@discord.ui.button(label='Cancel', style=discord.ButtonStyle.primary, custom_id='cancel_btn', disabled=True, row=0)
	async def cancel_button(self, interaction: discord.Interaction, button: discord.Button):
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
			await interaction.response.edit_message(view=self)

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
		img_file = discord.File(img_buf, 'pour_game.png')
		
		embed.set_image(url='attachment://pour_game.png')
		await interaction.response.edit_message(embed=embed, attachments=[img_file], view=self)

class BlockSelector(discord.ui.Select):
	def __init__(self, selector_pos):
		options = [
			discord.SelectOption(label=f'Grass Block', value='1', default=True),
			discord.SelectOption(label=f'Water', value='2'),
			discord.SelectOption(label=f'Sand Block', value='3'),
			discord.SelectOption(label=f'Stone Block', value='4'),
			discord.SelectOption(label=f'Wood Planks', value='5'),
			discord.SelectOption(label=f'Glass Block', value='6'),
			discord.SelectOption(label=f'Redstone Block', value='7'),
			discord.SelectOption(label=f'Brick Block', value='9'),
			discord.SelectOption(label=f'Iron Block', value='8'),
			discord.SelectOption(label=f'Gold Block', value='g'),
			discord.SelectOption(label=f'Diamond Block', value='d'),
			discord.SelectOption(label=f'Purple Block', value='p'),
			discord.SelectOption(label=f'Coal Block', value='c'),
			discord.SelectOption(label=f'Leaf Block', value='l'),
			discord.SelectOption(label=f'Wooden Log', value='o'),
			discord.SelectOption(label=f'Hay Bale', value='h'),
			discord.SelectOption(label=f'Poppy', value='y'),
			discord.SelectOption(label=f'Cake', value='k'),
			discord.SelectOption(label=f'Lava', value='v'),
		]
		super().__init__(options=options, row=0)

	async def callback(self, interaction):
		self.view.block = self.values[0]
		for option in self.options:
			option.default = False
			if option.value == self.values[0]:
				option.default = True

		await interaction.response.edit_message(view=self.view)

class InteractiveIsoView(discord.ui.View):
	block_names = {
		'1': 'Grass Block',
		'2': 'Water',
		'3': 'Sand Block',
		'4': 'Stone Block',
		'5': 'Wooden Planks',
		'6': 'Glass Block',
		'7': 'Redstone Block',
		'8': 'Iron Block',
		'9': 'Brick Block',
		'g': 'Gold Block',
		'p': 'Purple Block',
		'd': 'Diamond Block',
		'c': 'Coal Block',
		'l': 'Leaf Block',
		'o': 'Wooden Log',
		'h': 'Hay Bale',
		'v': 'Lava',
		'y': 'Poppy',
		'k': 'Cake'
	}
	def __init__(self, ctx, shape = [50, 50, 50], selector_pos = None):
		super().__init__(timeout=None)
		self.ctx = ctx
		self.box = np.zeros(shape, np.uint8).astype(str)
		self.block = '1'
		self.selector_pos = selector_pos or [i//2 for i in shape]
		self.prev_pos = None
		self.message = None
		self.block_selector = BlockSelector(self.selector_pos)
		self.n_blocks = 0
		self.add_item(self.block_selector)

		self.selatan_btn = discord.ui.Button(emoji='<:arrow_s:981825970703056916>', style=discord.ButtonStyle.secondary, row=1)
		self.selatan_btn.callback = self.selatan_arrow
		self.add_item(self.selatan_btn)

		self.up_btn = discord.ui.Button(emoji='<:arrow_up:981825975170007090>', style=discord.ButtonStyle.secondary, row=1)
		self.up_btn.callback = self.up_arrow
		self.add_item(self.up_btn)

		self.barat_btn = discord.ui.Button(emoji='<:arrow_b:981825966278058004>', style=discord.ButtonStyle.secondary, row=1)
		self.barat_btn.callback = self.barat_arrow
		self.add_item(self.barat_btn)

		self.destroy_btn = discord.ui.Button(emoji='\U0001f4a5', style=discord.ButtonStyle.danger, disabled=True, row=2)
		self.destroy_btn.callback = self.destroy
		self.add_item(self.destroy_btn)

		self.place_btn = discord.ui.Button(emoji='<:minecraft:638603467358994442>', style=discord.ButtonStyle.success, row=2)
		self.place_btn.callback = self.place
		self.add_item(self.place_btn)

		self.finish_btn = discord.ui.Button(label='finish', style=discord.ButtonStyle.primary, disabled=True, row=2)
		self.finish_btn.callback = self.finish
		self.add_item(self.finish_btn)

		self.timur_btn = discord.ui.Button(emoji='<:arrow_t:981825973492277248>', style=discord.ButtonStyle.secondary, row=3)
		self.timur_btn.callback = self.timur_arrow
		self.add_item(self.timur_btn)

		self.down_btn = discord.ui.Button(emoji='<:arrow_down:981825966433239050>', style=discord.ButtonStyle.secondary, row=3)
		self.down_btn.callback = self.down_arrow
		self.add_item(self.down_btn)

		self.utara_btn = discord.ui.Button(emoji='<:arrow_u:981825975216136192>', style=discord.ButtonStyle.secondary, row=3)
		self.utara_btn.callback = self.utara_arrow
		self.add_item(self.utara_btn)

	async def interaction_check(self, interaction):
		if interaction.user != self.ctx.author:
			await interaction.response.send_message("You can't use this button!", ephemeral=True)
			return False
		
		return True

	async def update(self, interaction: discord.Interaction):
		self.destroy_btn.disabled = self.box[tuple(self.selector_pos)] == '0'
		self.finish_btn.disabled = np.all(self.box == '0')

		code = '- '.join([' '.join([''.join(row) for row in lay]) for lay in self.box])
		if '2' in code or 'v' in code:
			code = liquid(code)

		buf, c = await isometric_func(code.split(), self.selector_pos)
		c -= 1
		buf_file = discord.File(buf, 'interactive_iso.png')
		
		await interaction.response.edit_message(content=f"`{tuple(reversed(self.selector_pos))}::rendered {c} block{['', 's'][c > 1]}`\n\u200b", attachments=[buf_file], view=self)

	async def selatan_arrow(self, interaction):
		if self.selector_pos[2] > 0:
			self.utara_btn.disabled = False
		self.selector_pos[2] -= 1
		if self.selector_pos[2] == 0:
			self.selatan_btn.disabled = True
		
		await self.update(interaction)

	async def up_arrow(self, interaction):
		if self.selector_pos[0] > 0:
			self.down_btn.disabled = False
		self.selector_pos[0] += 1
		if self.selector_pos[0] == self.box.shape[0] - 1:
			self.up_btn.disabled = True
		
		await self.update(interaction)

	async def barat_arrow(self, interaction):
		if self.selector_pos[1] > 0:
			self.timur_btn.disabled = False
		self.selector_pos[1] -= 1
		if self.selector_pos[1] == 0:
			self.barat_btn.disabled = True
		
		await self.update(interaction)

	async def destroy(self, interaction):

		self.box[tuple(self.selector_pos)] = '0'

		await self.update(interaction)

	async def place(self, interaction):

		self.box[tuple(self.selector_pos)] = self.block

		await self.update(interaction)

	async def finish(self, interaction: discord.Interaction):

		code = '- '.join([' '.join([''.join(row) for row in lay]) for lay in self.box])

		if '2' in code or 'v' in code:
			code = liquid(code)

		buf, _ = await isometric_func(code.split())
		await self.ctx.reply(file=discord.File(buf, 'interactive_iso.png'), mention_author=False)

		for child in self.children[:]:
			child.disabled = True
		await interaction.response.edit_message(view=self)

		self.stop()

	async def timur_arrow(self, interaction):
		if self.selector_pos[1] < self.box.shape[1] - 1:
			self.barat_btn.disabled = False
		self.selector_pos[1] += 1
		if self.selector_pos[1] == self.box.shape[1] - 1:
			self.timur_btn.disabled = True
		
		await self.update(interaction)

	async def down_arrow(self, interaction):
		if self.selector_pos[0] < self.box.shape[0] - 1:
			self.up_btn.disabled = False
		self.selector_pos[0] -= 1
		if self.selector_pos[0] == 0:
			self.down_btn.disabled = True
		
		await self.update(interaction)

	async def utara_arrow(self, interaction):
		if self.selector_pos[2] < self.box.shape[2] - 1:
			self.selatan_btn.disabled = False
		self.selector_pos[2] += 1
		if self.selector_pos[2] == self.box.shape[2] - 1:
			self.utara_btn.disabled = True
		
		await self.update(interaction)

class RoomyView(discord.ui.View):
	def __init__(self, ctx):
		self.ctx = ctx
		self.floor_tex = 'white'
		self.wall_tex = 'brown'
		self.avatar = None
		self.message = None

	async def interaction_check(self, interaction):
		if interaction.user != self.ctx.author:
			await interaction.response.send_message('This is not your interaction!', ephemeral=True)
			return False

		return True

	async def update(self):
		if not self.avatar:
			self.avatar = await self.ctx.to_image()
		buf = await roomy_func(self.avatar, self.floor_tex, self.wall_tex)
		url = await self.ctx.upload_bytes(buf.getvalue(), 'image/png', 'roomy')
		await self.message.edit(content=url)

	async def update_floor(self, tex):
		self.floor_tex = tex

		for child in self.children[:]:
			if child.custom_id.startswith('floor'):
				...

	@discord.ui.button(label='Finish', style=discord.ButtonStyle.success)
	async def finish(self, interaction, button):
		...

	@discord.ui.button(label='Floor: white', disabled=True, custom_id='floor white', style=discord.ButtonStyle.primary, row=1)
	async def floor_white(self, interaction, button):
		self.floor_tex = 'white'


	@discord.ui.button(label='Floor: red', custom_id='floor red', style=discord.ButtonStyle.secondary, row=1)
	async def floor_red(self, interaction, button):
		...

	@discord.ui.button(label='Floor: brown', custom_id='floor brown', style=discord.ButtonStyle.secondary, row=1)
	async def floor_brown(self, interaction, button):
		...

	@discord.ui.button(label='Floor: tan', custom_id='floor tan', style=discord.ButtonStyle.secondary, row=1)
	async def floor_tan(self, interaction, button):
		...

	@discord.ui.button(label='Floor: Custom', custom_id='floor custom', style=discord.ButtonStyle.secondary, row=1)
	async def floor_custom(self, interaction, button):
		...

	# @discord.ui.button(label='', style=discord.ButtonStyle.secondary)
	# async def (self, button, interaction):
	# 	...

	# @discord.ui.button(label='', style=discord.ButtonStyle.secondary)
	# async def (self, button, interaction):
	# 	...

	# @discord.ui.button(label='', style=discord.ButtonStyle.secondary)
	# async def (self, button, interaction):
	# 	...

	# @discord.ui.button(label='', style=discord.ButtonStyle.secondary)
	# async def (self, button, interaction):
	# 	...

	# @discord.ui.button(label='', style=discord.ButtonStyle.secondary)
	# async def (self, button, interaction):
	# 	...


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
	async def set_title(self, interaction: discord.Interaction, button: discord.ui.Button):
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
	
	async def update(self, interaction: discord.Interaction, button: discord.Button | None = None, identifier: str | None = None):
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
			await interaction.response.edit_message(content=f'```ansi\n{self.code}{self.text}\u001b[0m\n```', view=self)
		else:
			self.code = ''
			await interaction.response.edit_message(content=f'```ansi\n{self.text}\n```', view=self)
			
	async def interaction_check(self, interaction: discord.Interaction):
		if interaction.user != self.ctx.author:
			await interaction.response.send_message('This is not your interaction!', ephemeral=True)
			return False

		return True

	@discord.ui.button(label='Finish', style=discord.ButtonStyle.success)
	async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.send_message(f'\`\`\`ansi\n{self.code}{self.text}\u001b[0m\n\`\`\`', view=DeleteView(interaction.user))
		
	@discord.ui.button(label='Delete', style=discord.ButtonStyle.danger)
	async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
		await self.msg.delete()

	@discord.ui.button(label='Bold', style=discord.ButtonStyle.primary)
	async def bolder(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.state['format']['bold']:
			self.state['format']['bold'] = False
			button.style = discord.ButtonStyle.primary
		else:
			self.state['format']['bold'] = True
			button.style = discord.ButtonStyle.danger

		await self.update(interaction)

	@discord.ui.button(label='Underline', style=discord.ButtonStyle.primary)
	async def underliner(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.state['format']['underline']:
			self.state['format']['underline'] = False
			button.style = discord.ButtonStyle.primary
		else:
			self.state['format']['underline'] = True
			button.style = discord.ButtonStyle.danger

		await self.update(interaction)

	@discord.ui.button(label='T Gray', style=discord.ButtonStyle.primary)
	async def t_gray(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.state['color'] == '30':
			self.state['color'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['color'] = '30'
			button.style = discord.ButtonStyle.danger

		await self.update(interaction, button, 'T')

	@discord.ui.button(label='T Red', style=discord.ButtonStyle.primary)
	async def t_red(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.state['color'] == '31':
			self.state['color'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['color'] = '31'
			button.style = discord.ButtonStyle.danger

		await self.update(interaction, button, 'T')

	@discord.ui.button(label='T Green', style=discord.ButtonStyle.primary)
	async def t_green(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.state['color'] == '32':
			self.state['color'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['color'] = '32'
			button.style = discord.ButtonStyle.danger

		await self.update(interaction, button, 'T')

	@discord.ui.button(label='T Yellow', style=discord.ButtonStyle.primary)
	async def t_yellow(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.state['color'] == '33':
			self.state['color'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['color'] = '33'
			button.style = discord.ButtonStyle.danger

		await self.update(interaction, button, 'T')

	@discord.ui.button(label='T Blue', style=discord.ButtonStyle.primary)
	async def t_blue(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.state['color'] == '34':
			self.state['color'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['color'] = '34'
			button.style = discord.ButtonStyle.danger

		await self.update(interaction, button, 'T')

	@discord.ui.button(label='T Pink', style=discord.ButtonStyle.primary)
	async def t_pink(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.state['color'] == '35':
			self.state['color'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['color'] = '35'
			button.style = discord.ButtonStyle.danger

		await self.update(interaction, button, 'T')

	@discord.ui.button(label='T Cyan', style=discord.ButtonStyle.primary)
	async def t_cyan(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.state['color'] == '36':
			self.state['color'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['color'] = '36'
			button.style = discord.ButtonStyle.danger

		await self.update(interaction, button, 'T')

	@discord.ui.button(label='T White', style=discord.ButtonStyle.primary)
	async def t_white(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.state['color'] == '37':
			self.state['color'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['color'] = '37'
			button.style = discord.ButtonStyle.danger

		await self.update(interaction, button, 'T')

	@discord.ui.button(label='BG D Blue', style=discord.ButtonStyle.primary)
	async def bg_d_blue(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.state['bgcolor'] == '40':
			self.state['bgcolor'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['bgcolor'] = '40'
			button.style = discord.ButtonStyle.danger

		await self.update(interaction, button, 'BG')

	@discord.ui.button(label='BG Orange', style=discord.ButtonStyle.primary)
	async def bg_orange(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.state['bgcolor'] == '41':
			self.state['bgcolor'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['bgcolor'] = '41'
			button.style = discord.ButtonStyle.danger

		await self.update(interaction, button, 'BG')

	@discord.ui.button(label='BG Gray 1', style=discord.ButtonStyle.primary)
	async def bg_gray_1(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.state['bgcolor'] == '42':
			self.state['bgcolor'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['bgcolor'] = '42'
			button.style = discord.ButtonStyle.danger

		await self.update(interaction, button, 'BG')

	@discord.ui.button(label='BG Gray 2', style=discord.ButtonStyle.primary)
	async def bg_gray_2(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.state['bgcolor'] == '43':
			self.state['bgcolor'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['bgcolor'] = '43'
			button.style = discord.ButtonStyle.danger

		await self.update(interaction, button, 'BG')

	@discord.ui.button(label='BG Gray 3', style=discord.ButtonStyle.primary)
	async def bg_gray_3(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.state['bgcolor'] == '44':
			self.state['bgcolor'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['bgcolor'] = '44'
			button.style = discord.ButtonStyle.danger

		await self.update(interaction, button, 'BG')

	@discord.ui.button(label='BG Gray 4', style=discord.ButtonStyle.primary)
	async def bg_gray_4(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.state['bgcolor'] == '46':
			self.state['bgcolor'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['bgcolor'] = '46'
			button.style = discord.ButtonStyle.danger

		await self.update(interaction, button, 'BG')

	@discord.ui.button(label='BG Indigo', style=discord.ButtonStyle.primary)
	async def bg_indigo(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.state['bgcolor'] == '45':
			self.state['bgcolor'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['bgcolor'] = '45'
			button.style = discord.ButtonStyle.danger

		await self.update(interaction, button, 'BG')

	@discord.ui.button(label='BG White', style=discord.ButtonStyle.primary)
	async def bg_white(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.state['bgcolor'] == '47':
			self.state['bgcolor'] = None
			button.style = discord.ButtonStyle.primary
		else:
			self.state['bgcolor'] = '47'
			button.style = discord.ButtonStyle.danger

		await self.update(interaction, button, 'BG')

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
	async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer()
		buf = await self.sounder.export()

		await self.ctx.message.reply(', '.join(self.sounder.sounds), file=discord.File(buf, 'sounder.mp3'), view=DeleteView(self.ctx.author), mention_author=False)

	@discord.ui.button(label='Clear', style=discord.ButtonStyle.primary, disabled=True)
	async def clear(self, interaction: discord.Interaction, button: discord.ui.Button):
		await self.sounder.init()
		self.sounder.count_sound = 0
		self.sounder.position = 0
		self.sounder.sounds = []
		
		for btn in self.children:
			if btn.label in ['Finished', 'Clear']:
				btn.disabled = True
			else:
				btn.disabled = False

		await interaction.response.edit_message(content=', '.join(self.sounder.sounds), view=self)
		
	@discord.ui.button(label='Delete', style=discord.ButtonStyle.danger)
	async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.message.delete()

	def create_callback(self, sound):
		async def callback(interaction):
			await self.sounder.append_sound(sound)
			for btn in self.children:
				if btn.label in ['Finish', 'Clear']:
					btn.disabled = False
				else:
					if self.sounder.position > 15:
						btn.disabled = True
			
			return await interaction.response.edit_message(content=', '.join(self.sounder.sounds), view=self)
			
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
		self.c = None
		self.message = None
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
				
			await interaction.response.edit_message(embed=self.create_embed(), view=self)
			
		return callback

	async def cancel(self, interaction):
		if interaction.user == self.ctx.author:
			await self.end(interaction)
		else:
			await interaction.response.send_message('Only poll creator can stop this poll.', ephemeral=True)

	async def ping(self, interaction):
		if interaction.user not in self.ping_result:
			self.ping_result.append(interaction.user)
			await interaction.response.send_message(f'Okay {interaction.user.mention}, you will be dmed when the poll ends.', ephemeral=True)
		else:
			self.ping_result.remove(interaction.user)
			await interaction.response.send_message(f'Okay {interaction.user.mention}, you won\'t be dmed when the poll ends.', ephemeral=True)
	
	async def end(self, interaction=None):
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
		
		if interaction:
			await interaction.response.edit_message(embed=embed, view=self)
		else:
			await self.message.edit(embed=embed, view=self)
		
class CariResults(discord.ui.View):
	def __init__(self, ctx, msg, data):
		super().__init__(timeout=None)
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
		await interaction.response.edit_message(view=self)
		await interaction.followup.send(file=discord.File(s, f'{self.table_1_title}.txt'))

	async def button_2_callback(self, interaction: discord.Interaction):
		table = tabulate(self.table_2_data, headers='firstrow', tablefmt='pretty')
		s = StringIO()
		s.write(self.table_2_title + '\n')
		s.write(table)
		s.seek(0)

		self.button_2.disabled = True
		await interaction.response.edit_message(view=self)
		await interaction.followup.send(file=discord.File(s, f'{self.table_2_title}.txt'))

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

		source = await self.session.get_page_source()
		biodata, data = await self.parse_source(source)

		embed = discord.Embed(title=f'Biodata {self.tipe.capitalize()}', description='\n'.join(biodata), color=self.ctx.bot.c)

		result_view = CariResults(self.ctx, self.view.msg, data)
		await interaction.response.edit_message(content=None, embed=embed, view=result_view)
		
		await stop_session(self.session)

# Api cog
class ConfirmView(discord.ui.View):

	def __init__(self, ctx):
		super().__init__()
		self.message = None
		self.value = None
		self.ctx = ctx

	@discord.ui.button(emoji="<:check:827600687926870046>", style=discord.ButtonStyle.green)
	async def confirm(self, interaction, button):
		self.value = True
		await self.message.delete()
		self.stop()

	@discord.ui.button(emoji="<:redx:827600701768597554>", style=discord.ButtonStyle.red)
	async def cancel(self, interaction, button):
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
	def __init__(self, author):
		super().__init__()
		self.author = author

	@discord.ui.button(emoji="<:redx:827600701768597554>", style=discord.ButtonStyle.red)
	async def cancel(self, interaction, button):
		await interaction.message.delete()
		self.stop()

	async def interaction_check(self, interaction):
		if interaction.user != self.author:
			await interaction.response.send_message("This is not your interaction!", ephemeral=True)
			return False
		
		return True

class AkiView(discord.ui.View):
	def __init__(self, ctx):
		super().__init__()
		self.ctx = ctx
		self.result = None

	@discord.ui.button(emoji='\U0001f1fe', style=discord.ButtonStyle.primary)
	async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.result = 'yes'
		button.style = discord.ButtonStyle.green
		for child in self.children:
			child.disabled = True
		await interaction.response.edit_message(view=self)
		self.stop()

	@discord.ui.button(emoji='\U0001f1f3', style=discord.ButtonStyle.primary)
	async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.result = 'no'
		button.style = discord.ButtonStyle.green
		for child in self.children:
			child.disabled = True
		await interaction.response.edit_message(view=self)
		self.stop()

	@discord.ui.button(emoji='\U0001f937', style=discord.ButtonStyle.primary)
	async def idk(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.result = 'idk'
		button.style = discord.ButtonStyle.green
		for child in self.children:
			child.disabled = True
		await interaction.response.edit_message(view=self)
		self.stop()

	@discord.ui.button(emoji='\U0001f4ad', style=discord.ButtonStyle.primary)
	async def p(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.result = 'p'
		button.style = discord.ButtonStyle.green
		for child in self.children:
			child.disabled = True
		await interaction.response.edit_message(view=self)
		self.stop()
	
	@discord.ui.button(emoji='\U0001f5ef', style=discord.ButtonStyle.primary)
	async def pn(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.result = 'pn'
		button.style = discord.ButtonStyle.green
		for child in self.children:
			child.disabled = True
		await interaction.response.edit_message(view=self)
		self.stop()
	
	@discord.ui.button(emoji='\U0001f6d1', style=discord.ButtonStyle.red)
	async def exit_game(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.result = 'exit'
		button.style = discord.ButtonStyle.green
		for child in self.children:
			child.disabled = True
		await interaction.response.edit_message(view=self)
		self.stop()

	async def interaction_check(self, interaction):
		if interaction.user != self.ctx.author:
			await interaction.response.send_message('This is not your interaction!', ephemeral=True)
			return False

		return True
