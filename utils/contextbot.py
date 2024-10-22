import datetime as dt
import json
import os
import re
from io import BytesIO

import aiohttp
import async_cse
import asyncpg
import decouple
import discord
import humanize
import numpy as np
import PIL
import winerp
from bs4 import BeautifulSoup
from discord.ext import commands
from discord_together import DiscordTogether
from jishaku.functools import executor_function
from PIL import Image
from twemoji_parser import emoji_to_url
from zneitiz import NeitizClient, NeitizException, NeitizRatelimitException

from utils.converters import ToImage
from utils.imaging import wand_gif
from utils.paginator import Paginator
from utils.useful import Queue, chunk

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

	def check_buffer(self, buffer):
		if (size := buffer.getbuffer().nbytes) > 15000000:
			raise ConversionError(f'Provided image size ({humanize.naturalsize(size)}) is larger than 15 MB size limit.')

		try:
			Image.open(buffer)
		except PIL.UnidentifiedImageError:
			raise ConversionError('Could not open provided image. Make sure it is a valid image types')
		finally:
			buffer.seek(0)

		return buffer

	async def to_image(self, _input=None):
		"""Convert attachment, referenced attachment, emoji, partial emoji, member, user, url, tenor url to io.BytesIO object"""
		if self.message.attachments:
			buf = BytesIO(await self.message.attachments[0].read())
			buf.seek(0)
			return self.check_buffer(buf)
		elif self.message.reference and self.message.reference.resolved.attachments:
			buf = BytesIO(await self.message.reference.resolved.attachments[0].read())
			buf.seek(0)
			return self.check_buffer(buf)
		elif (ref := self.message.reference) and (embeds := ref.resolved.embeds) and (image := embeds[0].image) and _input is None:
			return await ToImage().convert(self, image.url)
		elif (ref := self.message.reference) and (content := ref.resolved.content) and _input is None:
			return await ToImage().convert(self, content)
	
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

		return self.check_buffer(_input)

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

	def to_wand(self, frames, durations=50):
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
			if self.interaction is None:
				return await self.channel.send(content, **kwargs)
			return await super().reply(content, **kwargs)

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
		self.ipc = winerp.Client(local_name=self.keys('WINERPLOCALNAME'), port=int(self.keys('WINERPPORT')))
		self.walk = 0
		self.commands_cache = None
		self.c = 0xf0ff1a
		self.snipe = {}
		self.context = None
		self.afk = {}
		self.username_cache = {}
		self.reply_cache = Queue(500)

	async def get_context(self, message, *, cls=JeyyContext):
		return await super().get_context(message, cls=cls)
	
	async def setup_hook(self):
		self.db = await asyncpg.create_pool(
			host=self.keys('DBHOST'), database=self.keys('DBNAME'),
			user=self.keys('DBUSER'), password=self.keys('DBPASS')
    	)

		for filename in os.listdir("./cogs"):
			if filename.endswith(".py"):
				await self.load_extension(f"cogs.{filename[:-3]}")
		await self.load_extension("jishaku")
		self.cmd_state = [cmd.__dict__ for cmd in self.walk_commands()]

		self.session = aiohttp.ClientSession()
		self.loop.create_task(self.ipc.start())
		self.togetherclient = await DiscordTogether(self.keys('BOTTOKEN'))
		self.znclient = NeitizClient()
		self.google_client = async_cse.Search([	
			self.keys('GOOGLEKEY1'),
			self.keys('GOOGLEKEY2'),
			self.keys('GOOGLEKEY3'),
			self.keys('GOOGLEKEY4'),
			self.keys('GOOGLEKEY5'),
		])
		self.jeyy_key = self.keys('JEYYAPIKEY')

		with open('./image/ios_emojis/emoji_lut.json', 'r') as f:
			self.emoji_lut = np.array(json.load(f), dtype='object')

		with open('./image/mc_blocks/mc_lut.json', 'r') as f:
			self.mc_lut = np.array(json.load(f), dtype='object')

	async def close(self):
		await self.session.close()
		await self.google_client.close()
		await self.znclient.close()

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

	async def get_api(self, endpoint, params=None, headers=None, method='GET'):

		if params is None:
			params = {}

		if headers is None:
			headers = {}

		headers |= {'Authorization': f'Bearer {self.jeyy_key}'}

		method = method.upper()
		if method == 'GET':
			r = await self.session.get(f'https://api.jeyy.xyz/v2/{endpoint}', params=params, headers=headers)
		elif method == 'POST':
			r = await self.session.post(f'https://api.jeyy.xyz/v2/{endpoint}', params=params, headers=headers)
		elif method == 'HEAD':
			r = await self.session.head(f'https://api.jeyy.xyz/v2/{endpoint}', params=params, headers=headers)
		elif method == 'PUT':
			r = await self.session.put(f'https://api.jeyy.xyz/v2/{endpoint}', params=params, headers=headers)
		elif method == 'DELETE':
			r = await self.session.delete(f'https://api.jeyy.xyz/v2/{endpoint}', params=params, headers=headers)
		elif method == 'OPTIONS':
			r = await self.session.options(f'https://api.jeyy.xyz/v2/{endpoint}', params=params, headers=headers)
		elif method == 'PATCH':
			r = await self.session.patch(f'https://api.jeyy.xyz/v2/{endpoint}', params=params, headers=headers)
		else:
			raise Exception('Invalid method')
		
		return r

	def get_command_list(self):
		if all(cs == cc for cs, cc in zip(self.cmd_state, [cmd.__dict__ for cmd in self.walk_commands()], strict=False)) and self.commands_cache is not None:
			print('using cached command list')
			return self.commands_cache
		
		class Ctx:
			clean_prefix = 'j;'

		self.help_command.context = Ctx()

		def walk_group(group, current):
			for command in group.commands:
				if command.hidden:
					return current
				cmd_data = {}
				cmd_data['short_doc'] = command.short_doc or None
				cmd_data['signature'] = self.help_command.get_command_signature(command) or None
				cmd_data['aliases'] = command.aliases or None
				cmd_data['extras'] = command.extras or None
				if isinstance(command, commands.Group):
					cmd_data['sub_commands'] = walk_group(command, {})
					current[command.name] = cmd_data
				else:
					cmd_data['sub_commands'] = None
					current[command.name] = cmd_data
			return current

		all_cmds = {}
		for cog_name in self.cogs:
			cog = self.get_cog(cog_name)
			if getattr(cog, 'hidden', False) or cog.qualified_name == 'Jishaku':
				continue

			cog_cmds = {}
			for cmd in cog.get_commands():
				if cmd.hidden:
					continue
				cmd_data = {}
				cmd_data['short_doc'] = cmd.short_doc or None
				cmd_data['signature'] = self.help_command.get_command_signature(cmd) or None
				cmd_data['aliases'] = cmd.aliases or None
				cmd_data['extras'] = cmd.extras or None
				if isinstance(cmd, commands.Group):
					cmd_data['sub_commands'] = walk_group(cmd, {})
					cog_cmds.update({cmd.name: cmd_data})
				else:
					cmd_data['sub_commands'] = None
					cog_cmds.update({cmd.name: cmd_data})
			all_cmds[cog_name] = cog_cmds

		self.commands_cache = all_cmds
		return all_cmds
