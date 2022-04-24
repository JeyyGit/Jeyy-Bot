import typing
import discord
from discord.ext import commands

class ToImage(commands.Converter):
    async def convert(self, ctx, argument):
        if argument is None:
            converted_union = None
        else:
            converted_union = await commands.run_converters(ctx, typing.Union[discord.PartialEmoji, discord.Emoji, discord.Member, discord.User, str], argument, ctx.current_parameter)

        return await ctx.to_image(converted_union)

    @staticmethod
    async def none(ctx):
        return await ctx.to_image(None)

