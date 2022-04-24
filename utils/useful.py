
from dataclasses import dataclass, field
from typing import List
import datetime as dt
import typing
import discord
from discord.ext import commands
import random
import secrets
import asyncio


class Loading:
	def __init__(self, ctx, content, embed):
		self.ctx = ctx
		self.content = content
		self.embed = embed
		self.message = None

	async def __aenter__(self):
		self.message = await self.ctx.reply(self.content, embed=self.embed, mention_author=False)

	async def __aexit__(self, exc_type, exc, tb):
		await self.message.delete()

class Queue:
	def __init__(self, size):
		self.size = size
		self.queue = []

	def put(self, element):
		self.queue.insert(0, element)
		if len(self.queue) > self.size:
			self.queue.pop()

	def get(self, index):
		try:
			return self.queue[index]
		except IndexError:
			return None
	
	@property
	def length(self):
		return len(self.queue)

@dataclass(frozen=True, order=True)
class Prey:
	message: discord.Message
	del_dt: dt.datetime
	att_urls: List[int] = field(default_factory=list, repr=False)

	def format_dt(self, style='f'):
		return f"<t:{int(self.del_dt.timestamp())}:{style}>"

def osc(iterable, double=False):
	"""Generator oscillates an iterable"""
	saved = []
	for element in iterable:
		yield element
		saved.append(element)
	
	if double:
		for element in iterable[::-1]:
			yield element
			saved.append(element)
	else:
		for element in iterable[-2:0:-1]:
			yield element
			saved.append(element)
			
	while saved:
		for element in saved:
			yield element

def chunk(lst, per=10, combine=False):

	result = [lst[i:i+per] for i in range(0, len(lst), per)]

	if not combine:
		return result

	return ['\n'.join(page) for page in result]

def randlistsum(n, max):
	arr = [0] * n
	for _ in range(max):
		arr[random.randint(0, max)%n] += 1
	return arr

def push(obj, l, depth):
	while depth > 0:
		l = l[-1]
		depth -= 1

	l.append(obj)

def parse_brackets(s):
	groups = []
	depth = 0

	try:
		for char in s:
			if char == '[':
				push([], groups, depth)
				depth += 1
			elif char == ']':
				depth -= 1
			else:
				push(char, groups, depth)
	except IndexError:
		raise ValueError('Brackets mismatch')

	if depth > 0:
		raise ValueError('Brackets mismatch')
	else:
		return groups

def recursive_parse(l):
	multiplied = []
	i = 0
	for _ in range(len(l)):
		if i < len(l):
			if l[i] == 'x':
				multiplied.append(l[i-1]*int(l[i+1]))
				i += 2
			else:
				if not isinstance(l[i], list) and i < len(l)-1 and l[i+1] != 'x':
					multiplied.append(l[i])
				elif i == len(l)-1 and l[i-1] != 'x':
					multiplied.append(l[i])
				i += 1

	new = []
	for el in multiplied:
		if isinstance(el, list):
			for val in el:
				new.append(val)
		else:
			new.append(el)

	if any([isinstance(el, list) for el in new]):
		return recursive_parse(new)
	else:
		return new

def parse_multiplication(blocks):

	l = parse_brackets(blocks)

	sudo_parsed = recursive_parse(l)
	if any(['x' in el for el in sudo_parsed]):
		return ''.join(recursive_parse(sudo_parsed))
	return ''.join(sudo_parsed)

def generate_ansi(
	text: str, 
	bold: bool | None, 
	underline: bool | None, 
	text_color: typing.Literal['gray', 'red', 'green', 'yellow', 'blue', 'pink', 'cyan', 'white'] | None,
	bg_color: typing.Literal['dark blue', 'orange', 'gray 1', 'gray 2', 'gray 3', 'gray 4', 'indigo', 'white'] | None,
	codeblock: bool | None
	):

	ansis = ['0']

	if text_color:
		match text_color:
			case 'gray':
				text_color = '30'
			case 'red':
				text_color = '31'
			case 'green':
				text_color = '32'
			case 'yellow':
				text_color = '33'
			case 'blue':
				text_color = '34'
			case 'pink':
				text_color = '35'
			case 'cyan':
				text_color = '36'
			case 'white':
				text_color = '37'

	if bg_color:
		match bg_color:
			case 'dark blue':
				bg_color = '40'
			case 'orange':
				bg_color = '41'
			case 'gray 1':
				bg_color = '42'
			case 'gray 2':
				bg_color = '43'
			case 'gray 3':
				bg_color = '44'
			case 'gray 4':
				bg_color = '46'
			case 'indigo':
				bg_color = '45'
			case 'white':
				bg_color = '47'

	if bold and underline:
		ansis.append('1')
		ansis.append('4')
	elif bold:
		ansis.append('1')
	elif underline:
		ansis.append('4')

	if text_color:
		ansis.append(text_color)
	if bg_color:
		ansis.append(bg_color)

	if codeblock:
		if any([bold, underline, text_color, bg_color]):
			code = f"\u001b[{';'.join(ansis)}m"
			return f'```ansi\n{code}{text}\u001b[0m\n```'
		else:
			return f'```ansi\n{text}\n```'
	else:
		code = f"\u001b[{';'.join(ansis)}m"
		return f'{code}{text}\u001b'

class TextInput:
	"""for storing our text input data"""
	def __init__(self, payload):
		self.type = payload['type']
		self.custom_id = payload['custom_id']
		self.style = payload['style']
		self.label = payload['label']
		self.min_length = payload.get('min_length')
		self.max_length = payload.get('max_length')
		self.required = payload.get('required')
		self.value = payload.get('value')
		self.placeholder = payload.get('placeholder')

class Modal:
	def __init__(self, bot: commands.Bot, title):
		self.bot = bot
		self.title = title
		self.custom_id = secrets.token_urlsafe(16)
		self.payload = {
			'title': title,
			'custom_id': self.custom_id,
			'components': []
		}
		self.adapter = discord.webhook.async_.async_context.get()
		self.fields = []

	def add_field(self, style, label, min_length=None, max_length=None, required=False, value=None, placeholder=None):
		component = {
			'type': 4,
			'custom_id': secrets.token_urlsafe(16),
			'style': style,
			'label': label,
			'required': str(required),
		}
		if min_length:
			component['min_length'] = min_length
		if max_length:
			component['max_length'] = max_length
		if value:
			component['value'] = value
		if placeholder:
			component['placeholder'] = placeholder

		self.payload['components'].append({
			'type': 1,
			'components': [component]
		})

		self.fields.append(TextInput(component))

	async def send_modal(self, interaction: discord.Interaction):
		interaction.response._responded = True

		await self.adapter.create_interaction_response(
			interaction_id = interaction.id,
			token = interaction.token,
			session = interaction._session,
			data = self.payload,
			type = 9
		)

	async def wait(self, timeout=180):
		def custom_check(interaction: discord.Interaction):
			return interaction.data.get('custom_id') == self.custom_id

		# this is probaably a bad implementation but its working
		try:
			# wait for interaction with that match this modal instance custom_id
			interaction = await self.bot.wait_for('interaction', check=custom_check, timeout=timeout)
		except asyncio.TimeoutError:
			# return None if user didn't respond to the modal
			return None, []

		components = interaction.data['components']

		# match each result field with corresponding TextInput field
		result = []
		for component in components:
			for field in self.fields:
				if component['components'][0]['custom_id'] == field.custom_id:
					field.value = component['components'][0]['value']
					result.append(field)

		# returns modal interactions and list of TextInput filled.
		return interaction, result

	
		

	
