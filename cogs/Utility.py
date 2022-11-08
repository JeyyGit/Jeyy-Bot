import logging
from PIL import Image, ImageOps
from PyPDF2 import PdfFileReader, PdfFileMerger
from dateutil.relativedelta import relativedelta
from discord.ext import commands
from googletrans import Translator, LANGUAGES
from io import BytesIO, StringIO
from jishaku.functools import executor_function
from arsenic import get_session, start_session, stop_session, services, browsers
from jishaku.codeblocks import codeblock_converter
from tabulate import tabulate
import async_cse
import asyncio
import datetime as dt
import discord
import importlib
import os
import io
import random
import re
import logging
import structlog
import typing
import urllib

from utils import views, useful, converters, trocr, sounder

importlib.reload(trocr)
importlib.reload(views)
importlib.reload(useful)
importlib.reload(converters)
importlib.reload(sounder)

from utils.imaging import (
	wheel_func,
	scrap_func,
	circle_func,
	scrolling_text_func,
	skyline_func
)

from utils.views import FileView, AnsiMaker, CariMenu, SounderView, PollView
from utils.converters import ToImage
from utils.trocr import TROCR, TROCRError
from utils.sounder import Sounder

service = services.Chromedriver(binary='../chromedriver', log_file=os.devnull)
browser = browsers.Chrome()
browser.capabilities = {"goog:chromeOptions": {"args": ["--no-sandbox", "--headless", "--disable-dev-shm-usage"]}}

logger = logging.getLogger('arsenic')

def logger_factory():
	return logger

structlog.configure(logger_factory=logger_factory)
logger.setLevel(logging.CRITICAL)

@executor_function
def img_to_emoji(image, best):
	with Image.open(image) as image4:
		im = image4.resize((best, best)).convert("RGBA")
		im = ImageOps.mirror(im)
		h = []
		x = 0

		dat = [
			(56, 56, 56), (242, 242, 242), (247, 99, 12), (0, 120, 215), (232, 18, 36), 
			(142, 86, 46), (136, 108, 228), (22, 198, 12), (255, 241, 0)
		]

		dat2 = "⬛⬜🟧🟦🟥🟫🟪🟩🟨"
		data = list(im.getdata())

		for p in data:
			x += 1
			p = list(p)

			def myFunc(e):
				r = p[0]
				g = p[1]
				b = p[2]

				er = e[0]
				eg = e[1]
				eb = e[2]

				return abs(r - er) + abs(g - eg) + abs(b - eb)

			if p[3] < 5:
				h.append("⬛")
			else:
				newlis = dat.copy()
				newlis.sort(key=myFunc)
				h.append(dat2[dat.index(newlis[0])])

			if x % im.width == 0:
				h.append("\n")

		al = [[] for _ in range(best)]
		row = 0
		for el in h:
			if el == '\n':
				row += 1
			else:
				al[row].append(el)
		
		text = '\n'.join([''.join(row[::-1]) for row in al])
		
		return text

def selected_servers(ctx):
	return ctx.guild.id in [750901194104504391, 776385025552941077, 332406449051402250]

class Utility(commands.Cog):
	"""Useful commands"""

	def __init__(self, bot):
		self.bot = bot
		self.thumbnail = "https://cdn.jeyy.xyz/image/wheel_spin_3845be.gif"
		self.translator = Translator()

	@commands.Cog.listener()
	async def on_ready(self):
		reminders = await self.bot.db.fetch('SELECT * FROM reminder ORDER BY time ASC')
		print(f"Utility Cog Loaded")

		for reminder in reminders:
			_id = reminder['id']
			user = self.bot.get_user(reminder['user_id']) or await self.bot.fetch_user(reminder['user_id'])
			channel = self.bot.get_channel(reminder['channel_id']) or await self.bot.fetch_channel(reminder['channel_id'])
			time = reminder['time']
			what = reminder['what']
			jump_url = reminder['jump_url']

			await discord.utils.sleep_until(time)
			await channel.send(f"{user.mention}: {what}\n\n{jump_url}")
			await self.bot.db.execute('DELETE FROM reminder WHERE id = $1', _id)
	
	@executor_function
	def translate_func(self, dest, text):
		translation = self.translator.translate(text, dest=dest)

		translated = translation.text
		source = LANGUAGES[translation.src.lower()]
		destination = LANGUAGES[translation.dest.lower()]
		
		return translated, source, destination

	@executor_function
	def translate_from_func(self, src, dest, text):
		try:
			translation = self.translator.translate(text, src=src, dest=dest)
		except ValueError:
			return "Failed", "Language is not listed. Please check `j;translate languages` to see available codes", ""
		else:
			translated = translation.text
			source = LANGUAGES[translation.src.lower()]
			destination = LANGUAGES[translation.dest.lower()]
			
			return translated, source, destination

	@commands.command(cooldown_after_parsing=True, aliases=['st', 'scroll_text'])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def scrolling_text(self, ctx, *, text: str):
		if len(text) > 70:
			ctx.command.reset_cooldown(ctx)
			return await ctx.reply('Text must be under or equal 70 characters')
		
		async with ctx.typing():
			buf = await scrolling_text_func(text)
		await ctx.reply(file=discord.File(buf, 'scroll_text.gif'))

	@commands.command(cooldown_after_parsing=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def demojify(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		_input = await ctx.to_image(_input)
		txt = await img_to_emoji(_input, 20)
		embed = discord.Embed(description=f'```\n{txt}```', color=self.bot.c)
		await ctx.reply(embed=embed, mention_author=False)

	@commands.command(cooldown_after_parsing=True)
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def ocr(self, ctx, image_url=None):
		"""Scan text from image"""
		if not image_url and not ctx.message.attachments:
			return await ctx.reply("Please provide the image.", mention_author=False)
		
		if not image_url:
			image_url = ctx.message.attachments[0].url

		r = await self.bot.session.post('https://api.openrobot.xyz/api/ocr', headers={'Authorization': ctx.keys('PROGUYKEY')}, params={'url': image_url})
		if r.status != 200:
			return await ctx.reply("An error occured, please input a valid image.", mention_author=False)
		json = await r.json()

		embed = discord.Embed(title="OCR result", description=json['text'], color=self.bot.c)
		await ctx.reply(embed=embed, mention_author=False)

	@commands.command(cooldown_after_parsing=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def together(self, ctx, activity=' '):
		"""Create an invite link for discord together.
		You have to be in a voice channel to use this.
		Activities: `youtube`, `poker`, `chess`, `fishing`, `betrayal`, `letter-tile`, `word-snack`, `doodle-crew`, `spellcast`, `awkword`, `checkers`
		"""

		valid = ['youtube', 'fishing', 'poker', 'chess', 'betrayal', 'letter-tile', 'word-snack', 'doodle-crew', 'spellcast', 'awkword', 'checkers']
		activity = activity.lower()

		if activity not in valid:
			return await ctx.reply(f"Please input activity type between {', '.join(f'`{v}`' for v in valid)}", mention_author=False)

		if not ctx.author.voice or ctx.author.voice.channel.guild != ctx.guild:
			return await ctx.reply("You are not in any voice channel.", mention_author=False)
		
		voice_channel = ctx.author.voice.channel
		
		link = await self.bot.togetherclient.create_link(voice_channel.id, activity)

		await ctx.reply(f"> Invite link for **{activity}** on {voice_channel.mention}\n{link}", mention_author=False)

	@commands.command(cooldown_after_parsing=True, aliases=['scrap'])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def scrapbook(self, ctx, *, text):
		"""Create scrapbook style gif from a given text
		Max length : `40`
		"""
		if len(text) > 40:
			return await ctx.reply("Max characters: `40`", mention_author=False)

		async with ctx.typing():
			buf = await scrap_func(text)
			if not buf:
				return await ctx.reply("No letters were detected.", mention_author=False)

			await ctx.reply(file=discord.File(buf, 'scrapbook.gif'), mention_author=False)

	@commands.group(invoke_without_command=True, aliases=['reminder'], hidden=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def remind(self, ctx, time, *, what="..."):

		if len(what) > 2000:
			return await ctx.reply("Character limit: 2000", mention_author=False)

		patterns = {
			'years': r"(\d+)(?= ?((years)|(year)|(y)))",
			'months': r"(\d+)(?= ?((months)|(month)|(mo)))",
			'weeks': r"(\d+)(?= ?((weeks)|(week)|(w)))",
			'days': r"(\d+)(?= ?((days)|(day)|(d)))",
			'hours': r"(\d+)(?= ?((hours)|(hour)|(h)))",
			'minutes': r"(\d+)(?= ?((minutes)|(minute)|(m[^o])|(m$)))",
			'seconds': r"(\d+)(?= ?((seconds)|(second)|(s)))"
		}

		res = {}
		for pattern in patterns:
			match = re.search(patterns[pattern], time)
			res[pattern] = 0 if match is None else int(match.group())

		if sum(res.values()) == 0:
			return await ctx.reply("Invalid time. example use `j;remind 1h30m code a bot`", mention_author=False)

		now = dt.datetime.utcnow()
		unix = dt.datetime.now()
		delta = relativedelta(**res).normalized()

		time = now + delta
		add = unix + delta
		add_ts = int(add.timestamp())

		_id = await self.bot.db.fetchval('''
			INSERT INTO reminder (
				user_id, channel_id, time, what, jump_url, expires)
			VALUES (
				$1, $2, $3, $4, $5, $6
			) RETURNING id''', ctx.author.id, ctx.channel.id, time, what, ctx.message.jump_url, add_ts
		)

		attrs = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
		human_readable = lambda delta: ['%d %s' % (getattr(delta, attr), attr if getattr(delta, attr) > 1 else attr[:-1]) for attr in attrs if getattr(delta, attr)]
		
		humanizeds = human_readable(delta)

		if len(humanizeds) == 1:
			humanized = humanizeds[0]
		elif len(humanizeds) == 2:
			humanized = f"{humanizeds[0]} and {humanizeds[1]}"
		else:
			humanized = f"{', '.join(humanizeds[:-1])}, and {humanizeds[-1]}"

		await ctx.reply(f"We will remind you {ctx.author.mention} in {humanized}: {what}")

		await discord.utils.sleep_until(time)
		await ctx.channel.send(f"{ctx.author.mention}: {what}\n\n{ctx.message.jump_url}")
		await self.bot.db.execute('DELETE FROM reminder WHERE id = $1', _id)

	@remind.command(cooldown_after_parsing=True, name="list", hidden=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def remind_list(self, ctx):
		
		reminders = await self.bot.db.fetch('SELECT * FROM reminder WHERE user_id = $1', ctx.author.id)

		embed = discord.Embed(title="You do not have any reminders" if not reminders else "Reminders", color=self.bot.c)
		
		for reminder in reminders:
			embed.add_field(name=f"id: {reminder['id']} | <t:{reminder['expires']}:R>", value=reminder['what'], inline=False)

		await ctx.reply(embed=embed, mention_author=False)

	@commands.group(invoke_without_command=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def todo(self, ctx):
		"""A way to keep track of your tasks.
		`j;todo list` to see your tasks\n`j;todo add [task]` to add new task\n`j;todo remove [task index]` to remove a task.\n`j;todo swap [index_1] [index_2]` to swap task indexes\n`j;todo prioritize [task index]` to prioritize a task\n`j;todo deprioritize` to deprioritize a prioritized task\n\nExample : `j;todo add Learn python`
		"""
		await ctx.send_help("todo")
		
	@todo.command(cooldown_after_parsing=True, usage="[task]")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def add(self, ctx, *, task:commands.clean_content=None):
		"""Add a task to your todo"""
		if not task:
			await ctx.reply("Missing the task you want to add.", mention_author=False, delete_after=15)
			ctx.command.reset_cooldown(ctx)
		else:
			author_id = ctx.author.id
			task = task.replace('`', "\u200b`\u200b")

			user = await self.bot.db.fetch("SELECT * FROM todo WHERE user_id = $1", author_id)

			if not user:
				await self.bot.db.execute("INSERT INTO todo (user_id, tasks) VALUES ($1, ARRAY[$2])", author_id, task)
			else:
				await self.bot.db.execute("UPDATE todo SET tasks = ARRAY_APPEND(tasks, $1) WHERE user_id = $2", task, author_id)

			tasks = await self.bot.db.fetchrow("SELECT tasks FROM todo WHERE user_id = $1", author_id)
			_len = len(tasks[0])

			await ctx.reply(embed=discord.Embed(title="Successfully added your task.", description=f"```c\n[{_len}] {task} ```", color=self.bot.c).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url), mention_author=False)

	@todo.command(cooldown_after_parsing=True, name="delete", aliases=["del", "remove"], usage="[task index]")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def deletes(self, ctx, index:int=None):
		"""Delete a task from you todo with given index"""
		author_id = ctx.author.id

		if not index:
			await ctx.reply("Missing index of the task you want to remove.", mention_author=False, delete_after=15)
			ctx.command.reset_cooldown(ctx)
		else:
			tasks = await self.bot.db.fetchrow("SELECT tasks FROM todo WHERE user_id = $1", author_id)
			if not tasks or not tasks[0]:
				await ctx.reply(embed=discord.Embed(title="You don't have any task.", color=self.bot.c).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url), mention_author=False)
				ctx.command.reset_cooldown(ctx)
			else:
				tasks = tasks[0]
				deleted_el = tasks[index-1]
				del tasks[index-1]
				await self.bot.db.execute("UPDATE todo SET tasks = $1 WHERE user_id = $2", tasks, author_id)
				await ctx.reply(embed=discord.Embed(title=f"Successfully deleted a task from your todo list", description=f"```c\n[{index}] {deleted_el} ```", color=self.bot.c).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url), mention_author=False)

	@todo.command(cooldown_after_parsing=True, name="list")
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def todo_list(self, ctx):
		"""Shows your todo list"""
		author_id = ctx.author.id

		tasks = await self.bot.db.fetchrow("SELECT tasks FROM todo WHERE user_id = $1", author_id)
		prioritized = await self.bot.db.fetchrow("SELECT prioritized FROM todo WHERE user_id = $1", author_id)
		
		if (not tasks or not tasks[0]) and (not prioritized or not prioritized[0]):
			await ctx.reply(embed=discord.Embed(title="You don't have any task.", color=self.bot.c).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url), mention_author=False)
			ctx.command.reset_cooldown(ctx)
		else:
			_list = [[]]
			text = []
			count = 0
			if not prioritized or not prioritized[0]:
				for i, task in enumerate(tasks[0]):
					_list[count].append(f"[{i+1}] {task}")
					if (i+1) % 10 == 0 and i+1 != len(tasks[0]):
						count += 1
						_list.append([])

				for pge in _list:
					text.append("```c\n{} ```".format("\n".join(pge)))

			elif not tasks or not tasks[0]:
				text.append("")
				text[0] = f"**```c\n[PRIORITIZED] {prioritized[0]} ```**"
			else:
				for i, task in enumerate(tasks[0]):
					_list[count].append(f"[{i+1}] {task}")
					if (i+1) % 10 == 0 and i+1 != len(tasks[0]):
						count += 1
						_list.append([])

				for pge in _list:
					text.append("**```c\n[PRIORITIZED] {}```** ```r\n{} ```".format(prioritized[0], "\n".join(pge)))

			embeds = []
			for page in text:
				embed = discord.Embed(title="Your task(s):", color=self.bot.c, description=page)
				embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
				embeds.append(embed)

			if len(embeds) == 1:
				return await ctx.reply(embed=embeds[0], mention_author=False)
			
			await ctx.Paginator().send(embeds, reply=True)

	@todo.command(cooldown_after_parsing=True, usage="[first index] [second index]")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def swap(self, ctx, i_1:int=None, i_2:int=None):
		"""Swap todo index"""
		author_id = ctx.author.id
		if not i_1 or not i_2:
			await ctx.reply("Missing index you want to swap.", mention_author=False, delete_after=15)
			ctx.command.reset_cooldown(ctx)
		else:
			tasks = await self.bot.db.fetchrow("SELECT tasks FROM todo WHERE user_id = $1", author_id)

			if not tasks or not tasks[0]:
				await ctx.reply(embed=discord.Embed(title="You don't have any task.", color=self.bot.c).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url), mention_author=False)
				ctx.command.reset_cooldown(ctx)
			else:
				tasks = tasks[0]
				tasks[i_1-1], tasks[i_2-1] = tasks[i_2-1], tasks[i_1-1]

				await self.bot.db.execute("UPDATE todo SET tasks = $1 WHERE user_id = $2", tasks, author_id)
				await ctx.reply(embed=discord.Embed(title="Successfully swapped your task.", description=f"```c\n[{i_1}->{i_2}] {tasks[i_2-1]} ``` ```c\n[{i_2}->{i_1}] {tasks[i_1-1]} ```", color=self.bot.c).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url), mention_author=False)

	@todo.command(cooldown_after_parsing=True, aliases=["p"], usage="[task index]")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def prioritize(self, ctx, index:int=None):
		"""Prioritize a task"""
		author_id = ctx.author.id

		if not index:
			await ctx.reply("Missing index you want to prioritize.", mention_author=False, delete_after=15)
			ctx.command.reset_cooldown(ctx)
		else:
			tasks = await self.bot.db.fetchrow("SELECT tasks FROM todo WHERE user_id = $1", author_id)

			if not tasks or not tasks[0]:
				await ctx.reply(embed=discord.Embed(title="You don't have any task.", color=self.bot.c).set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url), mention_author=False)
			else:
				prioritized = await self.bot.db.fetchrow("SELECT prioritized FROM todo WHERE user_id = $1", author_id)
				element = tasks[0][index-1]

				if not prioritized or not prioritized[0]:
					await self.bot.db.execute("UPDATE todo SET prioritized = $1 WHERE user_id = $2", element, author_id)
					await self.bot.db.execute("UPDATE todo SET tasks = ARRAY_REMOVE(tasks, $1) WHERE user_id = $2", element, author_id)
				else:
					tasks[0][index-1] = prioritized[0]
					await self.bot.db.execute("UPDATE todo SET (tasks, prioritized) = ($1, $2) WHERE user_id = $3", tasks[0], element, author_id)

				await ctx.reply(embed=discord.Embed(title="Successfully prioritizes a task.", description=f"**```c\n[PRIORITIZED] {element} ```**", color=self.bot.c).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url), mention_author=False)

	@todo.command(cooldown_after_parsing=True, aliases=["unprioritize", "dep", "unp"])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def deprioritize(self, ctx):
		"""Deprioritize already prioritized task"""
		author_id = ctx.author.id
		prioritized = await self.bot.db.fetchrow("SELECT prioritized FROM todo WHERE user_id = $1", author_id)

		if not prioritized or not prioritized[0]:
			await ctx.reply("You don't have any prioritized task!", mention_author=False, delete_after=15)
			ctx.command.reset_cooldown(ctx)
		else:
			await self.bot.db.execute("UPDATE todo SET tasks = ARRAY_APPEND(tasks, $1) WHERE user_id = $2", prioritized[0], author_id)
			await self.bot.db.execute("UPDATE todo SET prioritized = $1 WHERE user_id = $2", None, author_id)
			await ctx.reply(embed=discord.Embed(title="Successfully deprioritizes a task.", description=f"**```c\n[DEPRIORITIZED] {prioritized[0]} ```**", color=self.bot.c).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url), mention_author=False)

	@commands.command(cooldown_after_parsing=True, name="wheel", usage="[*arguments]")
	@commands.cooldown(1, 10, commands.BucketType.user)
	@commands.max_concurrency(1, commands.BucketType.channel)
	async def wheels(self, ctx, *args):
		"""Start a random picker wheel
		Put your choices and it will start a random picker wheel for you! For phrases, put it inside double quotes!\nAvailable number of options `2`, `3`, `4`, `6`.\n\nExample : `j;wheel me you \"not both\"`
		"""
		if len(args) not in [2, 3, 4, 6]:
			ctx.command.reset_cooldown(ctx)
			return await ctx.reply("Available number of arguments: `2`, `3`, `4`, `6`.", mention_author=False)

		colors = {
			"red"	: '\U0001f7e5', 
			"green" : '\U0001f7e9', 
			"blue" : '\U0001f7e6', 
			"yellow": '\U0001f7e8', 
			"orange": '\U0001f7e7', 
			"purple": '\U0001f7ea'
		}

		embed_colors = {
			"red": 0xDD2E44, 
			"green": 0x78B159, 
			"blue": 0x55ACEE, 
			"yellow": 0xFDCB58, 
			"orange": 0xF4900C, 
			"purple": 0xAA8ED6
		}

		async with ctx.Loading("<a:loading:747680523459231834> | Rendering wheel..."), ctx.typing():
			args = [i.replace("`", "\u200b") for i in args]
			_list = [f"{list(colors.values())[i]} :		{args[i]}" for i in range(len(args))]

			embed=discord.Embed(title="Picker Wheel", description="\n".join(_list), color=0x2F3136)
			embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)

			buf, res, _time, last, c = await wheel_func(args)

			link1 = await ctx.upload_bytes(buf.getvalue(), 'image/gif', 'wheel spin')
			link2 = await ctx.upload_bytes(last.getvalue(), 'image/png', 'wheel result')

			embed.set_image(url=link1)
		
		msg = await ctx.reply(embed=embed, mention_author=False)

		await asyncio.sleep(_time/1000+1)
		embed.add_field(name="\u2800", value=f"> **The result is {colors[c]} : {res} !**")
		embed.color = embed_colors[c]
		embed.set_image(url=link2)
		embed.set_thumbnail(url=link1)
		await msg.edit(embed=embed, allowed_mentions=discord.AllowedMentions.none())

	@commands.command(cooldown_after_parsing=True, usage="[*arguments]")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def choose(self, ctx, *choose:commands.clean_content):
		"""Argument chooser"""
		if not choose or len(choose) == 1:
			await ctx.reply("Please provide 2 or more arguments.", mention_author=False)
			ctx.command.reset_cooldown(ctx)
		else:
			await ctx.reply(f"I choose `{random.choice(choose)}`.", mention_author=False)

	@commands.command(cooldown_after_parsing=True, aliases=['polling', 'voting'], usage="[title] [timeout] [*choices]")
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def poll(self, ctx, title, timeout, *choices):
		"""Start a poll
		Please put title or options in \"\" for phrases\nTimeout format is `{number}s/h/d`\nmin choices: `2` | min timeout: `10`s\nmax choices: `10` | max timeout: `7`days \n\nExample : `j;polling \"Jeyy bot good?\" 3h yes no \"absolutely yes\"`
		"""
		if timeout.lower().endswith('d'):
			timeout = int(timeout.strip('d')) * 3600 * 24
		elif timeout.lower().endswith('h'):
			timeout = int(timeout.strip('h')) * 3600
		elif timeout.lower().endswith('m'):
			timeout = int(timeout.strip('m')) * 60
		elif timeout.lower().endswith('s'):
			timeout = int(timeout.strip('s'))
		else:
			timeout = int(timeout)

		if timeout > 604800 or timeout < 10:
			ctx.command.reset_cooldown(ctx)
			return await ctx.reply('Timeout must be more than 10s and less than 1 week.', mention_author=False)

		if len(choices) < 2 or len(choices) > 10:
			ctx.command.reset_cooldown(ctx)
			return await ctx.reply('Choices must be more than 2 and less than 10.', mention_author=False)

		if len(title) > 256:
			ctx.command.reset_cooldown(ctx)
			return await ctx.reply('Title length must be less than 256 characters.')

		if any(len(choice) > 80 for choice in choices):
			ctx.command.reset_cooldown(ctx)
			return await ctx.reply('Each choice length must be less than 80 characters.')
		
		poll_view = PollView(ctx, title, timeout, choices)
		await poll_view.start()

	@commands.group(invoke_without_command=True, cooldown_after_parsing=True, aliases=["trans", "tr"], usage="[destination] [text]")
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def translate(self, ctx, destination_lang, *, text:commands.clean_content=None):
		"""Translate to a given language
		`j;translate langs` to see all language destinations\nTranslate a given text to another language\n\nExample : `j;translate english Aku makan`, `j;translate zh-cn I want to eat`
		"""
		if destination_lang not in sum(LANGUAGES.items(), ()):
			await ctx.reply("Language is not listed. Please check `j;translate languages` to see available codes")
			return ctx.command.reset_cooldown(ctx)

		if not text:
			if ctx.message.reference and ctx.message.reference.resolved.content:
				text = ctx.message.reference.resolved.content
			else:
				await ctx.reply("Missing `text`.", mention_author=False)
				return ctx.command.reset_cooldown(ctx)

		async with ctx.typing():
			try:
				translated, source, destination = await self.translate_func(destination_lang, text)
				embeds = [
					discord.Embed(title=f"From {source.capitalize()}", description=f"```\n{text}```", color=self.bot.c).set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url),
					discord.Embed(title=f"To {destination.capitalize()}", description=f"```\n{translated}```", color=self.bot.c)
				]
				await ctx.reply(embeds=embeds, mention_author=False)
			except:
				await ctx.reply("An error occured", mention_author=False)
			
	@translate.command(name='from')
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def translate_from(self, ctx, from_lang, destination_lang, *, text:commands.clean_content=None):
		if not text:
			if ctx.message.reference and ctx.message.reference.resolved.content:
				text = ctx.message.reference.resolved.content
			else:
				await ctx.reply("Missing `text`.", mention_author=False)
				ctx.command.reset_cooldown(ctx)
				return

		async with ctx.typing():
			translated, source, destination = await self.translate_from_func(from_lang, destination_lang, text)

			if translated == "Failed":
				await ctx.reply(source, mention_author=False)
			else:
				
				embeds = []
				embeds.append(discord.Embed(title=f"From {source.capitalize()}", description=f"```\n{text}```", color=self.bot.c).set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url))
				embeds.append(discord.Embed(title=f"To {destination.capitalize()}", description=f"```\n{translated}```", color=self.bot.c))

				await ctx.reply(embeds=embeds, mention_author=False)

	@translate.command(aliases=['language', 'langs', 'lang'])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def languages(self, ctx):
		lines = ["`{} : {:30s}`".format(key, LANGUAGES[key]) for key in LANGUAGES]
		chunks = ctx.chunk(lines, combine=True)

		embeds = []
		for page in chunks:
			embed = discord.Embed(title="Language codes", description=page, color=self.bot.c)
			embeds.append(embed)

		await ctx.Paginator().send(embeds, reply=True)

	@commands.command(cooldown_after_parsing=True, aliases=["g", "ggl"])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def google(self, ctx, *, query):
		"""Search from Google"""
		query = query[:225]

		try:
			results = await self.bot.google_client.search(query)
		except async_cse.NoResults:
			return await ctx.reply(f'No result found for: "{query}"')
		except (async_cse.NoMoreRequests, async_cse.APIError):
			return await ctx.reply("An internal error occurred, please try again later.")
		
		pages = ctx.chunk(results, 4)
		embeds = []
		for page in pages:
			embed = discord.Embed(title=f'Search result for: {query}', color=self.bot.c, timestamp=dt.datetime.now())
			for result in page:
				embed.add_field(name=result.title, value=f'[*{result.url}*]({result.url})\n{result.description}', inline=False)
			embed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
			embeds.append(embed)

		await ctx.Paginator().send(embeds, reply=True)

	@commands.group(invoke_without_command=True, hidden=True)
	async def kas(self, ctx):
		kases = await self.bot.db.fetch("SELECT * FROM kas WHERE guild_id = $1", ctx.guild.id)

		if not kases:
			await ctx.reply("Tidak ada kas di server ini.", mention_author=False)
		else:
			kass = await self.bot.db.fetch("SELECT nama_kas FROM kas WHERE guild_id = $1 GROUP BY nama_kas", ctx.guild.id)
			text = [f"`{i+1}`. `{kas[0]}`" for i, kas in enumerate(kass)]
			await ctx.reply("List kas di server ini\n{}".format("\n".join(text)), mention_author=False)

	@kas.command(aliases=['buat'])
	async def create(self, ctx, nama_kas:str):

		kas = await self.bot.db.fetch("SELECT * FROM kas WHERE guild_id = $1 AND nama_kas = $2", ctx.guild.id, nama_kas)
		nama_kasses = await self.bot.db.fetch("SELECT nama_kas FROM kas WHERE guild_id = $1 GROUP BY nama_kas", ctx.guild.id)
		
		if len(nama_kasses) > 15:
			return await ctx.reply("Batas maksimum 15 kas sudah tercapai.", mention_author=False)
			
		if not kas:
			await self.bot.db.execute("INSERT INTO kas (guild_id, nama_kas) VALUES ($1, $2)", ctx.guild.id, nama_kas)
			await ctx.reply(f"Kas baru dengan nama **\"{nama_kas}\"** telah dibuat.", mention_author=False)
		else:
			await ctx.reply(f"Kas dengan nama **\"{nama_kas}\"** sudah ada sebelumnya.", mention_author=False)

	@kas.command(aliases=['remove', 'hapus'])
	async def delete(self, ctx, nama_kas:str):

		kas = await self.bot.db.fetch("SELECT * FROM kas WHERE guild_id = $1 AND nama_kas = $2", ctx.guild.id, nama_kas)

		if kas:
			await self.bot.db.execute("DELETE FROM kas WHERE guild_id = $1 AND nama_kas = $2", ctx.guild.id, nama_kas)
			await ctx.reply(f"Kas dengan nama **\"{nama_kas}\"** telah dihapus.", mention_author=False)
		else:
			await ctx.reply(f"Tidak ditemukan kas dengan nama **\"{nama_kas}\"**", mention_author=False)

	@kas.command(aliases=['add'])
	async def tambah(self, ctx, nama_kas:str, member:discord.Member, uang:int):

		kas = await self.bot.db.fetch("SELECT * FROM kas WHERE guild_id = $1 AND nama_kas = $2", ctx.guild.id, nama_kas)

		if not kas:
			await ctx.reply(f"Tidak ditemukan kas dengan nama **\"{nama_kas}\"**", mention_author=False)
			return

		if len(kas) > 51:
			return await ctx.reply(f"Batas maksimum 50 data untuk kas {nama_kas} sudah tercapai.", mention_author=False)

		uangs = f"Rp {uang}"
		date = dt.datetime.now()
		tanggal = date.strftime("%A, %d %b %Y %I:%M %p")
		await self.bot.db.execute("INSERT INTO kas (guild_id, nama_kas, user_id, uang, tanggal) VALUES ($1, $2, $3, $4, $5)", ctx.guild.id, nama_kas, member.id, uang, tanggal)
		await ctx.reply(f"**{member}** ditambahkan ke kas **\"{nama_kas}\"** sejumlah **{uangs}** pada **{tanggal}**.", mention_author=False)

	@kas.command(aliases=['hilangkan'])
	async def kurangi(self, ctx, nama_kas:str, member:discord.Member):

		kas = await self.bot.db.fetch("SELECT user_id FROM kas WHERE user_id = $1 AND guild_id = $2 AND nama_kas = $3", member.id, ctx.guild.id, nama_kas)
		
		if not kas:
			await ctx.reply(f"Gagal. **{member}** tidak ditemukan dalam kas atau nama kas **\"{nama_kas}\"** tidak ditemukan.", mention_author=False)
			return

		await self.bot.db.execute("DELETE FROM kas WHERE guild_id = $1 AND nama_kas = $2 AND user_id = $3", ctx.guild.id, nama_kas, member.id)
		await ctx.reply(f"**{member}** sudah di hilangkan dari kas **\"{nama_kas}\"**.", mention_author=False)

	@kas.command(aliases=['table'])
	async def tabel(self, ctx, nama_kas:str):

		kas = await self.bot.db.fetch("SELECT * FROM kas WHERE guild_id = $1 AND nama_kas = $2", ctx.guild.id, nama_kas)

		if not kas:
			await ctx.reply(f"Tidak ditemukan kas dengan nama **\"{nama_kas}\"**", mention_author=False)
			return

		q = await self.bot.db.fetch("SELECT * FROM kas WHERE guild_id = $1 AND nama_kas = $2", ctx.guild.id, nama_kas)
		j = await self.bot.db.fetchval("SELECT COALESCE(SUM(uang), 0) AS total FROM kas WHERE guild_id = $1 AND nama_kas = $2 GROUP BY guild_id, nama_kas", ctx.guild.id, nama_kas)
		q.pop(0)
		a = [{'No': i+1, 'Nama': str(self.bot.get_user(b['user_id']) or await self.bot.fetch_user(b['user_id'])), 'Uang': f"Rp {b['uang']}", 'Tanggal': b['tanggal']} for i, b in enumerate(q)]
		a.append({'No': "-", 'Nama': "Total", 'Uang': f"Rp {int(j)}", 'Tanggal': ""})
		tabel = tabulate(a, headers="keys", tablefmt="pretty", stralign="center", numalign="center")

		try:
			await ctx.reply(f"```swift\nTABEL KAS \"{nama_kas}\"\n{tabel}```", mention_author=False)
		except:
			s = StringIO()
			s.write(f"TABEL KAS \"{nama_kas}\"\n{tabel}")
			s.seek(0)
			try:
				await ctx.reply(file=discord.File(s, filename="Tabel.c"), mention_author=False)
			except:
				paste = await self.bot.mystbin_client.post(f"TABEL KAS \"{nama_kas}\"\n{tabel}", syntax='c')
				await ctx.reply(f"Tabel terlalu panjang. Klik {paste} untuk melihat tabel secara penuh", mention_author=False)

	@kas.command(aliases=['help'])
	async def cara(self, ctx):
		embed = discord.Embed(title="Command untuk kas", description="""
			`j;kas` melihat semua kas yang ada di server
			`j;kas cara` menunjukan pesan ini
			`j;kas buat "[nama kas]"` membuat kas baru
			`j;kas hapus "[nama kas]"` menghapus kas
			`j;kas tambah "[nama kas]" [@mention] [jumlah uang]` menambah orang yang di @mention ke sebuah kas dengan jumlah uang tertentu
			`j;kas hilangkan "[nama kas]" [@mention]` menghilangkan data yang di @mention dari sebuah kas
			`j;kas tabel "[nama kas]"` Menampilkan tabel sebuah kas

			`"[nama kas]"` harus di dalam tanda petik dua `"`
			""", color=self.bot.c)
		embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
		await ctx.reply(embed=embed, mention_author=False)

	@commands.command(aliases=['ms'], hidden=True)
	async def minesweeper(self, ctx):
		board = [[0]*8 for _ in range(8)]
		for _ in range(6):
			ri = random.choice([*range(1,7)])
			rj = random.choice([*range(1,7)])

			board[ri][rj] = 9

		for i in range(1, 7):
			for j in range(1, 7):
				c = 0
				if board[i][j] == 0:
					if board[i-1][j-1] == 9:
						c += 1
					if board[i-1][j] == 9:
						c += 1
					if board[i-1][j+1] == 9:
						c += 1
					if board[i][j-1] == 9:
						c += 1
					if board[i][j+1] == 9:
						c += 1
					if board[i+1][j-1] == 9:
						c += 1
					if board[i+1][j] == 9:
						c += 1
					if board[i+1][j+1] == 9:
						c += 1
					board[i][j] = c

		all_nums = ["\U00000030", "\U00000031", "\U00000032", "\U00000033", "\U00000034", "\U00000035", "\U00000036", "\U00000037", "\U00000038", "\U00000039"]
		text = []
		txt = []

		for i in range(1, 7):
			text.append([])
			for j in range(1, 7):
				if board[i][j] == 0:
					text[i-1].append(f"||{all_nums[0]}\U0000fe0f\U000020e3||")
				elif board[i][j] == 1:
					text[i-1].append(f"||{all_nums[1]}\U0000fe0f\U000020e3||")
				elif board[i][j] == 2:
					text[i-1].append(f"||{all_nums[2]}\U0000fe0f\U000020e3||")
				elif board[i][j] == 3:
					text[i-1].append(f"||{all_nums[3]}\U0000fe0f\U000020e3||")
				elif board[i][j] == 4:
					text[i-1].append(f"||{all_nums[4]}\U0000fe0f\U000020e3||")
				elif board[i][j] == 5:
					text[i-1].append(f"||{all_nums[5]}\U0000fe0f\U000020e3||")
				elif board[i][j] == 6:
					text[i-1].append(f"||{all_nums[6]}\U0000fe0f\U000020e3||")
				elif board[i][j] == 7:
					text[i-1].append(f"||{all_nums[7]}\U0000fe0f\U000020e3||")
				elif board[i][j] == 8:
					text[i-1].append(f"||{all_nums[8]}\U0000fe0f\U000020e3||")
				elif board[i][j] == 9:
					text[i-1].append("||\U0001f4a3||")
		
		text.insert(0, ['\U0001f7e8', '\U0001f7e8', '\U0001f7e8', '\U0001f7e8', '\U0001f7e8', '\U0001f7e8', '\U0001f7e8', '\U0001f7e8'])
		text.append(['\U0001f7e8', '\U0001f7e8', '\U0001f7e8', '\U0001f7e8', '\U0001f7e8', '\U0001f7e8', '\U0001f7e8', '\U0001f7e8'])
		for i in range(1, 7):
			text[i].insert(0, '\U0001f7e8')
			text[i].append('\U0001f7e8')

		[txt.append("".join(row)) for row in text]
		result = "\n".join(txt)
		await ctx.reply(f"There're max 6 bombs!\n{result}", mention_author=False)
			
	@commands.command(cooldown_after_parsing=True, aliases=['quote'], usage="[message id]")
	@commands.cooldown(1, 5, commands.BucketType.guild)
	async def quotes(self, ctx, message_id: discord.Message=None):
		"""Create a mock of message from message ID"""
		if not message_id:
			message_id = ctx.message
			msg = "I'm dumb because i did not provide the message i want to quote."
		else:
			msg = message_id.content

		if message_id.channel.nsfw and not ctx.channel.nsfw:
			await ctx.reply("That message is from NSFW channel.", mention_author=False)
			return

		avatar = await ctx.to_image(message_id.author.display_avatar.with_size(32).url)

		buf = await circle_func(avatar, (32, 32))
		avamoji = await self.bot.get_guild(776385025552941077).create_custom_emoji(name="cool_dude" if message_id.author.id in self.bot.owner_ids else "ugly", image=buf.read())

		await ctx.send(f">>> {avamoji} **{message_id.author}**\n{msg}", embed=message_id.embeds[0] if message_id.embeds else None, file=await message_id.attachments[0].to_file() if message_id.attachments else None, allowed_mentions=discord.AllowedMentions.none())
		await avamoji.delete()

	@commands.command(cooldown_after_parsing=True, usage="<member> [content]")
	@commands.cooldown(1, 5, commands.BucketType.guild)
	async def sayas(self, ctx, member: typing.Optional[discord.Member]=None, *, content):
		"""Create a mock of message given by someone with given content"""
		member = member or ctx.author

		avatar = await ctx.to_image(member.display_avatar.with_size(32).url)

		buf = await circle_func(avatar, (32, 32))
		avamoji = await self.bot.get_guild(776385025552941077).create_custom_emoji(name="cool_dude" if member.id in self.bot.owner_ids else "ugly", image=buf.read())

		await ctx.send(f">>> {avamoji} **{member}**\n{content}", allowed_mentions=discord.AllowedMentions.none())
		await avamoji.delete()

	@commands.command(cooldown_after_parsing=True, aliases=['gay'], usage="[member]")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def gaymeter(self, ctx, member:discord.Member=None):
		"""See how gay a person is"""
		member = member or ctx.author

		random.seed(member.id)
		percent = random.randint(0, 100)

		embed = discord.Embed(description=f"**{member}** is **{percent}%** gay! \U0001f3f3\U0000fe0f\U0000200d\U0001f308", timestamp=dt.datetime.utcnow(), color=self.bot.c)
		embed.set_author(name=f"{member} gaymeter", icon_url=member.avatar.url)
		embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

		await ctx.reply(embed=embed, mention_author=False)

	@commands.command(hidden=True)
	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.max_concurrency(1, commands.BucketType.user)
	async def pdf(self, ctx):
		"""Create a new PDF from another PDF(s)
		After you upload your PDF(s), you can specify which pages from those PDF(s)
		that you want to be on your new PDF.
		
		Format for new PDF: `{file number}:{start page}-{end page}`
		Example format = `1:2-5 3:19-25 2:5` -> page 2-5 from File 1 + page 19-25 from File 3 + page 5 from File 2
		"""
		pdfembed = discord.Embed(title="Please send the pdf file.", color=self.bot.c)
		msg = await ctx.reply(embed=pdfembed, allowed_mentions=discord.AllowedMentions.none())

		def filecheck(message):
			if not message.attachments or message.attachments[0].content_type != "application/pdf":
				return False
			
			return message.author == ctx.author and message.channel == ctx.channel

		attachments = []
		while True:
			try:
				file_msg = await self.bot.wait_for('message', check=filecheck, timeout=60)
				try:
					await msg.delete()
				except:
					pass
				try:
					await ask.delete()
				except:
					pass
			except asyncio.TimeoutError:
				return await msg.reply("Timed out.", mention_author=False)
		
			attachments.extend([attachment for attachment in file_msg.attachments if attachment.content_type == "application/pdf"])

			pdfs = []

			embed = discord.Embed(title="Files:", color=self.bot.c)
			for i, attachment in enumerate(attachments):
				pdf = PdfFileReader(BytesIO(await attachment.read()))
				pdfs.append(BytesIO(await attachment.read()))
				embed.add_field(name=f"File {i+1}: `{attachment.filename}`", value=f"Page number: `{pdf.getNumPages()}`", inline=False)
			embed.set_footer(text="Max files is 9.")

			file_view = FileView(ctx, len(attachments) > 10)
			file_view.start()
			ask = await ctx.reply(embed=embed, view=file_view, mention_author=False)

			await file_view.wait()

			if file_view.value is None:
				return await ask.delete()
			elif file_view.value == 1:
				msg = await ctx.send(embed=pdfembed)
				await ask.edit(embed=embed, view=None)
				continue
			elif file_view.value == 2:
				await ask.edit(embed=embed, view=None)
				break
			else:
				return await ask.delete()

		embed = discord.Embed(title="Type below how you want to create your new pdf: ", color=self.bot.c)
		embed.description = "Format = `{file number}:{start page}-{end page}`\n" + \
							"Example = `1:2-5 3:19-25` -> page 2-5 from file 1 & page 19-25 from file 3"

		msg = await ask.reply(embed=embed, mention_author=False)

		try:
			arg_msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=60)
		except asyncio.TimeoutError:
			return await msg.reply("Timed out.")

		merge = PdfFileMerger()

		try:
			argument = arg_msg.content
			keys = re.findall("\\d+(?=:)", argument)
			raw_range = re.findall("[\\d-]+(?!:)", argument)
			_range = [re.findall("\\d+", r) for r in raw_range]
			arg_list = [[keys[i], _range[i] if len(_range[i]) == 2 else _range[i]*2] for i in range(len(keys))]
			for sec in arg_list:
				merge.append(pdfs[int(sec[0])-1], pages=(int(sec[1][0])-1, int(sec[1][1])))
		except Exception as e:
			return await arg_msg.reply(f"Invalid argument.\n{e}", mention_author=False)

		send = await arg_msg.reply("Making new pdf from:\n"+',\n'.join([f"Page {'-'.join(_range[i])} of File {keys[i]}" for i in range(len(keys))]), mention_author=False)

		merged = BytesIO()
		merge.write(merged)
		merged.seek(0)

		class UploadPDF(discord.ui.View):
			@discord.ui.button(label="Upload PDF", style=discord.ButtonStyle.primary)
			async def upload(self, button, interaction):
				if interaction.user != ctx.author:
					return await interaction.response.send_message("This is not your interaction!", ephemeral=True)

				url = await ctx.upload_bytes(merged.getvalue(), 'application/pdf', f"PDF_{ctx.author.id}")
				url_button = discord.ui.Button(label="PDF Uploaded", url=url)

				self.clear_items()
				self.add_item(url_button)
				return await interaction.response.edit_message(view=self)

		await send.reply(file=discord.File(merged, f"PDF_{ctx.author.id}_{hash(merged)}.pdf"), view=UploadPDF())
		merge.close()

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def afk(self, ctx, *, reason=None):
		"""Set your status to AFK"""
		reason = reason or "Not specified"
		reason = reason if len(reason) < 500 else reason[:500] + "..."

		await self.bot.db.execute("INSERT INTO afk (user_id, reason, since) VALUES ($1, $2, $3)", ctx.author.id, reason, dt.datetime.utcnow())

		await ctx.reply(discord.utils.escape_mentions(f"I have set your status to AFK for : {reason}"))

	@commands.command(aliases=['ft', 'ansi'], hidden=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def format_text(self, ctx, *, text: codeblock_converter):
		"""Colored text format"""
		content = text.content.strip('\n')
		if len(content) > 980:
			return await ctx.reply('Text must be under 980 characters.')
		view = AnsiMaker(ctx, content)
		view.msg = await ctx.reply(f'```ansi\n{content}\n```', view=view, allowed_mentions=discord.AllowedMentions.none())

	@commands.command(aliases=['ss'])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def screenshot(self, ctx, url, delay=0):
		"""Get a screenshot of given url
		Screenshot will be send to you dm if channel not marked as NSFW to avoid sending inappropriate websites.
		You can set delay which waits for the screenshot so the page could load with min = 0 second and max = 10 seconds
		Url must starts with `http://` or `https://`
		"""
		url = url.strip("<>")

		if not url.startswith('http'):
			return await ctx.reply('Please include `http://` or `https://`.', mention_author=False)

		delay = 0 if delay < 0 else delay
		delay = 10 if delay > 10 else delay

		async with ctx.typing(), get_session(service, browser) as session:
			await session.set_window_size(1400, 1000)
			try:
				await session.get(url, 30)
			except Exception as e:
				if isinstance(e, asyncio.TimeoutError):
					return await ctx.reply('Aborting from taking too long.', mention_author=False)
				else:
					return await ctx.reply('URL not resolved. Please make sure it\'s correct.', mention_author=False)
			await asyncio.sleep(delay)

			buf = await session.get_screenshot()

		f = discord.File(buf, 'screenshot.png')
		embed = discord.Embed(title='Link', url=url, timestamp=dt.datetime.now(), color=self.bot.c)
		embed.set_image(url='attachment://screenshot.png')
		embed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)

		if isinstance(ctx.channel, discord.DMChannel) or ctx.channel.nsfw:
			await ctx.reply(embed=embed, file=f, mention_author=False)
		else:
			try:
				msg = await ctx.author.send(embed=embed, file=f)

				view = discord.ui.View()
				view.add_item(discord.ui.Button(label='Go to dm', url=msg.jump_url))
				og = await ctx.reply('Screenshot has been sent to your dm.', view=view, mention_author=False)

				back_view = discord.ui.View()
				back_view.add_item(discord.ui.Button(label=f'Back to #{ctx.channel}', url=og.jump_url))
				await msg.edit(view=back_view)
			except:
				return await ctx.reply('Could not send the result to your dm. Please make sure you have your dm open.', mention_author=False)
			
	@commands.command(hidden=True)
	async def cari(self, ctx, *, cari):
		async with ctx.Loading('Mencari data dosen dan mahasiswa...'):
			session = await start_session(service, browser)
			await session.set_window_size(700, 1200)
			await session.get(f'https://pddikti.kemdikbud.go.id/search/{urllib.parse.quote(cari)}')

			tables = await session.get_elements('div.table-responsive')

			dosen_rows = await tables[2].get_elements('tr')
			dosen_mapping = []
			for row in dosen_rows:
				link = await row.get_element('a.add-cart-parimary-btn')
				text = await row.get_text()
				if text.startswith('Cari kata kunci'):
					break
				label, desc = map(lambda t: t[:95] + '...' if len(t) > 100 else t, text.split('\n'))
				dosen_mapping.append([label, desc, link])

			mahasiswa_rows = await tables[3].get_elements('tr')
			mahasiswa_mapping = []
			for row in mahasiswa_rows:
				link = await row.get_element('a.add-cart-parimary-btn')
				text = await row.get_text()
				if text.startswith('Cari kata kunci'):
					break
				label, desc = map(lambda t: t[:95] + '...' if len(t) > 100 else t, text.split('\n'))
				mahasiswa_mapping.append([label, desc, link])

			if not dosen_mapping and not mahasiswa_mapping:
				await stop_session(session)
				return await ctx.reply('Data dosen/mahasiswa tidak ditemukan.', mention_author=False)

			menu_dosen = CariMenu(ctx, session, dosen_mapping, 'dosen')
			menu_mahasiswa = CariMenu(ctx, session, mahasiswa_mapping, 'mahasiswa')

			class View(discord.ui.View):
				async def interaction_check(self, interaction: discord.Interaction):
					if interaction.user != ctx.author:
						await interaction.response.send_message('This is not your interaction!', ephemeral=True)
						return False
					return True

				async def on_timeout(self):
					try:
						await stop_session(session)
						for child in self.children:
							child.disabled = True
						await self.msg.edit(view=self)
					except:
						...
					
			view = View(timeout=None)
			view.add_item(menu_dosen)
			view.add_item(menu_mahasiswa)

			view.msg = await ctx.reply('Hasil pencarian:', view=view, mention_author=False)

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def urban(self, ctx, *, term):
		"""Urban dictionary lookup"""

		url = 'http://api.urbandictionary.com/v0/define'
		
		r = await ctx.session.get(url, params={'term': term})
		js = await r.json()
		results = js.get('list', [])
		
		if not results:
			return await ctx.reply('No definition found.')

		embeds = []
		for result in results:
			definition = result['definition'].replace('[', '').replace(']', '')
			definition = definition if len(definition) < 2000 else definition[:2000] + '...'

			embed = discord.Embed(title=f'Term: {result["word"]}', url=result['permalink'], description=definition+'\n\u200b', timestamp=dt.datetime.now(), color=self.bot.c)
			embed.add_field(name='Votes', value=f'<:upvote:596577438461591562> {result["thumbs_up"]} | <:downvote:596577438952062977> {result["thumbs_down"]}', inline=True)
			embed.add_field(name='Author', value=result['author'], inline=True)
			embed.add_field(name='Created at', value=discord.utils.format_dt(discord.utils.parse_time(result['written_on'][:-1]), 'd'))
			embed.set_thumbnail(url='https://cdn.jeyy.xyz/image/7c0e71.png')
			embed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
			embeds.append(embed)

		await ctx.Paginator().send(embeds, reply=True)

	@commands.command()
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def trocr(self, ctx, lang, image: ToImage = None):
		"""Translate text on image"""
		if image is None:
			if ctx.message.reference and ctx.message.reference.resolved.attachments:
				image = await ctx.to_image(ctx.message.reference.resolved.attachments[0].url)
			elif ctx.message.attachments:
				image = await ctx.to_image(ctx.message.attachments[0].url)
			else:
				return await ctx.reply('Please provide the image.')

		async with ctx.typing():
			trocr = TROCR(self.bot, lang, image)
			
			try:
				result = await trocr.run()
				url = result.url
			except TROCRError as e:
				return await ctx.reply(e)
			
			r = await self.bot.session.get(url)
			img = io.BytesIO(await r.read())
			
			file = discord.File(img, 'trocr.png')

			await ctx.reply(file=file)

	@commands.command(hidden=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def sounder(self, ctx):
		sounder = Sounder()
		await sounder.init()
		sounder_view = SounderView(ctx, sounder)

		sounder_view.msg = await ctx.reply(f'\u200b', view=sounder_view, mention_author=False, allowed_mentions=discord.AllowedMentions.none())

	@commands.command(cooldown_after_parsing=True)
	@commands.cooldown(1, 30, commands.BucketType.user)
	async def skyline(self, ctx, github_username, year:int=2022):
		"""3D GitHub contribution graph"""
		if year < 2008 or year > 2022:
			ctx.command.reset_cooldown(ctx)
			return await ctx.reply('Invalid year')

		r = await self.bot.session.get(f'https://skyline.github.com/{github_username}/{year}.json')
		if r.status == 500:
			ctx.command.reset_cooldown(ctx)
			return await ctx.reply('Username not found.')

		async with ctx.Loading("<a:loading:747680523459231834> | Rendering data..."), ctx.typing():
			js = await r.json()
			buf = await skyline_func(js['contributions'], js['username'], str(year))
		await ctx.reply(file=discord.File(buf, 'github_skyline.gif'))		

def setup(bot):
	bot.add_cog(Utility(bot))
