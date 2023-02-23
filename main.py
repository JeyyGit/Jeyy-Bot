import asyncio
import os
import traceback

import asyncpg
import discord
from discord.ext import commands

from utils.contextbot import JeyyBot

intents = discord.Intents.default()
intents.message_content = True

PREFIXES = ['j;', "J;", "j:", "J:", "🌈 ",
            "jeyy ate my ", "||j||", "<@!779783517613588520> "]
bot = JeyyBot(command_prefix=PREFIXES, case_insensitive=True, owner_ids={
              624026977191329803, 699839134709317642}, intents=intents, activity=discord.Activity(type=discord.ActivityType.listening, name="`j;`"))


os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"


@bot.command(aliases=['l'], hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    extension = extension.capitalize()
    async with ctx.typing():
        try:
            await bot.load_extension(f"cogs.{extension}")
            await ctx.reply(f"{extension} cog loaded!", mention_author=False)
        except Exception as e:
            print(e)
            await ctx.reply("```py\n" + "".join(traceback.format_exception(type(e), e, e.__traceback__)) + "```", mention_author=False)


@bot.command(aliases=['u'], hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
    extension = extension.capitalize()
    async with ctx.typing():
        try:
            await bot.unload_extension(f"cogs.{extension}")
            await ctx.reply(f"{extension} cog unloaded!", mention_author=False)
        except Exception as e:
            print(e)
            await ctx.reply("```py\n" + "".join(traceback.format_exception(type(e), e, e.__traceback__)) + "```", mention_author=False)


@bot.command(aliases=['r'], hidden=True)
@commands.is_owner()
async def reload(ctx, extension):
    extension = extension.capitalize()
    async with ctx.typing():
        try:
            await bot.unload_extension(f"cogs.{extension}")
        except Exception as e:
            print(e)
            await ctx.reply("```py\n" + "".join(traceback.format_exception(type(e), e, e.__traceback__)) + "```", mention_author=False)
        else:
            try:
                await bot.load_extension(f"cogs.{extension}")
                await ctx.reply(f"{extension} cog reloaded!", mention_author=False)
                print(f"{extension} cog reloaded!")
            except Exception as e:
                print(e)
                await ctx.reply("```py\n" + "".join(traceback.format_exception(type(e), e, e.__traceback__)) + "```", mention_author=False)


@bot.command(aliases=['ra'], hidden=True)
@commands.is_owner()
async def reloadall(ctx):
    async with ctx.typing():
        try:
            bot.no_idle.cancel()
        except:
            pass
        success = []
        errors = []
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    await bot.unload_extension(f"cogs.{filename[:-3]}")
                except Exception as e:
                    print(e)
                    errors.append(
                        "```py\n" + "".join(traceback.format_exception(type(e), e, e.__traceback__)) + "```")
                else:
                    try:
                        await bot.load_extension(f"cogs.{filename[:-3]}")
                        success.append(filename[:-3])
                    except Exception as e:
                        print(e)
                        errors.append(
                            "```py\n" + "".join(traceback.format_exception(type(e), e, e.__traceback__)) + "```")

    await ctx.reply("Cogs reloaded:\n{}\n{}".format(", ".join(success), ['', "\n".join(errors)][1]), mention_author=False)
    print("Cogs reloaded:\n{}\n{}".format(
        ", ".join(success), "\n".join(errors)))


async def main():
    async with bot:
        await bot.start(bot.keys('BOTTOKEN'))
        print(bot.commands)

if __name__ == "__main__":
    asyncio.run(main())
