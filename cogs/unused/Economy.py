import discord
from discord.ext import commands
import random
import asyncio
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

pcanvas = Image.open("./image/profile/p_canvas1024x.png")
name_font = ImageFont.truetype("./image/profile/Cocogoose Pro Light Trial.ttf", 60)
title_font = ImageFont.truetype("./image/profile/Cocogoose Pro Light Trial.ttf", 46)
co = "<a:coin:839444870652231701>"
warn = "<:warning:839782890765942794>"
info = "<:info:839526979635118091>"
use = "<:use:839576952998592512>"
trash = "<:trash:839576952595284029>"
cross = "<:cross:839786086645104680>"
check = "<:check:839786086615613460>"
x = 64
positions = {
	1: (int(x*2.5), int(x*8.5)),
	2: (int(x*5), int(x*8)),
	3: (int(x*7), int(x*8)),
	4: (int(x*9), int(x*8)),
	5: (int(x*11), int(x*8.5)),
	6: (int(x*2.5), int(x*10.5)),
	7: (int(x*5), int(x*11)),
	8: (int(x*7), int(x*11)),
	9: (int(x*9), int(x*11)),
	10: (int(x*11), int(x*10.5))
}
items = {
	'Alien-1 Badge':{
		'name': 'Alien-1 Badge',
		'icon': '<:alien14x:839438904569364482>',
		'category': 'badge',
		'pic': Image.open("./image/profile/space/alien-1@2x.png").convert("RGBA"),
		'icon_url': 'https://cdn.discordapp.com/emojis/839438904569364482.png?v=1',
		'desc': "Cute little alien badge variant-1",
		'price': 1000,
		'sell_price': 200
	},
	'Alien-2 Badge':{
		'name': 'Alien-2 Badge',
		'icon': '<:alien24x:839438905237176340>',
		'category': 'badge',
		'pic': Image.open("./image/profile/space/alien-2@2x.png").convert("RGBA"),
		'icon_url': 'https://cdn.discordapp.com/emojis/839438905237176340.png?v=1',
		'desc': "Cute little alien badge variant-2",
		'price': 1000,
		'sell_price': 200
	},
	'Alien-3 Badge':{
		'name': 'Alien-3 Badge',
		'icon': '<:alien34x:839438905056821268>',
		'category': 'badge',
		'pic': Image.open("./image/profile/space/alien-3@2x.png").convert("RGBA"),
		'icon_url': 'https://cdn.discordapp.com/emojis/839438905056821268.png?v=1',
		'desc': "Cute little alien badge variant-3",
		'price': 1000,
		'sell_price': 200
	},
	'Alien-4 Badge':{
		'name': 'Alien-4 Badge',
		'icon': '<:alien44x:839438905027985428>',
		'category': 'badge',
		'pic': Image.open("./image/profile/space/alien-4@2x.png").convert("RGBA"),
		'icon_url': 'https://cdn.discordapp.com/emojis/839438905027985428.png?v=1',
		'desc': "Cute little alien badge variant-4",
		'price': 1000,
		'sell_price': 200
	},
	'Alien-5 Badge':{
		'name': 'Alien-5 Badge',
		'icon': '<:alien54x:839495690341056562>',
		'category': 'badge',
		'pic': Image.open("./image/profile/space/alien-5@2x.png").convert("RGBA"),
		'icon_url': 'https://cdn.discordapp.com/emojis/839495690341056562.png?v=1',
		'desc': "Cute little alien badge variant-5",
		'price': 1000,
		'sell_price': 200
	},
	'UFO-Green Badge':{
		'name': 'UFO-Green Badge',
		'icon': '<:alienship24x:839495690568728626> ',
		'category': 'badge',
		'pic': Image.open("./image/profile/space/alien-ship-2@2x.png").convert("RGBA"),
		'icon_url': 'https://cdn.discordapp.com/emojis/839495690568728626.png?v=1',
		'desc': "Cute little green UFO badge",
		'price': 1000,
		'sell_price': 200
	},
	'UFO-Blue Badge':{
		'name': 'UFO-Blue Badge',
		'icon': '<:alienship4x:839495690677780510>',
		'category': 'badge',
		'pic': Image.open("./image/profile/space/alien-ship@2x.png").convert("RGBA"),
		'icon_url': 'https://cdn.discordapp.com/emojis/839495690677780510.png?v=1',
		'desc': "Cute little blue UFO badge",
		'price': 1000,
		'sell_price': 200
	},
	'UFO-Red Badge':{
		'name': 'UFO-Red Badge',
		'icon': '<:alienshipbeam4x:839495690694295582> ',
		'category': 'badge',
		'pic': Image.open("./image/profile/space/alien-ship-beam@2x.png").convert("RGBA"),
		'icon_url': 'https://cdn.discordapp.com/emojis/839495690694295582.png?v=1',
		'desc': "Cute little red UFO badge",
		'price': 1000,
		'sell_price': 200
	},
	'Astronaut Badge':{
		'name': 'Astronaut Badge',
		'icon': '<:atronaut4x:839495690283646987>',
		'category': 'badge',
		'pic': Image.open("./image/profile/space/atronaut@2x.png").convert("RGBA"),
		'icon_url': 'https://cdn.discordapp.com/emojis/839495690283646987.png?v=1',
		'desc': "Cute little astronaut badge",
		'price': 1000,
		'sell_price': 200
	},
	'Earth Badge':{
		'name': 'Earth Badge',
		'icon': '<:earth4x:839495690475929601>',
		'category': 'badge',
		'pic': Image.open("./image/profile/space/earth@2x.png").convert("RGBA"),
		'icon_url': 'https://cdn.discordapp.com/emojis/839495690475929601.png?v=1s',
		'desc': "Cute little earth badge",
		'price': 1000,
		'sell_price': 200
	}
}

nums = [
	"<:one:839508697545965568>", "<:two:839511019553685575>", "<:three:839511019549229067>", 
	"<:four:839511019176853524>", "<:five:839511019122065418>", "<:six:839511019830116372>", 
	"<:seven:839511019238850580>", "<:eight:839511019066884146>", "<:nine:839511019155750923>",
	"<:one:839508697545965568><:zero:839524444921528331>"
]

def create_profile(name, pfp, badges, title):
	pcv = pcanvas.copy()
	pfp = Image.open(pfp).convert("RGBA")
	pfp = pfp.resize((x*3, x*3))

	pcv.paste(pfp, (x*3, x*3), pfp)
	for badge in badges:
		try:
			pic = items[badge['badge']]['pic']
			pos = positions[badge['badge_pos']]
			pcv.paste(pic, pos, pic)
		except:
			pass

	draw = ImageDraw.Draw(pcv)
	draw.text((int(x*6.5), x*3), name, font=name_font, fill="#69220d")
	try:
		draw.text((int(x*6.5), int(x*4.5)), title, font=title_font, fill="#69220d")
	except:
		pass

	buf = BytesIO()
	pcv.save(buf, "PNG")
	buf.seek(0)

	return buf

class Economy(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.bot.items = items

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"Economy Cog Loaded")

	async def cog_check(self, ctx):
		return await self.bot.is_owner(ctx.author)

	async def check_account(self, ctx):
		check = await self.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", ctx.author.id)

		if not check:
			await ctx.reply("You don't have an account. Do `j;start` to create one!", mention_author=False)
			return False

		return True

	async def get_coin(self, member):
		return await self.bot.db.fetchval("SELECT coins FROM economy WHERE user_id = $1 AND coins IS NOT NULL", member.id)

	async def get_badge(self, member):
		return await self.bot.db.fetch("SELECT badge, badge_pos FROM economy WHERE user_id = $1 AND badge IS NOT NULL", member.id)

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def start(self, ctx):

		check = await self.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", ctx.author.id)

		if check:
			return await ctx.reply("You already have an account!", mention_author=False)

		await self.bot.db.execute("INSERT INTO economy (user_id, coins) VALUES ($1, 100)", ctx.author.id)
		await ctx.reply(f"{check} | Successfully created your account!", mention_author=False)

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def settitle(self, ctx, *, title:str=None):
		"""Set your profile  title"""
		title = title.strip()

		if not await self.check_account(ctx):
			return

		if not title:
			ctx.command.reset_cooldown(ctx)
			return await ctx.reply(f"{warn} | Please input the title argument.", mention_author=False)

		if len(title) > 20:
			ctx.command.reset_cooldown(ctx)
			return await ctx.reply(f"{warn} | Title length must be below 20 characters!", mention_author=False)

		await self.bot.db.execute("UPDATE economy SET title = $1 WHERE user_id = $2", title, ctx.author.id)
		await ctx.reply(f"{check} | Success.", mention_author=False)

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def profile(self, ctx, member:discord.Member=None):

		if not member:
			member = ctx.author

		if not await self.check_account(ctx):
			return

		await ctx.trigger_typing()

		asset = member.avatar_url_as(size=512)
		pfp = BytesIO(await asset.read())
		pfp.seek(0)

		name = member.name
		title = await self.bot.db.fetchval("SELECT title FROM economy WHERE user_id = $1 AND title IS NOT NULL", member.id)
		badges = await self.get_badge(member)

		buf = await self.bot.loop.run_in_executor(None, create_profile, name, pfp, badges, title)
		await ctx.reply(f"> {use} Profile of **{member}**", file=discord.File(buf, "profile.png"), mention_author=False)

	@commands.command(aliases=["inv"])
	async def inventory(self, ctx):
		if not await self.check_account(ctx):
			return

		inv = await self.bot.db.fetch("SELECT inventory, count(*) AS count FROM economy WHERE user_id = $1 AND inventory IS NOT NULL GROUP BY inventory", ctx.author.id)

		title = f"{ctx.author}'s inventory."
		if not inv:
			title = "Your inventory is empty!"


		embed = discord.Embed(title=title, description=f"Your coins: `{await self.get_coin(ctx.author)}` {co}", color=self.bot.c)
		for i, item in enumerate(inv):
			embed.add_field(name=f"{nums[i]} {item['inventory']}", value=f"{items[item['inventory']]['icon']} `Amount: {item['count']}`", inline=True)
		if inv:
			embed.set_footer(text="React below to see information about an item")

		inv_message = await ctx.reply(embed=embed, mention_author=False)

		if not inv:
			return

		await inv_message.add_reaction(info)

		def check_react(reaction, user):
			return str(reaction) == info and user == ctx.author and reaction.message == inv_message

		def check_number(message):
			if not message.content.isnumeric():
				return False

			num = int(message.content)
			if num not in range(1, len(inv)+1):
				return False

			return message.author == ctx.author and message.channel == ctx.channel

		def check_badge(reaction, user):
			return str(reaction) in [use, trash] and user == ctx.author and reaction.message == info_msg

		def check_use(message):
			return message.content.isnumeric() and message.author == ctx.author and message.channel == ctx.channel

		try:
			reaction, user = await self.bot.wait_for('reaction_add', check=check_react, timeout=300)
		except asyncio.TimeoutError:
			try:
				await inv_message.clear_reactions()
			except:
				await inv_message.remove_reaction(info, self.bot.user)
			return
		else:
			type_num = await ctx.send(f"**{warn} | Type the item number you want to view**")

			try:
				await inv_message.clear_reactions()
			except:
				await inv_message.remove_reaction(info, self.bot.user)
			
			try:
				message = await self.bot.wait_for('message', check=check_number, timeout=60)
			except asyncio.TimeoutError:
				await type_num.delete()
				await ctx.send(f"{cross} | Info timed out.")
			else:
				num = int(message.content)
				selected = inv[num-1]

				embed = discord.Embed(title="-= Item info =-", color=self.bot.c)
				embed.add_field(name="Item name", value=f"{items[selected['inventory']]['icon']} {items[selected['inventory']]['name']}", inline=True)
				embed.add_field(name="Category", value=items[selected['inventory']]['category'], inline=True)
				embed.add_field(name="Amount", value=selected['count'], inline=True)
				embed.add_field(name="Item description", value=items[selected['inventory']]['desc'], inline=False)
				embed.add_field(name="Buy price", value=f"{items[selected['inventory']]['price']} {co}", inline=True)
				embed.add_field(name="Sell price", value=f"{items[selected['inventory']]['sell_price']} {co}")
				embed.set_thumbnail(url=items[selected['inventory']]['icon_url'])
				if items[selected['inventory']]['category'] == 'badge':
					embed.add_field(name="\u200b", value=f"React with {use} to use this item or {trash} to trash it", inline=False)
				
				info_msg = await ctx.reply(embed=embed, mention_author=False)

				await inv_message.delete()
				await type_num.delete()
				try:
					await message.delete()
				except:
					pass

				if items[selected['inventory']]['category'] == 'badge':
					await info_msg.add_reaction(use)
					await info_msg.add_reaction(trash)
					try:
						reaction, user = await self.bot.wait_for('reaction_add', check=check_badge, timeout=180)
					except asyncio.TimeoutError:
						try:
							await info_msg.clear_reactions()
						except:
							await info_msg.remove_reaction(use, self.bot.user)
							await info_msg.remove_reaction(trash, self.bot.user)
					else:
						try:
							await info_msg.clear_reactions()
						except:
							await info_msg.remove_reaction(use, self.bot.user)
							await info_msg.remove_reaction(trash, self.bot.user)

						if str(reaction) == use:
							badges = await self.get_badge(ctx.author)
							slotted = [badge['badge_pos'] for badge in badges]

							if len(slotted) >= 10:
								return await ctx.send(f"{cross} | Your badge slot is full!")
							using = await ctx.send("**{} | Type the desired position of this badge. Available positions: {}**".format(warn, ', '.join([f"`{x}`" for x in [*range(1, 11)] if x not in slotted])))

							while True:
								try:
									message = await self.bot.wait_for('message', check=check_use, timeout=60)
								except asyncio.TimeoutError:
									await ctx.send(f"{cross} | Timed out.")
									await using.delete()
									return
								else:
									pos = int(message.content)
									if pos in slotted:
										await ctx.send(f"{warn} | That position is occupied. Try again.", delete_after=10)

										try:
											await message.delete()
										except:
											pass
										continue

									if pos not in range(1, 11):
										await ctx.send(f"{warn} | That position does not exist [from 1 to 10]. Try again.", delete_after=10)

										try:
											await message.delete()
										except:
											pass
										continue

									await using.delete()
									await self.bot.db.execute("INSERT INTO economy (user_id, badge, badge_pos) VALUES ($1, $2, $3)", ctx.author.id, items[selected['inventory']]['name'], pos)
									await self.bot.db.execute("DELETE FROM economy WHERE ctid IN (SELECT ctid FROM economy WHERE user_id = $1 AND inventory = $2 LIMIT 1)", ctx.author.id, items[selected['inventory']]['name'])
									await ctx.send(f"{check} | {items[selected['inventory']]['icon']} {items[selected['inventory']]['name']} successfully equipped on position {pos}")
									
									try:
										await message.delete()
									except:
										pass
									break

						elif str(reaction) == trash:
							trashed = await ctx.send(f"{warn} | Type how many of {items[selected['inventory']]['name']} you want to trash")
							
							while True:
								try:
									message = await self.bot.wait_for('message', check=check_use, timeout=60)
								except asyncio.TimeoutError:
									await ctx.send(f"{cross} | Timed out.")
									await trashed.delete()
									return
								else:
									amount = int(message.content)
									if amount <= 0:
										await ctx.send(f"{warn} | Invalid input. Try again.", delete_after=10)

										try:
											await message.delete()
										except:
											pass
										continue

									if amount > selected['count']:
										await ctx.send(f"{warn} | You don't have that much. Try again", delete_after=10)

										try:
											await message.delete()
										except:
											pass
										continue

									await self.bot.db.execute("DELETE FROM economy WHERE ctid IN (SELECT ctid FROM economy WHERE user_id = $1 AND inventory = $2 LIMIT $3)", ctx.author.id, items[selected['inventory']]['name'], amount)
									await ctx.send(f">>> {check} | Successfully trashed {amount} {items[selected['inventory']]['icon']} {items[selected['inventory']]['name']}")
									await trashed.delete()
									break

	@commands.group(aliases=['badges'], invoke_without_command=True)
	async def badge(self, ctx, member:discord.Member=None):
		if not member:
			member = ctx.author

		if not await self.check_account(ctx):
			return

		badges = await self.get_badge(member)
		title = f"{member} equipped badges"
		if not badges:
			title = f"{member} does not have any badges equipped!"

		embed = discord.Embed(title=title, color=self.bot.c)

		slotted = {badge['badge_pos']: badge['badge'] for badge in badges}
		for i in range(1, 11):
			if i in slotted:
				field = f"{items[slotted[i]]['icon']} {items[slotted[i]]['name']}"
				embed.add_field(name=field, value=f"Position: `{i}`", inline=True)
			else:
				embed.add_field(name="Empty", value=f"Position: `{i}`", inline=True)

		if badges:
			embed.set_footer(text="Do `j;badge unequip <position>` to unequip a badge!")

		await ctx.reply(embed=embed, mention_author=False)
	
	@badge.command()
	async def unequip(self, ctx, position:int):
		if not await self.check_account(ctx):
			return

		badges = await self.get_badge(ctx.author)

		slotted = [badge['badge_pos'] for badge in badges]

		if position not in slotted:
			return await ctx.reply("There's nothing at that spot!", mention_author=False)

		removed_name = [badge['badge'] for badge in badges if badge['badge_pos'] == position][0]

		await self.bot.db.execute("DELETE FROM economy WHERE user_id = $1 AND badge_pos = $2", ctx.author.id, position)
		await self.bot.db.execute("INSERT INTO economy (user_id, inventory) VALUES ($1, $2)", ctx.author.id, removed_name)

		await ctx.reply(f"{check} | {items[removed_name]['icon']} {removed_name} is removed from position {position}!", mention_author=False)
		
	@commands.command()
	async def shop(self, ctx):
		if not await self.check_account(ctx):
			return

		coins = await self.get_coin(ctx.author)

		embed = discord.Embed(title="-= Shop =-", description=f"You have : `{coins}` {co}", color=self.bot.c)
		for i, item in enumerate(items.values()):
			embed.add_field(name=f"{nums[i]} {item['name']} {item['icon']}", value=f"Price: `{item['price']}` <a:coin:839444870652231701>")

		await ctx.reply(embed=embed, mention_author=False)


def setup(bot):
	bot.add_cog(Economy(bot))