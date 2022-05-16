from discord.ext import commands
from io import BytesIO
import discord
import importlib
import typing

from utils import imaging, useful, converters
importlib.reload(useful)
importlib.reload(imaging)
importlib.reload(converters)

from utils.imaging import *
from utils.converters import ToImage


class IMAGE(commands.Cog, name="Image"):
	"""Image generation/manipulation commands"""
	
	def __init__(self, bot):
		self.bot = bot
		self.bot.image_cache = {}
		self.thumbnail = "https://cdn.jeyy.xyz/image/patpat_4fe81e.gif"

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"Image Cog Loaded")

	@commands.command(aliases=['gb_cam', 'gbc'], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def gameboy_camera(self, ctx, imgb: ToImage = None):
		"""Can't play kirby here"""
		async with ctx.typing():
			buf = await gameboy_camera_func(imgb or await ToImage.none(ctx))

			await ctx.reply(file=discord.File(buf, "gameboy_camera.gif"))

	@commands.command(aliases=['melts'], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def melt(self, ctx, imgb: ToImage = None):
		"""It's melting on my tongue!"""
		async with ctx.typing():
			buf = await melt_func(imgb or await ToImage.none(ctx))

			await ctx.reply(file=discord.File(buf, "melt.gif"))

	@commands.command(aliases=['crack'], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def cracks(self, ctx, imgb: ToImage = None):
		"""It's cracking!"""
		async with ctx.typing():
			buf = await cracks_func(imgb or await ToImage.none(ctx))

			await ctx.reply(file=discord.File(buf, "japanify.png"))

	@commands.command(aliases=['planet'], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def globe(self, ctx, imgb: ToImage = None):
		"""Planet Y0-oU"""
		async with ctx.typing():
			buf = await globe_func(imgb or await ToImage.none(ctx))

			await ctx.reply(file=discord.File(buf, "globe.gif"))

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def cow(self, ctx, imgb: ToImage = None):
		"""Holy cow!"""
		async with ctx.typing():
			buf = await cow_func(imgb or await ToImage.none(ctx))

			await ctx.reply(file=discord.File(buf, "cow.gif"))

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def ripple(self, ctx, imgb: ToImage = None):
		"""Water ripple"""
		async with ctx.typing():
			buf = await ripple_func(imgb or await ToImage.none(ctx))

			await ctx.reply(file=discord.File(buf, "ripple.gif"))

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def fan(self, ctx, imgb: ToImage = None):
		"""I'm a fan"""
		async with ctx.typing():
			circled = await circly(imgb or await ToImage.none(ctx), (100, 100))

			buf = await fanning(circled)

			await ctx.reply(file=discord.File(buf, "fan.gif"))

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def painting(self, ctx, imgb: ToImage = None):
		"""Bob Rozz"""
		async with ctx.typing():
			buf = await oil_painting(imgb or await ToImage.none(ctx))

			await ctx.reply(file=discord.File(buf, "oil_painting.gif"))

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def undilate(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Remove water"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await undilating(_input)
			await ctx.reply(file=discord.File(buf, "undilate.gif"), mention_author=False)

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def dilate(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Add water"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await dilating(_input)
			await ctx.reply(file=discord.File(buf, "dilate.gif"), mention_author=False)

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def logoff(self, ctx, user: typing.Union[discord.Member, discord.User]=None):
		"""When you logoff"""
		async with ctx.typing():
			user = user or ctx.author

			img = await ctx.to_image(user)

			buf = await logoffing(img)
			await ctx.reply(f'> {user} logging off discord <a:discordwhite:846643324790243339>', file=discord.File(buf, 'logoff.gif'), mention_author=False)

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def cloth(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""It's still wet"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await clothing(_input)
			await ctx.reply(file=discord.File(buf, "cloth.gif"), mention_author=False)

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def bubble(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Blub blub"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await bubbling(_input)
			await ctx.reply(file=discord.File(buf, "bubble.gif"), mention_author=False)

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def pattern(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Stitch pattern"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await patterning(_input)
			await ctx.reply(file=discord.File(buf, "pattern.gif"), mention_author=False)

	@commands.command(aliases=["ad", "advertize"], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def ads(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""CLICK FOR MORE!!!"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await advertizing(_input)
			await ctx.reply(file=discord.File(buf, "ads.gif"), mention_author=False)

	@commands.command(usage="<User|Member|Emoji|URL> [frequency=0.05] [amplitude<1|2|3|4|5>=3]")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def wave(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None, frequency: float=0.05, amplitude: typing.Literal[1, 2, 3, 4, 5]=3):
		"""Me wavey wavey"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await waving(_input, frequency, amplitude*10)
			await ctx.reply(file=discord.File(buf, "wave.gif"), mention_author=False)

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def warp(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""wwaaaaarrrpppp"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await warping(_input)
			await ctx.reply(file=discord.File(buf, "warp.gif"), mention_author=False)

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def sensitive(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Emoji Movie pt.2"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await sensitiving(_input)
			await ctx.reply(file=discord.File(buf, "sensitive.gif"), mention_author=False)

	@commands.command(aliases=["yt"], usage="<Member|User> <title>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def youtube(self, ctx, author: typing.Union[discord.Member, discord.User], *, title):
		"""Storytime when-"""
		async with ctx.typing():
			pfp = BytesIO(await author.display_avatar.read())

			buf = await youtubing(pfp, author.name, title)

			await ctx.reply(file=discord.File(buf, "youtube.gif"), mention_author=False)

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def matrix(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""9874730847802234"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await matrixing(_input)
			await ctx.reply(file=discord.File(buf, "matrix.gif"), mention_author=False)

	@commands.command(aliases=["pprz", "ppz"], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def paparazzi(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Going to Met Gala"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await paparazzing(_input)
			await ctx.reply(file=discord.File(buf, "paparazzi.gif"), mention_author=False)

	@commands.command(name='print', usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def _print(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Out of ink"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await printing(_input)
			await ctx.reply(file=discord.File(buf, "print.gif"), mention_author=False)

	@commands.command(usage="<User|Member|Emoji|URL> <X|Y=X>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def shear(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None, axis: typing.Literal['Y', 'y', 'X', 'x']='x'):
		"""Shearing tears"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await shearing(_input, axis)
			await ctx.reply(file=discord.File(buf, "shear.gif"), mention_author=False)

	@commands.command(aliases=['magnifying'], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def magnify(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Detective business"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await magnifying(_input)
			await ctx.reply(file=discord.File(buf, "magnify.gif"), mention_author=False)

	@commands.command(aliases=['love', 'loves', 'heart'], usage="<User|Member|Emoji|URL> <rainbow=false>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def hearts(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None, rainbow:bool=False):
		"""Love is in the air"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await loving(_input, rainbow)
			await ctx.reply(file=discord.File(buf, "hearts.gif"), mention_author=False)

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def cartoon(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Cartoonify"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await cartooning(_input)
			await ctx.reply(file=discord.File(buf, "cartoon.gif"), mention_author=False)

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def canny(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Canny Edges"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await canning(_input)
			await ctx.reply(file=discord.File(buf, "canny.gif"), mention_author=False)

	@commands.command(usage="<User|Member|Emoji|URL> <level=2>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def boil(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None, level:int=2):
		"""It's HOT!"""
		async with ctx.typing():
			if level < 1 or level > 5:
				return await ctx.reply("Boiling level should be an integer between 1 and 5, inclusive.", mention_author=False)
			_input = await ctx.to_image(_input)

			buf = await boiling(_input, level)
			await ctx.reply(file=discord.File(buf, "boil.gif"), mention_author=False)

	@commands.command(aliases=['abs'], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def abstract(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Piccasso"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await abstracting(_input)
			await ctx.reply(file=discord.File(buf, "abstract.gif"), mention_author=False)

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def shock(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""WHAT!"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await shocking(_input)
			await ctx.reply(file=discord.File(buf, "shock.gif"), mention_author=False)

	@commands.command(aliases=["inf", "infinite"], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def infinity(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Never ending"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await infiniting(_input)
			await ctx.reply(file=discord.File(buf, "infinity.gif"), mention_author=False)

	@commands.command(aliases=['eq'], usage="<User|Member|Emoji|URL> <level=3>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def earthquake(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None, power:int=3):
		"""SAVE YOURSELF"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await earthquaking(_input, power)
			await ctx.reply(file=discord.File(buf, "earth-quake.gif"), mention_author=False)

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def tv(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Look ma!"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await tving(_input)
			await ctx.reply(file=discord.File(buf, "tv.gif"), mention_author=False)

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def roll(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Wheel simulator"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await rolling(_input)
			await ctx.reply(file=discord.File(buf, "roll.gif"), mention_author=False)

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def lamp(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""It's flickering..."""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await lamping(_input)
			await ctx.reply(file=discord.File(buf, "lamp.gif"), mention_author=False)

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def rain(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Bring your umbrella"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await raining(_input)
			await ctx.reply(file=discord.File(buf, "rain.gif"), mention_author=False)

	@commands.command(aliases=['optic'], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def optics(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Optical Distortion"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await opticing(_input)
			await ctx.reply(file=discord.File(buf, "optics.gif"), mention_author=False)

	@commands.command(name='half-invert', aliases=['hi', 'halfinvert', 'halfert'], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def halfinvert(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Why is it not full invertion?"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await halfinverting(_input)
			await ctx.reply(file=discord.File(buf, "half-invert.gif"), mention_author=False)

	@commands.command(aliases=["kills"], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def shoot(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Create a touching sort movie"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await killing(_input)
			await ctx.reply(file=discord.File(buf, "shoot.gif"), mention_author=False)

	@commands.command(hidden=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def recent(self, ctx, channel: discord.TextChannel=None):
		async with ctx.typing():
			channel = channel or ctx.channel

			authors = []
			async for message in channel.history():
				if len(authors) > 3:
					break
				if message.author in authors:
					continue
				authors.append(message.author)
			
			if len(authors) < 3:
				authors += authors*2

			authors = authors[:3]
			authors = [BytesIO(await auth.avatar.read()) for auth in authors]
			buf = await historing(authors)
		await ctx.reply(file=discord.File(buf, "recent.gif"), mention_author=False)
	
	@commands.command(aliases=['map'], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def mcmap(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Minecraft map"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await mcmapping(_input)
			await ctx.reply(file=discord.File(buf, "mcmap.png"), mention_author=False)

	@commands.command(aliases=['scroll', 'bar'], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def bars(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Moving bars"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await scrolling(_input)
			await ctx.reply(file=discord.File(buf, "scroll.gif"), mention_author=False)

	@commands.command(aliases=["rev"], usage="<User|Member|Emoji|URL>", hidden=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def reveal(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Scroll away"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await revealing(_input)
			await ctx.reply(file=discord.File(buf, "reveal.gif"), mention_author=False)

	@commands.command(aliases=["sub"], usage="<User|Member|Emoji|URL>", hidden=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def subtract(self, ctx, _input1: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str], _input2: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]):
		"""It's just a simple math"""
		async with ctx.typing():
			if _input1 == _input2:
				return await ctx.reply("Both input cannot be the same", mention_author=False)

			_input1 = await ctx.to_image(_input1)
			_input2 = await ctx.to_image(_input2)

			buf = await subtracting(_input1, _input2)
			await ctx.reply(file=discord.File(buf, "subtract.gif"), mention_author=False)

	@commands.command(aliases=["rad"], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def radiate(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Radiates good energy"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await radiating(_input)
			await ctx.reply(file=discord.File(buf, "radiate.gif"), mention_author=False)

	@commands.command(aliases=["gal"], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def gallery(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Create a moving gallery"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await moves(_input)
			await ctx.reply(file=discord.File(buf, "gallery.gif"), mention_author=False)

	@commands.command(aliases=["layer", "lay"], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def layers(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Shows layers with mirror
		Works on other gif
		"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await layerss(_input)
			await ctx.reply(file=discord.File(buf, "layers.gif"), mention_author=False)

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def clock(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Tick-tock"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await clocking(_input)
			await ctx.reply(file=discord.File(buf, "pie.gif"), mention_author=False)

	@commands.command(cooldown_after_parsing=True, usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def heat(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Feels like on the dessert"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await pixelle(_input)
			await ctx.reply(file=discord.File(buf, "heat.gif"), mention_author=False)

	@commands.command(cooldown_after_parsing=True, usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def fry(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Till golden brown"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await friedy(_input)
			await ctx.reply(file=discord.File(buf, "fry.gif"), mention_author=False)

	@commands.command(cooldown_after_parsing=True, usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def blur(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""I need glasses"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await blurrys(_input)
			await ctx.reply(file=discord.File(buf, "outoffocus.gif"), mention_author=False)

	@commands.command(cooldown_after_parsing=True, usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def explicit(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Parental Advisory required"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await explicity(_input)
			await ctx.reply(file=discord.File(buf, "explicit_content.gif"), mention_author=False)

	@commands.command(cooldown_after_parsing=True, usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def shift(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""I'm not tripping, you are"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await shifty(_input)
			await ctx.reply(file=discord.File(buf, "shift.gif"), mention_author=False)

	@commands.command(cooldown_after_parsing=True, usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def zoom(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Zoom in"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await zoomie(_input)
			await ctx.reply(file=discord.File(buf, "zoom.gif"), mention_author=False)

	@commands.command(cooldown_after_parsing=True, usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def disco(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Discordtics"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await discotic(_input)
			await ctx.reply(file=discord.File(buf, "disco.gif"), mention_author=False)

	@commands.command(cooldown_after_parsing=True, aliases=['scanner'], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def scan(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None, *, flags=None):
		"""Scan gifs"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			if flags and "--side" in flags:
				buf = await time_scan_side(_input)
			else:
				buf = await time_scan(_input)
			if not buf:
				return await ctx.reply("Only accept gif member avatar, emojis, url, tenor formats.", mention_author=False)
			await ctx.reply(file=discord.File(buf, "scan.gif"), mention_author=False)

	@commands.command(cooldown_after_parsing=True, aliases=['pats', 'pet', 'petpet'], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def patpat(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Pat-pat--"""
		async with ctx.typing():
			
			_input = await ctx.to_image(_input)

			buf = await patpats(_input)
			await ctx.reply(file=discord.File(buf, "patpat.gif"), mention_author=False)
	
	@commands.command(cooldown_after_parsing=True, aliases=['equation', 'equ'], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def equations(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""You're confused"""
		async with ctx.typing():
			
			_input = await ctx.to_image(_input)

			buf = await equa(_input)
			await ctx.reply(file=discord.File(buf, "equations.gif"), mention_author=False)
	
	@commands.command(aliases=['ava'], usage="<User|Member>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def avatar(self, ctx, member: typing.Union[discord.Member, discord.User]=None):
		"""Get someone's avatar"""
		if not member:
			member = ctx.author

		embed = discord.Embed(title=f"{member} avatar", description=f"`{member.id}`", color=self.bot.c)
		embed.set_image(url=member.display_avatar.url)
		await ctx.reply(embed=embed, mention_author=False)

	@commands.command(aliases=['hj', 'nh', 'nohorny', 'hornijail', 'nohorni'])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def hornyjail(self, ctx, bonked:discord.Member=None, bonker:discord.Member=None):
		"""Go to horny jail!"""
		async with ctx.typing():
			if not bonked:
				dataD = await ctx.to_image()
				dataR = None
			elif bonked and not bonker:
				dataD = await ctx.to_image(bonked)
				dataR = None
			elif bonked and bonker:
				dataD = await ctx.to_image(bonked)
				dataR = await ctx.to_image(bonker)
			
			buf = await nohorni(dataD, dataR)
			await ctx.reply(file=discord.File(buf, "hornijail.gif"), mention_author=False)

	@commands.command(usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def bomb(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Incoming explosion!"""
		async with ctx.typing():

			_input = await ctx.to_image(_input)

			buf = await dabomb(_input)
			await ctx.reply(file=discord.File(buf, "nuclear bomb.gif"), mention_author=False)

	@commands.command(aliases=['hell', 'elmo', 'flame'], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def burn(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""HAHAHAHAH"""
		async with ctx.typing():

			data = await ctx.to_image(_input)

			buf = await burning(data)
			await ctx.reply(file=discord.File(buf, "flaming elmo.gif"), mention_author=False)

	@commands.command(aliases=['screams', 'screaming', 'AAA'])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def scream(self, ctx, member:discord.Member=None):
		"""AAAAAAAAAAA"""
		async with ctx.typing():
			if not member:
				member = ctx.author

			asset = member.display_avatar.with_size(512)
			data = BytesIO(await asset.read())
			data.seek(0)

			buf = await screamm(data)
			await ctx.reply(file=discord.File(buf, "screaam.gif"), mention_author=False)

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def why(self, ctx, member:discord.Member=None):
		"""Just.. why.."""
		async with ctx.typing():
			if not member:
				member = ctx.author

			asset = member.display_avatar.with_size(512)
			data = BytesIO(await asset.read())
			data.seek(0)

			buf = await whyy(data)
			await ctx.reply(file=discord.File(buf, "screaam.gif"), mention_author=False)

	@commands.command(cooldown_after_parsing=True, aliases=['sob', 'crying'])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def eugh(self, ctx, member:discord.Member=None):
		"""SOBS SOBS"""
		async with ctx.typing():
			if not member:
				member = ctx.author

			asset = member.display_avatar.with_size(512)
			data = BytesIO(await asset.read())
			data.seek(0)

			buf = await eughh(data)
			await ctx.reply(file=discord.File(buf, "eugh.gif"), mention_author=False)

	@commands.command(aliases=['buffer'])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def buffering(self, ctx, member:discord.Member=None):
		"""Uhh.. what?"""
		async with ctx.typing():
			if not member:
				member = ctx.author

			asset = member.display_avatar.with_size(512)
			data = BytesIO(await asset.read())
			data.seek(0)

			buf = await bufff(data)
			await ctx.reply(file=discord.File(buf, "uhhhh.gif"), mention_author=False)

	@commands.command(cooldown_after_parsing=True, name="bonk", usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def bonkyy(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Bonk someone"""
		async with ctx.typing():
			
			_input = await ctx.to_image(_input)

			buf = await bonk(_input)

			await ctx.reply(file=discord.File(buf, "bonked.gif"), mention_author=False)
	
	@commands.command(cooldown_after_parsing=True, name="type", hidden=True)
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def typee(self, ctx, *args:commands.clean_content):
		"""ye. it type.
		Type your text and it'll turn into an image or a gif if you add `gif` argument on the end. Add the author by adding `auth` agument on the end. (if you're using `gif` and `auth` please type `gif` first)\nMax character: `150`\n\nExample : `j;type Lmao hii gif`
		"""
		async with ctx.typing():
			args = list(args)
			auth = ""
			if args[-1] == "auth":
				args.pop()
				if args[-1] == "gif":
					args.pop()
					if len(args) == 1:
						try:
							arg = args[0]
							arg = await commands.MessageConverter().convert(ctx, arg)
							args = [arg.clean_content]
							auth = "- " + arg.author.display_name
						except:
							auth = "- " + ctx.author.display_name
					buf, l = await types_gif(args, auth)

					if buf != "":
						await ctx.reply(file=discord.File(buf, "types.gif"), mention_author=False)
					else:
						await ctx.reply(f"Your text reached the limit of `150` characters: `{l}`", mention_author=False)
						ctx.command.reset_cooldown(ctx)

				else:
					if len(args) == 1:
						try:
							arg = args[0]
							arg = await commands.MessageConverter().convert(ctx, arg)
							args = [arg.clean_content]
							auth = "- " + arg.author.display_name
						except:
							auth = "- " + ctx.author.display_name

					buf, l = await types(args, auth)

					if buf != "":
						await ctx.reply(file=discord.File(buf, "types.png"), mention_author=False)
					else:
						await ctx.reply(f"Your text reached the limit of `150` characters: `{l}`", mention_author=False)
						ctx.command.reset_cooldown(ctx)
			
			else:
				if args[-1] == "gif":
					args.pop()
					if len(args) == 1:
						try:
							arg = args[0]
							arg = await commands.MessageConverter().convert(ctx, arg)
							args = [arg.clean_content]
						except:
							pass

					buf, l = await types_gif(args, "")

					if buf != "":
						await ctx.reply(file=discord.File(buf, "types.gif"), mention_author=False)
					else:
						await ctx.reply(f"Your text reached the limit of `150` characters: `{l}`", mention_author=False)
						ctx.command.reset_cooldown(ctx)

				else:
					if len(args) == 1:
						try:
							arg = args[0]
							arg = await commands.MessageConverter().convert(ctx, arg)
							args = [arg.clean_content]
						except:
							pass

					buf, l = await types(args, "")

					if buf != "":
						await ctx.reply(file=discord.File(buf, "types.png"), mention_author=False)
					else:
						await ctx.reply(f"Your text reached the limit of `150` characters: `{l}`", mention_author=False)
						ctx.command.reset_cooldown(ctx)

	@commands.command(cooldown_after_parsing=True, aliases=["ball"], usage="<User|Member|Emoji|URL>")
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def balls(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None):
		"""Ballz"""
		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await baller(_input)
			await ctx.reply(file=discord.File(buf, "balls.gif"), mention_author=False)

	@commands.command(cooldown_after_parsing=True, usage="<User|Member|Emoji|URL> <level=3>")
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def glitch(self, ctx, _input: typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str]=None, level:int=3):
		"""Glitchify"""
		if level < 1 or level > 10:
			return ctx.reply("Glitch level must be between 1 and 10.", mention_author=False)

		async with ctx.typing():
			_input = await ctx.to_image(_input)

			buf = await glitching(_input, level)
			await ctx.reply(file=discord.File(buf, "glitch.gif"), mention_author=False)

def setup(bot):
	bot.add_cog(IMAGE(bot))