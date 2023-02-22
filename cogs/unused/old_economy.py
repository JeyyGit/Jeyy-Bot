import discord
from discord.ext import commands
import random
import asyncio


class Economy(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"Economy Cog Loaded")

	@commands.command(name="daily")
	@commands.cooldown(1, 86400, commands.BucketType.user)
	async def daily(self, ctx):
		"""Claim your daily coins"""
		author_id = ctx.author.id

		user = await self.client.pg_con.fetch("SELECT * FROM eco WHERE user_id = $1", author_id)
		if not user:
			await self.client.pg_con.execute("INSERT INTO eco (user_id, coins, inv) VALUES ($1, $2, ARRAY[[$3, $4]])", author_id, 0, 'worm', '3')

		coins = await self.client.pg_con.fetchrow("SELECT coins FROM eco WHERE user_id = $1", ctx.author.id)
		coins = coins[0]
		coins += 100
		await ctx.reply("You got `100` coins from claiming you daily!", mention_author=False)

		await self.client.pg_con.execute("UPDATE eco SET coins = $1 WHERE user_id = $2", coins, ctx.author.id)

	@commands.command(name="fish")
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def fish(self, ctx):
		"""Catch a fish!
		You need `1 worm` each time you go fishing and you will get free 3 worms for your first time.\nYou can see things you have caught in `j;bucket`, sell your fish to get coins in `j;sell`, and buy worms in `j;shop`
		"""
		author_id = ctx.author.id
		user = await self.client.pg_con.fetch("SELECT * FROM eco WHERE user_id = $1", author_id)

		if not user:
			await self.client.pg_con.execute("INSERT INTO eco (user_id, coins, inv) VALUES ($1, $2, ARRAY[[$3, $4]])", author_id, 0, 'worm', '3')
		
		inv_all = await self.client.pg_con.fetchrow("SELECT * FROM eco WHERE user_id = $1", author_id)
		inv = inv_all["inv"]
		bucket = inv_all["bucket"]
		count = 0

		if not bucket:
			bucket = []
		if not inv:
			inv = []

		for i in inv:
			if i[0] == 'worm':
				count = int(i[1])
				if count > 0:
					fishes = ['pair of boots', 'cod', 'tropical fish', 'blowfish', 'shark']
					emojis = ['\U0001f462', '\U0001f41f', '\U0001f420', '\U0001f421', '\U0001f988']
					chosen = random.choices([0, 1, 2, 3, 4], weights=(37, 30, 20, 10, 3))[0]
					caught = fishes[chosen]
					emoji = emojis[chosen]
					count -= 1
					inv[inv.index(i)][1] = str(count)

					await ctx.reply(f"\U0001f3a3** | **You used **1 \U0001fab1 Worm** and caught a {emoji} **{caught}** !\n\nYou have **[{count}] \U0001fab1 worm(s)** left.", mention_author=False)

					for j in bucket:
						if j[0] == caught:
							count = int(j[1])
							count += 1
							bucket[bucket.index(j)][1] = str(count)
							await self.client.pg_con.execute("UPDATE eco SET (inv, bucket) = ($1, $2) WHERE user_id = $3", inv, bucket, author_id)
							break
					else:
						bucket.append([caught, '1'])
						await self.client.pg_con.execute("UPDATE eco SET (inv, bucket) = ($1, $2) WHERE user_id = $3", inv, bucket, author_id)

					for item in inv:
						if item[1] == '0':
							inv.remove(item)
							await self.client.pg_con.execute("UPDATE eco SET inv = $1 WHERE user_id = $2", inv, author_id)

				elif count == 0:
					await ctx.reply("You don't have any worms. You can buy worms in `j;shop`.", mention_author=False)
					break
				break
		else:
			await ctx.reply("You don't have any worms. You can buy worms in `j;shop`.", mention_author=False)

	@commands.command(name="inventory", aliases=["inv"])
	async def inventory(self, ctx):
		"""See your inventory"""
		author_id = ctx.author.id

		_items = []
		inv = await self.client.pg_con.fetchrow("SELECT inv FROM eco WHERE user_id = $1", author_id)
		if not inv or not inv[0]:
			await ctx.reply(embed=discord.Embed(title="You don't have any item.", color=self.client.c).set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url), mention_author=False)
		else:
			for i in inv[0]:
				_items.append(f"[{i[1]}] {i[0]}")
			await ctx.reply(embed=discord.Embed(title="Your item(s):", description="```c\n{} ```".format("\n".join(_items)), color=self.client.c).set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url), mention_author=False)

	@commands.command(name="bucket")
	async def bucket(self, ctx):
		"""See things you have caught"""
		author_id = ctx.author.id

		_items = []
		emojis = {'pair of boots':'\U0001f462', 'cod':'\U0001f41f', 'tropical fish':'\U0001f420', 'blowfish':'\U0001f421', 'shark':'\U0001f988'}
		bucket = await self.client.pg_con.fetchrow("SELECT bucket FROM eco WHERE user_id = $1", author_id)

		if not bucket or not bucket[0]:
			await ctx.reply(embed=discord.Embed(title="Your bucket is empty!", color=self.client.c).set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url), mention_author=False)
		else:
			for i in bucket[0]:
				_items.append(f"[{i[1]}] {i[0]} {emojis[i[0]]}")
			await ctx.reply(embed=discord.Embed(title="Your bucket contains:", description="```r\n{} ```".format("\n".join(_items)), color=self.client.c).set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url), mention_author=False)

	@commands.command(name="sell")
	async def sell(self, ctx, item:str=None, amount:str=None):
		"""Sell anything in your bucket
		Sell your items in your bucket for coins. Select what type of item you want to sell, the amount, and confirm!
		"""
		def check_react(reaction, user):
			return user == ctx.author and (str(reaction.emoji) in [f"{nums[i]}\U0000fe0f\U000020e3" for i in range(len(_items)-1)] or str(reaction.emoji) == "\U0000274e") and reaction.message == select

		def check_confirm(reaction, user):
			return user == ctx.author and str(reaction.emoji) in ["\U00002705", "\U0000274e"] and reaction.message == confirm

		def check_msg(msg:discord.Message):
			return msg.author == ctx.author and msg.channel == hm.channel

		author_id = ctx.author.id
		bucket = await self.client.pg_con.fetchrow("SELECT bucket FROM eco WHERE user_id = $1", author_id)
		coins = await self.client.pg_con.fetchrow("SELECT coins FROM eco WHERE user_id = $1", author_id)
		price = {'pair of boots':1, 'cod':3, 'tropical fish':4, 'blowfish':6, 'shark':10}

		if not bucket or not bucket[0]:
			await ctx.reply(embed=discord.Embed(title="Your bucket is empty!", color=self.client.c).set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url), mention_author=False)
		elif item:
			
			if item == "all":
				_items = []
				total = 0
				for i in bucket[0]:
					_items.append(f"[{i[1]}] {i[0]} for {int(i[1])*price[i[0]]} coins")
					total += int(i[1])*price[i[0]]

				_items.append(f"total = {total} coins")

				embed = discord.Embed(title="Sell confirmation:", description="```r\nAre you sure you want to sell:\n{}\n\nReact \U00002705 or \U0000274e . ```".format("\n".join(_items)), color=self.client.c)
				embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
				
				confirm = await ctx.reply(embed=embed, mention_author=False)
				await confirm.add_reaction("\U00002705")
				await confirm.add_reaction("\U0000274e")

				try:
					w, z = await self.client.wait_for('reaction_add', timeout=15.5, check=check_confirm)
					if w.emoji == "\U00002705":
						await confirm.delete()

						embed = discord.Embed(title="Confirmed!", description="```r\nYou sold:\n{} ```".format("\n".join(_items)), color=self.client.c)

						bucket = bucket[0]
						bucket = []
						coins = coins[0]
						coins += total

						await self.client.pg_con.execute("UPDATE eco SET (coins, bucket) = ($1, $2) WHERE user_id = $3", coins, bucket, author_id)

						await ctx.reply(embed=embed, mention_author=False)
					elif w.emoji == "\U0000274e":
						await confirm.delete()
						await ctx.reply("Cancelled.", mention_author=False)
						
				except asyncio.TimeoutError:
					await confirm.delete()
					await ctx.reply("Timed out.", mention_author=False, delete_after=15)

		else:
			_items = []
			nums = ['\U00000031', '\U00000032', '\U00000033', '\U00000034', '\U00000035']
			emojis = {'pair of boots':'\U0001f462', 'cod':'\U0001f41f', 'tropical fish':'\U0001f420', 'blowfish':'\U0001f421', 'shark':'\U0001f988'}
			for i, val in enumerate(bucket[0]):
				_items.append(f"{nums[i]}\U0000fe0f\U000020e3 {val[0]} {emojis[val[0]]}, you have [{val[1]}]")

			_items.append("\U0000274e cancel")

			select = await ctx.reply(embed=discord.Embed(title="Select what you want to sell:", description="```r\n{} ```".format("\n".join(_items)), color=self.client.c).set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url), mention_author=False)

			for i in range(len(_items)-1):
				await select.add_reaction(f"{nums[i]}\U0000fe0f\U000020e3")
			await select.add_reaction("\U0000274e")

			try:
				m, r = await self.client.wait_for('reaction_add', timeout=15.5, check=check_react)
				for i in range(len(_items)):
					if m.emoji == f"{nums[i]}\U0000fe0f\U000020e3":
						await select.delete()

						selected = bucket[0][i]
						selected_name = selected[0]
						selected_count = int(selected[1])

						embed = discord.Embed(title="Type how many items you want to sell:", description=f"```r\nType in how many {selected_name} you want to sell. You have {selected_count}.\n\nEach item sells for : {price[selected_name]} coins. ```", color=self.client.c)
						embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
						embed.set_footer(text=f"Type [cancel] to cancel.")

						hm = await ctx.reply(embed=embed, mention_author=False)	
						
						while True:
							try:
								m = await self.client.wait_for('message', timeout = 20.5, check=check_msg)
								if m.content.isdigit() and int(m.content) > 0 and int(m.content) <= selected_count:
									count = int(m.content)
									await hm.delete()

									embed = discord.Embed(title="Sell confirmation:", description=f"```r\nAre you sure you want to sell {count} {selected_name} ?\nReact \U00002705 or \U0000274e .\n\nEach item sells for : {price[selected_name]} coins.\nSelling {count} {selected_name} for total : {price[selected_name]*count} coins. ```", color=self.client.c)
									embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
									
									confirm = await ctx.reply(embed=embed, mention_author=False)
									await confirm.add_reaction("\U00002705")
									await confirm.add_reaction("\U0000274e")

									try:
										w, z = await self.client.wait_for('reaction_add', timeout=15.5, check=check_confirm)
										if w.emoji == "\U00002705":
											await confirm.delete()

											embed = discord.Embed(title="Confirmed!", description=f"```r\nYou sold {count} {selected_name} for {price[selected_name] * count} coins. ```", color=self.client.c)

											bucket = bucket[0]
											bucket[bucket.index([selected_name, str(selected_count)])][1] = str(selected_count-count)
											coins = coins[0]
											coins = coins + price[selected_name] * count

											await self.client.pg_con.execute("UPDATE eco SET (coins, bucket) = ($1, $2) WHERE user_id = $3", coins, bucket, author_id)

											await ctx.reply(embed=embed, mention_author=False)
										elif w.emoji == "\U0000274e":
											await confirm.delete()
											await ctx.reply("Cancelled.", mention_author=False)
											
									except asyncio.TimeoutError:
										await confirm.delete()
										await ctx.reply("Timed out.", mention_author=False, delete_after=15)
									
									break
								elif m.content.lower() == "cancel":
									await hm.delete()
									await m.reply("Canceled.", mention_author=False)
									break
								else:
									await m.reply("Invalid input. Try again.", mention_author=False, delete_after=5)
							except asyncio.TimeoutError:
								await hm.delete()
								await ctx.reply("Timed out.", mention_author=False, delete_after=15)
								break

						break

					elif m.emoji == "\U0000274e":
						await select.delete()
						await ctx.reply("Canceled.", mention_author=False)
						break

			except asyncio.TimeoutError:
				await select.delete()
				await ctx.reply("Timed out.", mention_author=False, delete_after=15)

			bucket = await self.client.pg_con.fetchrow("SELECT bucket FROM eco WHERE user_id = $1", author_id)

			for item in bucket[0]:
				if item[1] == '0':
					bucket[0].remove(item)
					await self.client.pg_con.execute("UPDATE eco SET bucket = $1 WHERE user_id = $2", bucket[0], author_id)

	@commands.command(name="pouch", aliases=["wallet", "bal", "balance"])
	async def pouch(self, ctx):
		"""Check your coins"""
		coins = await self.client.pg_con.fetchrow("SELECT coins FROM eco WHERE user_id = $1", ctx.author.id)

		if not coins:
			await ctx.reply(embed=discord.Embed(title="You have `0` coins.", color=self.client.c).set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url), mention_author=False)
		else:
			await ctx.reply(embed=discord.Embed(title=f"You have `{coins[0]}` coins.", color=self.client.c).set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url), mention_author=False)

	@commands.command(name="shop", aliases=["buy"])
	@commands.cooldown(1, 30, commands.BucketType.user)
	async def shop(self, ctx):
		"""Buy worm for fishing
		Buy anything you need with coins! You can buy worms for fishing or anything else
		"""
		nums = ['\U00000031', '\U00000032', '\U00000033', '\U00000034', '\U00000035']
		sell = {'worm': 1, 'ALMIGHTY JEYY': 999}
		_list = []

		for i, item in enumerate(sell):
			_list.append(f"{nums[i]}\U0000fe0f\U000020e3 {item}, price: {sell[item]} coin(s) each")
		
		author_id = ctx.author.id

		coins = await self.client.pg_con.fetchrow("SELECT coins FROM eco WHERE user_id = $1", author_id)
		inv = await self.client.pg_con.fetchrow("SELECT inv FROM eco WHERE user_id = $1", author_id)

		if not coins:
			coins = [0]

		def check_msg(msg:discord.Message):
			return msg.author == ctx.author and msg.channel in [page1.channel, hw.channel]

		def check_confirm(reaction, user):
			return user == ctx.author and str(reaction.emoji) in ["\U00002705", "\U0000274e"] and reaction.message == confirm

		embed = discord.Embed(title="=: Shop :=", description="```c\nYour coins : {}\n\n{} ```".format(coins[0], "\n".join(_list)), color=self.client.c)
		embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
		embed.set_footer(text="Type the number of item you want to buy. Type [cancel] to cancel.")

		page1 = await ctx.reply(embed=embed, mention_author=False)

		while True:
			try:
				w = await self.client.wait_for('message', timeout=15.5, check=check_msg)
				if w.content.isdigit() and int(w.content) > 0 and int(w.content) <= len(sell):
					await page1.delete()

					index = int(w.content)-1
					selected_name = list(sell.keys())[index]
					selected_price = sell[selected_name]

					embed = discord.Embed(title=f"Type how many {selected_name} you want to buy.", description=f"```c\nYour coins : {coins[0]}\n\nitem: {selected_name}\nprice: {selected_price} each ```", color=self.client.c)
					embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
					embed.set_footer(text="Type [cancel] to cancel.")

					hw = await ctx.reply(embed=embed, mention_author=False)

					while True:
						try:
							d = await self.client.wait_for('message', timeout=15.5, check=check_msg)
							if d.content.isdigit() and int(d.content) > 0:
								count = int(d.content)

								#if coins[0] <= (coins[0] // (count*selected_price)):
								if coins[0] - count*selected_price >= 0:
									await hw.delete()

									embed = discord.Embed(title="Buy confirmation:", description=f"```c\nAre you sure you want to buy {count} {selected_name} ?\nReact \U00002705 or \U0000274e .\n\nEach item price : {selected_price} coins.\nBuying {count} {selected_name} for total : {selected_price*count} coins. ```", color=self.client.c)
									embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

									confirm = await ctx.reply(embed=embed, mention_author=False)
									await confirm.add_reaction("\U00002705")
									await confirm.add_reaction("\U0000274e")

									try:
										c, v = await self.client.wait_for('reaction_add', timeout=15.5, check=check_confirm)
										if c.emoji == "\U00002705":
											await confirm.delete()

											embed = discord.Embed(title="Confirmed!", description=f"```c\nYou purchased {count} {selected_name} for {selected_price * count} coins. ```", color=self.client.c)

											coins = coins[0]
											coins = coins - selected_price*count

											for i in inv[0]:
												if i[0] == selected_name:
													howm = int(i[1])
													howm = howm + count
													inv[0][inv[0].index(i)][1] = str(howm)
													break
											else:
												inv[0].append([selected_name, str(count)])

											await self.client.pg_con.execute("UPDATE eco SET (coins, inv) = ($1, $2) WHERE user_id = $3", coins, inv[0], author_id)
											await ctx.reply(embed=embed, mention_author=False)

										elif c.emoji == "\U0000274e":
											await confirm.delete()
											await ctx.reply("Canceled.", mention_author=False)
											
									except asyncio.TimeoutError:
										await confirm.delete()
										await ctx.reply("Timed out.", mention_author=False, delete_after=15)

									break 
								else:
									await d.reply("You don't have enough coins to buy that much. Try again.", mention_author=False, delete_after=5)

							elif d.content.lower() == "cancel":
								await hw.delete()
								await d.reply("Canceled.", mention_author=False)
								break

							else:
								await d.reply("Invalid input. Try again.", mention_author=False, delete_after=5)

						except asyncio.TimeoutError:
							await hw.delete()
							await ctx.reply("Timed out.", mention_author=False, delete_after=15)
							break

					break
				elif w.content.lower() == "cancel":
					await page1.delete()
					await w.reply("Canceled.", mention_author=False)
					break
				else:
					await w.reply("Invalid input. Try again.", mention_author=False, delete_after=5)

			except asyncio.TimeoutError:
				await page1.delete()
				await ctx.reply("Timed out.", mention_author=False, delete_after=15)
				break

	@commands.command(name="slot", aliases=["slots", "casino", "csn"])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def slot(self, ctx, bet:int=None):
		"""Gamble your coins"""
		coins = await self.client.pg_con.fetchrow("SELECT coins FROM eco WHERE user_id = $1", ctx.author.id)
		if not coins:
			coins = [0]
		coins = coins[0]

		if bet == None:
			bet = 1

		if bet <= 0:
			await ctx.reply("Invalid amount.", mention_author=False)
			return
		elif bet > 1000:
			await ctx.reply("Max bet is 1000 coins.", mention_author=False)
			return
		elif coins - bet < 0:
			await ctx.reply("You don't have enough coins to do that bet.", mention_author=False)
			return 
		else:
			e = {'pair of boots':'\U0001f462', 'cod':'\U0001f41f', 'tropical fish':'\U0001f420', 'blowfish':'\U0001f421', 'shark':'\U0001f988'}
			c = [["","",""],["","",""],["","",""]]
			m = await ctx.reply("\u200b", mention_author=False)
			coins -= bet
			for k in range(3):
				for i in range(3):
					for j in range(3):
						c[i][j] = random.choice(["pair of boots", "cod", "tropical fish", "blowfish", "shark"])

				await m.edit(content=f"""╔═══════════╗
 :   {e[c[0][0]]}  │  {e[c[0][1]]}  │  {e[c[0][2]]}  :
╠═══════════╣
 :   {e[c[1][0]]}  │  {e[c[1][1]]}  │  {e[c[1][2]]}  :  \U00002b05\U0000fe0f {'<'*(k+1)}
╠═══════════╣
 :   {e[c[2][0]]}  │  {e[c[2][1]]}  │  {e[c[2][2]]}  :
╚═══════════╝
			""", allowed_mentions=discord.AllowedMentions.none())
			await asyncio.sleep(2)
		if True:
			for i in range(3):
				for j in range(3):
					c[i][j] = random.choice(["pair of boots", "cod", "tropical fish", "blowfish", "shark"])

			prob = random.choices(["l", "pair of boots", "cod", "tropical fish", "blowfish", "shark"], weights=[725, 300, 100, 50, 20, 5])[0]
			if prob == "l":
				if c[1][0] == c[1][1] and c[1][0] == c[1][2]:
					c[1][0], c[1][1] = 'cod', 'shark'

				w = 0
				ann = "LOSES IT ALL"
			elif prob == "pair of boots":
				c[1][0] = c[1][1] = c[1][2] = prob
				w = bet * 2
				ann = f"WON {w} COINS"
			elif prob == "cod":
				c[1][0] = c[1][1] = c[1][2] = prob
				w = bet * 5
				ann = f"WON {w} COINS"
			elif prob == "tropical fish":
				c[1][0] = c[1][1] = c[1][2] = prob
				w = bet * 10
				ann = f"WON {w} COINS"
			elif prob == "blowfish":
				c[1][0] = c[1][1] = c[1][2] = prob
				w = bet * 15
				ann = f"WON {w} COINS"
			elif prob == "shark":
				c[1][0] = c[1][1] = c[1][2] = prob
				w = bet * 50
				ann = f"WON {w} COINS"
			coins += w
			await self.client.pg_con.execute("UPDATE eco SET coins = $1 WHERE user_id = $2", coins, ctx.author.id)
			await m.edit(content=f"""╔═══════════╗
 :   {e[c[0][0]]}  │  {e[c[0][1]]}  │  {e[c[0][2]]}  :
╠═══════════╣
 **:   {e[c[1][0]]}  │  {e[c[1][1]]}  │  {e[c[1][2]]}  :  \U00002b05\U0000fe0f <<<**
╠═══════════╣
 :   {e[c[2][0]]}  │  {e[c[2][1]]}  │  {e[c[2][2]]}  :
╚═══════════╝
		**{ctx.author} BET {bet} COIN(S) AND {ann}**
			""", allowed_mentions=discord.AllowedMentions.none())


def setup(client):
	client.add_cog(Economy(client))