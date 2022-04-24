import aiohttp
import typing
import yarl
import datetime
from io import BytesIO


class APIError(Exception):
	pass


class JeyyAPIClient:
	def __init__(self, *, session: typing.Optional[aiohttp.ClientSession] = None) -> None:
		self.base_url: yarl.URL = yarl.URL('https://api.jeyy.xyz/')
		self.new_session = False
		if session is None:
			self.session = aiohttp.ClientSession()
			self.new_session = True
		else:
			self.session = session

	async def close(self) -> None:
		if self.new_session:
			if self.session.closed:
				raise TypeError('session is already closed')
				
			await self.session.close()
		else:
			raise TypeError('session was created manually. call .close() on the session instead.')

	async def __aenter__(self):
		if self.session.closed:
			raise TypeError('session has closed')
			
		return self

	async def __aexit__(self, exc_type, exc, tb):
		try:
			await self.close() # That's probably the only point of an async context manager. See https://github.com/JeyyGit/jeyyapi/pull/4
		except:
			pass

	# image
	async def _image_fetch(self, endpoint, **params) -> BytesIO:
		url = self.base_url / f'image/{endpoint}'
		async with self.session.get(url, params=params) as resp:
			if resp.status != 200:
				raise APIError(await resp.text())

			data = await resp.read()

		buffer = BytesIO(data)
		return buffer

	def patpat(self, image_url: str) -> BytesIO:
		return self._image_fetch('patpat', image_url=str(image_url))

	def burn(self, image_url: str) -> BytesIO:
		return self._image_fetch('burn', image_url=str(image_url))
	
	def glitch(self, image_url: str, level: typing.Optional[int] = 3) -> BytesIO:
		return self._image_fetch('glitch', image_url=str(image_url), level=int(level))
	
	def boil(self, image_url: str, level: typing.Optional[str] = 2) -> BytesIO:
		return self._image_fetch('boil', image_url=str(image_url), level=int(level))
	
	def earthquake(self, image_url: str, level: typing.Optional[int] = 3) -> BytesIO:
		return self._image_fetch('earthquake', image_url=str(image_url), level=int(level))

	def hearts(self, image_url: str, rainbow: typing.Optional[bool] = True) -> BytesIO:
		return self._image_fetch('hearts', image_url=str(image_url), rainbow=str(bool(rainbow)))
	
	def shock(self, image_url: str) -> BytesIO:
		return self._image_fetch('shock', image_url=str(image_url))
	
	def abstract(self, image_url: str) -> BytesIO:
		return self._image_fetch('abstract', image_url=str(image_url))
	
	def infinity(self, image_url: str) -> BytesIO:
		return self._image_fetch('infinity', image_url=str(image_url))
	
	def bomb(self, image_url: str) -> BytesIO:
		return self._image_fetch('bomb', image_url=str(image_url))
	
	def bonks(self, image_url: str) -> BytesIO:
		return self._image_fetch('bonks', image_url=str(image_url))
	
	def sob(self, image_url: str) -> BytesIO:
		return self._image_fetch('sob', image_url=str(image_url))
	
	def explicit(self, image_url: str) -> BytesIO:
		return self._image_fetch('explicit', image_url=str(image_url))
	
	def blur(self, image_url: str) -> BytesIO:
		return self._image_fetch('blur', image_url=str(image_url))
	
	def lamp(self, image_url: str) -> BytesIO:
		return self._image_fetch('lamp', image_url=str(image_url))
	
	def rain(self, image_url: str) -> BytesIO:
		return self._image_fetch('rain', image_url=str(image_url))
	
	def canny(self, image_url: str) -> BytesIO:
		return self._image_fetch('canny', image_url=str(image_url))
	
	def cartoon(self, image_url: str) -> BytesIO:
		return self._image_fetch('cartoon', image_url=str(image_url))
	
	def layers(self, image_url: str) -> BytesIO:
		return self._image_fetch('layers', image_url=str(image_url))
	
	def radiate(self, image_url: str) -> BytesIO:
		return self._image_fetch('radiate', image_url=str(image_url))
	
	def shoot(self, image_url: str) -> BytesIO:
		return self._image_fetch('shoot', image_url=str(image_url))
	
	def tv(self, image_url: str) -> BytesIO:
		return self._image_fetch('tv', image_url=str(image_url))
	
	def shear(self, image_url: str, axis: typing.Optional[str] = 'X') -> BytesIO:
		return self._image_fetch('shear', image_url=str(image_url), axis=str(axis))
	
	def magnify(self, image_url: str) -> BytesIO:
		return self._image_fetch('magnify', image_url=str(image_url))

	def print(self, image_url: str) -> BytesIO:
		return self._image_fetch('print', image_url=str(image_url))

	def matrix(self, image_url: str) -> BytesIO:
		return self._image_fetch('matrix', image_url=str(image_url))

	def sensitive(self, image_url: str) -> BytesIO:
		return self._image_fetch('sensitive', image_url=str(image_url))
	
	def dilute(self, image_url: str) -> BytesIO:
		return self._image_fetch('dilute', image_url=str(image_url))

	def pattern(self, image_url: str) -> BytesIO:
		return self._image_fetch('pattern', image_url=str(image_url))

	def logoff(self, image_url: str) -> BytesIO:
		return self._image_fetch('logoff', image_url=str(image_url))

	def ace(self, name: str, side: typing.Literal['attorney', 'prosecutor'], text: str) -> BytesIO:
		return self._image_fetch('ace', name=str(name), side=str(side), text=str(text))

	def gallery(self, image_url: str) -> BytesIO:
		return self._image_fetch('gallery', image_url=str(image_url))

	def paparazzi(self, image_url: str) -> BytesIO:
		return self._image_fetch('paparazzi', image_url=str(image_url))
	
	def balls(self, image_url: str) -> BytesIO:
		return self._image_fetch('balls', image_url=str(image_url))
	
	def equation(self, image_url: str) -> BytesIO:
		return self._image_fetch('equation', image_url=str(image_url))
	
	def half_invert(self, image_url: str) -> BytesIO:
		return self._image_fetch('half_invert', image_url=str(image_url))
	
	def roll(self, image_url: str) -> BytesIO:
		return self._image_fetch('roll', image_url=str(image_url))

	def clock(self, image_url: str) -> BytesIO:
		return self._image_fetch('clock', image_url=str(image_url))
	
	def optics(self, image_url: str) -> BytesIO:
		return self._image_fetch('optics', image_url=str(image_url))
	
	def warp(self, image_url: str) -> BytesIO:
		return self._image_fetch('warp', image_url=str(image_url))

	def ads(self, image_url: str) -> BytesIO:
		return self._image_fetch('ads', image_url=str(image_url))

	def bubble(self, image_url: str) -> BytesIO:
		return self._image_fetch('bubble', image_url=str(image_url))

	def cloth(self, image_url: str) -> BytesIO:
		return self._image_fetch('cloth', image_url=str(image_url))

	def youtube(self, avatar_url: str, author: str, title: str) -> BytesIO:
		return self._image_fetch('youtube', avatar_url=str(avatar_url), author=str(author), title=str(title))

	def scrapbook(self, text: str) -> BytesIO:
		return self._image_fetch('scrapbook', text=str(text))

	# text
	async def emojify(self, image_url: str) -> dict:
		params = {'image_url': str(image_url)}
		async with self.session.get(self.base_url / 'text/emojify', params=params) as resp:
			if resp.status != 200:
				raise APIError(await resp.text())
			
			result = await resp.json()

		return result

	# discord
	async def spotify(self, title: str, cover_url: str, duration: typing.Union[datetime.timedelta, int, float], start: typing.Union[datetime.datetime, float], artists: typing.List[str]) -> BytesIO:
		if isinstance(duration, datetime.timedelta):
			duration = int(duration.seconds)
		else:
			duration = int(duration)
			
		if isinstance(start, datetime.datetime):
			start = float(start.timestamp())
		else:
			start = float(start)
		
		params = {
			'title': str(title),
			'cover_url': str(cover_url),
			'duration_seconds': duration,
			'start_timestamp': start,
			'artists': artists
		}

		async with self.session.get(self.base_url / 'discord/spotify', params=params) as resp:
			if resp.status != 200:
				raise APIError(await resp.text())
			
			data = await resp.read()

		buffer = BytesIO(data)
		return buffer

	async def spotify_from_object(self, spotify: 'discord.Spotify') -> BytesIO:
		if spotify.__class__.__name__ != 'Spotify':
			raise TypeError(f'discord.Spotify is expected, {spotify.__class__.__name__} is passed instead.')

		kwargs = {
			'title': spotify.title,
			'cover_url': spotify.album_cover_url,
			'duration': spotify.duration.seconds,
			'start': spotify.start.timestamp(),
			'artists': spotify.artists
		}

		return await self.spotify(**kwargs)

	async def player(self, title: str, thumbnail_url: str, seconds_played: float, total_seconds: float, line_1: typing.Optional[str], line_2: typing.Optional[str]):
		params = {
			'title': title,
			'thumbnail_url': thumbnail_url,
			'seconds_played': seconds_played,
			'total_seconds': total_seconds,
			'line_1': line_1,
			'line_2': line_2,
		}

		async with self.session.get(self.base_url / 'discord/player', params=params) as resp:
			if resp.status != 200:
				raise APIError(await resp.text())
			
			data = await resp.read()

		buffer = BytesIO(data)
		return buffer

	async def wheel(self, args: typing.Union[typing.List[str], typing.Tuple[str]]) -> dict:
		async with self.session.get(self.base_url / 'discord/wheel', params={'args': args}) as resp:
			if resp.status != 200:
				raise APIError(await resp.text())
			
			result = await resp.json()

		return result

	async def ansi(
		self, 
		text: str, 
		bold: bool = False, 
		underline: bool = False, 
		text_color: typing.Literal['gray', 'red', 'green', 'yellow', 'blue', 'pink', 'cyan', 'white'] = None,
		bg_color: typing.Literal['dark blue', 'orange', 'gray 1', 'gray 2', 'gray 3', 'gray 4', 'indigo', 'white'] = None,
		codeblock: bool = True
		) -> str:

		params = {
			'text': text,
			'bold': str(bold),
			'underline': str(underline),
			'text_color': text_color,
			'bg_color': bg_color,
			'codeblock': str(codeblock),
		}

		async with self.session.get(self.base_url / 'discord/ansi', params=params) as resp:
			if resp.status != 200:
				raise APIError(await resp.text())
			
			result = await resp.json()

		return result

		