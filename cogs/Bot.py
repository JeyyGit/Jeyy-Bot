
import inspect
from jishaku.codeblocks import codeblock_converter
from difflib import get_close_matches
from discord.ext import commands
from io import BytesIO, StringIO
from tabulate import tabulate
import psutil
import asyncio
import humanize
import datetime as dt
import typing
import discord
import humanize
import importlib
import random
import time


from utils import views, useful, help_command

importlib.reload(views)
importlib.reload(useful)
importlib.reload(help_command)


from utils.views import EndpointView, SupportServerView
from utils.useful import Modal
from utils.contextbot import JeyyBot, JeyyContext
from utils.help_command import JeyyHelp


class Bots(commands.Cog, name='Bot'):
	"""Bot management commands"""

	def __init__(self, bot):
		self.bot: JeyyBot = bot
		self.thumbnail = "https://cdn.jeyy.xyz/image/jeyy_bot_d5698c.png"
		self.bot.help_command = JeyyHelp()
		self.bot.everyone = {}

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"Logged in as {self.bot.user}")
		print(f"Bot Cog Loaded")
		channel = await self.bot.fetch_channel(779892741696913438)
		await channel.send(f"Logged in as {self.bot.user}")

	@commands.command(hidden=True)
	@commands.guild_only()
	@commands.is_owner()
	async def sync(self, ctx, guilds: commands.Greedy[discord.Object], spec: typing.Optional[typing.Literal["~", "*", "^"]] = None):
		"""`j;sync` -> sync all guilds
		`j;sync [*guilds]` -> sync these guilds
		`j;sync ~` -> sync current guild
		`j;sync *` -> copy global to current guild and sync current guild
		`j;sync ^` -> clear commands in current guild and sync current guild
		"""
		if not guilds:
			if spec == "~":
				synced = await ctx.bot.tree.sync(guild=ctx.guild)
			elif spec == "*":
				ctx.bot.tree.copy_global_to(guild=ctx.guild)
				synced = await ctx.bot.tree.sync(guild=ctx.guild)
			elif spec == "^":
				ctx.bot.tree.clear_commands(guild=ctx.guild)
				await ctx.bot.tree.sync(guild=ctx.guild)
				synced = []
			else:
				synced = await ctx.bot.tree.sync()

			await ctx.send(
				f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
			)
			return

		ret = 0
		for guild in guilds:
			try:
				await ctx.bot.tree.sync(guild=guild)
			except discord.HTTPException:
				pass
			else:
				ret += 1

		await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

	@commands.command(hidden=True)
	@commands.is_owner()
	async def sql(self, ctx, method, *, query: codeblock_converter):
		query = query.content
		method = method.lower()
		if method == 'execute':
			value = await self.bot.db.execute(query)
		elif method == 'fetch':
			value = await self.bot.db.fetch(query)
			value = tabulate(value, headers='keys', tablefmt="psql")
		elif method == 'fetchrow':
			value = await self.bot.db.fetchrow(query)
			value = tabulate([value], headers='keys', tablefmt="psql")
		elif method == 'fetchval':
			value = await self.bot.db.fetchval(query)
		else:
			return await ctx.reply("Invalid.", mention_author=False)

		try:
			await ctx.reply(f'{"`"*3}py\n{value}{"`"*3}', mention_author=False)
		except:
			s = StringIO()
			s.write(value)
			s.seek(0)
			await ctx.reply(file=discord.File(s, "sql.py"), mention_author=False)

	@commands.command(hidden=True)
	@commands.is_owner()
	async def de(self, ctx, limit=10):
		if ctx.message.reference and ctx.message.reference.resolved.author == self.bot.user:
			await ctx.message.reference.resolved.delete()
			try:
				await ctx.message.delete()
			except:
				await ctx.message.add_reaction("\U00002705")
			finally:
				return

		await ctx.channel.purge(limit=limit, check=lambda m:m.author == self.bot.user, bulk=False)

		try:
			await ctx.message.delete()
		except:
			await ctx.message.add_reaction("\U00002705")

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def ping(self, ctx):
		"""Ping the bot"""
		embed = discord.Embed(title=":ping_pong: Ping...", color=self.bot.c)

		start = time.perf_counter()
		message = await ctx.reply(embed=embed, mention_author=False)
		end = time.perf_counter()
		bl = round((end - start) * 1000)

		start2 = time.perf_counter()
		await self.bot.db.fetch("SELECT 1")
		end2 = time.perf_counter()
		dbl = round((end2 - start2) * 1000)

		wl = round(self.bot.latency*1000)

		embed.title = ":ping_pong: Pong!"
		embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
		embed.add_field(name="Typing latency", value=f"```c\n{bl} ms```", inline=True)
		embed.add_field(name="Websocket latency", value=f"```c\n{wl} ms```", inline=True)
		embed.add_field(name="DB latency", value=f"```c\n{dbl} ms```", inline=True)
		embed.set_thumbnail(url=random.choice([
				'https://cdn.jeyy.xyz/image/pingpong_8f881f.gif',
				"https://cdn.jeyy.xyz/image/buffering_d00131.gif",
				"https://cdn.jeyy.xyz/image/buffering_8484c5.gif"
			])
		)
		
		await message.edit(embed=embed, allowed_mentions=discord.AllowedMentions.none())

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def invite(self, ctx):
		"""Jeyy Bot invite link"""

		bot_button = discord.ui.Button(label="Invite Jeyy Bot", url='https://discord.com/oauth2/authorize?client_id=779783517613588520&permissions=1644959366391&scope=applications.commands%20bot')
		support_button = discord.ui.Button(label="Support Server", url='https://discord.gg/uwKsfMzGJA')

		view = discord.ui.View()
		view.add_item(bot_button)
		view.add_item(support_button)

		await ctx.reply(f'Bot Invite : <https://jeyy.xyz/🤖>\nSupport Server : <https://jeyy.xyz/📜>', view=view, mention_author=False)

	@commands.command(aliases=['up'])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def uptime(self, ctx):
		"""See bot's uptime"""
		delta_uptime = dt.datetime.now() - self.bot.launch_time
		time = humanize.precisedelta(dt.timedelta(seconds=round(delta_uptime.total_seconds())))
		await ctx.reply(f"I've been up for {time}\n*Last load from {f'<t:{int(self.bot.launch_time.timestamp())}:f>'}*", mention_author=False)

	@commands.group(invoke_without_command=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def emojis(self, ctx):
		"""List of emojis bot could see
		do `j;toggle` to toggle on/off emoji auto response
		"""

		lines = [f"`{i+1}.` {str(emoji)} `;;{emoji.name}`" for i, emoji in enumerate(filter(lambda e: e.guild.id != 332406449051402250 and e.available, self.bot.emojis))]
		chunks = ctx.chunk(lines, per=15, combine=True)

		embeds = []
		for page in chunks:
			embed = discord.Embed(title="Available emojis", description="Do `j;toggle` to toggle on/off emoji auto response", color=self.bot.c)
			embed.add_field(name="\u200b", value=page)
			embeds.append(embed)
		
		await ctx.Paginator().send(embeds, reply=True)

	@emojis.command(aliases=['s'])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def search(self, ctx, search=None):
		"""Search every emoji the bot could see"""
		if not search:
			await ctx.reply("Missing the emoji you want to search.", mention_author=False)
			return

		last_emojis = []
		txt = []

		for emoji in self.bot.emojis:
			if emoji.guild.id == 332406449051402250:
				pass
			else:
				last_emojis.append(emoji)

		emoji_list = {emoji.name: emoji for emoji in last_emojis}
		keys = list(emoji_list)
		test = {n.lower():n for n in keys}

		guess = [test[r] for r in get_close_matches(search, test, 15, 0.6)]
		if guess:
			for i, emoji in enumerate(guess):
				txt.append(f"`{i+1}.` {emoji_list[emoji]} `;;{emoji_list[emoji].name}`")
			embed = discord.Embed(title=f"Emoji close matches result for **\"{search}\"**", description="\n".join(txt), color=self.bot.c)

			await ctx.reply(embed=embed, mention_author=False)
		else:
			await ctx.reply(f"Can't find close matches for **\"{search}\"**", mention_author=False)

	@emojis.command(name='toggle')
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def toggles(self, ctx):
		"""Toggle on/off emoji auto response
		You can check available emojis on `j;emojis`
		"""
		cmd = self.bot.get_command("toggle")
		await cmd(ctx)

	@commands.command(aliases=['info'])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def about(self, ctx):
		"""See information about Jeyy Bot"""
		info = await self.bot.application_info()

		embed = discord.Embed(title="Jeyy Bot Info", color=self.bot.c)
		embed.add_field(name="Developer", value=f"```\n{str(info.owner)}```", inline=False)
		embed.add_field(name="Library", value=f"```\ndiscord.py {discord.__version__}```", inline=True)
		embed.add_field(name="Total servers", value=f"```\n{len(self.bot.guilds)}```", inline=True)
		embed.add_field(name="Total members", value=f"```\n{sum([g.member_count for g in self.bot.guilds])}```", inline=True)
		embed.set_thumbnail(url=self.bot.user.avatar.url)

		bot_button = discord.ui.Button(label="Invite Jeyy Bot", url='https://discord.com/oauth2/authorize?client_id=779783517613588520&permissions=1644959366391&scope=applications.commands%20bot')
		support_button = discord.ui.Button(label="Support Server", url='https://discord.gg/uwKsfMzGJA')

		view = discord.ui.View()
		view.add_item(bot_button)
		view.add_item(support_button)
		
		await ctx.reply(embed=embed, view=view, mention_author=False)

	@commands.command(aliases=['src'])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def source(self, ctx, *, command=None):
		"""See bot's source code"""
		# num = random.choice([451, 204, 303, 400, 402, 403, 404, 405, 406, 410, 423, 444, 501, 450])

		# url = f"https://http.cat/{num}"
		# async with aiohttp.ClientSession() as session:
		# 	async with session.get(url) as response:
		# 		buf = BytesIO(await response.read())
		# 		await ctx.reply("||ish closed source :^||", file=discord.File(buf, f"error_code_{num}.jpg", spoiler=True), mention_author=False, delete_after=10)
		
		base = 'https://github.com/JeyyGit/Jeyy-Bot'
		branch = 'main'

		view = discord.ui.View()

		if command is None:
			view.add_item(discord.ui.Button(label='Jeyy Bot Source Code', url='https://github.com/JeyyGit/Jeyy-Bot'))
			return await ctx.reply('A \U00002b50 is very much appreciated \U0000270c\n\n<https://github.com/JeyyGit/Jeyy-Bot>', view=view)

		command = command.lower()
		if command == 'help':
			sub = type(self.bot.help_command)
			module = sub.__module__.replace('.', '/')
			lines, line_no = inspect.getsourcelines(sub)
		else:
			cmd = self.bot.get_command(command)
			if not cmd:
				return await ctx.reply(f'No command called "{command}" found.')
			if cmd.cog.__class__.__name__ == 'Jishaku':
				view.add_item(discord.ui.Button(label=f'Source code for Jishaku commands', url='https://github.com/Gorialis/jishaku'))
				return await ctx.reply('<https://github.com/Gorialis/jishaku>', view=view)
			elif not cmd.cog:
				module = 'Jeyy%20Bot'
			else:			
				module = cmd.callback.__module__.replace('.', '/')
			lines, line_no = inspect.getsourcelines(cmd.callback)

		link = f'{base}/blob/{branch}/{module}.py#L{line_no}-L{line_no+len(lines)-1}'
		
		view.add_item(discord.ui.Button(label=f'Source code for {command}', url=link))
		await ctx.reply(f'A \U00002b50 is very much appreciated \U0000270c\n\n<{link}>', view=view)

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def toggle(self, ctx):
		"""Toggle on/off emoji auto response
		You can check available emojis on `j;emojis`
		"""
		try:
			loc = ctx.guild.id
		except:
			loc = ctx.author
		else:
			loc = ctx.guild

		author_id = ctx.author.id
		guild_id = loc.id

		user = await self.bot.db.fetch("SELECT * FROM emoji WHERE user_id = $1 AND guild_id = $2", author_id, guild_id)

		if not user:
			await self.bot.db.execute("INSERT INTO emoji (guild_id, user_id, toggle) VALUES ($1, $2, $3)", guild_id, author_id, True)
			await ctx.reply("Emoji auto response will be enabled for you in this server.\nCheck `j;emojis` to see all available emojis!", mention_author=False)
		else:
			current = await self.bot.db.fetchrow("SELECT toggle FROM emoji WHERE user_id = $1 AND guild_id = $2", author_id, guild_id)
			if current[0]:
				await self.bot.db.execute("UPDATE emoji SET toggle = $1 WHERE user_id = $2 AND guild_id = $3", False, author_id, guild_id)
				await ctx.reply("Emoji auto response will be disabled for you in this server.", mention_author=False)
			else:
				await self.bot.db.execute("UPDATE emoji SET toggle = $1 WHERE user_id = $2 AND guild_id = $3", True, author_id, guild_id)
				await ctx.reply("Emoji auto response will be enabled for you in this server.\nCheck `j;emojis` to see all available emojis!", mention_author=False)
	
	@commands.command(hidden=True)
	@commands.cooldown(1, 30, commands.BucketType.user)
	async def fhelp(self, ctx):
		emojis = {'left': "\U00002b05\U0000fe0f",
				'stop': "\U000023f9\U0000fe0f",
				'right': "\U000027a1\U0000fe0f"}

		def check_react(reaction, user):
			return user == ctx.author and str(reaction.emoji) in ["\U00002b05\U0000fe0f", "\U000023f9\U0000fe0f", "\U000027a1\U0000fe0f"] and reaction.message == sent

		c = 0
		page = 1
		sent = await ctx.reply("https://i.ibb.co/rwd0sRj/main.png", mention_author=False)
		await sent.add_reaction(emojis['left'])
		await sent.add_reaction(emojis['stop'])
		await sent.add_reaction(emojis['right'])

		while True:
			if page == 1:
				pic = "https://i.ibb.co/rwd0sRj/main.png"
			elif page == 2:
				pic = "https://i.ibb.co/z6sH7FZ/image.png"
			elif page == 3:
				pic = "https://i.ibb.co/z8ff9wp/economy.png"
			elif page == 4:
				pic = "https://i.ibb.co/mRrq2Vd/bot.png"

			await sent.edit(content=pic, allowed_mentions=discord.AllowedMentions.none())
			if c >= 10:
				await sent.remove_reaction(emojis['left'], self.bot.user)
				await sent.remove_reaction(emojis['stop'], self.bot.user)
				await sent.remove_reaction(emojis['right'], self.bot.user)
				break
			c += 1

			a, pending = await asyncio.wait([self.bot.wait_for('reaction_remove', timeout=600, check=check_react), self.bot.wait_for('reaction_add', timeout=180, check=check_react)], return_when=asyncio.FIRST_COMPLETED)
			try:
				a = a.pop().result()

			except asyncio.TimeoutError:
				await sent.remove_reaction(emojis['left'], self.bot.user)
				await sent.remove_reaction(emojis['stop'], self.bot.user)
				await sent.remove_reaction(emojis['right'], self.bot.user)
				break

			[j.cancel() for j in pending]
			if a[0].emoji == emojis['left']:
				page -= 1
				if page == 0:
					page = 4
			elif a[0].emoji == emojis['right']:
				page += 1
				if page == 5:
					page = 1
			elif a[0].emoji == emojis['stop']:
				await sent.delete()
				break

	@commands.group(aliases=['cmdusage', 'commanduse', 'cmduse', 'usage', 'cu'], invoke_without_command=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def commandusage(self, ctx, is_all:bool=False):
		"""Shows command usage on this server.
		Use `j;commandusage all` to see command usage across all server
		"""
		try:
			loc = ctx.guild.id
		except:
			loc = ctx.author
		else:
			loc = ctx.guild

		if not is_all:
			_list = await self.bot.db.fetch("SELECT name, sum(usage) FROM commands WHERE guild_id = $1 GROUP BY name ORDER BY sum(usage) DESC", loc.id)
		else:
			_list = await self.bot.db.fetch("SELECT name, sum(usage) FROM commands GROUP BY name ORDER BY sum(usage) DESC")
		
		lines = []
		total = 0
		for i, cmd in enumerate(_list):
			lines.append(f"`{i+1:2d}. {cmd['name']:20s} {cmd['sum']:5d}`")
			total += cmd['sum']

		chunks = ctx.chunk(lines, per=10)
		
		embeds = []
		for page in chunks:
			embed = discord.Embed(title=f"Commands usage on **{[loc.name, 'all servers'][is_all]}**", description="\n".join(page), color=self.bot.c)
			embed.set_footer(text=f"Total usages : {total}")
			embeds.append(embed)

		await ctx.Paginator().send(embeds, reply=True)
		
	@commandusage.command(aliases=['true', 'True', 'yes', 'Yes', 'All', 'ALL', 'TRUE', "YES"])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def all(self, ctx):
		"""Shows command usage across all server"""
		cmd = self.bot.get_command("commandusage")
		await cmd(ctx, True)

	@commands.command(aliases=['upl'], hidden=True)
	@commands.is_owner()
	async def upload(self, ctx, content_type, name='', url=None):

		if url:
			link = await ctx.upload_url(url, content_type, name)
		elif ctx.message.attachments:
			attachment = ctx.message.attachments[0]
			link = await ctx.upload_url(attachment.url, content_type, name)
		elif ctx.message.reference and (attachments := ctx.message.reference.resolved.attachments):
			attachment = attachments[0]
			link = await ctx.upload_url(attachment.url, content_type, name)
		else:
			return await ctx.reply('invalid', mention_author=False)
		
		await ctx.reply(f"> {link}", mention_author=False)

	@commands.command(hidden=True)
	@commands.is_owner()
	async def proc(self, ctx):
		class MadeUp:
			content = "free -h && echo 3 | sudo tee /proc/sys/vm/drop_caches && free -h"
		
		await self.bot.get_command('jsk sh')(ctx, argument=MadeUp())

	@commands.group(invoke_without_command=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def api(self, ctx, endpoint=None):
		"""Info for [JeyyAPI](https://api.jeyy.xyz)"""
		if endpoint is None:
			s = time.perf_counter()
			r = await self.bot.session.get("https://api.jeyy.xyz/v2/general/ping", headers={'Authorization': f'Bearer {self.bot.jeyy_key}'})
			e = time.perf_counter()

			info = psutil.virtual_memory()
			cb = f'```py\nTotal     : {humanize.naturalsize(info[0])}\nAvailable : {humanize.naturalsize(info[1])}\nUsed      : {humanize.naturalsize(info[3])}\nPercent   : {["", "⚠️ "][info[2]>80]}{info[2]}% {["", "⚠️"][info[2]>80]}```'

			embed = discord.Embed(url="https://api.jeyy.xyz", title="Jeyy API", description="Public API with wide range of image manipulation endpoints"+cb, color=self.bot.c)
			
			embed.add_field(name="Status", value=['Offline <:status_offline:596576752013279242>', 'Online <:status_online:596576749790429200>'][r.status == 200])
			if r.status == 200:
				embed.add_field(name="Ping", value=f"{int((e-s)*1000)} ms :ping_pong:", inline=True)

			view = SupportServerView()
			return await ctx.reply(embed=embed, view=view, mention_author=False)
		
		async with ctx.typing():
			s = time.perf_counter()
			r = await self.bot.session.get(f'https://api.jeyy.xyz/v2/image/{endpoint}', params={'image_url': ctx.author.display_avatar.url}, headers={'Authorization': f'Bearer {self.bot.jeyy_key}'})
			e = time.perf_counter()

			if r.status != 200:
				raise commands.CommandError(f'{r.status}: {await r.text()}')

			cs = time.perf_counter()
			buf = BytesIO(await r.read())
			ce = time.perf_counter()

		ss = time.perf_counter()
		msg = await ctx.reply(file=discord.File(buf, f'{endpoint}.gif'), mention_author=False)
		se = time.perf_counter()

		results = f"[{endpoint} endpoint](https://api.jeyy.xyz/docs#/IMAGE/{endpoint.capitalize()}_v2_image_{endpoint}_get \"Click me for docs!\") took `{e-s}` seconds.\nreading response took `{ce-cs}` seconds.\nsending message took `{se-ss}` seconds."
		view = EndpointView(results)
		await msg.edit(view=view, allowed_mentions=discord.AllowedMentions.none())

	@api.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def usage(self, ctx):

		r = await self.bot.session.get("https://api.jeyy.xyz/v2/general/ping", headers={'Authorization': f'Bearer {self.bot.jeyy_key}'})

		endpoints = await self.bot.db.fetch("SELECT method, endpoint, SUM(usage) AS usage FROM api_usage GROUP BY method, endpoint ORDER BY usage DESC")

		lines = [f"{i+1}. [`{endpoint['endpoint']:<23}{endpoint['usage']:>5}`](https://api.jeyy.xyz/docs#/{endpoint['endpoint'].split('/')[1].upper()}/{endpoint['endpoint'].split('/')[2].capitalize()}_{endpoint['endpoint'].split('/')[1]}_{endpoint['endpoint'].split('/')[2]}_{endpoint['method'].lower()} \"Click me for docs!\")" for i, endpoint in enumerate(endpoints)]

		chunks = ctx.chunk(lines, combine=True)

		embeds = []
		for page in chunks:
			embed = discord.Embed(title=f"Jeyy API usages | {['Offline <:status_offline:596576752013279242>', 'Online <:status_online:596576749790429200>'][r.status == 200]}", url="https://api.jeyy.xyz", description=page, color=self.bot.c, timestamp=dt.datetime.now())
			embed.set_footer(text=f'Total requests: {sum([endpoint["usage"] for endpoint in endpoints])}')
			embeds.append(embed)

		await ctx.Paginator().send(embeds, reply=True)

	@commands.Cog.listener()
	async def on_interaction(self, interaction: discord.Interaction):
		if interaction.data.get('custom_id') == 'cool_modal':
			print(f'\n{interaction.user}\n{interaction.data}\n\n')

			components = interaction.data.get('components')

			embed = discord.Embed(title='modal')
			for component in components:
				for comp in component.get('components'):
					embed.add_field(name=comp['custom_id'], value=comp['value'])

			await interaction.response.send_message(embed=embed, ephemeral=True)

	@commands.command(hidden=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def test_modal(self, ctx):

		class View(discord.ui.View):
			def __init__(self):
				super().__init__(timeout=None)
				self.submiter = []

			@discord.ui.button(label='Form-aline', style=discord.ButtonStyle.success)
			async def btn(self, interaction, button):
				if interaction.user.id in self.submiter:
					return await interaction.response.send_message('you have filled this form.', ephemeral=True)

				form = Modal(ctx.bot, f'Form for {interaction.user}')

				form.add_field(1, 'Name', max_length=100, placeholder='ur stopid name', required=True)
				form.add_field(2, 'reason why ur dumb', max_length=200, placeholder='what is it')
				form.add_field(1, 'ur age', max_length=100)

				await form.send_modal(interaction)
				interacted, result = await form.wait()
				if not interacted:
					return

				self.submiter.append(interacted.user.id)

				fields = [f'`{field.label}` : {field.value}' for field in result]
				embed = discord.Embed(title=form.title, description='\n'.join(fields), color=ctx.bot.c, timestamp=dt.datetime.now())
				await interacted.response.send_message(embed=embed)
		discord.utils
		await ctx.reply('STUPIDITY SURVEY 2022', view=View(), mention_author=False)

	@commands.command(hidden=True)
	@commands.is_owner()
	async def push(self, ctx: JeyyContext, *, commit_message='update'):
		await ctx.push(commit_message)

async def setup(bot):
	await bot.add_cog(Bots(bot))