from collections import namedtuple
from jishaku.functools import executor_function
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageFont
from googletrans import LANGUAGES
from io import BytesIO


class TROCRError(Exception):
	...


Polygon = namedtuple('Polygon', ['x', 'y'])

class DataField:
	def __init__(self, img_size, data):
		self.img_size = img_size
		self.text = data['Text']
		bounding_box = data['Geometry']['BoundingBox']
		self.bounding_box = {
			'width': int(bounding_box['Width'] * img_size[0]),
			'height': int(bounding_box['Height'] * img_size[1]),
			'left': int(bounding_box['Left'] * img_size[0]),
			'top': int(bounding_box['Top'] * img_size[1]),
		}
		polygon = data['Geometry']['Polygon']
		self.polygon = [Polygon(int(poly['X'] * img_size[0]), int(poly['Y'] * img_size[1])) for poly in polygon]


class TROCR:
	font = ImageFont.truetype('/home/jeyy/Jeyy Bot/fonts/SourceHanSans-Bold.ttc', 50)
	def __init__(self, bot, translator, lang, image):
		self.bot = bot
		self.translator = translator
		self.lang = lang
		self.image = ImageOps.contain(Image.open(image), (1024, 1024))

	async def run(self):
		data = await self.get_data_pg()
		parsed_data = [DataField(self.image.size, dt) for dt in data['Blocks'] if dt['BlockType'] == 'LINE']
		await self.replace_text(parsed_data)

		buf = BytesIO()
		self.image.save(buf, 'PNG')
		buf.seek(0)

		return buf

	async def get_data_pg(self):
		buf = BytesIO()
		self.image.save(buf, 'PNG')
		buf.seek(0)

		image_url = await self.bot.upload_bytes(buf.getvalue(), 'image/png', 'trocr')
		r = await self.bot.session.post('https://api.openrobot.xyz/api/ocr/raw', headers={'Authorization': self.bot.keys('PROGUYKEY')}, params={'url': image_url})
		
		return await r.json()

	@executor_function
	def replace_text(self, data):
		for field in data:
			translated, source, destination = self.translate_func(self.lang, field.text)

			tl, tr, br, bl = field.polygon

			if tl.x >= br.x or tl.y >= br.y:
				raise TROCRError('invalid bounding box')

			crop_field = self.image.crop((tl.x, tl.y, br.x, br.y))
			blurred = crop_field.filter(ImageFilter.GaussianBlur(15))
			self.image.paste(blurred, (tl.x, tl.y))

			placeholder = Image.new('RGBA', (1024*5, 1024), (0, 0, 0, 0))
			draw = ImageDraw.Draw(placeholder)
			draw.text((placeholder.size[0]//2, 512), translated, 'white', self.font, 'mt', align='center', stroke_width=4, stroke_fill='black')
			
			bbox = placeholder.getbbox()
			cropped_placeholder = placeholder.crop((bbox[0]-2, bbox[1]-2, bbox[2]+2, bbox[3]+2))
			fit_field = cropped_placeholder.resize((field.bounding_box['width'], field.bounding_box['height']))
			
			self.image.paste(fit_field, (tl.x, tl.y), fit_field)

	def translate_func(self, dest, text):
		try:
			translation = self.translator.translate(text, dest=dest)
		except ValueError:
			return "Failed", "Language is not listed. Please check `j;translate languages` to see available codes", ""
		else:
			translated = translation.text
			source = LANGUAGES[translation.src.lower()]
			destination = LANGUAGES[translation.dest.lower()]
			
			return translated, source, destination

