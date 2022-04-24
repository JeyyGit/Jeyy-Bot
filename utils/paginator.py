import discord

class Paginator(discord.ui.View):
	def __init__(self, ctx):
		super().__init__(timeout=None)
		self.ctx = ctx
		self.embeds = None
		self.length = 0
		self.index = 0
		self.button_first = None
		self.button_previous = None
		self.button_index = None
		self.button_next = None
		self.button_last = None

	async def send(self, embeds, reply=False):
		self.embeds = embeds
		self.length = len(self.embeds)
		
		self.button_first = discord.ui.Button(style=discord.ButtonStyle.secondary, label="\u00AB")
		self.button_previous = discord.ui.Button(style=discord.ButtonStyle.secondary, label="\u2039")
		self.button_index = discord.ui.Button(style=discord.ButtonStyle.red, emoji="\U0001f6d1", label=f"Page 1 of {self.length}")
		self.button_next = discord.ui.Button(style=discord.ButtonStyle.secondary, label="\u203A")
		self.button_last = discord.ui.Button(style=discord.ButtonStyle.secondary, label="\u00BB")

		self.button_first.callback = self.button_first_callback
		self.button_previous.callback = self.button_previous_callback
		self.button_index.callback = self.button_index_callback
		self.button_next.callback = self.button_next_callback
		self.button_last.callback = self.button_last_callback
		
		self.button_next.disabled = False
		self.button_last.disabled = False
		self.button_previous.disabled = False
		self.button_first.disabled = False

		if self.index == self.length-1:
			self.button_next.disabled = True
			self.button_last.disabled = True

		if self.index == 0:
			self.button_previous.disabled = True
			self.button_first.disabled = True

		self.add_item(self.button_first)
		self.add_item(self.button_previous)
		self.add_item(self.button_index)
		self.add_item(self.button_next)
		self.add_item(self.button_last)

		if reply:
			self.message = await self.ctx.reply(embed=embeds[self.index], view=self, allowed_mentions=discord.AllowedMentions.none())
		else:
			self.message = await self.ctx.send(embed=embeds[self.index], view=self)

	async def on_timeout(self):
		self.clear_items()
		await self.message.edit(embed=self.embeds[self.index], view=None)
		self.stop()

	async def interaction_check(self, interaction):
		if interaction.user != self.ctx.author:
			await interaction.response.send_message("This is not your interaction!", ephemeral=True)
			return False

		return True

	async def button_first_callback(self, interaction):
		if self.index == 0:
			return

		self.index = 0
		await self.update()

	async def button_previous_callback(self, interaction):
		if self.index == 0:
			return

		self.index -= 1
		await self.update()

	async def button_index_callback(self, interaction):
		await self.message.delete()
		self.stop()

	async def button_next_callback(self, interaction):
		if self.index == self.length-1:
			return

		self.index += 1
		await self.update()

	async def button_last_callback(self, interaction):
		if self.index == self.length-1:
			return

		self.index = self.length-1
		await self.update()
		
	async def update(self):
		self.button_index.label = f"Page {self.index+1} of {self.length}"

		self.button_next.disabled = False
		self.button_last.disabled = False
		self.button_previous.disabled = False
		self.button_first.disabled = False

		if self.index == self.length-1:
			self.button_next.disabled = True
			self.button_last.disabled = True

		if self.index == 0:
			self.button_previous.disabled = True
			self.button_first.disabled = True

		await self.message.edit(embed=self.embeds[self.index], view=self)

