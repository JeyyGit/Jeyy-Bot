from akinator.async_aki import Akinator
from discord.ext import commands
from io import BytesIO
import aiohttp
import discord
import importlib
import json
import math
import random
import re
import typing
import xkcd

from utils import views, converters
importlib.reload(views)
importlib.reload(converters)

from utils.views import (
	ConfirmView,
	ConfirmationView,
	DeleteView,
	AkiView
)

from utils.converters import ToImage

url_regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

def get_xckd(color):
	comic = xkcd.getRandomComic()

	embed = discord.Embed(title=comic.getTitle(), url=comic.getImageLink(), color=color)
	embed.set_image(url=comic.getImageLink())

	return embed

class Api(commands.Cog):
	"""External API commands"""

	def __init__(self, bot):
		self.bot = bot
		self.thumbnail = "https://cdn.jeyy.xyz/image/http_2a872d.png"

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"Api Cog Loaded")

	async def get_url(self, ctx, _input):
		
		if ctx.message.attachments:
			return ctx.message.attachments[0].url
		elif ctx.message.reference and ctx.message.reference.resolved.attachments:
			return ctx.message.reference.resolved.attachments[0].url
		
		if not _input:
			return ctx.author.avatar.url
		elif isinstance(_input, discord.Emoji) or isinstance(_input, discord.PartialEmoji):
			return _input.url
		elif isinstance(_input, discord.Member):
			return _input.url
		else:
			url = re.findall(url_regex, _input)
			if url:
				return url[0]
			else:
				return False

	async def get_zz(self, ctx, _input, endpoint, percent=80):
		url = await self.get_url(ctx, _input)
		if not url:
			return False

		headers = {'Authorization': f'Bearer {ctx.keys("ZZKEY")}'}
		if endpoint == 'sand':
			json = {'image_url': url}
		elif endpoint == 'explode':
			json = {'image_url': url, 'percent':percent}

		response = await self.bot.session.get(
			f'https://zneitiz.herokuapp.com/image/{endpoint}',
			headers=headers,
			json=json
			)

		if response.status == 200:
			buf = BytesIO(await response.read())
			buf.seek(0)
			return buf
		else:
			return False

	async def get_waifu_sfw(self, endpoint):

		res = await self.bot.session.get(f'https://waifu.pics/api/sfw/{endpoint}')
		res = await res.json()

		return res['url']

	async def get_waifu_nsfw(self, ctx, endpoint):
		if isinstance(ctx.channel, discord.channel.DMChannel) or ctx.channel.is_nsfw():
			confirm = await ConfirmationView(ctx).ask('This command is NSFW, are you sure you want to open?')
			if not confirm:
				return

			r = await self.bot.session.get(f"https://waifu.pics/api/nsfw/{endpoint}")
			res = await r.json()
			embed = discord.Embed(color=self.bot.c)
			embed.set_image(url=res['url'])
			embed.set_footer(text="Message will be deleted in 60s or click delete button")

			delview = DeleteView(ctx)
			delview.message = await ctx.reply(embed=embed, view=delview, delete_after=60, mention_author=False)
		else:
			await ctx.reply("That command is NSFW. You can open it on NSFW channel only.", mention_author=False)

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.channel)
	async def dream(self, ctx, image: ToImage = None):
		async with ctx.typing():
			buf = image or await ToImage.none(ctx)
			r = await self.bot.session.post(
				'https://api.deepai.org/api/deepdream', 
				data={'image': buf.read()}, 
				headers={'api-key': ctx.keys('DEEPAIKEY')}
			)
			js = await r.json()
			res = await self.bot.session.get(js['output_url'])
			buf = BytesIO(await res.read())
			buf.seek(0)
		await ctx.reply(file=discord.File(buf, 'dream.png'))

	@commands.command(cooldown_after_parsing=True, hidden=True)
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def replace_colors(self, ctx, *colors: discord.Color):
		"""Powered by zneitiz api"""
		async with ctx.typing():
			excolors = []
			for color in colors:
				excolors.extend(color.to_rgb())

			json = {
				'image_url': ctx.author.display_avatar.url,
				'animated': ctx.author.display_avatar.is_animated(),
				'colors':  [color.to_rgb() for color in colors],
				'max_distance': 16
			}
			
			headers = {'Authorization': f'Bearer {ctx.keys("ZZKEY")}'}
			r = await self.bot.session.get(
				f'https://zneitiz.herokuapp.com/image/replace_colors',
				headers=headers,
				json=json
			)

			# print(await r.text())
			buf = BytesIO(await r.read())

			return await ctx.reply( file=discord.File(buf, f'zz.{["png", "gif"][ctx.author.display_avatar.is_animated()]}'), mention_author=False)

	@commands.command(cooldown_after_parsing=True)
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def sand(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, str]=None):
		"""Powered by zneitiz api"""
		async with ctx.typing():
			buf = await self.get_zz(ctx, _input, 'sand')
			if not buf:
				return await ctx.reply("An error occured.", mention_author=False)

			return await ctx.reply(file=discord.File(buf, 'zzsand.gif'), mention_author=False)

	@commands.command(cooldown_after_parsing=True)
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def explode(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, str]=None, level: int=80):
		"""Powered by zneitiz api"""
		async with ctx.typing():
			buf = await self.get_zz(ctx, _input, 'explode', level)
			if not buf:
				return await ctx.reply("An error occured.", mention_author=False)

			return await ctx.reply(file=discord.File(buf, 'zzexplode.gif'), mention_author=False)

	@commands.command(aliases=["comic"])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def xkcd(self, ctx):
		"""Random XKCD comics"""
		async with ctx.typing():
			embed = await self.bot.loop.run_in_executor(None, get_xckd, self.bot.c)

		await ctx.reply(embed=embed, mention_author=False)

	@commands.group(aliases=['cat'], invoke_without_command=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def http(self, ctx, num:int=None):
		"""Show random or given http error cat images"""
		async with ctx.typing():
			nums = [100, 101, 102, 200, 201, 202,
					204, 206, 207, 300, 301, 302,
					303, 304, 305, 307, 308, 400, 401,
					402, 403, 404, 405, 406, 407, 408,
					409, 410, 411, 412, 413, 414,
					415, 416, 417, 418, 420, 421,
					422, 423, 424, 425, 426, 429,
					431, 444, 450, 451, 497, 498, 499, 500,
					501, 502, 503, 504, 506, 507,
					508, 509, 510, 511, 521, 523, 525, 599]

			if not num:
				num = random.choice(nums)
			elif num not in nums:
				num = 404

			url = f"https://http.cat/{num}"
			async with aiohttp.ClientSession() as session:
				async with session.get(url) as response:
					buf = BytesIO(await response.read())
					await ctx.reply(file=discord.File(buf, f"error_code_{num}.jpg"), mention_author=False)

	@http.command(name='list')
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def _list(self, ctx):
		"""Shows every HTTP error codes"""
		nums = [100, 101, 102, 200, 201, 202,
				204, 206, 207, 300, 301, 302,
				303, 304, 305, 307, 308, 400, 401,
				402, 403, 404, 405, 406, 407, 408,
				409, 410, 411, 412, 413, 414,
				415, 416, 417, 418, 420, 421,
				422, 423, 424, 425, 426, 429,
				431, 444, 450, 451, 497, 498, 499, 500,
				501, 502, 503, 504, 506, 507,
				508, 509, 510, 511, 521, 523, 525, 599]

		await ctx.reply(f', '.join([f'`{num}`' for num in nums]), mention_author=False)

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def gif(self, ctx, *, search=""):
		"""Search or random gif"""
		async with ctx.typing():
			session = aiohttp.ClientSession()
			if search == "":
				embed = discord.Embed(title="Here's a random gif", color=self.bot.c).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
				response = await session.get(f"https://api.giphy.com/v1/gifs/trending?api_key={ctx.keys('GIPHYKEY')}&limit=25&rating=pg-13")
			else:
				embed = discord.Embed(title=f"{search} search result", color=self.bot.c).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
				response = await session.get('http://api.giphy.com/v1/gifs/search?q=' + search + '&api_key=' + ctx.keys('GIPHYKEY') + '&limit=20')

			data = json.loads(await response.text())
			gif_choice = random.randint(0, len(data['data'])-1)
			embed.set_image(url=data['data'][gif_choice]['images']['original']['url'])

			await ctx.reply(embed=embed, mention_author=False)

	@commands.command(aliases=['memes'])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def meme(self, ctx):
		"""Random reddit memes"""
		async with ctx.typing():
			sub = random.choice(["memes", "funny", "dankmemes"])
			while True:
				async with aiohttp.ClientSession() as cs:
					async with cs.get(f"https://meme-api.herokuapp.com/gimme/{sub}") as r:
						res = await r.json()
						if res['nsfw'] == False:
							break

			name = res['title']
			url = res['url']
			embed = discord.Embed(title=name, description=f"<:upvote:596577438461591562> {res['ups']}", color=self.bot.c).set_image(url=url).set_image(url=url).set_footer(text=f"Posted by u/{res['author']} on r/{res['subreddit']}")
			await ctx.reply(embed=embed, mention_author=False)

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def reddit(self, ctx, subreddit:str='all'):
		"""Search or random or given subreddit post"""
		if subreddit == "keqing":
			return await ctx.send("no.")
		async with ctx.typing():
			nsfw = 0

			while True:
				async with aiohttp.ClientSession() as cs:
					async with cs.get(f"https://meme-api.herokuapp.com/gimme/{subreddit}") as r:
						res = await r.json()

						try:
							code = res['code']
							url = f"https://http.cat/{code}"
							async with aiohttp.ClientSession() as session:
								async with session.get(url) as response:
									buf = BytesIO(await response.read())
									await ctx.reply(f"`{res['code']}: {res['message']}`", file=discord.File(buf, f"error_code_{code}.jpg"), mention_author=False)
							break

						except:
							if res.get('nsfw') is False:
								name = res['title']
								url = res['url']
								embed = discord.Embed(title=name, description=f"<:upvote:596577438461591562> {res['ups']}", color=self.bot.c).set_image(url=url).set_footer(text=f"Posted by u/{res['author']} on r/{res['subreddit']}")
								await ctx.reply(embed=embed, mention_author=False)
								break
							else:
								if ctx.channel.is_nsfw():
									confirm = await ConfirmationView(ctx).ask('This post is marked as NSFW, are you sure you want to open?')
									if not confirm:
										return

									name = res['title']
									url = res['url']

									embed = discord.Embed(title=name, description=f"<:upvote:596577438461591562> {res['ups']}", color=self.bot.c).set_image(url=url).set_footer(text=f"Posted by u/{res['author']} on r/{res['subreddit']}")
									
									del_view = DeleteView(ctx)
									del_view.message = await ctx.reply(embed=embed, view=del_view, delete_after=60, mention_author=False)
									return
								else:
									nsfw += 1
									if nsfw == 3:
										await ctx.reply("That subreddit is marked as NSFW. You can open it on NSFW channel only.", mention_author=False)
										break

	@commands.command()
	@commands.cooldown(1, 30, commands.BucketType.user)
	@commands.max_concurrency(1, commands.BucketType.user)
	async def guess(self, ctx):
		"""The bot will try to guess your character"""
		buttons = {
			'yes': "\U0001f1fe", 
			'no': "\U0001f1f3", 
			'idk': "\U0001f937", 
			'p': "\U0001f4ad", 
			'pn': "\U0001f5ef", 
			'exit': "\U0001f6d1"
		}

		bar = "\U000025fe" * 10
		text = f"{buttons['yes']} : yes\n{buttons['no']} : no\n{buttons['idk']} : i don't know\n{buttons['p']} : probably\n{buttons['pn']} : probably not\n{buttons['exit']} : exit\n[{bar}]"

		async with ctx.typing():
			async with ctx.Loading("<a:loading:747680523459231834> | Preparing questions..."):
				aki = Akinator()
				q = await aki.start_game(client_session=self.bot.session)
				count = 1
				
				embed = discord.Embed(title="Character Guesser (beta)", description="question number 1", color=self.bot.c)
				embed.add_field(name=q, value=text)
				embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
				embed.set_footer(text="click the button to answer")
		
		view = AkiView(ctx)
		sent = await ctx.reply(embed=embed, view=view, allowed_mentions=discord.AllowedMentions.none())
		while aki.progression <= 80:
			await view.wait()

			if view.result is None:
				await aki.win()
				embed.set_footer(text="Timed out!")
				await sent.edit(embed=embed, view=None, allowed_mentions=discord.AllowedMentions.none())
				return

			if view.result == 'exit':
				await sent.delete()
				await aki.win()
				return
			
			q = await aki.answer(view.result)

			if aki.progression <= 80:
				prog = math.floor(aki.progression * 10 / 80)
				unprog = 10 - prog
				bar = "\U0001f7e8" * prog + "\U000025fe" * unprog
				text = f"{buttons['yes']} : yes\n{buttons['no']} : no\n{buttons['idk']} : i don't know\n{buttons['p']} : probably\n{buttons['pn']} : probably not\n{buttons['exit']} : exit\n[{bar}]"
				embed.clear_fields()
				embed.add_field(name=q, value=text)
				embed.set_footer(text="click the button to answer")
				count = aki.step + 1
				embed.description = f"question number {count}"
				view = AkiView(ctx)
				await sent.edit(embed=embed, view=view, allowed_mentions=discord.AllowedMentions.none())
			
			if count > 75:
				await aki.win()
				embed.clear_fields()
				embed.description = "Number of question passed 75 :( I can't guess your character"
				return await sent.edit(embed=embed, view=None, allowed_mentions=discord.AllowedMentions.none())

		await aki.win()
		bar = "\U0001f7e8" * 10
		embed.clear_fields()
		embed.add_field(name="Guessed character: ", value=f"**{aki.first_guess['name']}** !\n{aki.first_guess['description']}\n\n[{bar}]")
		embed.set_image(url=aki.first_guess['absolute_picture_path'])
		embed.set_footer(text="Was i correct?")
		embed.description = f"Total questions : {count}"
		await sent.edit(embed=embed, view=None, allowed_mentions=discord.AllowedMentions.none())

	@commands.group(invoke_without_command=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def anime(self, ctx):
		"""Sends a waifu image/gif"""
		text = f"{ctx.author.display_name} asked for waifu"

		url = await self.get_waifu_sfw('waifu')
		embed = discord.Embed(title=text, color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def slap(self, ctx, member:discord.Member=None):
		if not member:
			text = f"{ctx.author.display_name} slapped themself really hard!"
		else:
			text = f"{ctx.author.display_name} slapped {member.display_name} really hard!"

		url = await self.get_waifu_sfw('slap')
		embed = discord.Embed(title=text, color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def cuddle(self, ctx, member:discord.Member=None):
		if not member:
			text = f"{ctx.author.display_name} cuddles with their imaginary waifu!"
		else:
			text = f"{ctx.author.display_name} cuddles with {member.display_name}!"

		url = await self.get_waifu_sfw('cuddle')
		embed = discord.Embed(title=text, color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def hug(self, ctx, member:discord.Member=None):
		if not member:
			text = f"{ctx.author.display_name} hugged their imaginary waifu!"
		else:
			text = f"{ctx.author.display_name} hugged {member.display_name}!"

		url = await self.get_waifu_sfw('hug')
		embed = discord.Embed(title=text, color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def kiss(self, ctx, member:discord.Member=None):
		if not member:
			text = f"{ctx.author.display_name} kisses their imaginary waifu!"
		else:
			text = f"{ctx.author.display_name} kisses {member.display_name}!"

		url = await self.get_waifu_sfw('kiss')
		embed = discord.Embed(title=text, color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def lick(self, ctx, member:discord.Member=None):
		if not member:
			text = f"{ctx.author.display_name} licked random people! (ew)"
		else:
			text = f"{ctx.author.display_name} licked {member.display_name}!"

		url = await self.get_waifu_sfw('lick')
		embed = discord.Embed(title=text, color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def pat(self, ctx, member:discord.Member=None):
		if not member:
			text = f"pat pat-"
		else:
			text = f"{ctx.author.display_name} pats {member.display_name}!"

		url = await self.get_waifu_sfw('pat')
		embed = discord.Embed(title=text, color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def smug(self, ctx, member:discord.Member=None):
		if not member:
			text = f"{ctx.author.display_name} smugs!"
		else:
			text = f"{ctx.author.display_name} smugs {member.display_name}!"

		url = await self.get_waifu_sfw('smug')
		embed = discord.Embed(title=text, color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def hit(self, ctx, member:discord.Member=None):
		if not member:
			text = f"{ctx.author.display_name} hits themself!"
		else:
			text = f"{ctx.author.display_name} hits {member.display_name}!"

		url = await self.get_waifu_sfw('bonk')
		embed = discord.Embed(title=text, color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command(aliases=['hf'])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def highfive(self, ctx, member:discord.Member=None):
		if not member:
			text = f"{ctx.author.display_name} highfives random people (weirdo)!"
		else:
			text = f"{ctx.author.display_name} highfives {member.display_name}!"

		url = await self.get_waifu_sfw('highfive')
		embed = discord.Embed(title=text, color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command(aliases=['hh'])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def handhold(self, ctx, member:discord.Member=None):
		if not member:
			text = f"{ctx.author.display_name} handholds random people (weirdo)!"
		else:
			text = f"{ctx.author.display_name} handholds {member.display_name}!"

		url = await self.get_waifu_sfw('handhold')
		embed = discord.Embed(title=text, color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def bite(self, ctx, member:discord.Member=None):
		if not member:
			text = f"{ctx.author.display_name} bit random people (weirdo)!"
		else:
			text = f"{ctx.author.display_name} bit {member.display_name}!"

		url = await self.get_waifu_sfw('bite')
		embed = discord.Embed(title=text, color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def glomp(self, ctx, member:discord.Member=None):
		if not member:
			text = f"{ctx.author.display_name} glomps to random people (weirdo)!"
		else:
			text = f"{ctx.author.display_name} glomps to {member.display_name}!"

		url = await self.get_waifu_sfw('glomp')
		embed = discord.Embed(title=text, color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def kill(self, ctx, member:discord.Member=None):
		if not member:
			text = f"{ctx.author.display_name} kills innocent people!"
		else:
			text = f"{ctx.author.display_name} kills {member.display_name}!"

		url = await self.get_waifu_sfw('kill')
		embed = discord.Embed(title=text, color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def poke(self, ctx, member:discord.Member=None):
		if not member:
			text = f"{ctx.author.display_name} pokes random people (weirdo)!"
		else:
			text = f"{ctx.author.display_name} pokes {member.display_name}!"

		url = await self.get_waifu_sfw('poke')
		embed = discord.Embed(title=text, color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def neko(self, ctx):
		url = await self.get_waifu_sfw('neko')
		embed = discord.Embed(title="neko neko \U0001f431", color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def cry(self, ctx):
		url = await self.get_waifu_sfw('cry')
		embed = discord.Embed(title=f"{ctx.author.display_name} is crying :'(", color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def yeet(self, ctx):
		url = await self.get_waifu_sfw('yeet')
		embed = discord.Embed(title=f"{ctx.author.display_name} yeeted!", color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def blush(self, ctx):
		url = await self.get_waifu_sfw('blush')
		embed = discord.Embed(title=f"{ctx.author.display_name} is blushing \U0001f633!", color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def smile(self, ctx):
		url = await self.get_waifu_sfw('smile')
		embed = discord.Embed(title=f"{ctx.author.display_name} is smiling!", color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def nom(self, ctx):
		url = await self.get_waifu_sfw('nom')
		embed = discord.Embed(title=f"nom nom nom", color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def happy(self, ctx):
		url = await self.get_waifu_sfw('happy')
		embed = discord.Embed(title=f"{ctx.author.display_name} is happy!", color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def dance(self, ctx):
		url = await self.get_waifu_sfw('dance')
		embed = discord.Embed(title=f"{ctx.author.display_name} is dancing!", color=self.bot.c)
		embed.set_image(url=url)
		await ctx.reply(embed=embed, mention_author=False)

	@anime.command(hidden=False)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def nsfwwaifu(self, ctx):
		await self.get_waifu_nsfw(ctx, 'waifu')

	@anime.command(hidden=False)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def nsfwneko(self, ctx):
		await self.get_waifu_nsfw(ctx, 'neko')

	@anime.command(hidden=False)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def nsfwtrap(self, ctx):
		await self.get_waifu_nsfw(ctx, 'trap')

	@anime.command(name="nsfwbj", aliases=["nsfwblowjob"], hidden=False)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def nsfwblowjob(self, ctx):
		await self.get_waifu_nsfw(ctx, 'blowjob')

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def catboy(self, ctx):
		res = await self.bot.session.get('https://api.catboys.com/img/catboy')
		url = (await res.json())['url']

		embed = discord.Embed(color=self.bot.c).set_image(url=url)

		await ctx.reply(embed=embed, mention_author=False)

	@anime.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def yaoi(self, ctx):
		res = await self.bot.session.get('https://api.catboys.com/img/yaoi')
		url = (await res.json())['url']

		embed = discord.Embed(color=self.bot.c).set_image(url=url)

		await ctx.reply(embed=embed, mention_author=False)

def setup(bot):
	bot.add_cog(Api(bot))