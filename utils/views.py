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

from utils import pour_puzzle
importlib.reload(pour_puzzle)

from utils.pour_puzzle import Liquid, Bottle, levels

# Bot cog
class HelpView(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.ctx = None
		self.clean_prefix = None
		self.message = None
		self.page = 0
		self.embed = None

	async def start(self, ctx, clean_prefix):
		self.ctx = ctx
		self.clean_prefix = clean_prefix
		self.embed = discord.Embed(title="Help", description="List of commands available", color=self.ctx.bot.c)
		self.embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
		self.embed.add_field(name="Categories:", value="\U000025ab\U0000fe0f Fun\n\U000025ab\U0000fe0f Image\n\U000025ab\U0000fe0f API\n\U000025ab\U0000fe0f Utility\n\U000025ab\U0000fe0f Bot", inline=False)
		self.message = await self.ctx.reply(embed=self.embed, view=self, allowed_mentions=discord.AllowedMentions.none())

	@discord.ui.button(label="Fun", style=discord.ButtonStyle.primary)
	async def help_fun(self, button: discord.ui.Button, interaction: discord.Interaction):
		if interaction.user != self.ctx.author:
			return await interaction.response.send_message(f"Only {self.ctx.author} can use this button.", ephemeral=True)
		if self.page == 1:
			return

		self.embed.clear_fields()
		self.embed.add_field(name="-=: Fun :=-", value="Where All The Fun Begins!", inline=False)
		self.embed.add_field(name="`isometric`", value="Draw your own blocks", inline=True)
		self.embed.add_field(name="`wordle`", value="Word guessing game", inline=True)
		self.embed.add_field(name="`golf`", value="Play mini golf", inline=True)
		self.embed.add_field(name="`typerace`", value="How fast can you type?", inline=True)
		self.embed.add_field(name="`ace`", value="Objection!", inline=True)
		self.embed.add_field(name="`sort_puzzle`", value="Sort liquid color!", inline=True)
		self.embed.add_field(name="`nonogram`", value="Sudoku wannabe", inline=True)
		self.embed.add_field(name="`build`", value="A way to save, share, and find isometric builds", inline=True)
		self.embed.add_field(name="`texttoiso`", value="Turn text into isometric")
		self.embed.add_field(name="`imagetoiso`", value="Turn avatar, emoji, image url into isometric", inline=True)
		#self.embed.add_field(name="`land`", value="Draw blocks in square fit", inline=True)
		self.embed.add_field(name="\u200b", value=f"Use `{self.clean_prefix}help [command]` for more info on a command.", inline=False)
		self.embed.set_thumbnail(url='https://cdn.jeyy.xyz/image/isometric_4e4954.gif')
		await self.message.edit(embed=self.embed)
		self.page = 1

	@discord.ui.button(label="Image", style=discord.ButtonStyle.primary)
	async def help_image(self, button: discord.ui.Button, interaction: discord.Interaction):
		if interaction.user != self.ctx.author:
			return await interaction.response.send_message(f"Only {self.ctx.author} can use this button.", ephemeral=True)
		if self.page == 2:
			return

		self.embed.clear_fields()
		self.embed.add_field(name="-=: Image :=-", value="Image generation/manipulation", inline=False)
		# self.embed.add_field(name="`avatar`", value="See avatar", inline=True)
		# self.embed.add_field(name="`patpat`", value="Pats someone", inline=True)
		# self.embed.add_field(name="`glitch`", value="Error occured.", inline=True)
		# self.embed.add_field(name="`bonk`", value="Bonk someone", inline=True)
		# self.embed.add_field(name="`balls`", value="Ball pit", inline=True)
		# self.embed.add_field(name="`bomb`", value="Nuclear avatar", inline=True)
		# self.embed.add_field(name="`shift`", value="Sheeeft", inline=True)
		# self.embed.add_field(name="`burn`", value="Muahaha", inline=True)
		# self.embed.add_field(name="`hornyjail`", value="No horny!", inline=True)
		# self.embed.add_field(name="`equation`", value="Thinking..", inline=True)
		# self.embed.add_field(name="`disco`", value="Disco-rd", inline=True)
		# self.embed.add_field(name="`eugh`", value="Sobs sobs", inline=True)
		# self.embed.add_field(name="`radiate`", value="\U0001f300", inline=True)
		# self.embed.add_field(name="`shoot`", value="\U0001f464 \U0001f52b", inline=True)
		# self.embed.add_field(name="`scan`", value="Scan through gifs", inline=True)
		# self.embed.add_field(name="`zoom`", value="Magnify \U0001f50e", inline=True)
		# self.embed.add_field(name="`explicit`", value="! Parental Advisory !", inline=True)
		# self.embed.add_field(name="`blur`", value="I need glasses", inline=True)
		# self.embed.add_field(name="`fry`", value="Til golden brown", inline=True)
		# self.embed.add_field(name="`gallery`", value="Cool exhibit", inline=True)
		# self.embed.add_field(name="`golf`", value="\U000026f3", inline=True)
		self.embed.add_field(name='\u200b', value=
			'`avatar` `patpat` `glitch` `bonk` `balls` `bomb` `shift` `burn` `logoff` `hornyjail` `equation` ' \
			'`disco` `eugh` `radiate` `shoot` `zoom` `explicit` `blur` `fry` `gallery` `layers` `boil` ' \
			'`hearts` `matrix` `tv` `print` `half-invert` `shock` `infinity` `canny` `earthquake` ' \
			'`roll` `lamp` `rain` `cartoon` `abstract` `optics` `paparazzi` `shear` `magnify` `youtube` ' \
			'`sensitive` `warp` `wave` `ads` `pattern` `bubble` `cloth` `clock`'
		, inline=False)

		self.embed.add_field(name='\u200b', value='Most of image command is available on [Jeyy API](https://api.jeyy.xyz \"JeyyAPI\")! Feel free to check it out :)', inline=False)
		
		# self.embed.add_field(name="\u200b", value="\u200b", inline=True)
		self.embed.add_field(name="\u200b", value=f"Use `{self.clean_prefix}help [command]` for more info on a command.", inline=False)
		self.embed.set_thumbnail(url='https://cdn.jeyy.xyz/image/patpat_4fe81e.gif')
		await self.message.edit(embed=self.embed)
		self.page = 2

	@discord.ui.button(label="API", style=discord.ButtonStyle.primary)
	async def help_api(self, button: discord.ui.Button, interaction: discord.Interaction):
		if interaction.user != self.ctx.author:
			return await interaction.response.send_message(f"Only {self.ctx.author} can use this button.", ephemeral=True)
		if self.page == 3:
			return

		self.embed.clear_fields()
		self.embed.add_field(name="-=: Api :=-", value="External API commands.", inline=False)
		self.embed.add_field(name="`http`", value="Search or random http error cat images", inline=True)
		self.embed.add_field(name="`gif`", value="Search or random gif", inline=True)
		self.embed.add_field(name="`guess`", value="My bot will try to guess your character", inline=True)
		self.embed.add_field(name="`meme`", value="Random reddit memes", inline=True)
		self.embed.add_field(name="`reddit`", value="Search or random subreddit post", inline=True)
		self.embed.add_field(name="`xkcd`", value="Random XKCD comic", inline=True)
		self.embed.add_field(name="`sand`", value="Sandman", inline=True)
		self.embed.add_field(name="`explode`", value="Yes", inline=True)
		self.embed.add_field(name="\u200b", value="\u200b", inline=True)
		self.embed.add_field(value="`waifu` `slap` `catboy` `cuddle` `hug` `kiss` `lick` `pat` `smug` `hit` `wave` `dance` `highfive` `handhold` `bite` `glomp` `kill` `poke` `neko` `cry` `yeet` `yaoi` `blush` `smile` `nom` `happy` ||`nsfwwaifu`|| ||`nsfwneko`|| ||`nsfwtrap`|| ||`nsfwbj`||", name="Anime commands", inline=False)
		self.embed.add_field(name="\u200b", value=f"Use `{self.clean_prefix}help [command]` for more info on a command.", inline=False)
		self.embed.set_thumbnail(url='https://cdn.jeyy.xyz/image/http_2a872d.png')
		await self.message.edit(embed=self.embed)
		self.page = 3

	@discord.ui.button(label="Utility", style=discord.ButtonStyle.primary)
	async def help_utility(self, button: discord.ui.Button, interaction: discord.Interaction):
		if interaction.user != self.ctx.author:
			return await interaction.response.send_message(f"Only {self.ctx.author} can use this button.", ephemeral=True)
		if self.page == 4:
			return

		self.embed.clear_fields()
		self.embed.add_field(name="-=: Utility :=-", value="Useful commands.", inline=False)
		self.embed.add_field(name="`todo`", value="Keep track of your tasks", inline=True)
		self.embed.add_field(name="`wheel`", value="Start a random picker wheel", inline=True)
		self.embed.add_field(name="`choose`", value="I'll choose it for you :)", inline=True)
		# self.embed.add_field(name="`poll`", value="Set a polling", inline=True)
		self.embed.add_field(name="`translate`", value="Translate to a specified language", inline=True)
		self.embed.add_field(name="`google`", value="Search from google", inline=True)
		self.embed.add_field(name="`quotes`", value="Quotes a message", inline=True)
		self.embed.add_field(name="`sayas`", value="Say as someone else", inline=True)
		self.embed.add_field(name="`gaymeter`", value="See how gay a person is", inline=True)
		self.embed.add_field(name="`scrapbook`", value="Scrapbook style text", inline=True)
		self.embed.add_field(name="`together`", value="Start discord beta activities", inline=True)
		self.embed.add_field(name="`format_text`", value="Format text with ansi", inline=True)
		self.embed.add_field(name="`screenshot`", value="Screenshot given url", inline=True)
		self.embed.add_field(name="\u200b", value=f"Use `{self.clean_prefix}help [command]` for more info on a command.", inline=False)
		self.embed.set_thumbnail(url='https://cdn.jeyy.xyz/image/wheel_spin_4ddcac.gif')
		await self.message.edit(embed=self.embed)
		self.page = 4

	@discord.ui.button(label="Bot", style=discord.ButtonStyle.primary)
	async def help_bot(self, button: discord.ui.Button, interaction: discord.Interaction):
		if interaction.user != self.ctx.author:
			return await interaction.response.send_message(f"Only {self.ctx.author} can use this button.", ephemeral=True)
		if self.page == 5:
			return

		self.embed.clear_fields()
		self.embed.add_field(name="-=: Bot :=-", value="Bot management commands.", inline=False)
		self.embed.add_field(name="`ping`", value="Ping the bot", inline=True)
		self.embed.add_field(name="`invite`", value="Jeyy Bot invite link", inline=True)
		self.embed.add_field(name="`uptime`", value="See bot's uptime", inline=True)
		self.embed.add_field(name="`commandusage`", value="See command usages", inline=True)
		self.embed.add_field(name="`about`", value="See bot's info", inline=True)
		self.embed.add_field(name="`emojis`", value="List of emojis bot could see", inline=True)
		self.embed.add_field(name="`toggle`", value="Toggle emoji auto response", inline=True)
		self.embed.add_field(name="\u200b", value=f"Use `{self.clean_prefix}help [command]` for more info on a command.", inline=False)
		self.embed.set_thumbnail(url='https://cdn.jeyy.xyz/image/jeyy_bot_d5698c.png')
		await self.message.edit(embed=self.embed)
		self.page = 5

	@discord.ui.button(emoji="\U0001f6d1", style=discord.ButtonStyle.red)
	async def exit(self, button: discord.ui.Button, interaction: discord.Interaction):
		if interaction.user != self.ctx.author:
			return await interaction.response.send_message(f"Only {self.ctx.author} can use this button.", ephemeral=True)
		await self.message.delete()
		self.stop()

class HelpView(discord.ui.View):
	def __init__(self, ctx, help_command, *, timeout=None):
		self.ctx = ctx
		self.help = help_command
		self.message = None
		super().__init__(timeout=timeout)

	async def interaction_check(self, interaction):
		if interaction.user != self.ctx.author:
			await interaction.response.send_message("This is not your interaction!", ephemeral=True)
			return False
		
		return True

	async def del_button_callback(self, interaction):
		await self.message.delete()
		self.stop()

	async def start_cog_help(self, mapping):
		for cog, commands in mapping.items():
			commands = await self.help.filter_commands(commands, sort=True)
			if getattr(cog, 'hidden', False) or not cog or cog.qualified_name == 'Jishaku':
				continue

			await self.create_cog_ui(cog, commands)

		del_button = discord.ui.Button(emoji="\U0001f6d1", style=discord.ButtonStyle.red)
		del_button.callback = self.del_button_callback

		self.add_item(del_button)

		self.message = await self.ctx.reply(embed=self.create_home_embed(), view=self, allowed_mentions=discord.AllowedMentions.none())

	def create_home_embed(self):
		embed = discord.Embed(title="Help", description="List of commands available", color=self.ctx.bot.c)
		embed.set_author(name=self.ctx.author.name, icon_url=self.ctx.author.display_avatar.url)
		embed.add_field(name="Categories:", value="\n".join(f"\U000025ab\U0000fe0f {cog.qualified_name}" for cog in self.ctx.bot.cogs.values() if not (getattr(cog, 'hidden', False) or not cog or cog.qualified_name == 'Jishaku')), inline=False)
		return embed
			
	def create_cog_embed(self, cog, commands):
		embed = discord.Embed(title="Help", description="List of commands available", color=self.ctx.bot.c)
		embed.set_author(name=self.ctx.author.name, icon_url=self.ctx.author.display_avatar.url)
		embed.set_thumbnail(url=getattr(cog, 'thumbnail', discord.Embed.Empty))
		embed.add_field(name=f"-=: {cog.qualified_name} :=-", value=cog.description, inline=False)

		for command in commands:
			embed.add_field(name=f"`{command.name}`", value=command.short_doc or "-", inline=True)

		if len(commands) % 3 != 0:
			for _ in range(3 - len(commands) % 3):
				embed.add_field(name="\u200b", value="\u200b", inline=True)

		embed.add_field(name="\u200b", value=f"Use `{self.ctx.clean_prefix}help [command]` for more info on a command.", inline=False)
		
		return embed

	async def create_cog_ui(self, cog, commands):
		button = discord.ui.Button(label=cog.qualified_name, style=discord.ButtonStyle.primary)
		button.callback = self.create_callback(cog, commands)

		self.add_item(button)

	def create_callback(self, cog, commands):

		async def callback(interaction):
			print(f'called {cog.qualified_name}')
			await self.message.edit(embed=self.create_cog_embed(cog, commands))

		return callback

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

		while any(isinstance(btn, BottleButton) for btn in self.children):
			for btn in self.children:
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

		for btn in self.children:
			if btn.custom_id == 'cancel_btn':
				btn.disabled = True
				continue
			if btn.custom_id == 'reset_btn' or btn.custom_id == 'exit_btn':
				btn.disabled = False
				continue
			if isinstance(btn, BottleButton) or btn.custom_id == 'next_lvl_btn':
				self.remove_item(btn)

		while any(isinstance(btn, BottleButton) for btn in self.children):
			for btn in self.children:
				if isinstance(btn, BottleButton):
					self.remove_item(btn)

		while 'next_lvl_btn' in [b.custom_id for b in self.children]:
			for btn in self.children:
				if btn.custom_id == 'next_lvl_btn':
					self.remove_item(btn)

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
		super().__init__()
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
