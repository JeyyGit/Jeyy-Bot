import importlib
import discord
from discord.ext import commands

from utils import views
importlib.reload(views)

from utils.views import HelpView

class JeyyHelp(commands.MinimalHelpCommand):
	def get_context(self):
		return self.context
		
	async def send_bot_help(self, mapping):
		await HelpView(self.context, self).start_cog_help(mapping)

	async def send_command_help(self, command):
		ctx = self.get_context()
		if ctx.guild.id == 336642139381301249 and command.name == "snipe":
			return
			
		aliases = command.aliases
		if aliases:
			aliases = [f"`{alias}`" for alias in aliases]
			embed = discord.Embed(title=f"{self.get_command_signature(command)}", description="**Aliases: **"+", ".join(aliases), color=ctx.bot.c)
		else:
			embed = discord.Embed(title=f"{self.get_command_signature(command)}", color=ctx.bot.c)
		if command.help:
			embed.add_field(name=command.name, value=command.help, inline=False)

		await ctx.reply(embed=embed, mention_author=False)

	async def send_group_help(self, command):
		ctx = self.get_context()

		if command.name == "isometric":
			cmd = ctx.bot.get_command("isometric help")
			await cmd(ctx)
			return

		aliases = command.aliases
		if aliases:
			aliases = [f"`{alias}`" for alias in aliases]
			embed = discord.Embed(title=f"{self.get_command_signature(command)}", description="**Aliases: **"+", ".join(aliases), color=ctx.bot.c)
		else:
			embed = discord.Embed(title=f"{self.get_command_signature(command)}", color=ctx.bot.c)
		if command.help:
			embed.add_field(name=command.name, value=command.help.replace("j;", ctx.prefix), inline=False)

		children = [self.get_command_signature(cmd) for cmd in command.walk_commands()]
		embed.add_field(name="Command(s)", value="\n".join(children))
		await ctx.reply(embed=embed, mention_author=False)

	async def send_cog_help(self, cog):
		await self.context.reply(embed=HelpView(self.context, self).create_cog_embed(cog, cog.get_commands()))

	