from io import BytesIO
from dataclasses import dataclass

import aiohttp


@dataclass
class TranslateOCRResult:
    url: str
    original_text: str
    translated_text: str


class TROCRError(Exception):
	...


class TROCR:
	font = ImageFont.truetype('/home/jeyy/Jeyy Bot/fonts/SourceHanSans-Bold.ttc', 50)
	languages = []
	
	def __init__(self, bot, lang, image):
		self.bot = bot
		self.lang = lang
		self.image = ImageOps.contain(Image.open(image), (1024, 1024))

	async def run(self):
		langs = await self.get_languages()
		
		if self.lang not in langs:
			raise TROCRError(f"Invalid language: {self.lang}")
		
		data = await self.call_api()
		
		passed_data = {
            		'url': data['url'],
            		'original_text': data['originalText'],
            		'translated_text': data['translatedText']
        	}
		
		return TranslateOCRResult(**parsed_data)
	
	async def get_languages(self):
		if self.languages:
			return self.languages
		
		r = await self.bot.session.get('https://api.yodabot.xyz/api/translate-ocr/languages')
		data = await r.json()
		
		languages = data['supportedLanguages']
		
		self.languages = [x['code'] for x in languages]
		
		return self.languages

	async def call_api(self):
		buf = BytesIO()
		self.image.save(buf, 'PNG')
		buf.seek(0)
		
		data = aiohttp.FormData()
		data.add_field('image', buf, content_type='image/png')

		r = await self.bot.session.post('https://api.yodabot.xyz/api/translate-ocr/render', data=data, params={'lang': self.lang})
		
		return await r.json()
