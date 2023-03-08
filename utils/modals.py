import discord

class AceModal(discord.ui.Modal):
    name_input = discord.ui.TextInput(
            label='Name', 
            min_length=1,
            max_length=100
    )
    text_input = discord.ui.TextInput(
            label='Text',
            style=discord.TextStyle.paragraph,
            min_length=1,
            max_length=240
    )

    def __init__(self, ctx, title):
        super().__init__(title=title)
        self.ctx = ctx
        self.name_input.default = str(ctx.author)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.stop()


