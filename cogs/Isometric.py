from difflib import get_close_matches
from click import style
from discord.ext import commands
from io import BytesIO, StringIO
from itsdangerous import exc
from matplotlib import interactive
from matplotlib.image import thumbnail
from si_prefix import si_format
from difflib import SequenceMatcher
import asyncio
import datetime as dt
import discord
import humanize
import importlib
import re
import time
import json
import typing
import random
import enchant
import textwrap

from utils import imaging, views, useful, nonogram_maps, golf_maps
importlib.reload(imaging)
importlib.reload(views)
importlib.reload(useful)
importlib.reload(nonogram_maps)
importlib.reload(golf_maps)

from utils.imaging import (
	letters,
	codes,
	codeses,
	isometric_func,
	isometric_gif_func,
	land,
	lever_gif,
	img_to_iso,
	gif_to_iso,
	logic,
	wires,
	fences,
	liquid,
	wordle_keyboard,
	wordle_statistic,
	wordle_func,
	create_stat,
	typerace_func,
	attorney_func,
	prosecutor_func,
	golf_func
)

from utils.views import (
	InteractiveIsoView,
	Switch,
	BuildView,
	NonoView,
	PourView
)

from utils.useful import parse_multiplication, Modal
from utils.nonogram_maps import ans_maps
from utils.golf_maps import golf_maps

class Fun(commands.Cog):
	"""Where All The Fun Begins!"""

	def __init__(self, bot):
		self.bot = bot
		self.thumbnail = "https://cdn.jeyy.xyz/image/isometric_4e4954.gif"
		self.bot.chars = letters
		self.bot.iso_codes = codes
		self.block_codes = "```\n- 0 = blank block\t- g = Gold Block\n" + \
			"- 1 = Grass Block\t- p = Purple Block\n" + \
			"- 2 = Water\t\t  - l = Leaf Block\n" + \
			"- 3 = Sand Block\t - o = Log Block\n" + \
			"- 4 = Stone block\t- c = Coal Block\n" + \
			"- 5 = Wood Planks\t- d = Diamond Block\n" + \
			"- 6 = Glass Block\t- v = Lava\n" + \
			"- 7 = Redstone Block - h = Hay Bale\n" + \
			"- 8 = Iron Block 	- s = Snow Layer\n" + \
			"- 9 = Brick Block\t- f = Wooden Fence\n" + \
			"- w = Redstone Dust  - r = Redstone Lamp\n" + \
			"- e = Lever (off)\t- # = Lever (on)\n" + \
			"- k = Cake\t\t   - y = Poppy```"
		self.checker = enchant.Dict('en_US')
		self.words = list(set([w for w in open('./image/5words.txt', 'r').read().lower().splitlines() if self.checker.check(w)]))
		with open('./image/quotes.json') as f:
			self.quotes = json.load(f)['quotes']

	@commands.Cog.listener()
	async def on_ready(self):
		print("Isometric Cog Loaded")

	@commands.command(cooldown_after_parsing=True, name="land", hidden=True, usage="[length=max(300)] [width=max(300)]")
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def landd(self, ctx, length: int=None, width: int=None):
		"""Draw blocks in square fit
		Draw a 2D square fit isometric grass land\n\nExample : `j;land 4 12`
		"""
		if not length:
			await ctx.reply("Missing land length.", mention_author=False)
			ctx.command.reset_cooldown(ctx)
			return

		if not width:
			await ctx.reply("Missing land width.", mention_author=False)
			ctx.command.reset_cooldown(ctx)
			return

		if length > 300 or width > 300:
			await ctx.reply("Max length & width is `300`.", mention_author=False)
			ctx.command.reset_cooldown(ctx)
			return

		async with ctx.typing():
			buf = await land(length, width)
			await ctx.reply(file=discord.File(buf, "land.png"), mention_author=False)

	@commands.group(cooldown_after_parsing=True, invoke_without_command=True, aliases=['iso'])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def isometric(self, ctx, *, blocks=None):
		"""Draw your own blocks"""
		# return await ctx.reply('Command is on maintenance')
		async with ctx.typing():
			if not blocks:
				await ctx.send_help("isometric")
				ctx.command.reset_cooldown(ctx)
			else:
				blocks = blocks.lower()
				blocks = blocks.replace("`", "")
				blocks = blocks.replace("-", "- ")
				blocks = blocks.strip()

				if 'x' in blocks:
					try:
						blocks = parse_multiplication(blocks)
					except Exception as e:
						ctx.command.reset_cooldown(ctx)
						raise e
					# blocks = list(blocks)
					# for i, code in enumerate(blocks):
					# 	try:
					# 		if code == 'x':
					# 			inserted = blocks[i-1] * int(blocks[i+1])
					# 			blocks[i-1] = inserted
					# 			del blocks[i:i+2]
					# 	except Exception as e:
					# 		ctx.command.reset_cooldown(ctx)
					# 		return await ctx.reply(f"Invalid multiply expression.", mention_author=False)
					# blocks = ''.join(blocks)
					if not blocks:
						ctx.command.reset_cooldown(ctx)
						return await ctx.reply(f"Invalid multiply expression.", mention_author=False)

					if len(blocks) > 4000:
						return await ctx.send('Block count reached more than 4000.')

				if '2' in blocks or 'v' in blocks:
					blocks = liquid(blocks)

				if 'e' in blocks or '#' in blocks:
					if blocks[-3:] == 'gif':
						blocks = blocks[:-3]

						lgif = True
					else:
						lgif = False
					if 'f' in blocks:
						blocks = fences(blocks)
					blocks1 = blocks
					if 'w' in blocks1:
						blocks1 = wires(blocks1)

					if 'r' in blocks1:
						if '7' in blocks1 or '#' in blocks1:
							blocks1 = logic(blocks1)

					blocks1 = blocks1.split()
					buf1, c = await self.bot.loop.run_in_executor(None, isometric_func, blocks1)
					# channel = self.bot.get_channel(851740000814628915) or self.bot.fetch_channel(851740000814628915)

					blocks2 = blocks.replace('e', '／')
					blocks2 = blocks2.replace('#', 'e')
					blocks2 = blocks2.replace('／', '#')

					if 'w' in blocks2:
						blocks2 = wires(blocks2)

					if 'r' in blocks2:
						if '7' in blocks2 or '#' in blocks2:
							blocks2 = logic(blocks2)

					blocks2 = blocks2.split()
					buf2, c = await self.bot.loop.run_in_executor(None, isometric_func, blocks2)

					if not lgif:
						# first = await channel.send(file=discord.File(buf1, "firststate.png"))
						# second = await channel.send(file=discord.File(buf2, "secondstate.png"))
						# await asyncio.sleep(0.1)
						# link1 = self.bot._connection._get_message(first.id).attachments[0].url
						# link2 = self.bot._connection._get_message(second.id).attachments[0].url
						link1 = await ctx.upload_bytes(buf1.getvalue(), 'image/png', name='first state')
						link2 = await ctx.upload_bytes(buf2.getvalue(), 'image/png', name='second state')

					if not lgif:
						await Switch(ctx).switch(link1, link2)
						return

					else:
						igif = await lever_gif(buf1, buf2)
						return await ctx.reply(file=discord.File(igif, "auto_lever.gif"), mention_author=False)

				if 'w' in blocks:
					blocks = wires(blocks)
				
				if 'r' in blocks:
					if '7' in blocks or '#' in blocks:
							blocks = logic(blocks)

				blocks = blocks.split()
				start = time.perf_counter()
				if blocks[-1] == "gif":
					blocks = ' '.join(blocks)
					if 'f' in blocks:
						blocks = fences(blocks)

					blocks = blocks.split()
					if len(blocks) > 1:
						blocks.pop()

					igif, c = await isometric_gif_func(blocks, "")

					if not igif:
							return await ctx.reply("Render time exceeds 20s limit.", mention_author=False)
					if c > 1000:
						await ctx.reply(f"gif block limit is 1000 blocks. Your blocks: `{c}`.", mention_author=False)
						ctx.command.reset_cooldown(ctx)
					elif c == 0:
						await ctx.reply("Did not detect any blocks. Do `j;iso blocks` or `j;help iso` to see available blocks", mention_author=False)
						ctx.command.reset_cooldown(ctx)
					else:
						end = time.perf_counter()
						t = end - start
						t = si_format(t, 4)+'s'
						await ctx.reply(f"`finished in {t}::rendered {c} block{['', 's'][c > 1]}`\n\u200b", file=discord.File(igif, "isometric_gif.gif"), mention_author=False)

				elif len(blocks) > 1:
					if blocks[-2] == "gif":
						blocks = ' '.join(blocks)
						if 'f' in blocks:
							blocks = fences(blocks)
						
						blocks = blocks.split()
						blocks = list(blocks)
						loop = blocks[-1]
						blocks.pop()
						blocks.pop()

						igif, c = await isometric_gif_func(blocks, loop)
						if not igif:
							return await ctx.reply("Render time exceeds 20s limit.", mention_author=False)
						if c > 1000:
							await ctx.reply(f"gif block limit is 1000 blocks. Your blocks: `{c}`.", mention_author=False)
							ctx.command.reset_cooldown(ctx)
							
						elif c == 0:
							await ctx.reply("Did not detect any blocks. Do `j;iso blocks` or `j;help iso` to see available blocks", mention_author=False)
							ctx.command.reset_cooldown(ctx)
							
						else:
							end = time.perf_counter()
							t = end - start
							t = si_format(t, 4)+'s'
							await ctx.reply(f"`finished in {t}::rendered {c} block{['', 's'][c > 1]}`\n\u200b", file=discord.File(igif, "isometric_gif.gif"), mention_author=False)
							
					else:
						blocks = ' '.join(blocks)
						if 'f' in blocks:
							blocks = fences(blocks)
						
						blocks = blocks.split()
						buf, c = await self.bot.loop.run_in_executor(None, isometric_func, blocks)
						end = time.perf_counter()
						t = end - start
						t = si_format(t, 4)+'s'
						if c == 0:
							await ctx.reply("Did not detect any blocks. Do `j;iso blocks` or `j;help iso` to see available blocks", mention_author=False)
							ctx.command.reset_cooldown(ctx)
						else:
							await ctx.reply(f"`finished in {t}::rendered {c} block{['', 's'][c > 1]}`\n\u200b", file=discord.File(buf, "isometric_draw.png"), mention_author=False)
				
				else:
					blocks = ' '.join(blocks)
					if 'f' in blocks:
						blocks = fences(blocks)
					blocks = blocks.split()
					buf, c = await self.bot.loop.run_in_executor(None, isometric_func, blocks)
					end = time.perf_counter()
					t = end - start
					t = si_format(t, 4)+'s'
					if c == 0:
						await ctx.reply("Did not detect any blocks. Do `j;iso blocks` or `j;help iso` to see available blocks", mention_author=False)	
						ctx.command.reset_cooldown(ctx)
					else:
						await ctx.reply(f"`finished in {t}::rendered {c} block{['', 's'][c > 1]}`\n\u200b", file=discord.File(buf, "isometric_draw.png"), mention_author=False)

	@isometric.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def interactive(self, ctx):
		interactive_view = InteractiveIsoView(ctx, [50, 50, 50])

		code = '- '.join([' '.join([''.join(row) for row in lay]) for lay in interactive_view.box])

		buf, _ = await self.bot.loop.run_in_executor(None, isometric_func, code.split(), interactive_view.selector_pos)
		link = await ctx.upload_bytes(buf.getvalue(), 'image/png', 'interactive_iso')

		interactive_view.message = await ctx.reply(link, view=interactive_view, mention_author=False)

	@isometric.command(cooldown_after_parsing=True, name='help')
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def _help(self, ctx):
		s_code = "There are currently **25** codes corresponding to a unique block.```\n" + \
			"- 0 = blank block\t- g = Gold Block\n" + \
			"- 1 = Grass Block\t- p = Purple Block\n" + \
			"- 2 = Water\t\t  - l = Leaf Block\n" + \
			"- 3 = Sand Block\t - o = Log Block\n" + \
			"- 4 = Stone block\t- c = Coal Block\n" + \
			"- 5 = Wood Planks\t- d = Diamond Block\n" + \
			"- 6 = Glass Block\t- v = Lava\n" + \
			"- 7 = Redstone Block - h = Hay Bale\n" + \
			"- 8 = Iron Block 	- s = Snow Layer\n" + \
			"- 9 = Brick Block\t- f = Wooden Fence\n" + \
			"- w = Redstone Dust  - r = Redstone Lamp\n" + \
			"- e = Lever (off)\t- # = Lever (on)\n" + \
			"- k = Cake\t\t   - y = Poppy```"

		s_tutorial = "**See `j;iso tutorial` for more detailed explanation.**\n" + \
			"Each group of codes (without space in between) corresponds to a row of blocks.\n" + \
			"Everytime there's a space or new line, it becomes a new row. A '`-`' character would make the drawing restart from (0, 0) and up 1 block.\n" + \
			"Adding '`gif`' at the end would make the drawing animated in form of a gif. After the '`gif`' argument, you can put a number of loops you want for the gif─with 0 is looping forever.\n" + \
			"If your build has a lever, after it being rendered, you can add/remove reaction added to see both state of build when it turned off or on. While adding '`gif`' argument at the end would make it a gif that automaticly switches the lever on and off repeatedly.\n" + \
			"***new*** - We've added expression to make drawing easier, with '`x`'.\n" + \
			"Example: `1x5 gx8-fx31` equals to `11111 gggggggg-fff1`\n" + \
			"**Note**: gifs might not render well.\n"

		embed = discord.Embed(title="j;isometric [codes] [gif [loops]]", description="**Alias: **`iso`", color=self.bot.c)
		embed.add_field(inline=False, name="Draw your own blocks!", value=s_code)
		embed.add_field(inline=False, name="How to", value=s_tutorial)
		embed.add_field(name="Example", value="`j;iso 401 133 332 - 1 0 5 - 6` or `j;iso 401 133 332 - 1 0 5 - 6 gif 0`", inline=False)

		await ctx.reply(embed=embed, mention_author=False)

	@isometric.command(cooldown_after_parsing=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def tutorial(self, ctx):

		s_code = "- 0 = blank block\t- g = Gold Block\n" + \
			"- 1 = Grass Block\t- p = Purple Block\n" + \
			"- 2 = Water\t\t  - l = Leaf Block\n" + \
			"- 3 = Sand Block\t - o = Log Block\n" + \
			"- 4 = Stone block\t- c = Coal Block\n" + \
			"- 5 = Wood Planks\t- d = Diamond Block\n" + \
			"- 6 = Glass Block\t- v = Lava\n" + \
			"- 7 = Redstone Block - h = Hay Bale\n" + \
			"- 8 = Iron Block 	- s = Snow Layer\n" + \
			"- 9 = Brick Block\t- f = Wooden Fence\n" + \
			"- w = Redstone Dust  - r = Redstone Lamp\n" + \
			"- e = Lever (off)\t- # = Lever (on)\n" + \
			"- k = Cake\t\t   - y = Poppy```"

		pages = [
			"How to use Isometric",
			"You can see `1111` represent a group of codes (without spaces) renders to a row of 4 grass blocks.\n\n- `1` = Grass Block",
			"This is what would happen if you change `1` (code for grass) to `2` (code for water)\n\n- `1` = Grass Block\n- `2` = Water",
			"You can combine codes to get mixed blocks in a row (without spaces)\n\n- `1` = Grass Block\n- `2` = Water",
			"A `space` is an indicator for a new row of blocks.\n`1111 2222` = row of 4 grass blocks and row of 4 waters\n\n- `1` = Grass Block\n- `2` = Water",
			"If you want to skip blocks, adding `0` (blank block) would render as nothing.\n`11022` a row of grass,grass,blank,water,water\n\n- `0` = blank block\n- `1` = Grass Block\n- `2` = Water",
			"Here's an example on how you skip a row.\n`vvvv 0 2222` = a row of 4 lava, a row with only blank block, a row of 4 water\n\n- `0` = blank block\n- `2` = Water\n- `v` = Lava",
			"code: `22222 20002 20102 20002 22222`\nDescription:\nFirst row : `22222` - water,water,water,water,water\nSecond row : `20002` - water,blank,blank,blank,water\nThird row : `20102` - water,blank,grass,blank,water\nFourth row : `20002` - water,blank,blank,blank,water\nFifth row : `22222` - water,water,water,water,water",
			"Here's an example on how you build layers.",
			"To up a layer, simply put `-` before you write codes for the next layer.\nOn this example you see `111 111 111 - 5` which means 3 rows of 3 grass, and any code after `-` which is `5` (code for wooden planks) restarted from first block and up a layer",
			"After that you could build your layers same as how you build your first layer",
			"Here's another example with multiple layers.\n`j;iso 111 111 111 - 525 202 52 - f0f 0 f- f0f 0 f- ppp pp p`\n\n`0` = blank block\n`1` = Grass Block\n`2` = Water\n`f` = Fence\n`p` = Purpur Block",
			"To render it as a gif, simply put `gif` argument at the end of your build codes. (the gif will play once)\n**Note: **gifs might not render well.\n\n`j;iso 111 111 111 - 525 202 52 - f0f 0 f- f0f 0 f- ppp pp p gif`",
			"After the `gif` argument, you can specify how many loops the gif you want to be played with `0` is looping forever.\n**Note: **gifs might not render well.\n\n`j;iso 111 111 111 - 525 202 52 - f0f 0 f- f0f 0 f- ppp pp p gif 2`",
			f"All **24** block codes.```\n{s_code}"
			]
		images = [
			"https://cdn.discordapp.com/attachments/785808264591704095/844761819657535568/isometric_gif.gif",
			"https://cdn.discordapp.com/attachments/779892741696913438/844770502970834954/unknown.png",
			"https://cdn.discordapp.com/attachments/779892741696913438/844773365309898763/unknown.png",
			"https://cdn.discordapp.com/attachments/779892741696913438/844774418500026428/unknown.png",
			"https://cdn.discordapp.com/attachments/779892741696913438/844775487234244618/unknown.png",
			"https://cdn.discordapp.com/attachments/779892741696913438/844776758016213042/unknown.png",
			"https://cdn.discordapp.com/attachments/779892741696913438/844777744034562068/unknown.png",
			"https://cdn.discordapp.com/attachments/779892741696913438/844823707268677632/unknown.png",
			"https://cdn.discordapp.com/attachments/779892741696913438/844832642418606119/unknown.png",
			"https://cdn.discordapp.com/attachments/779892741696913438/844832642418606119/unknown.png",
			"https://cdn.discordapp.com/attachments/779892741696913438/844834255887532062/unknown.png",
			"https://cdn.discordapp.com/attachments/779892741696913438/844853924040802314/unknown.png",
			"https://cdn.discordapp.com/attachments/785808264591704095/844761819657535568/isometric_gif.gif",
			"https://cdn.discordapp.com/attachments/785808264591704095/844761990458900530/isometric_gif.gif",
			discord.Embed.Empty
			]

		embeds = []
		for i, page in enumerate(pages):
			embed = discord.Embed(description=page, color=self.bot.c, timestamp=dt.datetime.utcnow())
			embed.set_author(name="Isometric Tutorial", icon_url=ctx.author.display_avatar.url)
			embed.set_image(url=images[i])
			embed.set_footer(text=f"Requested by {ctx.author}")
			embeds.append(embed)
		
		await ctx.Paginator().send(embeds, reply=True)

	@isometric.command(cooldon_after_parsing=True)
	async def blocks(self, ctx):

		embed = discord.Embed(color=self.bot.c)
		embed.add_field(name="Block codes", value=self.block_codes)
		await ctx.reply(embed=embed, mention_author=False)

	@commands.group(invoke_without_command=True, cooldown_after_parsing=True, aliases=['tti', 'ttiso'])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def texttoiso(self, ctx, block='1', *, text):
		"""Turn text into isometric"""
		text = text.lower()

		if text[-3:] == "gif":
			gif = True
			text = text[:-3]
		else:
			gif = False

		coded = []
		for letter in text[::-1]:
			try:
				coded.append(letters[letter])
			except:
				pass

		output = " 0 ".join(coded)
		
		output = output.replace('1', block[0])

		# await ctx.reply(f"`code::`\n```j;iso {output + ['', ' gif'][gif]}```", mention_author=False)
		cmd = self.bot.get_command("isometric")
		await cmd(ctx, blocks='0 '+output + ['', ' gif'][gif])

	@texttoiso.command(name="code", cooldown_after_parsing=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def texttoiso_code(self, ctx, block, *, text):
		text = text.lower()

		if text[-3:] == "gif":
			gif = True
			text = text[:-3]
		else:
			gif = False

		coded = []
		for letter in text[::-1]:
			try:
				coded.append(letters[letter])
			except:
				pass

		output = " 0 ".join(coded)
		
		output = output.replace('1', block[0])

		try:
			await ctx.reply(f"`code::`\n```j;isometric {output + ['', ' gif'][gif]}```", mention_author=False)
		except:
			s = StringIO()
			s.write(f"j;isometric {output + ['', ' gif'][gif]}")
			s.seek(0)
			await ctx.reply(file=discord.File(s, "texttoiso.txt"), mention_author=False)

	@commands.group(aliases=['iti', 'imgtoiso'], cooldown_after_parsing=True, invoke_without_command=True)
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def imagetoiso(self, ctx, image: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Turn avatar, emoji, image url to isometric build
		- converter code credit: <@486148342108127253>
		"""
		async with ctx.typing():
			image = await ctx.to_image(image)

			code = await self.bot.loop.run_in_executor(None, img_to_iso, image, 64)

			cmd = self.bot.get_command("isometric")
			await cmd(ctx, blocks=code)

	@imagetoiso.command(name="code", cooldown_after_parsing=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def imagetoiso_code(self, ctx, image: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""See code generated of imagetoiso command"""
		async with ctx.typing():
			image = await ctx.to_image(image)

			text = await self.bot.loop.run_in_executor(None, img_to_iso, image, 40)
			try:
				msg = await ctx.reply(f"```j;isometric {text}```", mention_author=False)
			except:
				s = StringIO()
				s.write(f"j;isometric {text}")
				s.seek(0)
				await ctx.reply(file=discord.File(s, "imagetoiso.txt"), mention_author=False)

	@commands.command(cooldown_after_parsing=True, hidden=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	@commands.is_owner()
	async def gifiso(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		async with ctx.typing():
			_input = await ctx.to_image(_input)
			if _input == "invalid":
				return

			buf = await gif_to_iso(_input)
			await ctx.reply(file=discord.File(buf, "gifiso.gif"), mention_author=False)

	@commands.group(invoke_without_command=True, aliases=["builds"], usage="[build name]")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def build(self, ctx, *, build_name=None):
		"""A way to save, share, and find isometric builds!
		You can save your build with `j;build create [build name] [iso code]`,
		see other's build with `j;build all`, `j;build search [build name]`, or `j;build owned [user=None]`.

		Example :
		`j;build create "basic tree" 111 111 111- 0 0o- 0 0o- lll lol lll- lll lll lll- 0 0l` - to create build
		`j;build basic tree` - to show build
		`j;build all` - to see other builds
		"""
		if not build_name:
			await ctx.send_help("build") 
			return

		build_name = build_name.lower()

		build_search = await self.bot.db.fetchrow("SELECT * FROM builds WHERE LOWER(build_name) = $1", build_name)

		if not build_search or not build_search[0]:

			all_builds = await self.bot.db.fetch("SELECT build_name FROM builds")
			all_builds = [build["build_name"] for build in all_builds]

			close_matches = get_close_matches(build_name, all_builds, 10)

			if not close_matches:
				await ctx.reply("No builds found.", mention_author=False)
			else:
				text = "Build not found. Did you mean...\n" + "\n".join([f"{i+1}. {name}" for i, name in enumerate(close_matches)])
				await ctx.reply(text, mention_author=False)

			return

		await BuildView(ctx, build_search).start()

	@build.command(cooldown_after_parsing=True, usage="[build name] [code]")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def create(self, ctx, build_name, *, code):
		"""Save and share your build publicly"""
		if not build_name.replace("\u2800", "").replace("\u200b", "").replace("\uFEFF", "").strip(" "):
			return await ctx.reply("Missing build name.", mention_author=False)

		if not code:
			return await ctx.reply("Missing block codes.", mention_author=False)

		if build_name.replace("\u2800", "").replace("\u200b", "").replace("\uFEFF", "").strip(" ").startswith(('all', 'create', 'edit', 'info', 'owned' , 'remove', 'render', 'search', 'star', 'rename')):
			return await ctx.reply(f"You can't name your build `{build_name}`.", mention_author=False)

		if len(build_name) > 100:
			return await ctx.reply("Build name is a maximum of 100 characters.", mention_author=False)

		code = code.replace('j;isometric', '').replace('j;iso', '').strip()
		code = re.sub(" +", ' ', code)

		if any(l not in codeses for l in code):
			noo = ", ".join([f"`{i}`" for i in code if i not in codeses])
			return await ctx.reply(f"Your build has a code that i don't recognize. {noo}", mention_author=False)
		
		if not set(code).intersection(set(codes)):
			return await ctx.reply("Your build has no blocks.", mention_author=False)

		if 'x' in code:
			try:
				blocks = parse_multiplication(code)
			except Exception as e:
				ctx.command.reset_cooldown(ctx)
				raise e
			if not blocks:
				ctx.command.reset_cooldown(ctx)
				return await ctx.reply(f"Invalid multiply expression.", mention_author=False)

			if len(blocks) > 4000:
				return await ctx.send('Block count reached more than 4000.')

		code = code.lower().strip()
		build_name = build_name.replace("\u2800", "").replace("\u200b", "").replace("\uFEFF", "").strip(" ")

		
		build_search = await self.bot.db.fetch("SELECT * FROM builds WHERE LOWER(build_name) = $1", build_name.lower())

		if build_search:
			return await ctx.reply(f'Build called "{build_name}" already exists.', mention_author=False)

		await self.bot.db.execute("INSERT INTO builds (owner_id, build_name, build, stars, date, uses) VALUES ($1, $2, $3, $4, $5, $6)", ctx.author.id, build_name, code, 0, dt.datetime.utcnow(), 0)
		await ctx.reply(f'Build "{build_name}" successfully created.', mention_author=False)

	@build.command(usage="[build name]")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def info(self, ctx, *, build_name):
		"""See info of a build"""
		build_name = build_name.lower()

		build_search = await self.bot.db.fetchrow("SELECT * FROM builds WHERE LOWER(build_name) = $1", build_name)

		if not build_search or not build_search[0]:
			await ctx.send("Build not found.", mention_author=False)
			return

		block_count = len([i for i in build_search["build"] if i in codes])
		
		owner = self.bot.get_user(build_search["owner_id"]) or await self.bot.fetch_user(build_search["owner_id"])
		date = dt.datetime.combine(build_search["date"], dt.datetime.min.time())

		embed = discord.Embed(title=build_search["build_name"], timestamp=date, color=self.bot.c)
		embed.set_author(name=str(owner), icon_url=owner.display_avatar.url)
		embed.add_field(name="Creator", value=owner.mention, inline=True)
		embed.add_field(name="Uses", value=build_search["uses"], inline=True)
		embed.add_field(name="Stars \U00002b50", value=build_search["stars"], inline=True)
		embed.add_field(name="Block Count", value=block_count, inline=True)
		embed.add_field(name="\u200b", value="\u200b", inline=True)
		embed.set_footer(text="Build created at")

		class InfoView(discord.ui.View):
			@discord.ui.button(label=f'Builds owned by {owner}')
			async def owned(self, button: discord.ui.Button, interaction:discord.Interaction):
				if interaction.user == ctx.author:
					button.disabled = True
					cmd = ctx.bot.get_command('build owned')
					await msg.edit(view=self)
					await cmd(ctx, member=owner)

		msg = await ctx.reply(embed=embed, view=InfoView(), mention_author=False)

	@build.command(usage="[build name] [new code]")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def edit(self, ctx, build_name, *, code=None):
		"""Edit your build code"""
		if not code:
			return await ctx.reply("Missing block codes.", mention_author=False)

		code = code.replace('j;isometric', '').replace('j;iso', '').strip()
		code = re.sub(" +", ' ', code)
		# build_name = build_name.lower()
		build_search = await self.bot.db.fetchrow("SELECT * FROM builds WHERE LOWER(build_name) = $1", build_name.lower())

		if not build_search or not build_search[0]:
			await ctx.send("Build not found.", mention_author=False)
			return

		if build_search["owner_id"] != ctx.author.id:
			await ctx.reply("You are not the owner of this build!", mention_author=False)
			return

		if any(l not in codeses for l in code):
			noo = ", ".join([f"`{i}`" for i in code if i not in codeses])
			return await ctx.reply(f"Your build has a code that i don't recognize. {noo}", mention_author=False)
		
		if not set(code).intersection(set(codes)):
			return await ctx.reply("Your build has no blocks.", mention_author=False)

		if 'x' in code:
			try:
				blocks = parse_multiplication(code)
			except Exception as e:
				ctx.command.reset_cooldown(ctx)
				raise e
			if not blocks:
				ctx.command.reset_cooldown(ctx)
				return await ctx.reply(f"Invalid multiply expression.", mention_author=False)

			if len(blocks) > 4000:
				return await ctx.send('Block count reached more than 4000.')

		await self.bot.db.execute("UPDATE builds SET build = $1 WHERE LOWER(build_name) = $2", code, build_name)
		# return await ctx.send(build_search)
		await ctx.reply(f'Successfully edited build \"{build_search["build_name"]}\".', mention_author=False)

	@build.command(aliases=["delete"], usage="[build name]")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def remove(self, ctx, *, build_name):
		"""Remove your build"""
		build_name = build_name.lower()
		build_search = await self.bot.db.fetchrow("SELECT * FROM builds WHERE LOWER(build_name) = $1", build_name)

		if not build_search or not build_search[0]:
			await ctx.send("Build not found.", mention_author=False)
			return

		if build_search["owner_id"] != ctx.author.id:
			await ctx.reply("You are not the owner of this build!", mention_author=False)
			return

		await self.bot.db.execute("DELETE FROM builds WHERE build_name = $1", build_name)
		await ctx.reply(f'Successfully removed \"{build_search["build_name"]}\" build.', mention_author=False)

	@build.group(name="render", invoke_without_command=True, cooldown_after_parsing=True, usage="[build name]")
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def build_render(self, ctx, *, build_name):
		"""Render a build immediately"""
		build_name = build_name.lower()

		build_search = await self.bot.db.fetchrow("SELECT * FROM builds WHERE build_name = $1", build_name)

		if not build_search or not build_search[0]:

			all_builds = await self.bot.db.fetch("SELECT build_name FROM builds")
			all_builds = [build["build_name"] for build in all_builds]

			close_matches = get_close_matches(build_name, all_builds, 10)

			if not close_matches:
				await ctx.reply("No builds found.", mention_author=False)
			else:
				text = "Build not found. Did you mean...\n" + "\n".join([f"{i+1}. {name}" for i, name in enumerate(close_matches)])
				await ctx.reply(text, mention_author=False)

			ctx.command.reset_cooldown(ctx)
			return

		cmd = self.bot.get_command("isometric")
		await cmd(ctx, blocks=build_search["build"])
		await self.bot.db.execute("UPDATE builds SET uses = uses + 1 WHERE build_name = $1", build_name)

	@build_render.command(name="gif", cooldown_after_parsing=True, usage="[build name]")
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def render_gif(self, ctx, *, build_name):
		"""Render a build gif immediately"""
		build_name = build_name.lower()

		build_search = await self.bot.db.fetchrow("SELECT * FROM builds WHERE build_name = $1", build_name)

		if not build_search or not build_search[0]:

			all_builds = await self.bot.db.fetch("SELECT build_name FROM builds")
			all_builds = [build["build_name"] for build in all_builds]

			close_matches = get_close_matches(build_name, all_builds, 10)

			if not close_matches:
				await ctx.reply("No builds found.", mention_author=False)
			else:
				text = "Build not found. Did you mean...\n" + "\n".join([f"{i+1}. {name}" for i, name in enumerate(close_matches)])
				await ctx.reply(text, mention_author=False)

			ctx.command.reset_cooldown(ctx)
			return

		cmd = self.bot.get_command("isometric")
		await cmd(ctx, blocks=build_search["build"]+" gif")
		await self.bot.db.execute("UPDATE builds SET uses = uses + 1 WHERE build_name = $1", build_name)

	@build.command(cooldown_after_parsing=True, usage="[build name]")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def search(self, ctx, *, build_name):
		"""Search builds name"""
		build_name = build_name.lower()

		all_builds = await self.bot.db.fetch("SELECT build_name FROM builds")
		all_builds = [build["build_name"] for build in all_builds]

		close_matches = get_close_matches(build_name, all_builds, 10)

		if not close_matches:
			await ctx.reply("No builds found.", mention_author=False)
		else:
			text = "\n".join([f"{i+1}. {name}" for i, name in enumerate(close_matches)])
			await ctx.reply(text, mention_author=False)

	@build.command(cooldown_after_parsing=True, usage="<order=default(name)>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def all(self, ctx, *, order:str="name"):
		"""See all builds saved
		Orders : `name`, `uses`, `stars`, and `date`
		"""
		if order.lower() in ["name", "build name"]:
			all_builds = await self.bot.db.fetch("SELECT build_name FROM builds ORDER BY build_name ASC")
		elif order.lower() in ["use", "usage", "uses"]:
			all_builds = await self.bot.db.fetch("SELECT build_name FROM builds ORDER BY uses DESC")
		elif order.lower() in ["star", "stars"]:
			all_builds = await self.bot.db.fetch("SELECT build_name FROM builds ORDER BY stars DESC")
		elif order.lower() == "date":
			all_builds = await self.bot.db.fetch("SELECT build_name FROM builds ORDER BY date ASC")
		else:
			order = "name"
			all_builds = await self.bot.db.fetch("SELECT build_name FROM builds ORDER BY build_name ASC")
			
		all_builds = [build["build_name"] for build in all_builds]

		lines = [f"{i+1}. {name}" for i, name in enumerate(all_builds)]

		chunks = ctx.chunk(lines, combine=True)

		embeds = []
		for page in chunks:
			embed = discord.Embed(title="All builds", description=page, color=self.bot.c, timestamp=dt.datetime.now())
			embed.set_footer(text=f"Total query: {len(all_builds)} | sorted by {order}")
			embeds.append(embed)

		await ctx.Paginator().send(embeds, reply=True)

	@build.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def owned(self, ctx, member:typing.Union[discord.Member, discord.User]=None):
		"""See owned build by you or others"""
		if not member:
			member = ctx.author

		page = 0

		all_builds = await self.bot.db.fetch("SELECT build_name FROM builds WHERE owner_id = $1", member.id)

		if not all_builds:
			await ctx.reply(f"{member} has no builds.", mention_author=False)
			return

		all_builds = [build["build_name"] for build in all_builds]

		lines = [f"{i+1}. {name}" for i, name in enumerate(all_builds)]

		chunks = ctx.chunk(lines, combine=True)

		embeds = []
		for page in chunks:
			embed = discord.Embed(title=f"Builds owned by {member}", description=page, color=self.bot.c)
			embeds.append(embed)

		if len(embeds) == 1:
			return await ctx.reply(embed=embeds[0], mention_author=False)

		await ctx.Paginator().send(embeds, reply=True)

	@build.command(usage="[old name] [new name]")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def rename(self, ctx, old_name, *, new_name):
		"""Rename your build"""
		old_name = old_name.lower()
		new_name = new_name.lower().strip('"')
		
		if len(new_name) > 100:
			return await ctx.reply("Build name is a maximum of 100 characters.", mention_author=False)

		if not new_name.replace("\u2800", "").replace("\u200b", "").replace("\uFEFF", "").strip(" "):
			return await ctx.reply("Missing build name.", mention_author=False)

		if new_name.replace("\u2800", "").replace("\u200b", "").replace("\uFEFF", "").strip(" ").startswith(('all', 'create', 'edit', 'info', 'owned' , 'remove', 'render', 'search', 'star', 'rename')):
			return await ctx.reply(f"You can't name your build `{new_name}`.", mention_author=False)

		if not new_name.replace("\u2800", "").replace("\u200b", "").replace("\uFEFF", "").strip(" "):
			return await ctx.reply("Missing build name.", mention_author=False)

		new_name = new_name.replace("\u2800", "").replace("\u200b", "").replace("\uFEFF", "").strip(" ")
		old_name = old_name.replace("\u2800", "").replace("\u200b", "").replace("\uFEFF", "").strip(" ")

		old_search = await self.bot.db.fetchrow("SELECT * FROM builds WHERE build_name = $1", old_name)
		new_search = await self.bot.db.fetchrow("SELECT * FROM builds WHERE build_name = $1", new_name)

		if not old_search or not old_search[0]:
			return await ctx.send("Build not found.", mention_author=False)

		if old_search["owner_id"] != ctx.author.id:
			return await ctx.reply("You are not the owner of this build!", mention_author=False)

		if new_search:
			return await ctx.reply("That build name is occupied.", mention_author=False)

		await self.bot.db.execute("UPDATE builds SET build_name = $1 WHERE build_name = $2", new_name, old_name)
		await ctx.reply(f'Successfully renamed build "{old_name}" to "{new_name}".', mention_author=False)

	@commands.group(invoke_without_command=True, aliases=['word', 'worlde'])
	@commands.max_concurrency(1, commands.BucketType.user)
	async def wordle(self, ctx):
		"""Word guessing game
		Type in your guesses, if the letter is green that means that letter is exists and on the right spot
		if it turns yellow that means that letter exists but not on the right spot.
		And if it turns grey that means that letter doesn't exists in the word.
		"""
		word = random.choice(self.words)
		print(word)
		guesses = [None] * 6
		guess = ctx.message
		i = 0

		if not self.bot.username_cache.get(ctx.author.id):
			self.bot.username_cache[ctx.author.id] = str(ctx.author)

		current_stat = await self.bot.db.fetchrow('SELECT * FROM wordle_stat WHERE user_id = $1', ctx.author.id)
		if not current_stat:
			await self.bot.db.execute('''
			INSERT INTO wordle_stat 
				(user_id, played, current_streak, max_streak, guess_distrib)
 			VALUES 
			 	($1, 0, 0, 0, '{0, 0, 0, 0, 0, 0}') 
			''', ctx.author.id)
		# else:
		# 	await self.bot.db.execute('UPDATE wordle_stat SET played = played + 1 WHERE user_id = $1', ctx.author.id)

		class WordleView(discord.ui.View):
			def __init__(self):
				super().__init__()
				self.exit = False
				self.msg = None
				
			@discord.ui.button(label='Example')
			async def example(self, button: discord.Button, interaction: discord.Interaction):
				await interaction.response.send_message('https://cdn.discordapp.com/attachments/381963689470984203/937701492561965066/example.png', ephemeral=True)

			@discord.ui.button(label='Exit', style=discord.ButtonStyle.red)
			async def exit(self, button: discord.Button, interaction: discord.Interaction):
				if interaction.user == ctx.author:
					await interaction.response.send_message(f'Exited. Correct word is **{word}**')
					self.exit = True
					button.disabled = True
					await self.msg.edit(view=self)

		def msg_check(message):
			return (message.channel == ctx.channel and message.author == ctx.author) or wordle_view.exit

		while len([g for g in guesses if g is not None]) < 6 and guess.content.lower() != word:
			board = await wordle_func(word, guesses)
			keyboard = await wordle_keyboard(word, guesses)
			board_file = discord.File(board, 'wordle.png')
			keyboard_file = discord.File(keyboard, 'keyboard.png')
			stat = create_stat(word, guesses)
			wordle_view = WordleView()
			embed = discord.Embed(title='Wordle', description=f'Type your guess below!\n{stat}', timestamp=ctx.message.created_at, color=0x2F3136)
			embed.set_image(url="attachment://wordle.png")
			embed.set_thumbnail(url="attachment://keyboard.png")
			embed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
			wordle_view.msg = msg = await ctx.reply(embed=embed, files=[board_file, keyboard_file], view=wordle_view, mention_author=False)

			while True:
				try:
					guess = await self.bot.wait_for('message', check=msg_check, timeout=300)
				except asyncio.TimeoutError:
					await self.bot.db.execute('UPDATE wordle_stat SET current_streak = 0 WHERE user_id = $1', ctx.author.id)
					return await msg.reply(f'Aborting from taking too long. Correct word is **{word}**')
				if wordle_view.exit:
					await self.bot.db.execute('UPDATE wordle_stat SET current_streak = 0 WHERE user_id = $1', ctx.author.id)
					return 
				if guess.content.lower() == 'exit':
					await self.bot.db.execute('UPDATE wordle_stat SET current_streak = 0 WHERE user_id = $1', ctx.author.id)
					return await guess.reply(f'Exited. Correct word is **{word}**', mention_author=False)
				if len(guess.content) != 5:
					await ctx.reply('Guess word length must be **5**!', delete_after=5, mention_author=False)
				elif not self.checker.check(guess.content.lower()):
					await ctx.reply(f'Word **{guess.content.lower()}** is not listed!', delete_after=5, mention_author=False)
				else:
					break

			await msg.delete()
			guesses[i] = guess.content.lower()
			if i == 0:
				await self.bot.db.execute('UPDATE wordle_stat SET played = played + 1 WHERE user_id = $1', ctx.author.id)
			i += 1
			
		board = await wordle_func(word, guesses)
		keyboard = await wordle_keyboard(word, guesses)
		board_file = discord.File(board, 'wordle.png')
		keyboard_file = discord.File(keyboard, 'keyboard.png')
		stat = create_stat(word, guesses)

		if guess.content.lower() != word:
			embed = discord.Embed(title='Wordle', description=f'You failed! Correct word is **{word}**\n{stat}', timestamp=ctx.message.created_at, color=discord.Color.red())
			await self.bot.db.execute('UPDATE wordle_stat SET current_streak = 0 WHERE user_id = $1', ctx.author.id)
		else:
			embed = discord.Embed(title='Wordle', description=f'You won! Correct word is **{word}**\n{stat}', timestamp=ctx.message.created_at, color=discord.Color.green())
			await self.bot.db.execute('''
				UPDATE wordle_stat 
				SET 
					current_streak = current_streak + 1,
					max_streak = max_streak + $1,
					guess_distrib[$2] = guess_distrib[$2] + 1
				WHERE user_id = $3
				''', 1 if not current_stat or current_stat['current_streak'] == current_stat['max_streak'] else 0, i, ctx.author.id)
		
		embed.set_image(url="attachment://wordle.png")
		embed.set_thumbnail(url="attachment://keyboard.png")
		embed.set_author(name='Do `j;wordle stat` to see your wordle statistic!')
		embed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
		await ctx.reply(embed=embed, files=[board_file, keyboard_file], mention_author=False)

	@wordle.command(name='statistic', aliases=['stat', 'stats'])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def wordle_stat(self, ctx, user: typing.Union[discord.Member, discord.User]=None):
		user = user or ctx.author

		data = await self.bot.db.fetchrow('SELECT * FROM wordle_stat WHERE user_id = $1', user.id)
		if not data:
			embed = discord.Embed(title='No data', description=f'Can not find any wordle data for {user.mention}', color=self.bot.c, timestamp=dt.datetime.now())
			embed.set_footer(text='Play a wordle game with j;wordle', icon_url=user.display_avatar.url)
			return await ctx.reply(embed=embed, mention_author=False)

		buf = await wordle_statistic(data["guess_distrib"])
		f = discord.File(buf, 'guess_distribution.png')

		desc = f'> Played : `{data["played"]}`\n'
		desc += f'> Win count : `{sum(data["guess_distrib"])}`\n'
		desc += f'> Win rate: `{sum(data["guess_distrib"])/data["played"]:.0%}`\n'
		desc += f'> Current streak : `{data["current_streak"]}`\n'
		desc += f'> Max streak : `{data["max_streak"]}`'
				
		embed = discord.Embed(title=f'{user} Wordle Statistics', description=desc, color=self.bot.c, timestamp=dt.datetime.now())
		embed.set_image(url="attachment://guess_distribution.png")
		embed.set_thumbnail(url=user.display_avatar.url)
		embed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)

		await ctx.reply(embed=embed, file=f, mention_author=False)

	@wordle.command(name='leaderboard', aliases=['lb'])
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def wordle_leaderboard(self, ctx):
		lines = []

		datas = await self.bot.db.fetch('SELECT user_id, guess_distrib FROM wordle_stat')
		for i, data in enumerate(sorted(datas, key=lambda d: sum(d['guess_distrib']), reverse=True), start=1):
			if i > 10:
				break
			name = self.bot.username_cache.get(data['user_id'])
			if not name:
				name = str(await self.bot.fetch_user(data["user_id"]))
				self.bot.username_cache[data['user_id']] = name
			lines.append(f'`{i:>3}. {name:<30} ({sum(data["guess_distrib"]):^3})`')

		chunks = ctx.chunk(lines, combine=True)
		embeds = []
		for page in chunks:
			embed = discord.Embed(title='TOP 10 Wordle Players', description=page, color=self.bot.c, timestamp=dt.datetime.now())
			embed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
			embeds.append(embed)

		await ctx.reply(embeds=embeds)

	@commands.group(invoke_without_command=True)
	@commands.cooldown(1, 10, commands.BucketType.user)
	@commands.max_concurrency(1, commands.BucketType.user)
	async def golf(self, ctx):
		"""Play mini golf
		Type where the ball will shoot by degrees [0-360] and the power [1-20].
		Format : `<degree> <power>`

		type `exit` if you wish to exit the game.
		"""
		_map = random.choice(golf_maps)
		startx, starty  = _map.start
		finx, finy = _map.finish
		first_img, posx, posy = await golf_func(startx, starty, 0, 0, 1, _map, 0)
		msg = await ctx.reply("Type shooting degree [0-360] and power [1-20], `exit` to exit\n`<degree> <power>`", file=discord.File(first_img, 'board.png'), mention_author=False)

		def check(msg):
			return msg.author == ctx.author and msg.channel == ctx.channel

		counter = 0
		while True:
			try:
				degree_power = await self.bot.wait_for('message', check=check, timeout=60)
			except asyncio.TimeoutError:
				return await ctx.reply("Timed out.", mention_author=False)

			if degree_power.content.lower() == 'exit':
				return await ctx.reply('Exited the game.', mention_author=False)

			try:
				degree, power = map(int, degree_power.content.split())
			except:
				continue

			try:
				await degree_power.delete()
			except:
				pass

			if power > 20:
				power = 20
			elif power < 1:
				power = 1

			counter += 1
			buf, posx, posy= await golf_func(posx, posy, degree, power, 100, _map, counter)

			await msg.delete()
			msg = await ctx.reply(f"Type shooting degree [0-360] and power [1-20], `exit` to exit.\n`<degree> <power>`", file=discord.File(buf, 'board.gif'), mention_author=False)
			
			if (posx-finx)**2 + (posy - finy)**2 < 15**2:
				await asyncio.sleep(3)
				return await ctx.reply(f"You've won with {counter} stroke{['', 's'][counter>1]}!", mention_author=False)

	@commands.command(aliases=["trc", "typeracer"], cooldown_after_parsing=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	@commands.max_concurrency(1, commands.BucketType.channel)
	async def typerace(self, ctx):
		"""How fast can you type?"""
		text = random.choice(list(filter(lambda q: len(q['text']) < 200 and len(q['text']) > 30 and len(textwrap.wrap(q['text'], width=25)) <= 8, self.quotes)))['text']
		
		buf = await typerace_func(text)

		file = discord.File(buf, 'typerace.png')
		desc = 'Type the text below as fast as you can!'
		loc = random.randint(0, len(desc))
		try:
			desc = desc[:loc] + '\u200b'*random.randint(1, 5) + desc[loc:]
		except:
			desc = 'Type the text below as fast as you can!'
		embed = discord.Embed(description=desc, color=0x2F3136)
		embed.set_image(url="attachment://typerace.png")

		s = time.perf_counter()
		image = await ctx.reply(embed=embed, file=file, mention_author=False)

		def check(msg):
			return msg.channel == ctx.channel and SequenceMatcher(None, msg.content, text).ratio() >= 0.5 and not msg.author.bot

		try:
			message = await self.bot.wait_for('message', check=check, timeout=60)
		except asyncio.TimeoutError:
			return await image.reply('Timed out. No recognized message.')
		e = time.perf_counter()

		match = SequenceMatcher(None, message.content, text).ratio()
		wpm = len(message.content.split())*60/(e-s)

		await message.add_reaction('\U0001f3c6')
		embed = discord.Embed(description=f'**{message.author}** won with accuracy score : `{match:.2%}`, `{wpm:.2f}` words per minute.', color=0x2F3136)
		
		await message.reply(embed=embed, mention_author=False)

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def ace(self, ctx: commands.Context, side=None, *, text=None):
		"""Objection!"""
		file_limit = ctx.guild.filesize_limit

		if side and not text:
			return await ctx.reply('Please send the text', mention_author=False)
		if side and text:
			if len(text) > 240:
				return await ctx.reply('Text length must be under 240 characters!', mention_author=False)
			if side.lower() not in ['a', 'attorney', 'p', 'prosecutor']:
				return await ctx.reply('Side must be one of these: `a`, `attorney`, `p`, `prosecutor`', mention_author=False)
			async with ctx.typing():
				if side.lower() in ['a', 'attorney']:
					buf = await attorney_func(str(ctx.author), text)
				elif side.lower() in ['p', 'prosecutor']:
					buf = await prosecutor_func(str(ctx.author), text)
				if (bsize := buf.getbuffer().nbytes) > file_limit:
					return await ctx.reply(f'Resulting gif size: `{humanize.naturalsize(bsize)}` is bigger than this guild file size limit: `{humanize.naturalsize(file_limit)}`. Please lessen the text to make its size smaller.', mention_author=False)
				return await ctx.reply(file=discord.File(buf, 'ace.gif'), mention_author=False)
			
		class View(discord.ui.View):
			def __init__(self):
				super().__init__()
				self.msg = None

			async def interaction_check(self, interaction):
				if interaction.user != ctx.author:
					await interaction.response.send_message('This is not your interaction!', ephemeral=True)
					return False
				return True

			async def on_timeout(self):
				for item in self.children:
					item.disabled = True
				try:
					await self.msg.edit(view=self)
				except:
					pass

			@discord.ui.button(label='Attorney', style=discord.ButtonStyle.green)
			async def inp(self, button, interaction):
				modal = Modal(ctx.bot, 'Attorney Dialogue')
				modal.add_field(1, 'Name', value=str(ctx.author), min_length=1, max_length=240, required=True)
				modal.add_field(2, 'Text', min_length=1, max_length=240, required=True)
				await modal.send_modal(interaction)
				interacted, result = await modal.wait()
				if not interacted:
					return
				await modal.adapter.create_interaction_response(
					interacted.id,
					interacted.token,
					session=interacted._session,
					type=6
				)
				await self.msg.delete()
				name = result[0].value
				text = result[1].value
				async with ctx.typing():
					buf = await attorney_func(name, text)
				if (bsize := buf.getbuffer().nbytes) > file_limit:
					return await ctx.reply(f'Resulting gif size: `{humanize.naturalsize(bsize)}` is bigger than this guild file size limit: `{humanize.naturalsize(file_limit)}`. Please lessen the text to make its size smaller.', mention_author=False)
				await ctx.reply(file=discord.File(buf, 'attorney.gif'), mention_author=False)

			@discord.ui.button(label='Prosecutor', style=discord.ButtonStyle.red)
			async def prosecutor(self, button, interaction):
				modal = Modal(ctx.bot, 'Prosecutor Dialogue')
				modal.add_field(1, 'Name', value=str(ctx.author), min_length=1, max_length=240, required=True)
				modal.add_field(2, 'Text', min_length=1, max_length=240, required=True)
				await modal.send_modal(interaction)
				interacted, result = await modal.wait()
				if not interacted:
					return
				await modal.adapter.create_interaction_response(
					interacted.id,
					interacted.token,
					session=interacted._session,
					type=6
				)
				await self.msg.delete()
				name = result[0].value
				text = result[1].value
				async with ctx.typing():
					buf = await prosecutor_func(name, text)
				if (bsize := buf.getbuffer().nbytes) > file_limit:
					return await ctx.reply(f'Resulting gif size: `{humanize.naturalsize(bsize)}` is bigger than this guild file size limit: `{humanize.naturalsize(file_limit)}`. Please lessen the text to make its size smaller.', mention_author=False)
				await ctx.reply(file=discord.File(buf, 'prosecutor.gif'), mention_author=False)
		
		view = View()
		view.msg = await ctx.reply('Choose side', view=view, mention_author=False)

	@commands.command(aliases=['nono'])
	async def nonogram(self, ctx):
		"""Sudoku wannabe"""
		mapp = random.choice(ans_maps)
		view = NonoView(ctx, mapp)
		buf = await view.draw_board()
		url = await ctx.upload_bytes(buf.getvalue(), 'image/png', 'nonogram')

		embed = discord.Embed(title='Nonogram', color=self.bot.c, timestamp=dt.datetime.now())
		embed.set_image(url=url)
		embed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)

		view.msg = await ctx.reply(embed=embed, view=view, mention_author=False)	

	@commands.command(aliases=['sp', 'pp', 'pour', 'sort'])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def sort_puzzle(self, ctx, level:int=None):
		"""Sort liquid color!"""
		info = await ctx.db.fetchval('SELECT level FROM pour_level WHERE user_id = $1', ctx.author.id)

		if not info:
			await ctx.db.execute('INSERT INTO pour_level (user_id, level) VALUES ($1, 1)', ctx.author.id)
			highest_level = 1
		else:
			highest_level = info

		if level:
			if level > highest_level:
				return await ctx.reply('You haven\'t reached that level yet.', mention_author=False)
			highest_level = level

		view = PourView(ctx, highest_level)

		embed = discord.Embed(title='Pour Puzzle', description=f'Level : {highest_level}', timestamp=dt.datetime.now(), color=self.bot.c)
		img_buf = await view.draw_image()
		url = await ctx.upload_bytes(img_buf.getvalue(), 'image/png', 'pour game')
		embed.set_image(url=url)
		embed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)

		view.msg = await ctx.reply(embed=embed, view=view, mention_author=False)

def setup(bot):
	bot.add_cog(Fun(bot))