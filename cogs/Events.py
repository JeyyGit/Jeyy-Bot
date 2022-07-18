import discord
from discord.ext import commands
import re
from difflib import get_close_matches
import humanize
import datetime as dt
import asyncio
import importlib

from utils import useful
importlib.reload(useful)

from utils.useful import Queue, Prey

MUTED_WORDS = ['@everyone']
class Events(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.hidden = True
		self.banned_emojis = {
			'guild': [
				892933428641665025,
				332406449051402250
			],
			'emoji': [],
		}

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		if isinstance(error, commands.CommandNotFound):
			return
		elif isinstance(error, commands.MissingRequiredArgument):
			embed = discord.Embed(description=f"Missing required argument: `{error.param.name}`", color=self.bot.c)
			try:
				await ctx.reply(embed=embed, mention_author=False)
			except:
				pass
		elif isinstance(error, commands.CommandOnCooldown):
			try:
				left = discord.utils.format_dt(dt.datetime.now() + dt.timedelta(seconds=error.retry_after+1), 'R')
				embed = discord.Embed(title="\U000026a0 Command on cooldown! \U000026a0", description=f"Please try again {left}.", color=0xf0ff1a)
				await ctx.reply(embed=embed, mention_author=False, delete_after=error.retry_after)
			except:
				await ctx.send("Missing permission to send embed.")
		elif isinstance(error, commands.MaxConcurrencyReached):
			await ctx.reply(f"Another instance of this command is currently running.\nIt can only be used {error.number} time per {error.per.name} concurrently.", mention_author=False)
		else:
			try:
				if isinstance(error, commands.ConversionError):
					error = getattr(error, 'original', error)
				embed = discord.Embed(title="Error", description=f"```diff\n- {error}```", color=0xf0ff1a, timestamp=dt.datetime.now())
				try:
					await ctx.reply(embed=embed, mention_author=False)
				except:
					await ctx.send(embed=embed)
				if ctx.author.id not in self.bot.owner_ids:
					try:
						embed.add_field(name=f"Server: {ctx.guild.name}", value=f"command: {ctx.invoked_with}\nby: {ctx.author}\nurl: {ctx.message.jump_url}")
						await self.bot.get_channel(824859630881865748).send(embed=embed)
					except:
						pass
			except Exception as e:
				print(e)
				try:
					await ctx.send("Missing permission to send.")
				except:
					await ctx.author.send("Missing permission to send.")
	
	@commands.Cog.listener()
	async def on_message(self, message):
		mauthor = message.author
		mchannel = message.channel
		mguild = message.guild
		mcontent = message.content

		afks = await self.bot.db.fetch('SELECT * FROM afk')
		set_afk = set([record['user_id'] for record in afks])
		set_mention = set([mentioned.id for mentioned in message.mentions])

		if mauthor.id in set_afk:
			for afk in afks:
				if mauthor.id == afk['user_id']:
					since = afk['since']
					break
			delta = dt.datetime.utcnow() - since
			if delta.total_seconds() > 1:
				await self.bot.db.execute('DELETE FROM afk WHERE user_id = $1', mauthor.id)
				await message.reply(f"Welcome back {mauthor.mention}! You have been AFK for {humanize.naturaldelta(delta)}")
				set_afk.discard(mauthor.id)
		
		if set_mention and not mauthor.bot:
			intersect = set_afk.intersection(set_mention)
			if intersect:
				for mentioned_id in intersect:
					for afk in afks:
						if mentioned_id == afk['user_id']:
							reason = afk['reason']
							break
					mentioned = await self.bot.fetch_user(mentioned_id)
					await message.reply(f'Sorry {mauthor.mention}, {mentioned} is currently AFK for : {reason}', allowed_mentions=discord.AllowedMentions.none())

		if self.bot.user.mentioned_in(message):
			if (mcontent == '<@!779783517613588520>' or mcontent == '<@779783517613588520>') and not mauthor.bot:
				await message.reply(f"Hello {mauthor.mention} \U0001f44b, my prefix is `j;`")

		# @everyone prevention (on test guilds)
		if mguild and mguild.id in [750901194104504391, 776385025552941077] and not mauthor.bot:
			if mauthor.id not in self.bot.everyone:
				self.bot.everyone[mauthor.id] = 0
			if any([word in mcontent for word in MUTED_WORDS]):
				self.bot.everyone[mauthor.id] += 1
				if self.bot.everyone[mauthor.id] == 1:
					await asyncio.sleep(300)
					self.bot.everyone[mauthor.id] = 0
			
			if self.bot.everyone[mauthor.id] == 3 and any([word in mcontent for word in MUTED_WORDS]):
				print(f"muted {str(mauthor)}")
				muted_role = discord.utils.get(mguild.roles, name='Muted')
				roles = mauthor.roles[1:]
				await mauthor.remove_roles(*roles)
				await mauthor.add_roles(muted_role)
				await mchannel.send(f"{mauthor.mention} has been given {muted_role.mention} for 5 minutes due to 3 `{MUTED_WORDS}` messages.")
				await asyncio.sleep(300)
				await mauthor.remove_roles(muted_role)
				await mauthor.add_roles(*roles)
				await mchannel.send(f"{mauthor.mention}, {muted_role.mention} role has been lifted.")
				self.bot.everyone[mauthor.id] = 0

		# emojis
		search = re.findall(r"((?<=;;).+?(?=;;|$|\s))", mcontent)

		if len(search) > 0:
			self.bot.dispatch('emoji', message, search)

		if message.reference:
			self.bot.dispatch('reply', message)

	@commands.Cog.listener()
	async def on_message_edit(self, before: discord.Message, after: discord.Message):
		if after.embeds or before.embeds:
			return

		if after.author.id == before.author.id:
			await self.bot.process_commands(after)

	@commands.Cog.listener()
	async def on_message_delete(self, message):
		try:
			for reply in self.bot.reply_cache.queue:
				if reply.reference.message_id == message.id:
					try:
						await reply.delete()
					except:
						pass
					self.bot.reply_cache.queue = [msg for msg in self.bot.reply_cache.queue if msg.id != reply.id]
					break
		except:
			pass

	@commands.Cog.listener()
	async def on_command_completion(self, ctx):
		self.bot.c = discord.Color.random()
		command = ctx.command.root_parent
		if not command:
			command = ctx.command

		try:
			loc = ctx.guild.id
		except:
			loc = ctx.author
		else:
			loc = ctx.guild

		date = dt.datetime.now()
		waktu = date.strftime("%d/%m/%y %I:%M %p")

		try:
			text = f"`{waktu}` | **{ctx.author}** used `{command.name}` command on `#{ctx.channel}`, **{loc}**"
			print(text.replace('*', '').replace('`', ''))
		except:
			text = f"`{waktu}` | **{ctx.author}** used `{command.name}` command on **{loc}**"
			print(text.replace('*', '').replace('`', ''))

		if command.hidden:
			return
		
		cmd = await self.bot.db.fetchrow("SELECT * FROM commands WHERE name = $1 AND guild_id = $2", command.name, loc.id)
		
		if not cmd:
			await self.bot.db.execute("INSERT INTO commands (name, usage, guild_id) VALUES ($1, $2, $3)", command.name, 1, loc.id)
		else:
			cmduse = cmd['usage'] + 1
			await self.bot.db.execute("UPDATE commands SET usage = $1 WHERE name = $2 AND guild_id = $3", cmduse, command.name, loc.id)
		
		channel = self.bot.get_channel(845895127611211786) or self.bot.fetch_channel(845895127611211786)
		await channel.send(f'{discord.utils.format_dt(date)} | **{ctx.author}** used `{command.name}` command on `#{ctx.channel}`, **{loc}**')

	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		embed = discord.Embed(title=f"Joined to `{guild.name}`", description=f"""
		Name : {guild.name}
		ID : {guild.id}
		Owner : {await self.bot.fetch_user(guild.owner_id)}
		Members : {guild.member_count}
		Bots : {len([m for m in guild.members if m.bot])}
		Created at: {discord.utils.format_dt(guild.created_at, 'F')}
		""", color=self.bot.c)
		embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
		embed.set_footer(text=f"Now in {len(self.bot.guilds)} servers with {sum(g.member_count for g in self.bot.guilds)} members.", icon_url=self.bot.user.avatar.url)
		await self.bot.get_channel(779893084791635969).send(embed=embed)

		print(f"\nJoined to `{guild.name}` with {guild.member_count} members.\n")

	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		embed = discord.Embed(title=f"Left `{guild.name}`", description=f"""
		Name : {guild.name}
		ID : {guild.id}
		Owner : {await self.bot.fetch_user(guild.owner_id)}
		Members : {guild.member_count}
		Bots : {len([m for m in guild.members if m.bot])}
		Created at: {discord.utils.format_dt(guild.created_at, 'F')}
		""", color=self.bot.c)
		embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
		embed.set_footer(text=f"Now in {len(self.bot.guilds)} servers with {sum([g.member_count for g in self.bot.guilds])} members.", icon_url=self.bot.user.avatar.url)
		await self.bot.get_channel(779893084791635969).send(embed=embed)

		print(f"\nLeft `{guild.name}` with {guild.member_count} members.\n")
	
	@commands.Cog.listener()
	async def on_emoji(self, message: discord.Message, search):
		last_emojis = [emoji for emoji in self.bot.emojis if emoji.guild.id not in self.banned_emojis['guild'] and emoji.available and emoji.id not in self.banned_emojis['emoji']]
		emoji_list = {emoji.name: emoji for emoji in last_emojis}
		guesses = []
		keys = list(emoji_list)
		test = {n.lower():n for n in keys}

		for emoji in search:
			guess = [test[r] for r in get_close_matches(emoji, test)]
			if guess:
				guesses.append(str(emoji_list[guess[0]]))
			else:
				guesses.append("")

		if len(guesses) > 0 and guesses[0]:
			current = await self.bot.db.fetchrow("SELECT toggle FROM emoji WHERE user_id = $1 AND guild_id = $2", message.author.id, message.guild.id)
			if current and current[0]:
				coded = re.sub(r"((?=;;).+?(?=;;|$|\s))", "<J3yY[b0T>", message.content)
				if "<J3yY[b0T>" in coded:
					for i in range(len(guesses)):
						coded = coded.replace("<J3yY[b0T>", guesses[i], 1)
				coded = coded.replace("<J3yY[b0T>", "")

				permissions = dict(message.channel.permissions_for(message.guild.me))
				overrides = message.channel.overwrites_for(message.guild.default_role)
				overrides = dict(iter(overrides))['external_emojis']

				if permissions['manage_webhooks']:
					if dict(message.guild.default_role.permissions)['external_emojis']:
						if overrides == None or overrides == True:
							webhooks = await message.channel.webhooks()
							webhook = discord.utils.get(webhooks, name="Jeyy Bot Emoji")
							if webhook is None:
								webhook = await message.channel.create_webhook(name="Jeyy Bot Emoji")
							if len(coded) < 2000:
								await webhook.send(f"{coded}", username=message.author.display_name, avatar_url=message.author.avatar.url, allowed_mentions=discord.AllowedMentions.none())
								try:
									await message.delete()
								except:
									pass
							else:
								temp = await message.channel.send("error. content must be 2000 or fewer in length.", mention_author=False)
								await asyncio.sleep(5)
								await temp.delete()
						else:
							embed = discord.Embed(title="Uh oh", description="It seems like @everyone role doesn't have permission to use `external_emojis` on this **channel**. Please enable it to use external emojis.", color=self.bot.c)
							embed.set_image(url="https://cdn.discordapp.com/attachments/779892741696913438/821106922174283867/unknown.png")
							await message.channel.send(embed=embed)
					else:
						embed = discord.Embed(title="Uh oh", description="It seems like @everyone role doesn't have permission to use `external_emojis` on this **server**. Please enable it to use external emojis.", color=self.bot.c)
						embed.set_image(url="https://cdn.discordapp.com/attachments/781487758308671520/820893933646249984/unknown.png")
						await message.channel.send(embed=embed)
				else:
					if message.reference:
						await message.reference.resolved.reply(coded, allowed_mentions=discord.AllowedMentions.all() if message.mentions else discord.AllowedMentions.none())
					else:
						await message.channel.send(coded, allowed_mentions=discord.AllowedMentions.none())

	@commands.Cog.listener()
	async def on_reply(self, message):
		if message.author == self.bot.user:
			self.bot.reply_cache.put(message)


def setup(bot):
	bot.add_cog(Events(bot))