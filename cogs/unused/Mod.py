import discord
from discord.ext import commands
from utils.contextbot import JeyyBot, JeyyContext

class Mod(commands.Cog):

    def __init__(self, bot: JeyyBot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: JeyyContext, member: discord.Member, *, reason=None):
        await ctx.guild.ban(member, reason=reason)

    @commands.command(hidden=True)
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: JeyyContext, user: discord.User, *, reason=None):
        user = discord.Object(id=user)
        await ctx.guild.unban(user, reason=reason)

def setup(bot):
	bot.add_cog(Mod(bot))