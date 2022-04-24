from discord.ext import commands
import asyncpg
import discord
import os
import traceback


from utils.contextbot import JeyyBot

intents = discord.Intents.default()
# intents.message_content = True

PREFIXES = ['j;', "J;", "j:", "J:", "🌈 ", "jeyy ate my ", "||j||", "<@!779783517613588520> "]
bot = JeyyBot(command_prefix=PREFIXES, case_insensitive=True, owner_ids={624026977191329803, 699839134709317642}, intents=intents, activity=discord.Activity(type=discord.ActivityType.listening, name="`j;`"))

bot.load_extension("jishaku")
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True" 
os.environ["JISHAKU_HIDE"] = "True"

async def create_db_pool():
	bot.db = await asyncpg.create_pool(
  		host=bot.keys('DBHOST'), database=bot.keys('DBNAME'), 
  		user=bot.keys('DBUSER'), password=bot.keys('DBPASS')
	)

@bot.command(aliases=['l'], hidden=True)
@commands.is_owner()
async def load(ctx, extension):
	extension = extension.capitalize()
	await ctx.trigger_typing()
	try:
		bot.load_extension(f"cogs.{extension}")
		await ctx.reply(f"{extension} cog loaded!", mention_author=False)
	except Exception as e:
		print(e)
		await ctx.reply("```py\n"+ "".join(traceback.format_exception(type(e), e, e.__traceback__))+ "```", mention_author=False)

@bot.command(aliases=['u'], hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
	extension = extension.capitalize()
	await ctx.trigger_typing()
	try:
		bot.unload_extension(f"cogs.{extension}")
		await ctx.reply(f"{extension} cog unloaded!", mention_author=False)
	except Exception as e:
		print(e)
		await ctx.reply("```py\n"+ "".join(traceback.format_exception(type(e), e, e.__traceback__))+ "```", mention_author=False)

@bot.command(aliases=['r'], hidden=True)
@commands.is_owner()
async def reload(ctx, extension):
	extension = extension.capitalize()
	await ctx.trigger_typing()
	try:
		bot.unload_extension(f"cogs.{extension}")
	except Exception as e:
		print(e)
		await ctx.reply("```py\n"+ "".join(traceback.format_exception(type(e), e, e.__traceback__))+ "```", mention_author=False)
	else:
		try:
			bot.load_extension(f"cogs.{extension}")
			await ctx.reply(f"{extension} cog reloaded!", mention_author=False)
			print(f"{extension} cog reloaded!")
		except Exception as e:
			print(e)
			await ctx.reply("```py\n"+ "".join(traceback.format_exception(type(e), e, e.__traceback__))+ "```", mention_author=False)

@bot.command(aliases=['ra'], hidden=True)
@commands.is_owner()
async def reloadall(ctx):
	await ctx.trigger_typing()
	# bot.ipc.update_endpoints()
	try:
		bot.no_idle.cancel()
	except:
		pass
	success = []
	errors = []
	for filename in os.listdir("./cogs"):
		if filename.endswith(".py"):
			try:
				bot.unload_extension(f"cogs.{filename[:-3]}")
			except Exception as e:
				print(e)
				errors.append("```py\n"+ "".join(traceback.format_exception(type(e), e, e.__traceback__))+ "```")
			else:
				try:
					bot.load_extension(f"cogs.{filename[:-3]}")
					success.append(filename[:-3])
				except Exception as e:
					print(e)
					errors.append("```py\n"+ "".join(traceback.format_exception(type(e), e, e.__traceback__))+ "```")

	await ctx.reply("Cogs reloaded:\n{}\n{}".format(", ".join(success), ['', "\n".join(errors)][1]), mention_author=False)
	print("Cogs reloaded:\n{}\n{}".format(", ".join(success), "\n".join(errors)))


for filename in os.listdir("./cogs"):
	if filename.endswith(".py"):
		bot.load_extension(f"cogs.{filename[:-3]}")





























if __name__ == "__main__":
	bot.loop.run_until_complete(create_db_pool())
	bot.run(bot.keys('BOTTOKEN'))
