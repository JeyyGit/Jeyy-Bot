import discord
from discord.ext import commands
from io import BytesIO
from twemoji_parser import emoji_to_url
from jishaku.functools import executor_function
from discord_together import DiscordTogether
from bs4 import BeautifulSoup
import datetime as dt
import async_cse
import aiohttp
import decouple
import re


from utils.useful import chunk, Queue
from utils.paginator import Paginator
from utils.imaging import wand_gif
from utils.converters import ToImage


url_regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"


class ConversionError(Exception):
	...


class HTTPUploadError(Exception):
	...


class Loading:
	def __init__(self, ctx, content, embed):
		self.ctx = ctx
		self.content = content
		self.embed = embed
		self.message = None

	async def __aenter__(self):
		self.message = await self.ctx.reply(self.content, embed=self.embed, mention_author=False)

	async def __aexit__(self, exc_type, exc, tb):
		await self.message.delete()


class JeyyContext(commands.Context):

	@property
	def chunk(self):
		return chunk

	@property
	def session(self):
		return self.bot.session

	@property
	def db(self):
		return self.bot.db

	@property
	def keys(self):
		return self.bot.keys

	def Paginator(self):
		return Paginator(self)

	def Loading(self, content=None, embed=None):
		return Loading(self, content, embed)

	async def to_image(self, _input=None):
		"""Convert attachment, referenced attachment, emoji, partial emoji, member, user, url, tenor url to io.BytesIO object"""
		if self.message.attachments:
			buf = BytesIO(await self.message.attachments[0].read())
			buf.seek(0)
			return buf
		elif self.message.reference and self.message.reference.resolved.attachments:
			buf = BytesIO(await self.message.reference.resolved.attachments[0].read())
			buf.seek(0)
			return buf
		elif (ref := self.message.reference) and (content := ref.resolved.content):
			url = re.findall(url_regex, self.message.reference.resolved.content)
			if not url:
				url = await emoji_to_url(_input)
				url = re.findall(url_regex, url) # need to fix
				if not url:
					_input = BytesIO(await self.author.display_avatar.read())
					_input.seek(0)
					return _input
					# raise ConversionError("Could not convert input to Emoji, Member, or Image URL")

			url = url[0]

			response = await self.bot.session.get(url)
			if 'https://tenor.com' in url or 'https://tenor.com' in url or 'https://media.tenor' in url:
				html = await response.read()
				url_tenor = await self.scrape_tenor(html)
				resp = await self.bot.session.get(url_tenor)
				_input = BytesIO(await resp.read())
				_input.seek(0)
				return _input
			else:
				_input = BytesIO(await self.author.display_avatar.read())
				_input.seek(0)
				return _input
	
		if (stickers := self.message.stickers) and stickers[0].format != discord.StickerFormatType.lottie:
			response = await self.bot.session.get(self.message.stickers[0].url)
			buf = BytesIO(await response.read())
			buf.seek(0)
			return buf

		if _input is None:
			_input = BytesIO(await self.author.display_avatar.read())
			_input.seek(0)
		elif isinstance(_input, int):
			return await ToImage().convert(self, str(_input))
		elif isinstance(_input, discord.Emoji | discord.PartialEmoji):
			_input = BytesIO(await _input.read())
			_input.seek(0)
		elif isinstance(_input, discord.User | discord.Member):
			_input = BytesIO(await _input.display_avatar.read())
			_input.seek(0)
		else:
			url = re.findall(url_regex, _input)
			if not url:
				url = await emoji_to_url(_input)
				url = re.findall(url_regex, url)
				if not url:
					raise ConversionError("Could not convert input to Emoji, Member, or Image URL")

			url = url[0]

			response = await self.bot.session.get(url)
			if 'https://tenor.com' in url or 'https://media.tenor' in url:
				html = await response.read()
				url_tenor = await self.scrape_tenor(html)
				resp = await self.bot.session.get(url_tenor)
				_input = BytesIO(await resp.read())
				_input.seek(0)

			else:
				_input = BytesIO(await response.read())
				_input.seek(0)

		return _input

	def to_df(self, img, duration=50, **kwargs):
		if isinstance(img, list):
			igif = BytesIO()
			img[0].save(igif, format='GIF', append_images=img[1:], save_all=True, duration=duration, **kwargs)
			igif.seek(0)
			return discord.File(igif, 'output.gif')
		else:
			buf = BytesIO()
			img.save(buf, 'PNG')
			buf.seek(0)
			return discord.File(buf, 'output.png')

	def to_wand(self, frames, durations):
		return discord.File(wand_gif(frames, durations), 'output.gif')

	async def upload_bytes(self, *args, **kwargs):
		return await self.bot.upload_bytes(*args, **kwargs)

	async def upload_url(self, *args, **kwargs):
		return await self.bot.upload_url(*args, **kwargs)

	async def pull(self):   
		class MadeUp:
			content = 'git pull'

		await self.bot.get_command('jsk sh')(self, argument=MadeUp)

	async def push(self, commit_message='update'):
		class MadeUp:
			content = f'git add .\ngit commit -m "{commit_message}"\ngit push'

		await self.bot.get_command('jsk sh')(self, argument=MadeUp)

	@property
	async def cdn_size(self):
		
		r = await self.bot.session.get(
			'https://cdn.jeyy.xyz/size',
			headers={'auth': self.keys('CDNKEY')}
		)

		return await r.json()

	@discord.utils.copy_doc(discord.Message.reply)
	async def reply(self, content=None, mention_author=False, **kwargs):
		if self.bot._connection._get_message(self.message.id):
			return await self.message.reply(content, mention_author=mention_author, **kwargs)
		else:
			return await self.channel.send(content, **kwargs)

	@executor_function
	def scrape_tenor(self, html):

		soup = BeautifulSoup(html, features='html.parser')
		find = soup.find('div', {'class': 'Gif'})
		url = find.img['src']

		return url

	def get_ref(self, default=None):
		if self.message.reference:
			return self.message.reference.resolved
		
		return default

class JeyyBot(commands.Bot):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.launch_time = dt.datetime.now()
		self.keys = decouple.config
		self.walk = 0
		self.c = 0xf0ff1a
		self.snipe = {}
		self.context = None
		self.afk = {}
		self.username_cache = {}
		self.reply_cache = Queue(500)

	async def get_context(self, message, *, cls=JeyyContext):
		return await super().get_context(message, cls=cls)

	async def start(self, *args, **kwargs):
		self.session = aiohttp.ClientSession()
		self.togetherclient = await DiscordTogether(self.keys('BOTTOKEN'))
		self.google_client = async_cse.Search([	
			self.keys('GOOGLEKEY1'),
			self.keys('GOOGLEKEY2'),
			self.keys('GOOGLEKEY3'),
			self.keys('GOOGLEKEY4'),
			self.keys('GOOGLEKEY5'),
		])
		
		await super().start(*args, **kwargs)

	async def close(self):
		await self.session.close()
		await self.google_client.close()

		await super().close()

	async def upload_bytes(self, bytes, content_type, name=''):
		
		r = await self.session.post(
			'https://cdn.jeyy.xyz/upload_bytes',
			headers={'auth': self.keys('CDNKEY')},
			data={'bytes': bytes, 'content_type': content_type, 'name': name}
		)

		if r.status == 200:
			json = await r.json()
			return json['url']
		else:
			raise HTTPUploadError(f'Upload raises {r.status} HTTP exception: {await r.text()}')
	
	async def upload_url(self, url, content_type, name=''):
		
		r = await self.session.post(
			'https://cdn.jeyy.xyz/upload_url',
			headers={'auth': self.keys('CDNKEY')},
			data={'url': url, 'content_type': content_type, 'name': name}
		)

		if r.status == 200:
			json = await r.json()
			return json['url']
		else:
			raise HTTPUploadError(f'Upload raises {r.status} HTTP exception: {await r.text()}')


