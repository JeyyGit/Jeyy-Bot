from bisect import bisect_left
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageSequence, ImageOps, ImageEnhance, ImageChops
from colorthief import ColorThief
from glitch_this import ImageGlitcher
from imgaug import augmenters as iaa
from io import BytesIO
from jishaku.functools import executor_function
from os.path import basename, dirname
from skimage.transform import swirl
from textwrap import TextWrapper
from wand.image import Image as wImage
import albumentations as alb
from pyvista import examples
from pixelsort import pixelsort
import colorsys
import pyvista as pv
import imageio
import cv2
import datetime as dt
import glob
import math
import numpy as np
import os
import pymunk
import random
import re
import string
import textwrap
import time

from utils.useful import osc


if True:
	res = 300
	pv.global_theme.transparent_background = True
	cow_mesh = examples.download_cow().smooth()
	cube_mesh = pv.read("./models/cube.obj")
	wall_mesh = pv.read("./models/wall.obj")
	bed_mesh = pv.read("./models/bed.obj")
	glitcher = ImageGlitcher()
	grass = Image.open("./image/game/grass64x.png").convert('RGBA')
	water = Image.open("./image/game/water64x.png").convert('RGBA')
	sand = Image.open("./image/game/sand64x.png").convert('RGBA')
	stone = Image.open("./image/game/stone64x.png").convert('RGBA')
	plank = Image.open("./image/game/plank64x.png").convert('RGBA')
	glass = Image.open("./image/game/glass64x.png").convert('RGBA')
	red = Image.open("./image/game/red64x.png").convert('RGBA')
	iron = Image.open("./image/game/iron64x.png").convert('RGBA')
	brick = Image.open("./image/game/brick64x.png").convert('RGBA')
	gold = Image.open("./image/game/gold64x.png").convert('RGBA')
	pur = Image.open("./image/game/pur64x.png").convert('RGBA')
	leaf = Image.open("./image/game/leaf64x.png").convert('RGBA')
	log = Image.open("./image/game/log64x.png").convert('RGBA')
	coal = Image.open("./image/game/coal64x.png").convert('RGBA')
	dia = Image.open("./image/game/diamond64x.png").convert('RGBA')
	lava = Image.open("./image/game/lava64x.png").convert('RGBA')
	hay = Image.open("./image/game/hay64x.png").convert('RGBA')
	snowy = Image.open("./image/game/snowy64x.png").convert('RGBA')
	layer = Image.open("./image/game/layer64x.png").convert('RGBA')
	loff = Image.open("./image/game/lamp_off64x.png").convert('RGBA')
	lon = Image.open("./image/game/lamp_on64x.png").convert('RGBA')
	fence = Image.open("./image/game/fence64x.png").convert('RGBA')
	man = Image.open("./image/game/man.png").convert('RGBA')
	cake = Image.open("./image/game/cake64x.png").convert('RGBA')
	pop = Image.open("./image/game/poppy64x.png").convert('RGBA')
	lapis = Image.open("./image/game/lapis64x.png").convert('RGBA')
	wfull = Image.open("./image/game/water_full64x.png").convert('RGBA')
	lfull = Image.open("./image/game/lava_full64x.png").convert('RGBA')
	wfullmid = Image.open("./image/game/water_full_mid64x.png").convert('RGBA')
	lfullmid = Image.open("./image/game/lava_full_mid64x.png").convert('RGBA')
	wmid = Image.open("./image/game/water_mid64x.png").convert('RGBA')
	lmid = Image.open("./image/game/lava_mid64x.png").convert('RGBA')

	fenu = Image.open("./image/game/fence_u64x.png").convert('RGBA')
	fent = Image.open("./image/game/fence_t64x.png").convert('RGBA')
	fens = Image.open("./image/game/fence_s64x.png").convert('RGBA')
	fenb = Image.open("./image/game/fence_b64x.png").convert('RGBA')
	fenbu = Image.open("./image/game/fence_bu64x.png").convert('RGBA')
	fensb = Image.open("./image/game/fence_sb64x.png").convert('RGBA')
	fentb = Image.open("./image/game/fence_tb64x.png").convert('RGBA')
	fents = Image.open("./image/game/fence_ts64x.png").convert('RGBA')
	fentsb = Image.open("./image/game/fence_tsb64x.png").convert('RGBA')
	fenus = Image.open("./image/game/fence_us64x.png").convert('RGBA')
	fenusb = Image.open("./image/game/fence_usb64x.png").convert('RGBA')
	fenut = Image.open("./image/game/fence_ut64x.png").convert('RGBA')
	fenutb = Image.open("./image/game/fence_utb64x.png").convert('RGBA')
	fenuts = Image.open("./image/game/fence_uts64x.png").convert('RGBA')
	fenutsb = Image.open("./image/game/fence_utsb64x.png").convert('RGBA')

	won = Image.open("./image/game/wire_on64x.png").convert('RGBA')
	wonu = Image.open("./image/game/wire_on_u64x.png").convert('RGBA')
	wont = Image.open("./image/game/wire_on_t64x.png").convert('RGBA')
	wons = Image.open("./image/game/wire_on_s64x.png").convert('RGBA')
	wonb = Image.open("./image/game/wire_on_b64x.png").convert('RGBA')
	wonbu = Image.open("./image/game/wire_on_bu64x.png").convert('RGBA')
	wonsb = Image.open("./image/game/wire_on_sb64x.png").convert('RGBA')
	wontb = Image.open("./image/game/wire_on_tb64x.png").convert('RGBA')
	wonts = Image.open("./image/game/wire_on_ts64x.png").convert('RGBA')
	wontsb = Image.open("./image/game/wire_on_tsb64x.png").convert('RGBA')
	wonus = Image.open("./image/game/wire_on_us64x.png").convert('RGBA')
	wonusb = Image.open("./image/game/wire_on_usb64x.png").convert('RGBA')
	wonut = Image.open("./image/game/wire_on_ut64x.png").convert('RGBA')
	wonutb = Image.open("./image/game/wire_on_utb64x.png").convert('RGBA')
	wonuts = Image.open("./image/game/wire_on_uts64x.png").convert('RGBA')
	wonutsb = Image.open("./image/game/wire_on_utsb64x.png").convert('RGBA')

	woff = Image.open("./image/game/wire_off64x.png").convert('RGBA')
	woffu = Image.open("./image/game/wire_off_u64x.png").convert('RGBA')
	wofft = Image.open("./image/game/wire_off_t64x.png").convert('RGBA')
	woffs = Image.open("./image/game/wire_off_s64x.png").convert('RGBA')
	woffb = Image.open("./image/game/wire_off_b64x.png").convert('RGBA')
	woffbu = Image.open("./image/game/wire_off_bu64x.png").convert('RGBA')
	woffsb = Image.open("./image/game/wire_off_sb64x.png").convert('RGBA')
	wofftb = Image.open("./image/game/wire_off_tb64x.png").convert('RGBA')
	woffts = Image.open("./image/game/wire_off_ts64x.png").convert('RGBA')
	wofftsb = Image.open("./image/game/wire_off_tsb64x.png").convert('RGBA')
	woffus = Image.open("./image/game/wire_off_us64x.png").convert('RGBA')
	woffusb = Image.open("./image/game/wire_off_usb64x.png").convert('RGBA')
	woffut = Image.open("./image/game/wire_off_ut64x.png").convert('RGBA')
	woffutb = Image.open("./image/game/wire_off_utb64x.png").convert('RGBA')
	woffuts = Image.open("./image/game/wire_off_uts64x.png").convert('RGBA')
	woffutsb = Image.open("./image/game/wire_off_utsb64x.png").convert('RGBA')

	leoff = Image.open("./image/game/lever_off64x.png").convert('RGBA')
	leon = Image.open("./image/game/lever_on64x.png").convert('RGBA')

	selector_back = Image.open("./image/game/selector_back.png").convert('RGBA')
	selector_front = Image.open("./image/game/selector_front.png").convert('RGBA')

	hands = [Image.open(f"./image/pat/{i}.png") for i in range(1, 6)]
	news = Image.open("./image/newspaper.png")
	mcmap = Image.open("./image/mcmap.png")
	why_gif = Image.open("./image/why.gif")
	scream_gif = Image.open("./image/scream.gif")
	man_gif = Image.open("./image/eugh.gif")
	elmo_gif = Image.open("./image/flamingelmo.gif")
	jail_gif = Image.open("./image/hornijail.gif")
	bomb_gif = Image.open("./image/bomb2.gif")
	math_gif = Image.open("./image/trans-eq.gif")
	buffer_gif = Image.open("./image/buffering.gif")
	explicit_png = Image.open("./image/explicit.png").resize((600, 600))
	tvt = ImageOps.contain(Image.open("./image/tvt.png"), (400, 400)).convert('RGBA')
	balleye = Image.open("./image/balleye.png").convert('RGBA')
	lup = Image.open("./image/lup.png").resize((200, 200))
	prt = Image.open("./image/printer2.gif")
	phone_gif = Image.open("./image/phone_girl.gif")
	sensitive = Image.open("./image/sensitive.png").resize((400, 400)).convert('RGBA')
	ads = Image.open('./image/ads.png').convert('RGBA').resize((400, 400))
	toilet_img = Image.open("./image/toilet.png").convert('RGBA')

	shot_street = Image.open("./image/shot/street.jpg").resize((400, 400)).convert('RGBA')
	shot_gun = ImageOps.fit(Image.open("./image/shot/gun.png"), (250, 250)).convert('RGBA')
	shot_wound = ImageOps.fit(Image.open("./image/shot/wound.png"), (50, 50)).convert('RGBA')
	shot_heaven = Image.open("./image/shot/heaven.jpg").resize((400, 400)).convert('RGBA')
	shot_hell = Image.open("./image/shot/hell.jpg").resize((400, 400)).convert('RGBA')

	fan_img = Image.open("./image/fan.png").resize((400, 400)).convert('RGBA')
	warm_palette = Image.open("./image/warm_palette.png").convert('RGBA')
	brush_mask = Image.open("./image/brush_mask.gif")
	flare_img = Image.open("./image/flare.png").resize((50, 50)).convert('RGBA')
	kanye_img = Image.open("./image/kanye.png").convert('RGBA')

	wheel_images = {
		'wheel_2' : [Image.open(f"./image/wheel/wheel_2/frame ({i+1}).png") for i in range(len(os.listdir("./image/wheel/wheel_2"))-1)],
		'wheel_3' : [Image.open(f"./image/wheel/wheel_3/frame ({i+1}).png") for i in range(len(os.listdir("./image/wheel/wheel_3"))-1)],
		'wheel_4' : [Image.open(f"./image/wheel/wheel_4/frame ({i+1}).png") for i in range(len(os.listdir("./image/wheel/wheel_4"))-1)],
		'wheel_6' : [Image.open(f"./image/wheel/wheel_6/frame ({i+1}).png") for i in range(len(os.listdir("./image/wheel/wheel_6"))-1)],
	}

	scrap_letters = {}
	for img_dir in glob.glob("./image/letters/*/*"):
		scrap_letters.setdefault(basename(dirname(img_dir)), []).append(Image.open(img_dir))

	codes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'g', 'p', 'l', 'o', 'c', 'd', 'v', 'h', 's', 'k', 'y', 'r', 'b', '%', 'f', 'w', '$', 'e', '#',
	'┌', '┐', '└', '┘', '│', '─', '┬', '┤', '┴', '├', '┼', '╌', '╎', '╍', '╏', '┏', '┓', '┗', '┛', '┃', '━', '┳', '┫', '┻', '┣', '╋', '┄', '┆', '┅', '┇',
	'╔' , '╗', '╚', '╝', '║', '═', '╩', '╠', '╦', '╣', '╬', '╴', '╶', '╵', '╷', '░', '▒', '▓', '█', '∙', '·']

	codeses = codes.copy()
	codeses.extend([' ', '-', '0', 'x', '\n', '[', ']'])

	code_dict = {
		'1': grass,
		'2': water,
		'3': sand,
		'4': stone,
		'5': plank,
		'6': glass,
		'7': red,
		'8': iron, 
		'9': brick,
		'g': gold, 
		'p': pur,
		'l': leaf,
		'o': log, 
		'c': coal, 
		'd': dia, 
		'v': lava, 
		'h': hay, 
		's': layer, 
		'k': cake,
		'y': pop,
		'r': loff, 
		'b': lapis,
		'%': lon, 
		'f': fence, 
		'w': woff, 
		'$': won, 
		'e': leoff, 
		'#': leon,
		'┌': woffut,
		'┐': woffts, 
		'└': woffbu,
		'┘': woffsb,
		'│': wofftb,
		'─': woffus,
		'┬': woffuts,
		'┤': wofftsb,
		'┴': woffusb, 
		'├': woffutb,
		'┼': woffutsb,
		'╌': woffu,
		'╎': wofft,
		'╍': woffs,
		'╏': woffb,
		'┏': wonut, 
		'┓': wonts,
		'┗': wonbu, 
		'┛': wonsb, 
		'┃': wontb, 
		'━': wonus, 
		'┳': wonuts, 
		'┫': wontsb, 
		'┻': wonusb, 
		'┣': wonutb, 
		'╋': wonutsb, 
		'┄': wonu, 
		'┆': wont, 
		'┅': wons, 
		'┇': wonb, 
		'╔': fenut, 
		'╗': fents, 
		'╚': fenbu, 
		'╝': fensb, 
		'║': fentb, 
		'═': fenus, 
		'╦': fenuts, 
		'╣': fentsb, 
		'╩': fenusb, 
		'╠': fenutb, 
		'╬': fenutsb, 
		'╶': fenu,
		'╷': fent,
		'╴': fens,
		'╵': fenb,
		'░': wfull,
		'▒': lfull,
		'▓': wfullmid, 
		'∙': wmid, 
		'█': lfullmid, 
		'·': lmid
	}

	letters = {
		' ': '0',
		"'": '11',
		'"': '11 0 11',
		'<': '10001 0101 001',
		'>': '001 0101 10001',
		':': '0101',
		';': '0101 00001',
		',': '0001 00001',
		'.': '00001',
		'-': '001 001 001',
		'+': '001 0111 001',
		'=': '0101 0101 0101',
		'_': '00001 00001 00001',
		'^': '01 1 01',
		'!': '11101',
		'?': '011 100101 1',
		'#': '0101 11111 0101 11111 0101',
		'%': '10001 01 001 0001 10001',
		')': '0111 10001',
		'(': '10001 0111',
		'\\':'00001 0001 001 01 1',
		'/': '1 01 001 0001 00001',
		'*': '101 01 101',
		'@': '01111 1 10111 10001 0111',
		'~': '01 1 01 1',
		']': '11111 10001',
		'[': '10001 11111',
		'}': '001 0111 10001',
		'{': '10001 0111 001',
		'a': '01111 10100 01111', 
		'b': '0101 10101 11111', 
		'c': '10001 10001 11111',
		'd': '0111 10001 11111',
		'e': '10101 10101 11111',
		'f': '101 101 11111',
		'g': '0011 10101 10001 0111',
		'h': '11111 001 11111',
		'i': '10001 11111 10001',
		'j': '11111 10001 10001 1001',
		'k': '10001 0101 001 11111',
		'l': '00001 00001 11111',
		'm': '11111 01 001 01 11111',
		'n': '11111 0001 001 01 11111',
		'o': '0111 10001 10001 0111',
		'p': '111 101 11111',
		'q': '00001 1111 1001 1111',
		'r': '11011 101 11111',
		's': '1011 10101 01101',
		't': '1 11111 1',
		'u': '11111 00001 11111',
		'v': '111 0001 00001 0001 111', 
		'w': '1111 00001 0111 00001 1111',
		'x': '10001 0101 001 0101 10001', 
		'y': '1 01 00111 01 1' , 
		'z': '10001 11001 10101 10011 10001',
		'0': '11111 10001 11111',
		'1': '00001 11111 10001',
		'2': '11101 10101 10111',
		'3': '11111 10101 10101',
		'4': '11111 001 111',
		'5': '10111 10101 11101',
		'6': '10111 10101 11111',
		'7': '11111 1 1',
		'8': '11111 10101 11111',
		'9': '11111 10101 11101'
	}

	golf_grass = Image.open("./image/golf/grass.png").convert("RGBA")
	golf_stone = Image.open("./image/golf/stone.png").convert("RGBA")
	golf_degrees = Image.open("./image/golf/degrees.png").convert("RGBA").resize((100, 100))
	golf_flag = Image.open("./image/golf/flag.png").convert("RGBA")
	font_arial = ImageFont.truetype("./image/arial.ttf", 24)
	font_arial2 = ImageFont.truetype("./image/arial.ttf", 12)
	font_arial3 = ImageFont.truetype("./image/arial.ttf", 20)
	font_arial4 = ImageFont.truetype("./image/arial.ttf", 60)

	red_carpet = Image.open('./image/redcarpet.png').convert('RGBA')
	flashes = Image.open('./image/Paparazzi_flashes.gif')

	heart_imgs = [Image.open(f'./image/hearts/heart_{i}.png').convert('RGBA') for i in range(7)]

	ace_asset = {
		'court': {
			'bg_l': Image.open('./image/ace/court_bg_left.jpg').convert('RGBA'),
			'bg_r': Image.open('./image/ace/court_bg_right.jpg').convert('RGBA'),
			'desk_l': Image.open('./image/ace/desk_left.png'),
			'desk_r': Image.open('./image/ace/desk_right.png'),
		},
		'wright': [
			{'talk':Image.open('./image/ace/wright_1.gif'), 'normal': Image.open('./image/ace/wright_normal_1.png').convert('RGBA')},
			{'talk':Image.open('./image/ace/wright_2.gif'), 'normal': Image.open('./image/ace/wright_normal_2.png').convert('RGBA')},
			{'talk':Image.open('./image/ace/wright_3.gif'), 'normal': Image.open('./image/ace/wright_normal_3.png').convert('RGBA')},
			{'talk':Image.open('./image/ace/wright_4.gif'), 'normal': Image.open('./image/ace/wright_normal_4.png').convert('RGBA')},
			{'talk':Image.open('./image/ace/wright_5.gif'), 'normal': Image.open('./image/ace/wright_normal_5.png').convert('RGBA')},
			{'talk':Image.open('./image/ace/wright_6.gif'), 'normal': Image.open('./image/ace/wright_normal_6.png').convert('RGBA')},
			{'talk':Image.open('./image/ace/wright_7.gif'), 'normal': Image.open('./image/ace/wright_normal_7.png').convert('RGBA')},
			{'talk':Image.open('./image/ace/wright_8.gif'), 'normal': Image.open('./image/ace/wright_normal_8.png').convert('RGBA')},
		],
		'miles': [
			{'talk': Image.open('./image/ace/miles_1.gif'), 'normal': Image.open('./image/ace/miles_normal_1.png').convert('RGBA')},
			{'talk': Image.open('./image/ace/miles_2.gif'), 'normal': Image.open('./image/ace/miles_normal_2.png').convert('RGBA')},
			{'talk': Image.open('./image/ace/miles_3.gif'), 'normal': Image.open('./image/ace/miles_normal_3.png').convert('RGBA')},
			{'talk': Image.open('./image/ace/miles_4.gif'), 'normal': Image.open('./image/ace/miles_normal_4.png').convert('RGBA')},
			{'talk': Image.open('./image/ace/miles_5.gif'), 'normal': Image.open('./image/ace/miles_normal_5.png').convert('RGBA')},
			{'talk': Image.open('./image/ace/miles_6.gif'), 'normal': Image.open('./image/ace/miles_normal_6.png').convert('RGBA')},
			{'talk': Image.open('./image/ace/miles_7.gif'), 'normal': Image.open('./image/ace/miles_normal_7.png').convert('RGBA')},
		]
	}

	creeps = [Image.open(path).convert('RGBA').resize((400, 400)) for path in glob.glob('./image/creepy/*')]

	ytgif = Image.open('./image/ytgif.gif')
	roboto_reg = ImageFont.truetype('./image/Roboto-Regular.ttf', 30)
	roboto_lig = ImageFont.truetype('./image/Roboto-Light.ttf', 25)

	sfontbold = ImageFont.truetype('./image/GothamBold.ttf', 70)
	sfont = ImageFont.truetype('./image/GothamMedium.ttf', 50)
	tfont = ImageFont.truetype('./image/GothamMedium.ttf', 80)
	mfont = ImageFont.truetype('./image/nk57-monospace-no-eb.ttf', 10)
	
	sfont_title = ImageFont.truetype('./fonts/SourceHanSans-Bold.ttc', 60)
	sfont_auth = ImageFont.truetype('./fonts/SourceHanSans-Bold.ttc', 50)

	wordle_font = ImageFont.truetype('./image/Roboto-Medium.ttf', 90)
	wordle_key = ImageFont.truetype('./image/Roboto-Medium.ttf', 20)

	ace_name_font = ImageFont.truetype('./image/arial.ttf', 25)
	ace_text_font = ImageFont.truetype('./image/arial.ttf', 20)

	player_bold_60 = ImageFont.truetype('./image/NotoSans-Bold.ttf', 60)
	player_bold_40 = ImageFont.truetype('./image/NotoSans-Bold.ttf', 40)
	player_reg = ImageFont.truetype('./image/NotoSans-Regular.ttf', 40)

	wstat_reg = ImageFont.truetype('./image/NotoSans-Regular.ttf', 20)
	wstat_bold_20 = ImageFont.truetype('./image/NotoSans-Bold.ttf', 20)
	wstat_bold_30 = ImageFont.truetype('./image/NotoSans-Bold.ttf', 30)


class Ball:
	def __init__(self, x, y, r, color, collision_type):
		self.r = r
		self.body = pymunk.Body()
		self.shape = pymunk.Circle(self.body, self.r)
		self.body.position = x, y
		self.body.velocity = random.uniform(-5, 5), random.uniform(-5, 5)
		self.shape.density = 10
		self.shape.elasticity = 1
		self.shape.collision_type = collision_type
		self.color = color

	def collided(self, arbiter, space, data):
		self.shape.collision_type = 1000
		return True

	def draw(self, draw):
		xb, yb = self.body.position
		draw.ellipse((xb-self.r, res-yb-self.r, xb+self.r, res-yb+self.r), fill=self.color, outline=self.color)

class Wall:
	def __init__(self, x0, y0, x1, y1):
		self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
		self.shape = pymunk.Segment(self.body, (x0, y0), (x1, y1), 10)
		# self.shape.density = 1
		self.shape.elasticity = 0.1
		self.shape.collision_type = 1000

class PachiBall:
	def __init__(self, x, y, r, resx):
		self.r = r
		self.body = pymunk.Body()
		self.shape = pymunk.Circle(self.body, self.r)
		self.body.position = x, y
		self.body.velocity = random.uniform(-2, 2), random.uniform(-2, 2)
		self.shape.density = 100
		self.shape.elasticity = 0.3
		self.shape.friction = 0.63
		self.color = 'green'
		self.resx = resx
		self.resy = self.resx * 2

	def draw(self, drawing):
		xb, yb = self.body.position
		drawing.ellipse((1*(xb-self.r), 1*(self.resy+yb-self.r), xb+self.r, self.resy-yb+self.r), fill=self.color, outline=self.color)

class PachiPeg:
	def __init__(self, x, y, r, resx):
		self.r = r
		self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
		self.shape = pymunk.Circle(self.body, self.r)
		self.body.position = x, y
		self.shape.elasticity = 0.3
		self.color = 'red'
		self.resx = resx
		self.resy = self.resx * 2

	def draw(self, drawing):
		xb, yb = self.body.position
		drawing.ellipse((xb-self.r, self.resy-yb-self.r, xb+self.r, self.resy-yb+self.r), fill=self.color, outline=self.color)

class GolfBall(Ball):
	def __init__(self, x, y, r, color, collision_type):
		super().__init__(x, y, r, color, collision_type)
		self.shape.density = 1
		self.shape.elasticity = 1

	def update(self, draw, offset):
		self.draw(draw, offset)
		direction, speed = self.body.velocity.normalized_and_length()
		self.body.apply_impulse_at_world_point(speed * 20 * -direction, self.body.position)
		self.body.angular_velocity *= 0.5

	def draw(self, draw, offset):
		xb, yb = self.body.position
		draw.ellipse((xb-self.r, offset+res-yb-self.r, xb+self.r, offset+res-yb+self.r), fill=self.color, outline='black')

class GolfWall:
	def __init__(self, x0, y0, x1, y1, r=20, plane='horizontal'):
		self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
		self.shape = pymunk.Segment(self.body, (x0, y0), (x1, y1), r)
		self.x0 = x0
		self.y0 = y0
		self.x1 = x1
		self.y1 = y1
		self.r = r
		self.plane = plane
		self.shape.elasticity = 1

	def draw(self, draw):
		x0, y0 = self.shape.a
		x1, y1 = self.shape.b
		if self.plane == 'horizontal':
			draw.line([x0-self.r, res-y0, x1+self.r, res-y1], fill='white', width=self.r*2, joint='curve')
		else:
			draw.line([x0, res-y0-self.r, x1, res-y1+self.r], fill='white', width=self.r*2, joint='curve')

class Heart:
	def __init__(self, xy, velocity, r, heart_img):
		self.x = xy[0]
		self.y = xy[1]
		self.velocity = velocity
		self.r = r
		self.heart_img = heart_img

	def draw(self, image):
		x, y = map(int, (self.x, self.y))
		image.paste(self.heart_img, (x, y), self.heart_img)

	def update(self, image):
		self.x += self.velocity[0]
		self.y += self.velocity[1]
		self.draw(image)

class Circle:
		def __init__(self, x, y, c):
			self.x = x
			self.y = y
			self.c = c
			self.r = 0
			self.growing = True

		def grow(self):
			if self.growing:
				self.r += 1

		def draw(self, drawing):
			center = (self.x-self.r, self.y-self.r, self.x+self.r, self.y+self.r)
			drawing.ellipse(center, self.c)

		def dist(self, other):
			return math.dist([self.x, self.y], [other.x, other.y])

class ClothBall:
	def __init__(self, x, y, r, c):
		self.body = pymunk.Body()
		self.body.position = x, y
		self.body.velocity = random.uniform(-5, 5), random.uniform(-5, 5)
		self.r = r
		self.shape = pymunk.Circle(self.body, r)
		self.shape.density = 1
		self.shape.elasticity = 1
		self.c = c

	def draw(self, drawing):
		xb, yb = self.body.position
		drawing.ellipse((xb-self.r, 300-yb-self.r, xb+self.r, 300-yb+self.r), self.c)

class String:
	def __init__(self, body_1, attachment, identifier='body'):
		self.body_1 = body_1
		if identifier == 'body':
			self.body_2 = attachment
		elif identifier == 'position':
			self.body_2 = pymunk.Body(body_type=pymunk.Body.STATIC)
			self.body_2.position = attachment
		self.joint = pymunk.PinJoint(self.body_1, self.body_2)

	def draw(self, drawing):
		pos_1 = (self.body_1.position[0], 300-self.body_1.position[1])
		pos_2 = (self.body_2.position[0], 300-self.body_2.position[1])
		drawing.line([pos_1, pos_2], 'black')


#
# Fun
# #
@executor_function
def golf_func(posx, posy, degree, power, ranges, _map, strokes):
	space = pymunk.Space()
	FPS = 60
	offset = 100
	degree = degree % 360

	velx = power * math.cos(math.radians(degree)) * 100
	vely = power * math.sin(math.radians(degree)) * 100
	finx, finy = _map.finish
	
	ball = GolfBall(posx, posy, 10, 'white', 1)
	ball.body.velocity = velx, vely
	
	walls = [
		GolfWall(0, 0, 0, res, 20, plane='vertical'),
		GolfWall(0, 0, res, 0, 20),
		GolfWall(res, 0, res, res, 20, plane='vertical'),
		GolfWall(0, res, res, res, 20),
	]

	for wall in _map.walls:
		walls.append(GolfWall(*wall))

	wall_canvas = Image.new('RGBA', (300, 300))
	wall_draw = ImageDraw.Draw(wall_canvas)

	for wall in walls:
		wall.draw(wall_draw)
		space.add(wall.body, wall.shape)
	
	wall_canvas = wall_canvas.convert('L')
	board_canvas = Image.new('RGBA', (300, 300))
	board_canvas.paste(golf_stone, (0, 0), wall_canvas)

	space.add(ball.body, ball.shape)

	screen = Image.new('RGBA', (res, res+offset), 'white')
	screen.paste(golf_grass.resize((res, res)), (0, offset))
	screen.paste(board_canvas, (0, offset), board_canvas)
	bar = Image.new("RGBA", (power*5, 20), 'red')
	screen.paste(bar, (170, 55), bar)
	draw = ImageDraw.Draw(screen)

	draw.ellipse((finx-15, offset+res-finy-15, finx+15, offset+res-finy+15), fill=(77, 52, 32), outline='black')
	draw.text((15, 20), f"Degree : {degree}°", 'black', font=font_arial)
	draw.text((170, 20), f"Power : {power}", 'black', font=font_arial)
	draw.text((15, 60), f"Stroke{['', 's'][strokes>1]} : {strokes}", 'black', font=font_arial)
	draw.text((167, 80), f"0    5    10    15    20", 'black', font=font_arial2)

	durations = [1000]
	frames = []
	for _ in range(ranges):
		screen2 = screen.copy()
		drawing = ImageDraw.Draw(screen2)

		ball.update(drawing, offset)
		screen2.paste(golf_degrees, (20, offset+20), golf_degrees)
		screen2.paste(golf_flag, (finx-15, offset+res-finy-25), golf_flag)
		durations.append(FPS)

		space.step(1/FPS)
		
		fobj = BytesIO()
		screen2.save(fobj, "GIF")
		screen2 = Image.open(fobj)
		frames.append(screen2)
	
	endx, endy = ball.body.position
	durations.pop()
	
	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=durations, disposal=2)
	igif.seek(0)

	return igif, endx, endy

def isometric_func(shape, selector_pos=None):
	"""Creates static isometric drawing"""
	t = 4
	resx = resy = 1024*5
	canvas = Image.new('RGBA', (resx, resy), (25, 25, 25, 0))

	shape = list(shape)
	mid = round(resx/2)

	i = j = lvl = count = 0
	for row in shape:
		for val in row:
			fx = mid + j*t*7 - i*t*7
			fy = mid + j*t*4 + i*t*4 - lvl*t*7
			# fx = mid + j*t*7 - i*t*7
			# fy = mid + j*t*6 + i*t*6 - lvl*t*7

			selected = False
			if [lvl, i, j] == selector_pos:
				canvas.paste(selector_back, (fx, fy),selector_back)
				selected = True

			if (img := code_dict.get(val)):
				canvas.paste(img, (fx, fy), img)

			if selected:
				canvas.paste(selector_front, (fx, fy), selector_front)
			
			j += 1
			if val == "-":
				i = -1
				j = 0
				lvl += 1

			if val in codes or selected:
				count += 1
		j = 0
		i += 1

	if count == 0:
		return 1, count

	canvasBox = canvas.getbbox()
	crop = canvas.crop(canvasBox)
	buf = BytesIO()
	crop.save(buf, "PNG")
	buf.seek(0)
	return buf, count

@executor_function
def isometric_gif_func(shape, loop):
	"""Creates gif isometric drawing"""
	t = 4
	frames = []
	resx = resy = 1024*5
	
	canvas = Image.new("RGB", [resx, resy], 'black')
	newcanvas = Image.new("RGB", [resx, resy], 'white')

	shape = list(shape)
	mid = round(resx/2)
	if shape[0].startswith("`"):
		shape.remove(shape[0])
		shape.pop()

	i = j = lvl = count = 0
	for row in shape:
		for val in row:
			fx = mid + j*t*7 - i*t*7
			fy = mid + j*t*4 + i*t*4 - lvl*t*7

			if (img := code_dict.get(val)):
				canvas.paste(img, (fx, fy), img)

			j += 1
			if val == "-":
				i = -1
				j = 0
				lvl += 1

			if val in codes:
				count += 1

		j = 0
		i += 1

	if count > 1000:
		return True, count
	if count == 0:
		return 1, count
	
	i = j = lvl = 0
	durations = []

	canvasBox = canvas.getbbox()

	if len(shape) == 1:
		canvCrop = newcanvas.crop(canvasBox)
		fobj = BytesIO()
		canvCrop.save(fobj, "GIF", transparency=0)
		canvCrop = Image.open(fobj)
		frames.append(canvCrop)

		durations.append(150)

	start = time.time()
	try:
		for row in shape:
			for val in row:
				end = time.time()
				if end-start > 20:
					raise Exception()

				fx = mid + j*t*7 - i*t*7
				fy = mid + j*t*4 + i*t*4 - lvl*t*7

				if (img := code_dict.get(val)):
					newcanvas.paste(img, (fx, fy), img)
				
				if val in codes:
					canvCrop = newcanvas.crop(canvasBox)
					fobj = BytesIO()
					canvCrop.save(fobj, "GIF", transparency=0)
					canvCrop = Image.open(fobj)
					frames.append(canvCrop)

					durations.append(150)

				j += 1
				if val == "-":
					i = -1
					j = 0
					lvl += 1

			j = 0
			i += 1
	except Exception:
		return None, None

	durations[-1] = 400
	
	igif = BytesIO()
	if loop.isnumeric():
		loop = int(loop)
		if 0 < loop <= 30:
			frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=durations, loop=loop)
		else:
			frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=durations, loop=0)
	else:
		frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=durations, disposal=0)

	igif.seek(0)
	return igif, count

@executor_function
def land(x, y):
	"""Creates square shaped isometric drawing"""
	t = 4
	resx = x*t*14+9*t
	resy = y*t*4+12*t
	grass = Image.open("./image/game/grass64x.png")
	canvas = Image.new('RGBA', (resx, resy), (25, 25, 25, 0))
	for i in range(y):
		for j in range(x):
			r = random.choice(list(range(-7, 8)))
			if i % 2 == 0:
				canvas.paste(grass, (j*t*14, i*t*4+r), grass)
			else:
				canvas.paste(grass, (j*t*14+7*t, i*t*4+r), grass)

	buf = BytesIO()
	canvas.save(buf, "PNG")
	buf.seek(0)

	return buf

@executor_function
def lever_gif(img1, img2):
	"""Animates isometric drawings with levers"""
	img1 = Image.open(img1).convert("RGBA")
	img2 = Image.open(img2).convert("RGBA")

	frames = []
	fobj = BytesIO()
	img1.save(fobj, "GIF", transparency=0)
	img1 = Image.open(fobj)
	frames.append(img1)
	fobj = BytesIO()
	img2.save(fobj, "GIF", transparency=0)
	img2 = Image.open(fobj)
	frames.append(img2)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=500, loop=0, disposal=2)
	igif.seek(0)

	return igif

def img_to_iso(image, best):
	with Image.open(image) as image4:
		im = image4.resize((best, best)).convert("RGBA")
		im = ImageOps.mirror(im)
		h = []
		x = 0

		dat = [
			(67, 54, 35), (33, 149, 243), (240, 233, 179), (69, 90, 100), (188, 152, 98), 
			(94, 174, 174), (227, 37, 12), (230, 230, 230), (150, 83, 68), (255, 237, 76), 
			(174, 125, 174), (61, 132, 41), (109, 76, 65), (8, 8, 8), (175, 253, 236), 
			(219, 130, 46), (196, 172, 15), (170, 117, 83), (246, 219, 180)
		]

		dat2 = "123456789gplocdvhr%"

		data = list(im.getdata())

		data = reversed(data)

		for p in data:
			x += 1
			p = list(p)

			def myFunc(e):
				r = p[0]
				g = p[1]
				b = p[2]

				er = e[0]
				eg = e[1]
				eb = e[2]

				return abs(r - er) + abs(g - eg) + abs(b - eb)

			if p[3] < 5:
				h.append("0")
			else:
				newlis = dat.copy()
				newlis.sort(key=myFunc)
				h.append(dat2[dat.index(newlis[0])])

			if x % im.width == 0:
				h.append("-")

		text = ''.join(h)

		return text

@executor_function
def gif_to_iso(image):
	img = Image.open(image)
	duration = img.info['duration']

	frames = []
	for frame in ImageSequence.Iterator(img):
		frame = frame.convert("RGBA")
		buf = BytesIO()
		frame.save(buf, 'PNG')
		buf.seek(0)
		code = img_to_iso(buf, 40)
		new_frame, count = isometric_func(code)
		with Image.open(new_frame) as new_frame:
			fobj = BytesIO()
			new_frame.save(fobj, "GIF", transparency=0)
			new_frame = Image.open(fobj)
			frames.append(new_frame)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=duration, loop=0, disposal=2)
	igif.seek(0)

	return igif

def logic(blocks):
	blocks = blocks.replace("\n", " ")
	blocks = blocks.strip()
	blocks = re.sub(" +", ' ', blocks)

	arr = [[[]]]
	i, j= 0, 0
	for c in blocks:
		if c not in [' ', '-']:
			arr[i][j].append(c)

		if c == ' ':
			arr[i].append([])
			j += 1

		if c == '-':
			arr.append([[]])
			i += 1
			j = 0

	arr = [list(filter(lambda x: x != [], lay)) for lay in arr]

	for i, lay in enumerate(arr):
		for j, row in enumerate(lay):
			for k, el in enumerate(row):
				if el == 'r':
					a = []
					if i-1 >= 0:
						try:
							a.append(arr[i-1][j][k])
						except IndexError:
							pass
					try:
						a.append(arr[i+1][j][k])
					except IndexError:
						pass
					if j-1 >= 0:
						try:
							a.append(arr[i][j-1][k])
						except IndexError:
							pass
					try:
						a.append(arr[i][j+1][k])
					except IndexError:
						pass
					if k-1 >= 0:
						try:
							a.append(arr[i][j][k-1])
						except IndexError:
							pass
					try:
						a.append(arr[i][j][k+1])
					except IndexError:
						pass

					if any(c in ['$', '7', '┏', '┓', '┗', '┛', '┃', '━', '┳', '┫', '┻', '┣', '╋', '┄', '┆', '┅', '┇', '#'] for c in a):
						arr[i][j][k] = '%'

	res = '- '.join([' '.join([''.join(row) for row in lay]) for lay in arr])
	res = res.strip()
	res = re.sub(" +", ' ', res)

	return res

def wires(blocks):
	blocks = blocks.replace("\n", " ")
	blocks = blocks.strip()
	blocks = re.sub(" +", ' ', blocks)

	arr = [[[]]]
	i, j= 0, 0
	for c in blocks:
		if c not in [' ', '-']:
			arr[i][j].append(c)

		if c == ' ':
			arr[i].append([])
			j += 1

		if c == '-':
			arr.append([[]])
			i += 1
			j = 0

	arr = [list(filter(lambda x: x != [], lay)) for lay in arr]
	
	while True:
		c = '-'
		for i, lay in enumerate(arr):
			for j, row in enumerate(lay):
				for k, el in enumerate(row):
					if el == '7' or el == '$' or el == '#':
						if i-1 >= 0:
							try:
								if arr[i-1][j][k] == 'w':
									arr[i-1][j][k] = '$'
									c += 'a'
							except IndexError:
								pass
						try:
							if arr[i+1][j][k] == 'w':
								arr[i+1][j][k] = '$'
								c += 'b'
						except IndexError:
							pass
						if j-1 >= 0:
							try:
								if arr[i][j-1][k] == 'w':
									arr[i][j-1][k] = '$'
									c += 'c'
							except IndexError:
								pass
						try:
							if arr[i][j+1][k] == 'w':
								arr[i][j+1][k] = '$'
								c += 'd'
						except IndexError:
							pass
						if k-1 >= 0:
							try:
								if arr[i][j][k-1] == 'w':
									arr[i][j][k-1] = '$'
									c += 'e'
							except IndexError:
								pass
						try:
							if arr[i][j][k+1] == 'w':
								arr[i][j][k+1] = '$'
								c += 'f'
						except IndexError:
							pass
						if i-1 >= 0 and j-1 > 0:
							try:
								if arr[i-1][j-1][k] == 'w':
									arr[i-1][j-1][k] = '$'
									c += 'g'
							except IndexError:
								pass
						if j-1 >= 0:
							try:
								if arr[i+1][j-1][k] == 'w':
									arr[i+1][j-1][k] = '$'
									c += 'h'
							except IndexError:
								pass
						if i-1 >= 0:
							try:
								if arr[i-1][j+1][k] == 'w':
									arr[i-1][j+1][k] = '$'
									c += 'i'
							except IndexError:
								pass
						try:
							if arr[i+1][j+1][k] == 'w':
								arr[i+1][j+1][k] = '$'
								c += 'j'
						except IndexError:
							pass
						if k-1 >= 0:
							try:
								if arr[i+1][j][k-1] == 'w':
									arr[i+1][j][k-1] = '$'
									c += 'k'
							except IndexError:
								pass
						if i-1 > 0:
							try:
								if arr[i-1][j][k-1] == 'w':
									arr[i-1][j][k-1] = '$'
									c += 'l'
							except IndexError:
								pass
						try:
							if arr[i+1][j][k+1] == 'w':
								arr[i+1][j][k+1] = '$'
								c += 'm'
						except IndexError:
							pass
						if i-1 >= 0:
							try:
								if arr[i-1][j][k+1] == 'w':
									arr[i-1][j][k+1] = '$'
									c += 'n'
							except IndexError:
								pass

		if c == '-':
			break
	
	wire_offs = ['w', 'r', '┌', '┐', '└', '┘', '│', '─', '┬', '┤', '┴', '├', '┼', '╌', '╎', '╍', '╏', 'e']
	wire_ons = ['$', '7', 'r', '┏', '┓', '┗', '┛', '┃', '━', '┳', '┫', '┻', '┣', '╋', '┄', '┆', '┅', '┇', '#']
	for i, lay in enumerate(arr):
		for j, row in enumerate(lay):
			for k, el in enumerate(row):
				if el == 'w':
					direction = ''
					try:
						if arr[i][j][k+1] in wire_offs or arr[i+1][j][k+1] in wire_offs:
							direction += 'u'
					except IndexError:
						pass
					if i-1 >= 0:
						try:
							if arr[i-1][j][k+1] in wire_offs:
								if 'u' not in direction:
									direction += 'u'
						except IndexError:
							pass
					try:
						if arr[i][j+1][k] in wire_offs or arr[i+1][j+1][k] in wire_offs:
							direction += 't'
					except IndexError:
						pass
					if i-1 >= 0:
						try:
							if arr[i-1][j+1][k] in wire_offs:
								if 't' not in direction:
									direction += 't'
						except IndexError:
							pass
					if k-1 >= 0:
						try:
							if arr[i][j][k-1] in wire_offs or arr[i+1][j][k-1] in wire_offs:
								direction += 's'
						except IndexError:
							pass
						if i-1 >= 0:
							try:
								if arr[i-1][j][k-1] in wire_offs:
									if 's' not in direction:
										direction += 's'
							except IndexError:
								pass

					if j-1 >= 0:
						try:
							if arr[i][j-1][k] in wire_offs or arr[i+1][j-1][k] in wire_offs:
								direction += 'b'
						except IndexError:
							pass
						if i-1 >= 0:
							try:
								if arr[i-1][j-1][k] in wire_offs:
									if 'b' not in direction:
										direction += 'b'
							except IndexError:
								pass
					# '┌', '┐', '└', '┘', '│', '─', '┬', '┤', '┴', '├', '┼' ╌ ╎ ╍ ╏

					dire = {
						'u': '╌', 't': '╎', 's': '╍', 'b': '╏',
						'ub': '└', 'ut': '┌', 'ts': '┐', 'sb': '┘', 
						'tb': '│', 'us': '─', 'uts': '┬', 'tsb': '┤', 
						'usb': '┴', 'utb': '├', 'utsb': '┼'
					}

					for d in dire:
						if direction == d:
							arr[i][j][k] = dire[d]
							break

				if el == '$':
					direction = ''
					try:
						if arr[i][j][k+1] in wire_ons or arr[i+1][j][k+1] in wire_ons:
							direction += 'u'
					except IndexError:
						pass
					if i-1 >= 0:
						try:
							if arr[i-1][j][k+1] in wire_ons:
								if 'u' not in direction:
									direction += 'u'
						except IndexError:
							pass
					try:
						if arr[i][j+1][k] in wire_ons or arr[i+1][j+1][k] in wire_ons:
							direction += 't'
					except IndexError:
						pass
					if i-1 >= 0:
						try:
							if arr[i-1][j+1][k] in wire_ons:
								if 't' not in direction:
									direction += 't'
						except IndexError:
							pass
					if k-1 >= 0:
						try:
							if arr[i][j][k-1] in wire_ons or arr[i+1][j][k-1] in wire_ons:
								direction += 's'
						except IndexError:
							pass
						if i-1 >= 0:
							try:
								if arr[i-1][j][k-1] in wire_ons:
									if 's' not in direction:
										direction += 's'
							except IndexError:
								pass

					if j-1 >= 0:
						try:
							if arr[i][j-1][k] in wire_ons or arr[i+1][j-1][k] in wire_ons:
								direction += 'b'
						except IndexError:
							pass
						if i-1 >= 0:
							try:
								if arr[i-1][j-1][k] in wire_ons:
									if 'b' not in direction:
										direction += 'b'
							except IndexError:
								pass
					# , '┏', '┓', '┗', '┛', '┃', '━', '┳', '┫', '┻', '┣', '╋', '┄', '┆', '┅', '┇'
					
					dire = {
						'u': '┄', 't': '┆', 's': '┅', 'b': '┇',
						'ub': '┗', 'ut': '┏', 'ts': '┓', 'sb': '┛',
						'tb': '┃', 'us': '━', 'uts': '┳', 'tsb': '┫',
						'usb': '┻', 'utb': '┣', 'utsb': '╋'
					}
					
					for d in dire:
						if direction == d:
							arr[i][j][k] = dire[d]
							break

	res = '- '.join([' '.join([''.join(row) for row in lay]) for lay in arr])
	res = res.strip()
	res = re.sub(" +", ' ', res)

	return res

def fences(blocks):

	blocks = blocks.replace("\n", " ")
	blocks = blocks.strip()
	blocks = re.sub(" +", ' ', blocks)

	arr = [[[]]]
	i, j= 0, 0
	for c in blocks:
		if c not in [' ', '-']:
			arr[i][j].append(c)

		if c == ' ':
			arr[i].append([])
			j += 1

		if c == '-':
			arr.append([[]])
			i += 1
			j = 0

	arr = [list(filter(lambda x: x != [], lay)) for lay in arr]
	conns = ['1', '3', '4', '5', '7', '8', '9', 'g', 'p', 'o', 'c', 'd', 'h', 'r', 'f', '%', '╔' , '╗', '╚', '╝', '║', '═', '╩', '╠', '╦', '╣', '╬', '╴', '╶', '╵', '╷']
	for i, lay in enumerate(arr):
		for j, row in enumerate(lay):
			for k, el in enumerate(row):
				if el == 'f':
					direction = ''
					try:
						if arr[i][j][k+1] in conns:
							direction += 'u'
					except IndexError:
						pass
					try:
						if arr[i][j+1][k] in conns:
							direction += 't'
					except IndexError:
						pass
					if k-1 >= 0:
						try:
							if arr[i][j][k-1] in conns:
								direction += 's'
						except IndexError:
							pass
					if j-1 >= 0:
						try:
							if arr[i][j-1][k] in conns:
								direction += 'b'
						except IndexError:
							pass

					# '╔' , '╗', '╚', '╝', '║', '═', '╩', '╠', '╦', '╣', '╬', '╴', '╶', '╵', '╷'
					dire = {
						'u': '╶', 't': '╷', 's': '╴', 'b': '╵',
						'ub': '╚', 'ut': '╔', 'ts': '╗', 'sb': '╝',
						'tb': '║', 'us': '═', 'uts': '╦', 'tsb': '╣',
						'usb': '╩', 'utb': '╠', 'utsb': '╬'
					}

					for d in dire:
						if direction == d:
							arr[i][j][k] = dire[d]
							
	res = '- '.join([' '.join([''.join(row) for row in lay]) for lay in arr])
	res = res.strip()
	res = re.sub(" +", ' ', res)

	return res

def liquid(blocks):
	blocks = blocks.replace("\n", " ")
	blocks = blocks.strip()
	blocks = re.sub(" +", ' ', blocks)

	arr = [[[]]]
	i, j= 0, 0
	for c in blocks:
		if c not in [' ', '-']:
			arr[i][j].append(c)

		if c == ' ':
			arr[i].append([])
			j += 1

		if c == '-':
			arr.append([[]])
			i += 1
			j = 0

	arr = [list(filter(lambda x: x != [], lay)) for lay in arr]

	waters = ['2', '░', '▓', '∙']
	lavas = ['v', '▒', '█', '·']
	for i, lay in enumerate(arr):
		for j, row in enumerate(lay):
			for k, el in enumerate(row):
				if el == '2':
					try:
						if arr[i+1][j][k] in waters:
							arr[i][j][k] = '░'
					except:
						pass

				if el == 'v':
					try:
						if arr[i+1][j][k] in lavas:
							arr[i][j][k] = '▒'
					except:
						pass
	
	for i, lay in enumerate(arr):
		for j, row in enumerate(lay):
			for k, el in enumerate(row):
				if el == '2':
					try:
						if arr[i-1][j][k] in ['░', '▓']:
							arr[i][j][k] = '∙'
					except:
						pass
				if el == '░':
					try:
						if arr[i-1][j][k] in ['░', '▓']:
							arr[i][j][k] = '▓'
					except:
						pass
				if el == 'v':
					try:
						if arr[i-1][j][k] in ['▒', '█']:
							arr[i][j][k] = '·'
					except:
						pass
				if el == '▒':
					try:
						if arr[i-1][j][k] in ['▒', '█']:
							arr[i][j][k] = '█'
					except:
						pass

	res = '- '.join([' '.join([''.join(row) for row in lay]) for lay in arr])
	res = res.strip()
	res = re.sub(" +", ' ', res)

	return res

@executor_function
def wordle_func(word, guesses):
	canvas = Image.new('RGBA', (500, 600), 'white')
	draw = ImageDraw.Draw(canvas)
	
	for i, prev_guess in enumerate(guesses):
		if prev_guess is not None:
			for j, (word_letter, prev_guess_letter) in enumerate(zip(word, prev_guess)):
				if word_letter == prev_guess_letter:
					draw.rectangle([
						(20+j*95, 20+i*95),
						(100+j*95, 100+i*95)
					], '#6aaa64')
				elif prev_guess_letter in word:
					draw.rectangle([
						(20+j*95, 20+i*95),
						(100+j*95, 100+i*95)
					], '#cab456')
				else:
					draw.rectangle([
						(20+j*95, 20+i*95),
						(100+j*95, 100+i*95)
					], '#787c7e')
				draw.text((60+j*95, 27+i*95), prev_guess_letter.upper(), 'white', wordle_font, 'mt')
		else:
			for j in range(5):
				draw.rectangle([
					(20+j*95, 20+i*95),
					(100+j*95, 100+i*95)
				], 'white', '#d3d6da', 5)

	buf = BytesIO()
	canvas.save(buf, 'PNG')
	buf.seek(0)

	return buf

def create_stat(word, guesses):
	if (tries := len(list(filter(lambda g: g is not None, guesses)))) == 6 and guesses[-1] != word:
		tries = 'X'

	result = f'>>> Wordle {tries}/6\n'
	for prev_guess in guesses:
		if prev_guess is not None:
			for word_letter, prev_guess_letter in zip(word, prev_guess):
				if word_letter == prev_guess_letter:
					result += '🟩'
				elif prev_guess_letter in word:
					result += '🟨'
				else:
					result += '⬜'
			result += '\n'

	return result

@executor_function
def wordle_statistic(scores):
	canvas = Image.new('RGBA', (500, 300), 'white')
	draw = ImageDraw.Draw(canvas)
	draw.text((250, 25), 'GUESS DISTRIBUTION', 'black', wstat_bold_30, 'ma')
	for i, score in enumerate(scores):
		color = '#6aaa64' if score == max(scores) else '#787c7e'
		try:
			maxl = 50+int(score/max(scores)*400)
		except:
			maxl = 70
			color = '#787c7e'
		draw.rectangle([(50, 90+i*30), (maxl if maxl > 70 else 70, 110+i*30)], color)
		draw.text((34, 85+i*30), str(i+1), 'black', wstat_reg)
		draw.text((maxl-4 if maxl > 66 else 66, 86+i*30), str(score), 'white', wstat_bold_20, 'ra')

	buf = BytesIO()
	canvas.save(buf, 'PNG')
	buf.seek(0)
	return buf

@executor_function
def wordle_keyboard(word, guesses):
	keys = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm']
	done = set()
	there = set()
	no = set()

	for i, prev_guess in enumerate(guesses):
		if prev_guess is not None:
			for j, (word_letter, prev_guess_letter) in enumerate(zip(word, prev_guess)):
				if word_letter == prev_guess_letter:
					done.add(word_letter)
				elif prev_guess_letter in word:
					there.add(prev_guess_letter)
				else:
					no.add(prev_guess_letter)

	canvas = Image.new('RGBA', (290, 130), (0, 0, 0, 0))
	draw = ImageDraw.Draw(canvas)
	for i, row in enumerate(keys):
		for j, key in enumerate(row):
			fcolor = 'white'
			if key in done:
				color = '#6aaa64'
			elif key in there:
				color = '#cab456'
			elif key in no:
				color = '#787c7e'
			else:
				color = '#d3d6da'
				fcolor = 'black'
			if i == 0:
				x = 20
			elif i == 1:
				x = 33
			elif i == 2:
				x = 58
			draw.rounded_rectangle((x+j*25, 20+i*30, x+20+j*25, 45+i*30), 3, color)
			draw.text((x+10+j*25, 21+i*30), key.capitalize(), fcolor, wordle_key, 'ma')

	buf = BytesIO()
	canvas.save(buf, 'PNG')
	buf.seek(0)

	return buf

def shorten_ace(font, txt, length):
	last = [[]]
	i = 0
	for word in txt.split():
		last[i].append(word)
		if font.getlength(' '.join(last[i])) > length:
			last.append([])
			last[i+1].append(last[i].pop())
			i += 1
	return '\n'.join(' '.join(line) for line in last)

@executor_function
def attorney_func(name, text):
	bg = ace_asset['court']['bg_l']
	desk = ace_asset['court']['desk_l']
	wright = random.choice(ace_asset['wright'])

	text = '\n'.join(textwrap.wrap(text.replace('\n', ' '), 60)[:4])
	if not text:
		text = '   '

	text_box = Image.new('RGBA', (596, 100), (0, 0, 0, 0))
	text_box_draw = ImageDraw.Draw(text_box)
	text_box_draw.rounded_rectangle([(0, 0), (595, 100)], 7, (0, 0, 0, 200), 'gray', 2)

	name_img = Image.new('RGBA', (550, 40))
	name_draw = ImageDraw.Draw(name_img)
	name_box = name_draw.textbbox((10, 20), name, anchor='lm', font=ace_name_font)
	name_draw.rounded_rectangle((name_box[0]-10, 0, name_box[2]+10, 40), 5, '#000663', 'gray', 2)
	name_draw.text((10, 20), name, anchor='lm', font=ace_name_font)

	char_frames = [frame.convert('RGBA') for frame in ImageSequence.Iterator(wright['talk'])]

	text_drawn = ''
	frames = []
	for i, char in enumerate(text):
		frame = char_frames[i%len(char_frames)]
		canv = Image.new('RGBA', bg.size)
		canv.paste(bg, (0, 0), bg)
		canv.paste(frame, (0, 0), frame)
		canv.paste(desk, (-1, 255), desk)
		canv.paste(text_box, (0, 235), text_box)
		canv.paste(name_img, (0, 195), name_img)
		draw = ImageDraw.Draw(canv)
		text_drawn += char
		draw.multiline_text((7, 240), text_drawn, 'white', ace_text_font)
		frames.append(canv)

	canv = Image.new('RGBA', bg.size)
	canv.paste(bg, (0, 0), bg)
	canv.paste(wright['normal'], (0, 0), wright['normal'])
	canv.paste(desk, (-2, 255), desk)
	canv.paste(text_box, (0, 235), text_box)
	canv.paste(name_img, (0, 195), name_img)
	draw = ImageDraw.Draw(canv)
	draw.multiline_text((7, 240), text_drawn, 'white', ace_text_font)
	frames.append(canv)

	durations = [100]*len(text) + [1500]

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, optimize=True, duration=durations, loop=0)
	igif.seek(0)

	return igif

@executor_function
def prosecutor_func(name, text):
	bg = ace_asset['court']['bg_r']
	desk = ace_asset['court']['desk_r']
	miles = random.choice(ace_asset['miles'])

	text = '\n'.join(textwrap.wrap(text.replace('\n', ' '), 60)[:4])
	if not text:
		text = '   '

	text_box = Image.new('RGBA', (596, 100), (0, 0, 0, 0))
	text_box_draw = ImageDraw.Draw(text_box)
	text_box_draw.rounded_rectangle([(0, 0), (595, 100)], 7, (0, 0, 0, 200), 'gray', 2)

	name_img = Image.new('RGBA', (550, 40))
	name_draw = ImageDraw.Draw(name_img)
	name_box = name_draw.textbbox((10, 20), name, anchor='lm', font=ace_name_font)
	name_draw.rounded_rectangle((name_box[0]-10, 0, name_box[2]+10, 40), 5, '#000663', 'gray', 2)
	name_draw.text((10, 20), name, anchor='lm', font=ace_name_font)

	char_frames = [frame.convert('RGBA') for frame in ImageSequence.Iterator(miles['talk'])]

	text_drawn = ''
	frames = []
	for i, char in enumerate(text):
		frame = char_frames[i%len(char_frames)]
		canv = Image.new('RGBA', bg.size)
		canv.paste(bg, (0, 0), bg)
		canv.paste(frame, (75, 5), frame)
		canv.paste(desk, (-45, 255), desk)
		canv.paste(text_box, (0, 235), text_box)
		canv.paste(name_img, (0, 195), name_img)
		draw = ImageDraw.Draw(canv)
		text_drawn += char
		draw.multiline_text((7, 240), text_drawn, 'white', ace_text_font)
		frames.append(canv)

	canv = Image.new('RGBA', bg.size)
	canv.paste(bg, (0, 0), bg)
	canv.paste(miles['normal'], (75, 5), miles['normal'])
	canv.paste(desk, (-45, 255), desk)
	canv.paste(text_box, (0, 235), text_box)
	canv.paste(name_img, (0, 195), name_img)
	draw = ImageDraw.Draw(canv)
	draw.multiline_text((7, 240), text_drawn, 'white', ace_text_font)
	frames.append(canv)

	durations = [100]*len(text) + [1500]

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, optimize=True, duration=durations, disposal=0, loop=0)
	igif.seek(0)

	return igif

@executor_function
def roomy_func(avatar, floor_texture, wall_texture):
	def add_bg(img):
		bg = Image.new('RGBA', (300, 300), 'black')
		img = ImageOps.fit(Image.open(img), (300, 300)).convert('RGBA')
		bg.paste(img, (0, 0), img)
		bg = bg.convert('RGB')

		buf = BytesIO()
		bg.save(buf, 'PNG')
		buf.seek(0)
		return buf

	# floor
	floor = pv.Box((-5, 5, -5, 5, -1, 0))
	floor.texture_map_to_plane(inplace=True)

	# wall
	wall_scale = 5
	wall = wall_mesh.copy(deep=False).scale((wall_scale, wall_scale, wall_scale), inplace=False).translate([0, 5, 0], inplace=False)

	# picture
	pic = pv.Box((3, 0, 3, 0, 0.5, 0)).translate([-2, 5, -4.3], inplace=False)
	pic.texture_map_to_plane(inplace=True)
	pic_tex = pv.Texture(imageio.imread(avatar))

	# bed
	bed_scale = 0.0003
	bed = bed_mesh.copy(deep=True).scale((bed_scale, bed_scale, bed_scale), inplace=True).translate((0, 0, 0.7), inplace=False)
	bed_tex = pv.read_texture("./models/bed_tex.png")

	# plot
	pl = pv.Plotter(off_screen=True, window_size=(400, 400))

	if isinstance(wall_texture, BytesIO):
		buf = add_bg(wall_texture)
		wall_tex = pv.Texture(imageio.imread(buf))
		pl.add_mesh(wall.rotate_x(90, inplace=False), texture=wall_tex)
	else:
		pl.add_mesh(wall.rotate_x(90, inplace=False), color=wall_texture)

	if isinstance(floor_texture, BytesIO):
		buf = add_bg(floor_texture)
		floor_tex = pv.Texture(imageio.imread(buf))
		pl.add_mesh(floor, texture=floor_tex)
	else:
		pl.add_mesh(floor, color=floor_texture)

	pl.add_mesh(pic.rotate_z(180, inplace=False).rotate_x(-90, inplace=False), texture=pic_tex)
	pl.add_mesh(bed.rotate_y(-90, inplace=False).rotate_x(90, inplace=False), texture=bed_tex)

	buf = BytesIO()
	pl.screenshot(buf)
	buf.seek(0)

	pl.close()
	return buf
#
# image
# #

def wand_gif(frames, durations=50):
	if len(frames) == 1:
		if isinstance(frames[0], np.ndarray):
			frames[0] = Image.fromarray(frame[0])
		buf = BytesIO()
		frames[0].save(buf, 'PNG')
		buf.seek(0)
		return buf

	if isinstance(durations, int):
		durations = [durations] * len(frames)

	is_npa = isinstance(frames[0], np.ndarray)
	
	durations = np.array(durations) // 10

	with wImage.from_array(frames[0] if is_npa else np.array(frames[0])) as bg:
		for i, pframe in enumerate(frames):
			with wImage.from_array(pframe if is_npa else np.array(pframe.convert('RGBA'))) as frame:
				frame.dispose = 'background'
				bg.composite(frame, 0, 0)
				frame.delay = durations[i]
				bg.sequence.append(frame)
		bg.sequence.pop(0)
		bg.dispose = 'background'
		bg.format = 'gif'
		buf = BytesIO()
		bg.save(file=buf)
		buf.seek(0)

	return buf

def pil_gif(frames, durations=50, **kwargs):
	if len(frames) == 1:
		buf = BytesIO()
		frames[0].save(buf, 'PNG')
		buf.seek(0)
		return buf

	buf = BytesIO()
	frames[0].save(buf, format='GIF', save_all=True, append_images=frames[1:], durations=durations, **kwargs)
	buf.seek(0)

	return buf

@executor_function
def ball_func(img):
	space = pymunk.Space()
	space.gravity = 0, -3000
	FPS = 60

	balls = []

	img = ImageOps.fit(Image.open(img), (32, 32)).convert('RGBA')
	colors = list(img.getdata())
	colors = np.array([colors[i:i+32] for i in range(0, len(colors), 32)])
	colors = np.rot90(colors, k=-1)

	balls = []
	
	for i in range(32):
		for j in range(32):
			balls.append(Ball(60+i*6, 320+j*6, 2, tuple(colors[i][j]), 1))
		
	walls = [
		Wall(0, 0, 0, res+100),
		Wall(0, 0, res, 0),
		Wall(res, 0, res, res+100)
	]
	
	for wall in walls:
		space.add(wall.body, wall.shape)

	for ball in balls:
		space.add(ball.body, ball.shape)

	frames = []
	for i in range(160):
		screen = Image.new("RGBA", (res, res), (0, 0, 0, 0))
		draw = ImageDraw.Draw(screen)

		for ball in balls:
			ball.draw(draw)
	  
		if i == 85:
			space.gravity = 0, 1500

		space.step(1/FPS)
		frames.append(screen)

	return wand_gif(frames, FPS)

@executor_function
def swirly(img):
	frames = []
	img_type = Image.open(img)
	img_type = img_type.resize((256, 256))
	ndarr = np.array(img_type)
	for i in range(-10, 11, 2):
		swirled = swirl(ndarr, strength=i, radius=250)

		swirled_img = Image.fromarray((swirled*255).astype(np.uint8))

		if swirled_img.mode != 'RGB':
			swirled_img = swirled_img.convert('RGB')
		fobj = BytesIO()
		swirled_img.save(fobj, "GIF")
		swirled_img = Image.open(fobj)
		frames.append(swirled_img)
	for j in range(10, -11, -2):
		swirled = swirl(ndarr, strength=j, radius=250)
		swirled_img = Image.fromarray((swirled*255).astype(np.uint8))
		if swirled_img.mode != 'RGB':
			swirled_img = swirled_img.convert('RGB')
		fobj = BytesIO()
		swirled_img.save(fobj, "GIF")
		swirled_img = Image.open(fobj)
		frames.append(swirled_img)
	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=150, loop=0)
	igif.seek(0)
	return igif

@executor_function
def bonk_func(img):
	frames = []
	npp = news.convert('RGBA')
	npp = npp.resize((350, 350))
	bonk = Image.open(img).convert('RGBA')
	bonk = bonk.resize((300, 300))
	for i in range(3, -3, -2):
		rot = 20*i
		cent = (50, 300)
		nppr = npp.rotate(rot, center=cent, expand=True)
		canvas = Image.new("RGBA", (512, 350), (0, 0, 0, 0))
		z = i + 3
		bonk = bonk.resize((300, round(300 * z / 6)))
		canvas.paste(bonk, (212, 350 - round(300 * z / 6)), bonk)

		canvas.paste(nppr, (0, -30), nppr)
		frames.append(canvas)

	return wand_gif(frames, 100)

@executor_function
def types(args, auth):
	text = " ".join(args)
	lines = textwrap.wrap(text, width=40)
	txt = []

	l = len(text)
	if l > 150:
		return "", l

	canvas = Image.new("RGB", [690, 200], 'black')
	font = ImageFont.truetype("Squad-Regular.otf", 25)
	draw = ImageDraw.Draw(canvas)

	margin = offset = 40
	for line in lines:
		draw.text((margin, offset), line, font=font, fill="white")
		offset += font.getsize(line)[1]

	draw.text((400, 150), auth, font=font, fill="white")

	buf = BytesIO()
	canvas.save(buf, "PNG")
	buf.seek(0)

	return buf, l

@executor_function
def types_gif(args, auth):
	text = " ".join(args)
	lines = textwrap.wrap(text, width=40)
	font = ImageFont.truetype("Squad-Regular.otf", 25)
	margin = offset = 40
	frames = []
	txt = ["" for i in range(len(lines))]

	l = len(text)
	if l > 150:
		return "", l

	for i, line in enumerate(lines):
		for char in line:
			canvas = Image.new("RGB", [650, 240], 'black')
			draw = ImageDraw.Draw(canvas)
			draw.text((400, 150), auth, font=font, fill="white")
			txt[i] = "".join([txt[i], char])

			margin = offset = 40
			for ln in txt:
				draw.text((margin, offset), ln, font=font, fill="white")
				offset += font.getsize(line)[1]

			fobj = BytesIO()
			canvas.save(fobj, "GIF")
			canvas = Image.open(fobj)
			frames.append(canvas)
			
	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=100)
	igif.seek(0)

	return igif, l

@executor_function
def nohorni_func(bonked, bonker):
	bonked = Image.open(bonked).convert('RGBA')
	bonked = bonked.resize((128, 128))
	if bonker:
		bonker = Image.open(bonker).convert('RGBA')
		bonker = bonker.resize((128, 128))

	jail = jail_gif

	frames = []
	newframes = [f.copy() for f in ImageSequence.Iterator(jail)]
	for frame in newframes:
		newframe = frame.convert("RGBA")
		newframe.paste(bonked, (400, 300), bonked)
		if bonker:
			newframe.paste(bonker, (150, 170), bonker)

		frames.append(newframe)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', save_all=True, append_images=frames[1:])
	igif.seek(0)
	return igif

@executor_function
def burn_func(img):
	burn = Image.open(img).convert('RGBA')
	burn = burn.resize((64, 64))
	
	elmo = elmo_gif

	frames = []
	for frame in ImageSequence.Iterator(elmo):
		newframe = frame.convert("RGBA")
		newframe.paste(burn, (130, 100), burn)

		frames.append(newframe)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', save_all=True, append_images=frames[1:])
	igif.seek(0)
	return igif

@executor_function
def eugh_func(img):
	
	man = man_gif
	eugh = Image.open(img).convert('RGBA')
	eugh = eugh.resize((330, 330))

	frames = []
	for i, frame in enumerate(ImageSequence.Iterator(man)):
		if 50 < i < 110:
			newframe = frame.convert("RGBA")
			newframe = newframe.resize((330, 330))
			newframe = Image.blend(newframe, eugh, 0.5)

			frames.append(newframe)
	
	igif = BytesIO()
	frames[0].save(igif, format='GIF', save_all=True, append_images=frames[1:], loop=0)
	igif.seek(0)
	return igif

@executor_function
def scream_func(img):
	
	gif = scream_gif
	img = Image.open(img).convert('RGBA')
	img = img.resize((330, 330))

	frames = []
	for frame in ImageSequence.Iterator(gif):
		newframe = frame.convert("RGBA")
		newframe = newframe.resize((330, 330))
		newframe = Image.blend(newframe, img, 0.4)

		frames.append(newframe)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', save_all=True, append_images=frames[1:], loop=0)
	igif.seek(0)
	return igif

@executor_function
def why_func(img):
	
	gif = why_gif
	img = Image.open(img).convert('RGBA')
	img = img.resize((330, 330))

	frames = []
	for frame in ImageSequence.Iterator(gif):
		newframe = frame.convert("RGBA")
		newframe = newframe.resize((330, 330))
		newframe = Image.blend(newframe, img, 0.5)

		frames.append(newframe)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', save_all=True, append_images=frames[1:], loop=0)
	igif.seek(0)
	return igif

@executor_function
def bomb_func(img):

	bomb = bomb_gif

	img = Image.open(img).convert('RGBA')
	img = img.resize((165, 165))

	frames = []
	canvas = Image.new("RGBA", (165, 165), (25, 25, 25, 0))
	canvas.paste(img, (0, 0), img)

	frames.append(canvas)

	durations = [1000]
	for frame in ImageSequence.Iterator(bomb):
		newframe = frame.convert("RGBA")
		newframe = newframe.resize((165, 165))
		canvas = Image.new("RGBA", (165, 165), (25, 25, 25, 0))
		canvas.paste(newframe, (0, 0), newframe)
		durations.append(100)

		fobj = BytesIO()
		canvas.save(fobj, "GIF")
		canvas = Image.open(fobj)
		frames.append(canvas)

	durations[-1] = 200

	return wand_gif(frames, durations)

@executor_function
def patpat_func(img):
	patted = Image.open(img).convert('RGBA')
	patted =  ImageOps.fit(patted, (80, 80))

	seq = { 0: [(80,  70), (11,   30)], 
			1: [(90,  60), (11-5, 30+10)], 
			2: [(96, 55), (11-8, 30+15)], 
			3: [(100, 50), (11-10, 30+20)], 
			4: [(90, 60), (11-5, 30+10)]}

	frames = []
	for i, hand in enumerate(hands):
		canvas = Image.new('RGBA', (120, 110), (25, 25, 25, 0))
		
		patted = patted.resize(seq[i][0])
		canvas.paste(patted, seq[i][1], patted)

		canvas.paste(hand, (0, 0), hand)

		fobj = BytesIO()
		canvas.save(fobj, "GIF", transparency=0)
		canvas = Image.open(fobj)
		frames.append(canvas)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=60, disposal=2, loop=0)
	igif.seek(0)
	return igif

@executor_function
def equation_func(img):

	gif = math_gif
	img = Image.open(img).convert("RGBA")
	img = img.resize((330, 330))

	frames = []
	loc = random.randint(0, 238-150)
	for i, frame in enumerate(ImageSequence.Iterator(gif)):
		if loc < i < loc+150:
			frame = frame.convert("RGBA")
			frame = frame.resize((330, 330))

			canvas = Image.new("RGBA", (330, 330), (25, 25, 25, 0))

			canvas.paste(img, (0, 0), img)
			canvas.paste(frame, (0, 0), frame)
			frames.append(canvas)

	return wand_gif(frames, 100)

@executor_function
def buffering_func(img):
	
	gif = buffer_gif
	img = Image.open(img).convert('RGBA')
	img = img.resize((330, 330))

	frames = []
	for frame in ImageSequence.Iterator(gif):
		newframe = frame.convert("RGBA")
		newframe = newframe.resize((330, 330))
		newframe = Image.blend(newframe, img, 0.4)

		frames.append(newframe)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', save_all=True, append_images=frames[1:], loop=0)
	igif.seek(0)
	return igif

@executor_function
def glitch_func(img, level):
	img = Image.open(img).convert('RGBA')

	glitch = glitcher.glitch_image(img, level, gif=True, scan_lines=True, color_offset=True)

	buf = BytesIO()
	glitch[0].save(buf, format='GIF', append_images=glitch[1:], save_all=True, duration=200, loop=0)
	buf.seek(0)

	return buf

@executor_function
def pachinko_game():
	space = pymunk.Space()
	space.gravity = 0, -2000
	FPS = 60

	resx = 200
	resy = 2*resx

	ball = PachiBall(random.uniform(20, resy-20), resy-20, 12, 400)
	space.add(ball.body, ball.shape)
	
	pegs = []
	for i in np.linspace(20, resy-20, 10):
		for j in np.linspace(40, resy-40, 10):
			peg = PachiPeg(j, i, 4, 400)

	frames = []
	for _ in range(300):
		screen = Image.new('RGB', (resy, resy), 'white')
		drawing = ImageDraw.Draw(screen)

		ball.draw(drawing)
		for peg in pegs:
			peg.draw(drawing)

		space.step(1/FPS)

		fobj = BytesIO()
		screen.save(fobj, "GIF", transparency=0)
		screen = Image.open(fobj)
		frames.append(screen)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=FPS, loop=0, disposal=2)
	igif.seek(0)

	return igif

@executor_function
def time_scan_func(img):
	img = Image.open(img)
	width, height = img.size
	
	FIXED_HEIGHT = 200
	scaled_width = int((float(width) * float(FIXED_HEIGHT / float(height))))
	img = [frame.copy() for frame in ImageSequence.Iterator(img)]
	if len(img) == 1:
		return False

	crops = []
	frames = []
	for i in range(1, 201):
		canvas = Image.new('RGBA', (scaled_width, FIXED_HEIGHT))
		frame = img[i%len(img)]
		frame = frame.resize((scaled_width, FIXED_HEIGHT))
		frame = frame.convert('RGB')
		canvas.paste(frame, (0, 0))

		crops.append(frame.crop((0, i, scaled_width, i*2)))
		for j, crop in enumerate(crops):
			canvas.paste(crop, (0, j+1))

		draw = ImageDraw.Draw(canvas)
		draw.line((0, i, scaled_width, i), fill='blue', width=2)
		frames.append(canvas)

	igif = wand_gif(frames)
	
	[crop.close() for crop in crops]
	[frame.close() for frame in img]
	return igif

@executor_function
def time_scan_side_func(img):
	img = Image.open(img)
	width, height = img.size
	FIXED_WIDTH = 200
	scaled_height = int((float(height) * float(FIXED_WIDTH / float(width))))
	img = [frame.copy() for frame in ImageSequence.Iterator(img)]
	if len(img) == 1:
		return False

	crops = []
	frames = []
	for i in range(1, 201):
		canvas = Image.new('RGBA', (FIXED_WIDTH, scaled_height))
		frame = img[i%len(img)]
		frame = frame.resize((FIXED_WIDTH, scaled_height))
		frame.convert('RGB')
		canvas.paste(frame, (0, 0))

		crops.append(frame.crop((i, 0, i*2, scaled_height)))
		for j, crop in enumerate(crops):
			canvas.paste(crop, (j, 0))

		draw = ImageDraw.Draw(canvas)
		draw.line((i, 0, i, scaled_height), fill='blue', width=2)
		frames.append(canvas)

	igif = wand_gif(frames)
	
	[crop.close() for crop in crops]
	[frame.close() for frame in img]
	return igif

@executor_function
def zoom_func(img):
	img = ImageOps.contain(Image.open(img), (400, 400)).convert('RGBA')
	bg = Image.new('RGBA', img.size, (0, 0, 0, 0))
	bg.paste(img, (0, 0), img)

	frames = []
	for i in range(1, 240, 3):
		frame = ImageOps.crop(bg, i).resize(img.size)

		npa = np.array(frame)
		
		if npa.max() == 0:
			break

		frames.append(frame)

	return wand_gif(frames, 50)

@executor_function
def discotic_func(img):
	img = ImageOps.fit(Image.open(img), (200, 200)).convert('RGB')

	w, h = img.size

	color_step = (
		(np.linspace(255, 254, 18), np.linspace(  1, 164, 18), np.linspace( 25,  44, 18)),
		(np.linspace(254, 255, 18), np.linspace(165, 255, 18), np.linspace( 45,  65, 18)),
		(np.linspace(255,   2, 18), np.linspace(254, 128, 18), np.linspace( 64,  24, 18)),
		(np.linspace(  1,   0, 18), np.linspace(127,   4, 18), np.linspace( 25, 249, 18)),
		(np.linspace(  1, 134, 18), np.linspace(  3,   2, 18), np.linspace(248, 125, 18)),
		(np.linspace(135, 254, 18), np.linspace(  1,   0, 18), np.linspace(124,  24, 18))
	)

	c = 0
	frames = []
	for i, e in enumerate(osc(range(10))):
		if i >= 108 or c == 6:
			break

		color = (int(color_step[c][0][i%18]), int(color_step[c][1][i%18]), int(color_step[c][2][i%18]))
		
		if i % 18 == 0:
			c += 1

		fil = Image.new('RGB', img.size, color)

		percent = float(w-1) / w
		crop = img.crop((e*percent, e*percent, w-(e*percent), h-(e*percent)))
		crop = crop.resize((w, h))
		
		blend = Image.blend(crop, fil, 0.5)
		
		fobj = BytesIO()
		blend.save(fobj, "GIF")
		blend = Image.open(fobj)
		frames.append(blend)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=50, disposal=2, loop=0)
	igif.seek(0)

	return igif

@executor_function
def shift_func(img):
	img = Image.open(img)
	img = ImageOps.fit(img, (400, 400))
	durations = []

	img_1_pre = img.crop((0, 0, 400, 200))
	img_1 = Image.new('RGBA', (400, 200), (0, 0, 0, 0))
	img_1.paste(img_1_pre.crop((200, 0, 400, 200)), (0, 0))
	img_1.paste(img_1_pre.crop((0, 0, 200, 200)), (200, 0))

	img_2 = img.crop((200, 0, 400, 400))
	img_3 = img.crop((0, 0, 200, 400))

	img_4_pre = img.crop((0, 200, 400, 400))
	img_4 = Image.new('RGBA', (400, 200), (0, 0, 0, 0))
	img_4.paste(img_4_pre.crop((200, 0, 400, 200)), (0, 0))
	img_4.paste(img_4_pre.crop((0, 0, 200, 200)), (200, 0))

	frames = []
	for i in np.linspace(0, 200, 50): # reversed(np.geomspace(0.01, 200, 100)):
		img_1_crop = img_1.crop((i, 0, 200+i, 200))
		img_2_crop = img_2.crop((0, 200-i, 200, 400-i))
		img_3_crop = img_3.crop((0, i, 200, 200+i))
		img_4_crop = img_4.crop((200-i, 0, 400-i, 200))

		canvas = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
		canvas.paste(img_1_crop, (0, 0), img_1_crop)
		canvas.paste(img_2_crop, (200, 0))
		canvas.paste(img_3_crop, (0, 200))
		canvas.paste(img_4_crop, (200, 200))

		frames.append(canvas)
		durations.append(50)
	
	durations[-1] = 1000

	return wand_gif(frames, durations)

@executor_function
def explicit_func(img):
	img = Image.open(img)

	frames = []
	durations = []
	for i, frame in enumerate(ImageSequence.Iterator(img)):
		if i > 100:
			break
		
		durations.append(frame.info.get('duration', 100))
		frame = frame.copy().resize((518, 518)).convert('RGBA')

		blurred = frame.crop((100, 100, 418, 418)).resize((600, 600)).convert('RGBA').filter(ImageFilter.GaussianBlur(5))
		blurred.paste(frame, (41, 28), frame)
		blurred.paste(explicit_png, (0, 0), explicit_png)

		frames.append(blurred)
		# fobj = BytesIO()
		# blurred.save(fobj, "GIF")
		# blurred = Image.open(fobj)
		# frames.append(blurred)

	return wand_gif(frames, durations)

@executor_function
def blur_func(img):
	img = Image.open(img).convert('RGBA').resize((400, 400))

	frames = []
	for i in range(0, 31):
		
		frame = img.copy()
		frame = frame.filter(ImageFilter.GaussianBlur(i))
		frame = frame.filter(ImageFilter.UnsharpMask(i))

		fobj = BytesIO()
		frame.save(fobj, "GIF")
		frame = Image.open(fobj)
		frames.append(frame)

	frames.extend(frames[::-1])

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=50, disposal=0, loop=0)
	igif.seek(0)

	return igif

@executor_function
def fry_func(img):
	img = Image.open(img).convert('RGBA').resize((400, 400))
	enhancer = ImageEnhance.Sharpness(img)

	frames = []
	for i, e in enumerate(osc(range(1, 32))):
		if i >= 61:
			break
		
		frame = img.copy()
		frame = enhancer.enhance(e*10)

		fobj = BytesIO()
		frame.save(fobj, "GIF")
		frame = Image.open(fobj)
		frames.append(frame)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=50, disposal=2, loop=0)
	igif.seek(0)

	return igif 

@executor_function
def pixel_func(img):
	n = 320
	img = Image.open(img).convert('RGBA').resize((n, n))
	red = Image.new('RGBA', (n, n), 'red')

	frames = []
	for i in range(n-16, 128, -16):
		frame = img.copy()

		frame = frame.resize((i, i), resample=Image.BILINEAR)
		frame = frame.resize((n, n), resample=Image.NEAREST)
		frame = Image.blend(frame, red, 0.1)

		fobj = BytesIO()
		frame.save(fobj, "GIF")
		frame = Image.open(fobj)
		frames.append(frame)

	frames += frames[len(frames)-2:0:-1]
	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=100, disposal=2, loop=0)
	igif.seek(0)

	return igif 

@executor_function
def gallery_func(img):
	img = Image.open(img).resize((200, 200)).convert('RGBA')
	gmi = img.copy().transpose(Image.FLIP_TOP_BOTTOM)

	frames = []
	for i in range(105):
		frame = Image.new('RGBA', (400, 400), 'white')
		frame.paste(img, (-110, -530+i*4), img)
		frame.paste(gmi, (-110, -320+i*4), gmi)
		frame.paste(img, (-110, -110+i*4), img)
		frame.paste(gmi, (-110, 100+i*4), gmi)
		frame.paste(img, (-110, 310+i*4), img)

		frame.paste(img, (310, -530+i*4), img)
		frame.paste(gmi, (310, -320+i*4), gmi)
		frame.paste(img, (310, -110+i*4), img)
		frame.paste(gmi, (310, 100+i*4), gmi)
		frame.paste(img, (310, 310+i*4), img)

		frame.paste(gmi, (100, -110-i*4), gmi)
		frame.paste(img, (100, 100-i*4), img)
		frame.paste(gmi, (100, 310-i*4), gmi)
		frame.paste(img, (100, 520-i*4), img)
		frame.paste(gmi, (100, 730-i*4), gmi)

		fobj = BytesIO()
		frame.save(fobj, "GIF")
		frame = Image.open(fobj)
		frames.append(frame)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=20, disposal=2, loop=0)
	igif.seek(0)

	return igif 

@executor_function
def layer_func(img):
	img = Image.open(img)


	shape1 = Image.new('RGBA', (400, 400), (0, 0, 0, 0)).convert('L')
	shape2 = Image.new('RGBA', (300, 300), (0, 0, 0, 0)).convert('L')
	shape3 = Image.new('RGBA', (200, 200), (0, 0, 0, 0)).convert('L')

	draw1 = ImageDraw.Draw(shape1)
	draw2 = ImageDraw.Draw(shape2)
	draw3 = ImageDraw.Draw(shape3)

	draw1.rounded_rectangle([0, 0, 400, 400], 50, fill='white')
	draw2.rounded_rectangle([0, 0, 300, 300], 50, fill='white')
	draw3.rounded_rectangle([0, 0, 200, 200], 50, fill='white')

	frames = []
	durations = []
	for i, frame in enumerate(ImageSequence.Iterator(img)):
		if i > 150:
			break

		durations.append(frame.info.get('durations', 50))

		img1 = frame.copy().resize((400, 400)).convert('RGBA')
		img2 = frame.copy().resize((300, 300)).convert('RGBA').transpose(Image.FLIP_LEFT_RIGHT)
		img3 = frame.copy().resize((200, 200)).convert('RGBA')
		
		canvas1 = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
		canvas2 = canvas1.copy().resize((300, 300))
		canvas3 = canvas1.copy().resize((200, 200))

		canvas1.paste(img1, (0, 0), img1)
		canvas2.paste(img2, (0, 0), shape2)
		canvas3.paste(img3, (0, 0), shape3)

		canvas1.paste(canvas2, (50, 50), canvas2)
		canvas1.paste(canvas3, (100, 100), canvas3)

		frames.append(canvas1)

	return wand_gif(frames, durations)

@executor_function
def clock_func(img):
	img = Image.open(img).resize((400, 400)).convert('RGBA')

	frames = []
	for i in range(0, 90, 2):
		frame = Image.new('RGBA', (400, 400), 'white')
		canvas = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
		shape = canvas.copy()
		
		draw = ImageDraw.Draw(shape)
		draw.pieslice([0, 0, 400, 400], 270, 270+i*4, fill='white')
		shape = shape.convert('L')

		canvas.paste(img, (0, 0), shape)
		frame.paste(canvas, (0, 0), canvas)
		frames.append(canvas)

	for i in range(0, 90, 2):
		frame = Image.new('RGBA', (400, 400), 'white')
		canvas = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
		shape = canvas.copy()
		
		draw = ImageDraw.Draw(shape)
		draw.pieslice([0, 0, 400, 400], -90+i*4, 270, fill='white')
		shape = shape.convert('L')

		canvas.paste(img, (0, 0), shape)
		frame.paste(canvas, (0, 0), canvas)
		frames.append(canvas)

	return wand_gif(frames, 40)

@executor_function
def radiate_func(img):
	img = Image.open(img).resize((728, 728)).convert('RGBA')

	canvas0 = Image.new('RGBA', (728, 728), (0, 0, 0, 0))
	shape0 = canvas0.copy()
	draw0 = ImageDraw.Draw(shape0)
	draw0.pieslice([0, 0, 728, 728], -90, 270, fill='white')
	shape0 = shape0.convert('L')
	canvas0.paste(img, (0, 0), shape0)

	canvas1 = Image.new('RGBA', (564, 564), (0, 0, 0, 0))
	shape1 = canvas1.copy()
	draw1 = ImageDraw.Draw(shape1)
	draw1.pieslice([0, 0, 564, 564], -90, 270, fill='white')
	shape1 = shape1.convert('L')
	canvas1.paste(img.resize((564, 564)), (0, 0), shape1)

	canvas2 = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
	shape2 = canvas2.copy()
	draw2 = ImageDraw.Draw(shape2)
	draw2.pieslice([0, 0, 400, 400], -90, 270, fill='white')
	shape2 = shape2.convert('L')
	canvas2.paste(img.resize((400, 400)), (0, 0), shape2)

	canvas3 = Image.new('RGBA', (236, 236), (0, 0, 0, 0))
	shape3 = canvas3.copy()
	draw3 = ImageDraw.Draw(shape3)
	draw3.pieslice([0, 0, 236, 236], -90, 270, fill='white')
	shape3 = shape3.convert('L')
	canvas3.paste(img.resize((236, 236)), (0, 0), shape3)

	frames = []
	for i in range(40):
		frame = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
		
		canvas0 = canvas0.copy().resize((728-i*4, 728-i*4))
		canvas1 = canvas1.copy().resize((564-i*4, 564-i*4))
		canvas2 = canvas2.copy().resize((400-i*4, 400-i*4))
		canvas3 = canvas3.copy().resize((236-i*5, 236-i*5))

		frame.paste(canvas0, (-164+i*2, -164+i*2), canvas0)
		frame.paste(canvas1, (-82+i*2, -82+i*2), canvas1)
		frame.paste(canvas2, (i*2, i*2), canvas2)
		frame.paste(canvas3, (int(82+i*2.236), int(82+i*2.236)), canvas3)

		frames.append(frame)

	frames = frames[::-1]

	return wand_gif(frames, 20)

@executor_function
def scroll_func(img):
	img = Image.open(img)

	frames = []
	for i in range(0, 100, 3):
		frame = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
		crop = ImageOps.fit(img, (100, 400), centering=(0.01*i, 0)).convert('RGBA')
		frame.paste(crop, (0, 0), crop)
		frame.paste(crop, (100, 0), crop)
		frame.paste(crop, (200, 0), crop)
		frame.paste(crop, (300, 0), crop)
		frames.append(frame)

	frames += frames[::-1]

	return wand_gif(frames, 50)

@executor_function
def subtract_func(img1, img2):
	im1 = Image.open(img1).resize((400, 400)).convert('RGBA')
	im2 = Image.open(img2).resize((400, 400)).convert('RGBA')

	frames = []
	for i in range(100):
		frame = ImageChops.subtract(im1, im2, 0.01*i, i*4)

		fobj = BytesIO()
		frame.save(fobj, "GIF")
		canvas = Image.open(fobj)
		frames.append(canvas)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=20, disposal=2, loop=0)
	igif.seek(0)

	return igif

@executor_function
def reveal_func(img):
	img = Image.open(img).convert('RGBA')
	canvas = Image.new('RGBA', img.size, 'white')
	canvas.paste(img, (0, 0), img)

	frames = []
	for i in range(51):
		frame = Image.new('RGBA', (400, 400), 'white')
		scene = ImageOps.fit(img, (400, 100), centering=(0, 0.02*i)).convert('RGBA')
		frame.paste(scene, (0, 6*i), scene)

		fobj = BytesIO()
		frame.save(fobj, "GIF")
		canvas = Image.open(fobj)
		frames.append(canvas)

	frames += frames[:len(frames)//2:-1]
	for i in range(51):
		frame = Image.new('RGBA', (400, 400), 'white')
		scene = ImageOps.fit(img, (400, 100+6*i), centering=(0, 1-0.04*i)).convert('RGBA')
		frame.paste(scene, (0, 200-4*i), scene)

		fobj = BytesIO()
		frame.save(fobj, "GIF")
		canvas = Image.open(fobj)
		frames.append(canvas)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=20, disposal=2)
	igif.seek(0)

	return igif

@executor_function
def palette_func(img, c=5):
	ct = ColorThief(img)
	img = ImageOps.contain(Image.open(img), (400, 400)).convert('RGBA')
	x, y = img.size

	s = x//c
	canvas = Image.new('RGBA', (x, y+s), (0, 0, 0, 0))
	canvas.paste(img, (0, 0), img)
	draw = ImageDraw.Draw(canvas)
	colors = ct.get_palette(c)
	for i, color in enumerate(colors):
		draw.rectangle((i*s, y, i*s+s, y+s), fill=color)
	
	buf = BytesIO()
	canvas.save(buf, 'PNG')
	buf.seek(0)

	return buf

@executor_function
def mcmap_func(img):
	img = ImageOps.fit(Image.open(img), (390, 390))
	img = ImageOps.posterize(img.convert('RGB'), 2).convert('RGBA')
	img = img.resize((128, 128), resample=Image.BILINEAR)
	img = img.resize((390, 390), resample=Image.NEAREST)
	bg = Image.new('RGBA', (390, 390), (212, 189, 149, 255))
	bg.paste(img, (0, 0), img)

	canvas = Image.new('RGBA', (430, 430), (0, 0, 0, 0))
	mc_map = mcmap.copy().resize((430, 430)).convert('RGBA')
	canvas.paste(mc_map, (0, 0), mc_map)
	canvas.paste(bg, (20, 20), bg)

	buf = BytesIO()
	canvas.save(buf, 'PNG')
	buf.seek(0)

	return buf

@executor_function
def history_func(imgs):
	img1, img2, img3 = [Image.open(img).resize((200, 200)).convert('RGBA') for img in imgs]
	
	frames = []
	for i in range(210):
		frame = Image.new('RGBA', (400, 400), 'white')
		frame.paste(img3, (-110, -950+i*4), img3)
		frame.paste(img2, (-110, -740+i*4), img2)
		frame.paste(img1, (-110, -530+i*4), img1)
		frame.paste(img2, (-110, -320+i*4), img2)
		frame.paste(img3, (-110, -110+i*4), img3)
		frame.paste(img2, (-110, 100+i*4), img2)
		frame.paste(img1, (-110, 310+i*4), img1)

		frame.paste(img3, (310, -950+i*4), img3)
		frame.paste(img2, (310, -740+i*4), img2)
		frame.paste(img1, (310, -530+i*4), img1)
		frame.paste(img2, (310, -320+i*4), img2)
		frame.paste(img3, (310, -110+i*4), img3)
		frame.paste(img2, (310, 100+i*4), img2)
		frame.paste(img1, (310, 310+i*4), img1)

		frame.paste(img1, (100, -110-i*4), img1)
		frame.paste(img2, (100, 100-i*4), img2)
		frame.paste(img3, (100, 310-i*4), img3)
		frame.paste(img2, (100, 520-i*4), img2)
		frame.paste(img1, (100, 730-i*4), img1)
		frame.paste(img2, (100, 940-i*4), img2)
		frame.paste(img3, (100, 1150-i*4), img3)

		fobj = BytesIO()
		frame.save(fobj, "GIF")
		frame = Image.open(fobj)
		frames.append(frame)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=20, disposal=2, loop=0)
	igif.seek(0)

	return igif 

@executor_function
def shoot_func(img):
	dead = ImageOps.fit(Image.open(img), (100, 100)).convert('RGBA')
	walk = dead.copy().resize((80, 80))

	durations = []
	frames = []
	for i in range(16):
		canvas = shot_street.copy()
		canvas.paste(walk, (350-i*10, 120), walk)
		canvas.paste(shot_gun, (-50, 250), shot_gun)
		fobj = BytesIO()
		canvas.save(fobj, "GIF")
		frame = Image.open(fobj)
		frames.append(frame)
		durations.append(100)
	durations[-1] = 500

	for i in range(5):
		canvas = shot_street.copy()
		canvas.paste(walk, (350-15*10, 120), walk)
		canvas.paste(shot_wound, (220, 140), shot_wound)
		canvas.paste(shot_gun, (-50-i*2, 250+i*2), shot_gun)
		fobj = BytesIO()
		canvas.save(fobj, "GIF")
		frame = Image.open(fobj)
		frames.append(frame)
		durations.append(20)

	durations[0] = durations[-1] = 1000
	realm = random.choice([True, False])
	for i in range(40):
		if realm:
			canvas = shot_heaven.copy()
			canvas.paste(dead, (150, 300-i*4), dead)
		else:
			canvas = shot_hell.copy()
			canvas.paste(dead, (150, i*4), dead)
		fobj = BytesIO()
		canvas.save(fobj, "GIF")
		frame = Image.open(fobj)
		frames.append(frame)
		durations.append(50)

	durations[-1] = 3000
	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=durations, disposal=2, loop=0)
	igif.seek(0)

	return igif 

@executor_function
def halfinvert_func(img):
	img = ImageOps.fit(Image.open(img), (300, 300)).convert('RGB')
	img = ImageOps.invert(img)

	frames = []
	for i in range(16):
		gmi = ImageOps.invert(img)
		shape = Image.new('RGB', (300, 300), (0, 0, 0, 0)).convert('L')
		draw = ImageDraw.Draw(shape)
		draw.polygon([
			(0, 0), (300, 0), 
			(300, i*10), (0, i*10)
		], fill='white')
		gmi.paste(img, (0, 0), shape)
		fobj = BytesIO()
		gmi.save(fobj, "GIF")
		gmi = Image.open(fobj)
		frames.append(gmi)
	
	for i in range(15):
		gmi = ImageOps.invert(img)
		shape = Image.new('RGB', (300, 300), (0, 0, 0, 0)).convert('L')
		draw = ImageDraw.Draw(shape)
		draw.polygon([
			(0, 0), (300, 0), 
			(300, 150+i*10), (0, 150-i*10)
		], fill='white')
		gmi.paste(img, (0, 0), shape)
		fobj = BytesIO()
		gmi.save(fobj, "GIF")
		gmi = Image.open(fobj)
		frames.append(gmi)

	for i in range(15):
		gmi = ImageOps.invert(img)
		shape = Image.new('RGBA', (300, 300), (0, 0, 0, 0)).convert('L')
		draw = ImageDraw.Draw(shape)
		draw.polygon([
			(i*10, 0), (300, 0),
			(300, 300), (300-i*10, 300)
		], fill='white')
		gmi.paste(img, (0, 0), shape)
		fobj = BytesIO()
		gmi.save(fobj, "GIF")
		gmi = Image.open(fobj)
		frames.append(gmi)

	for i in range(15):
		gmi = ImageOps.invert(img)
		shape = Image.new('RGBA', (300, 300), (0, 0, 0, 0)).convert('L')
		draw = ImageDraw.Draw(shape)
		draw.polygon([
			(150+i*10, 0), (300, 0), 
			(300, 300), (150-i*10, 300)
		], fill='white')
		gmi.paste(img, (0, 0), shape)
		fobj = BytesIO()
		gmi.save(fobj, "GIF")
		gmi = Image.open(fobj)
		frames.append(gmi)

	for i in range(16):
		gmi = ImageOps.invert(img)
		shape = Image.new('RGBA', (300, 300), (0, 0, 0, 0)).convert('L')
		draw = ImageDraw.Draw(shape)
		draw.polygon([
			(0, 300-i*10), (300, 0+i*10), 
			(300, 300), (0, 300)
		], fill='white')
		gmi.paste(img, (0, 0), shape)
		fobj = BytesIO()
		gmi.save(fobj, "GIF")
		gmi = Image.open(fobj)
		frames.append(gmi)

	for i in range(15):
		gmi = ImageOps.invert(img)
		shape = Image.new('RGBA', (300, 300), (0, 0, 0, 0)).convert('L')
		draw = ImageDraw.Draw(shape)
		draw.polygon([
			(0, 150+i*10), (300, 150+i*10), 
			(300, 300), (0, 300)
		], fill='white')
		gmi.paste(img, (0, 0), shape)
		fobj = BytesIO()
		gmi.save(fobj, "GIF")
		gmi = Image.open(fobj)
		frames.append(gmi)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=60, disposal=0, loop=0)
	igif.seek(0)

	return igif

@executor_function
def optic_func(img):
	img = ImageOps.contain(Image.open(img).convert('RGBA'), (300, 300))
	img = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGRA)

	frames = []
	for i in range(45):
		transform = alb.OpticalDistortion((0.2*i, 0.2*i), (0.1, 0.1), border_mode=cv2.BORDER_REFLECT_101, p=1)
		result = transform(image=img)['image']

		_, buf = cv2.imencode(".png", result)
		buf = BytesIO(buf)
		frame = Image.open(buf)
		frames.append(frame)

	frames += frames[::-1]
	return wand_gif(frames)

@executor_function
def rain_func(img):
	img = Image.open(img)
	if img.is_animated:
		duration = []
		frames = []
		for i, frame in enumerate(ImageSequence.Iterator(img)):
			if i > 100:
				break
			duration.append(frame.info.get('duuration', 50))
			im = ImageOps.contain(frame.convert('RGBA'), (300, 300))
			bg = Image.new('RGBA', im.size, 'white')
			bg.paste(im, (0, 0), im)
			npimg = cv2.cvtColor(np.array(bg), cv2.COLOR_RGB2BGR)
			transform = alb.RandomRain(blur_value=3, p=1, drop_length=20)
			result = transform(image=npimg)['image']

			_, buf = cv2.imencode(".png", result)
			buf = BytesIO(buf)
			frame = Image.open(buf)

			fobj = BytesIO()
			frame.save(fobj, "GIF")
			frame = Image.open(fobj)
			frames.append(frame)
	else:
		duration = 50
		img = ImageOps.contain(img.convert('RGBA'), (300, 300))
		bg = Image.new('RGBA', img.size, (0, 0, 0, 0))
		bg.paste(img, (0, 0), img)
		img = cv2.cvtColor(np.array(bg), cv2.COLOR_RGB2BGR)

		frames = []
		for _ in range(15):
			transform = alb.RandomRain(blur_value=3, p=1, drop_length=20)
			result = transform(image=img)['image']

			_, buf = cv2.imencode(".png", result)
			buf = BytesIO(buf)
			frame = Image.open(buf)
			frames.append(frame)

	return wand_gif(frames, duration)

@executor_function
def lamp_func(img):
	img = ImageOps.contain(Image.open(img).convert('RGBA'), (300, 300))
	bg = Image.new('RGBA', img.size, 'white')
	bg.paste(img, (0, 0), img)
	img = cv2.cvtColor(np.array(bg), cv2.COLOR_RGB2BGR)

	frames = []
	for _ in range(30):
		transform = alb.RandomBrightnessContrast(p=1)
		result = transform(image=img)['image']

		_, buf = cv2.imencode(".png", result)
		buf = BytesIO(buf)
		frame = Image.open(buf)

		fobj = BytesIO()
		frame.save(fobj, "GIF")
		frame = Image.open(fobj)
		frames.append(frame)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=50, disposal=0, loop=0)
	igif.seek(0)

	return igif

@executor_function
def roll_func(img):
	img = ImageOps.contain(Image.open(img).convert('RGBA'), (200, 200))
	img = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGRA)

	frames = []
	for i in range(0, 90, 2):
		transform = alb.ShiftScaleRotate((0, 0), (0, 0), (i*4, i*4), p=1, border_mode=cv2.BORDER_TRANSPARENT)
		result = transform(image=img)['image']

		_, buf = cv2.imencode(".png", result)
		buf = BytesIO(buf)
		frame = Image.open(buf)
		frames.append(frame)

	return wand_gif(frames, 50)

@executor_function
def tv_func(img):
	img = ImageOps.fit(Image.open(img), (350, 280)).convert('RGBA')
	img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
	transform_optical = alb.OpticalDistortion((1.5, 1.5), (0.1, 0.1), p=1)

	result = transform_optical(image=img)['image']
	_, buf = cv2.imencode(".png", result)
	buf = BytesIO(buf)
	bulb = ImageOps.crop(Image.open(buf), 20)

	bulb = cv2.cvtColor(np.array(bulb), cv2.COLOR_RGB2BGR)

	frames = []
	for _ in range(10):
		canvas = Image.new('RGBA', tvt.size, (54, 57, 62, 0))
		transform_tv = alb.GaussNoise((8000, 10000), mean=0, p=1)
		result = transform_tv(image=bulb)['image']

		_, buf = cv2.imencode(".png", result)
		buf = BytesIO(buf)
		noise = Image.open(buf).convert('RGBA')
		
		canvas.paste(noise, (5, 10), noise)
		canvas.paste(tvt, (0, 0), tvt)
		frames.append(canvas)

	return wand_gif(frames, 50)

@executor_function
def earthquake_func(img, power):
	img = ImageOps.contain(Image.open(img).convert('RGBA'), (300, 300))
	img = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGRA)

	if power < 1:
		power = 1
	elif power > 10:
		power = 10
		
	frames = []
	for _ in range(30):
		transform = alb.MotionBlur((power*9, power*10), p=1)
		result = transform(image=img)['image']

		_, buf = cv2.imencode(".png", result)
		buf = BytesIO(buf)
		frame = Image.open(buf)
		frames.append(frame)

	return wand_gif(frames, 50)

@executor_function
def infinity_func(img):
	img = ImageOps.contain(Image.open(img).convert('RGBA'), (200, 200))
	img = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGRA)

	frames = []
	for i in range(90):
		transform = alb.GridDistortion(1, (i, i), p=1)
		result = transform(image=img)['image']

		_, buf = cv2.imencode(".png", result)
		buf = BytesIO(buf)
		frame = Image.open(buf)
		frames.append(frame)

	durations = [50]*90
	durations[0] = 500
	return wand_gif(frames, durations)

@executor_function
def shock_func(img):
	img = ImageOps.contain(Image.open(img).convert('RGBA'), (300, 300))
	canvas = Image.new('RGBA', img.size, 'white')
	canvas.paste(img, (0, 0), img)
	img = cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2BGR)

	frames = []
	for i in range(1, 6):
		result = iaa.imgcorruptlike.ZoomBlur(i).augment_image(img)

		_, buf = cv2.imencode(".png", result)
		buf = BytesIO(buf)
		frame = Image.open(buf)

		fobj = BytesIO()
		frame.save(fobj, "GIF")
		frame = Image.open(fobj)
		frames.append(frame)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=50, disposal=0, loop=0)
	igif.seek(0)

	return igif

@executor_function
def boil_func(img, level):
	if level < 1:
		level = 1
	elif level > 5:
		level = 5
	
	img = Image.open(img)
	anim = getattr(img, "is_animated", False)

	if anim:
		frames = []
		duration = []
		for i, frame in enumerate(ImageSequence.Iterator(img)):
			if i > 100:
				break
			im = ImageOps.contain(frame.convert('RGBA'), (300, 300))
			bg = Image.new('RGBA', im.size, 'white')
			bg.paste(im, (0, 0), im)

			npimg = cv2.cvtColor(np.array(bg), cv2.COLOR_RGB2BGR)
			result = iaa.imgcorruptlike.ElasticTransform(severity=level).augment_image(npimg)

			_, buf = cv2.imencode(".png", result)
			buf = BytesIO(buf)
			frame = Image.open(buf)

			fobj = BytesIO()
			frame.save(fobj, "GIF")
			frame = Image.open(fobj)
			frames.append(frame)
			duration.append(frame.info.get('duration', 100))
	else:
		duration = 50
		im = ImageOps.contain(img.convert('RGBA'), (300, 300))
		bg = Image.new('RGBA', im.size, 'white')
		bg.paste(im, (0, 0), im)
		img = cv2.cvtColor(np.array(bg), cv2.COLOR_RGB2BGR)

		frames = []
		for i in range(15):
			result = iaa.imgcorruptlike.ElasticTransform(severity=level).augment_image(img)

			_, buf = cv2.imencode(".png", result)
			buf = BytesIO(buf)
			frame = Image.open(buf)

			fobj = BytesIO()
			frame.save(fobj, "GIF")
			frame = Image.open(fobj)
			frames.append(frame)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=duration, disposal=0, loop=0)
	igif.seek(0)

	return igif

@executor_function
def abstract_func(img):
	img = Image.open(img)
	img = ImageOps.contain(img.convert('RGBA'), (300, 300))
	bg = Image.new('RGBA', img.size, 'white')
	bg.paste(img, (0, 0), img)
	img = cv2.cvtColor(np.array(bg), cv2.COLOR_RGB2BGR)

	frames = []
	for _ in range(10):
		result = iaa.RegularGridVoronoi(n_rows=15, n_cols=15, p_drop_points=0.5, p_replace=1, max_size=None).augment_image(img)

		_, buf = cv2.imencode(".png", result)
		buf = BytesIO(buf)
		frame = Image.open(buf)

		fobj = BytesIO()
		frame.save(fobj, "GIF")
		frame = Image.open(fobj)
		frames.append(frame)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=50, disposal=0, loop=0)
	igif.seek(0)

	return igif

@executor_function
def canny_func(img):
	img = Image.open(img)

	frames = []
	durations = []
	for i, frame in enumerate(ImageSequence.Iterator(img)):
		if i > 200:
			break

		durations.append(frame.info.get('duration', 50))
		npimg = cv2.cvtColor(np.array(ImageOps.contain(frame.convert('RGB'), (300, 300))), cv2.COLOR_RGB2BGR)
		result = iaa.Canny(1, sobel_kernel_size=4, colorizer=iaa.RandomColorsBinaryImageColorizer(color_true=255, color_false=0)).augment_image(npimg)

		_, buf = cv2.imencode(".png", result)
		buf = BytesIO(buf)
		new_frame = Image.open(buf)

		fobj = BytesIO()
		new_frame.save(fobj, "GIF")
		new_frame = Image.open(fobj)
		frames.append(new_frame)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=durations, disposal=0, loop=0)
	igif.seek(0)

	return igif

@executor_function
def cartoon_func(img):
	img = Image.open(img)

	frames = []
	durations = []
	for i, frame in enumerate(ImageSequence.Iterator(img)):
		if i > 50:
			break
		
		durations.append(frame.info.get('duration', 50))
		im = ImageOps.contain(frame.convert('RGBA'), (300, 300))
		bg = Image.new('RGBA', im.size, 'white')
		bg.paste(im, (0, 0), im)
		npimg = cv2.cvtColor(np.array(bg), cv2.COLOR_RGB2BGR)
		result = iaa.Cartoon(edge_prevalence=1, seed=0).augment_image(npimg)

		_, buf = cv2.imencode(".png", result)
		buf = BytesIO(buf)
		frame = Image.open(buf)

		fobj = BytesIO()
		frame.save(fobj, "GIF")
		frame = Image.open(fobj)
		frames.append(frame)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=durations, disposal=0, loop=0)
	igif.seek(0)

	return igif

@executor_function
def love_func(img, rainbow):
	img = ImageOps.contain(Image.open(img), (400, 400)).convert('RGBA')
	canvas = Image.new('RGBA', img.size, (0, 0, 0, 0))
	canvas.paste(img, (0, 0), img)
	
	hearts = [Heart((random.randint(-10, 400), random.randint(-10, 430)), (0, 0), 10, random.choice(heart_imgs).resize((20, 20)) if rainbow else heart_imgs[0].resize((20, 20))) for _ in range(100)]

	frames = []
	for _ in range(60):
		frame = canvas.copy()

		for heart in hearts:
			heart.velocity = [random.randint(-1, 1), random.randint(-3, 1)]
			heart.update(frame)

		frames.append(frame)

	return wand_gif(frames, 60)

@executor_function
def magnify_func(img):
	img = Image.open(img).resize((400, 400)).convert('RGBA')
	canvas = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
	canvas.paste(img, (0, 0), img)

	frames = []
	for i in range(0, 50, 3):
		frame = canvas.copy()
		frame.paste(lup, (50+3*i, 50+3*i), lup)
		frames.append(frame)
	for i in range(0, 50, 3):
		frame = canvas.copy()
		frame.paste(lup, (200-i*3, 200-i), lup)
		frames.append(frame)
	for i in range(0, 50, 3):
		frame = canvas.copy()
		frame.paste(lup, (50+i*3, 150-i*3), lup)
		frames.append(frame)
	for i in range(0, 50, 3):
		frame = canvas.copy()
		frame.paste(lup, (200-i*3, i), lup)
		frames.append(frame)

	return wand_gif(frames, 100)

@executor_function
def shear_func(img, axis):
	img = Image.open(img)
	img = ImageOps.contain(img.convert('RGBA'), (300, 300))
	canvas = Image.new('RGBA', (300, 300), 'white')
	canvas.paste(img, (0, 0), img)
	img = cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2BGR)

	frames = []
	for i in range(1, 53):
		if axis.lower() == 'x':
			result = iaa.ShearX((i*7, i*7), cval=255).augment_image(img)
		else:
			result = iaa.ShearY((i*7, i*7), cval=255).augment_image(img)

		_, buf = cv2.imencode(".png", result)
		buf = BytesIO(buf)
		frame = Image.open(buf)

		fobj = BytesIO()
		frame.save(fobj, "GIF")
		frame = Image.open(fobj)
		frames.append(frame)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=50, disposal=0, loop=0)
	igif.seek(0)

	return igif

@executor_function
def print_func(img):
	at = Image.new('RGBA', (85, 85), 'white')
	img = Image.open(img).convert('RGBA').resize((85, 85))

	at.paste(img, (0, 0), img)
	img = cv2.cvtColor(np.array(at), cv2.COLOR_RGBA2BGRA)

	shear = iaa.ShearX((337, 337), cval=255, fit_output=True).augment_image(img)

	_, buf = cv2.imencode(".png", shear)
	buf = BytesIO(buf)
	img = Image.open(buf).convert('RGBA').rotate(15, expand=True)

	frames = []
	for i, frame in enumerate(ImageSequence.Iterator(prt)):
		canvas = Image.new('RGBA', (375-2, 297-2), 'white')
		frame = ImageOps.scale(frame, 1.5)
		x, y = frame.size
		frame = frame.crop([1, 1, x-1, y-1])

		canvas.paste(frame, (0, 0))

		if i > 12:
			mask = Image.new("L", img.size, 0)
			draw = ImageDraw.Draw(mask)
			if i < 32:
				last = (int(135-(i-13)*2.7), int(75-(i-13)*3.5)), (int(50-(i-13)*2.7), int(95-(i-13)*3.5))

				draw.polygon([
					(50, 95), 
					(135, 75), 
					*last], 
				fill=255, outline=None)
			else:
				draw.polygon([
					(50, 95), 
					(135, 75), 
					*last], 
				fill=255, outline=None)
			canvas.paste(img, (int(70+i*2.7),  int(42+i*3.5)), mask)

		fobj = BytesIO()
		canvas.save(fobj, "GIF")
		frame = Image.open(fobj)
		frames.append(frame)

	durations = [200]*(len(frames)-1) + [2000]
	igif = BytesIO()
	frames[0].save(igif, format='GIF', save_all=True, append_images=frames[1:], loop=0, duration=durations)
	igif.seek(0)

	return igif

@executor_function
def paparazzi_func(img):
	img = ImageOps.fit(Image.open(img), (100, 100)).convert('RGBA')
	rc = red_carpet.copy()
	rc.paste(img, (150, 60), img)
	img = cv2.cvtColor(np.array(rc), cv2.COLOR_RGB2BGR)

	frames = []
	for frame in ImageSequence.Iterator(flashes):
		canv = Image.new('RGB', (400, 225), 'white')
		canv.paste(frame, (0, 0))
		fobj = BytesIO()
		canv.save(fobj, "GIF")
		frame = Image.open(fobj)
		frames.append(frame)

	for _ in range(30):
		transform = alb.RandomBrightnessContrast(p=1)
		result = transform(image=img)['image']

		_, buf = cv2.imencode(".png", result)
		buf = BytesIO(buf)
		frame = Image.open(buf)
		canv = Image.new('RGB', (400, 225), 'white')
		canv.paste(frame, (0, 0))

		fobj = BytesIO()
		canv.save(fobj, "GIF")
		frame = Image.open(fobj)
		frames.append(frame)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=100, disposal=2, loop=0)
	igif.seek(0)

	return igif
	
@executor_function
def matrix_func(img):
	img = ImageOps.contain(Image.open(img).convert('RGBA'), (300, 300))
	x, y = img.size
	
	frames = []
	for _ in range(5):
		frame = Image.new('RGBA', img.size, (0, 0, 0, 0))
		clip = frame.copy()
		draw = ImageDraw.Draw(clip)

		lines = [''.join(random.choices(string.ascii_uppercase+string.digits, k=x//6)) for _ in range(y//9)]
		for i, line in enumerate(lines):
			draw.text((-2, -5+i*10), line, font=mfont, color='white')

		frame.paste(img, (0, 0), clip)

		fobj = BytesIO()
		frame.save(fobj, "GIF")
		frame = Image.open(fobj)
		frames.append(frame)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=50, disposal=0, loop=0)
	igif.seek(0)

	return igif

@executor_function
def youtube_func(pfp, name, text):
	pfp = ImageOps.fit(Image.open(pfp), (50, 50)).convert('RGBA')

	bg = Image.new('RGBA', pfp.size, (0, 0, 0, 0))
	mask = bg.copy()
	mask_draw = ImageDraw.Draw(mask)
	mask_draw.ellipse((0, 0, *mask.size), 'white')
	mask = mask.convert('L')
	bg.paste(pfp, (0, 0), mask)

	lines = textwrap.wrap(text, width=27)

	frames = []
	for frame in ImageSequence.Iterator(ytgif):
		canvas = Image.new('RGBA', frame.size, 'white')
		canvas.paste(frame.convert('RGBA'), (0, 0))
		canvas.paste(bg, (15, 545), bg)
		
		draw = ImageDraw.Draw(canvas)

		for i, line in enumerate(lines[:2]):
			if i == 1 and len(lines) > 2:
				line = line[:27] + '...'
			draw.text((20, 320+i*35), line, 'black', roboto_reg)
		draw.text((85, 540), name, 'black', roboto_lig)

		fobj = BytesIO()
		canvas.save(fobj, "GIF")
		canvas = Image.open(fobj)
		frames.append(canvas)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=50, disposal=0, loop=0)
	igif.seek(0)

	return igif

@executor_function
def sensitive_func(img):
	img = Image.open(img)

	frames = []
	durations = []
	for i, frame in enumerate(ImageSequence.Iterator(img)):
		if i == 100:
			break

		durations.append(frame.info.get('duration', 50))
		canv = Image.new('RGBA', (400, 400), 'white')
		frame = ImageOps.fit(frame, ((400, 400))).convert('RGBA')
		frame = frame.filter(ImageFilter.GaussianBlur(3))
		canv.paste(frame, (0, 0), frame)
		canv.paste(sensitive, (0, 0), sensitive)

		fobj = BytesIO()
		canv.save(fobj, "GIF")
		canvas = Image.open(fobj)
		frames.append(canvas)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=durations, disposal=0, loop=0)
	igif.seek(0)

	return igif

@executor_function
def warp_func(img):
	trace = np.linspace(0, 2*np.pi, 100)
	img = Image.open(img).resize((900, 300)).convert('RGBA')

	frames = []
	for trcs in zip(*[np.sin(trace+i*0.033) for i in range(30)]):
		canvas = Image.new('RGBA', (300, 300), (0, 0, 0, 0))
		length = round(300//len(trcs))
		for i, x in enumerate(trcs):
			mask = Image.new('RGBA', img.size, (0, 0, 0, 0))
			draw = ImageDraw.Draw(mask)
			draw.rectangle((round(i*length-x*300+300), 0, round(i*length-x*300+300)+length, 300), 'white')
			canvas.paste(img, (round(x*300-300), 0), mask)

		frames.append(canvas)

	return wand_gif(frames, 50)

@executor_function
def wave_func(img, freq, amp):
	img = Image.open(img)
	img = ImageOps.contain(img, (200, 200)).convert('RGBA')

	frames = []
	for i in np.linspace(0, 2*np.pi, 50):
		canvas = Image.new('RGBA', (300, img.size[1]), (0, 0, 0, 0))
		for j in range(img.size[1]):
			x = round(np.sin(i+j*freq)*amp)
			slit = img.crop((0, j, img.size[0], j+1))
			canvas.paste(slit, (50+x, j))
		frames.append(canvas)

	return wand_gif(frames, durations=50)

@executor_function
def advertize_func(img):
	img = Image.open(img)

	frames = []
	durations = []
	for i, frame in enumerate(ImageSequence.Iterator(img)):
		if i == 100:
			break
		
		durations.append(frame.info.get('duration', 100))
		canvas = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
		frame = ImageOps.fit(frame.convert('RGBA'), (350, 350))
		canvas.paste(frame, (25, 25), frame)
		canvas.paste(ads, (0, 0), ads)
		frames.append(canvas)

	return wand_gif(frames, durations)

@executor_function
def pattern_func(img):
	img = ImageOps.fit(Image.open(img).convert('RGBA'), (400, 400))
	frames = []
	for _ in range(10):
		frame = Image.new('RGBA', (400, 400), 'black')
		x = 39
		y = 38
		vert = random.choices([False, True], k=y)
		hor = random.choices([False, True], k=x)

		boardx = boardy = np.zeros((x, y), 'uint8')
		for row, seed in list(zip(boardx, hor)):
			if seed:
				for i in range(len(row)):
					row[i] = i % 2
			else:
				for i in range(len(row)):
					row[i] = (i+1) % 2
		for row, seed in list(zip(boardy, vert)):
			if seed:
				for i in range(len(row)):
					row[i] = (i+1) % 2
			else:
				for i in range(len(row)):
					row[i] = i % 2

		canvas = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
		draw = ImageDraw.Draw(canvas)
		for i, row in enumerate(boardx):
			for j, el in enumerate(row):
				if el:
					draw.line([(10+i*10, 10+j*10), (10+i*10, 10+j*10+10)], 'white', 5)

		for i, row in enumerate(boardy.transpose()):
			for j, el in enumerate(row):
				if el:
					draw.line([(10+i*10, 10+j*10), (10+i*10+10, 10+j*10)], 'white', 5)

		frame.paste(img, (0, 0), canvas)
		frames.append(frame)

	return wand_gif(frames, 250)

@executor_function
def bubble_func(img):
	img = Image.open(img).convert('RGBA').resize((300, 300))
	colors = list(img.getdata())

	x = random.randint(10, 290)
	y = random.randint(10, 290)
	circles = [Circle(x, y, colors[x+y*img.height])]

	frames = []
	for _ in range(150):
		canv = Image.new('RGBA', (300, 300))
		draw = ImageDraw.Draw(canv)

		for _ in range(3):
			valid = False
			while not valid:
				valid += 1
				x = random.randint(10, 290)
				y = random.randint(10, 290)

				for circle in circles:
					if math.dist([x, y], [circle.x, circle.y]) < circle.r:
						valid = False
						break
					else:
						valid = True

			if valid:
				circles.append(Circle(x, y, colors[x+y*img.height]))

		for circle in circles:
			if circle.x - circle.r < 0 or circle.y - circle.r < 0 or circle.x + circle.r > 300 or circle.y + circle.r > 300:
				circle.growing = False
			else:
				for other in circles:
					if circle != other:
						if circle.dist(other) < circle.r + other.r + 2:
							circle.growing = False
							break
			circle.grow()
			circle.draw(draw)

		frames.append(canv)
	
	return wand_gif(frames, [50]*(len(frames)-1)+[500])
		
@executor_function
def cloth_func(img):
	img = ImageOps.fit(Image.open(img), (20, 20)).convert('RGBA')
	colors = list(img.getdata())
	colors = np.array([colors[i:i+20] for i in range(0, len(colors), 20)])
	colors = np.rot90(colors, k=-1)

	space = pymunk.Space()
	FPS = 50
	space.gravity = 0, -1800
	
	n_rows = n_cols = 20
	balls = [[ClothBall(110+i*10-j*3, j*10+60, 3, tuple(colors[i][j])) for j in range(n_cols)] for i in range(n_rows)]

	for row in balls:
		for ball in row:
			space.add(ball.body, ball.shape)

	strings = []
	for i in range(n_rows-1):
		for j in range(n_cols):
			string = String(balls[i][j].body, balls[i+1][j].body)
			space.add(string.joint)
			strings.append(string)

	for i in range(n_rows):
		for j in range(n_cols):
			if j == n_cols-1:
				string = String(balls[i][j].body, (110+i*10-j*3, (j+1)*10+60), 'position')
			else:
				string = String(balls[i][j].body, balls[i][j+1].body)
			space.add(string.joint)
			strings.append(string)

	frames = []
	for _ in range(200):
		canv = Image.new('RGBA', (300, 300), (0, 0, 0, 0))
		draw = ImageDraw.Draw(canv)

		for string in strings:
			string.draw(draw)

		for row in balls:
			for ball in row:
				ball.draw(draw)

		space.step(1/FPS)
		frames.append(canv)

	return wand_gif(frames, FPS)

@executor_function
def logoff_func(img):
	img = Image.open(img).convert('RGBA').resize((400, 400))
	creep = random.choice(creeps)

	frames = []
	for i in np.linspace(0, 1, 100):
		frames.append(Image.blend(img, creep, i))
	
	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=50, disposal=0)
	igif.seek(0)

	return igif

@executor_function
def dilate_func(img):
	img = Image.open(img).convert('RGBA')
	if img.size[0] > 400 or img.size[1] > 400:
		img = ImageOps.contain(img, (400, 400))
	img = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGRA)
	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

	frames = []
	for i in range(1, 100):
		dst = cv2.dilate(img, kernel, iterations=i)
		_, buf = cv2.imencode(".png", dst)
		buf = BytesIO(buf)
		frames.append(Image.open(buf))
	
	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=50, disposal=0, loop=0)
	igif.seek(0)

	return igif

@executor_function
def undilate_func(img):
	img = Image.open(img).convert('RGBA')
	if img.size[0] > 400 or img.size[1] > 400:
		img = ImageOps.contain(img, (400, 400))
	img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

	frames = []
	durations = []
	for i in range(100, 0, -1):
		dst = cv2.dilate(img, kernel, iterations=i)
		_, buf = cv2.imencode(".png", dst)
		buf = BytesIO(buf)
		frames.append(Image.open(buf))
		durations.append(50)

	durations[-1] = 1000
	
	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=durations, disposal=0, loop=0)
	igif.seek(0)

	return igif

@executor_function
def fan_func(circled):
	circled = Image.open(circled).convert('RGBA')

	fan = fan_img.copy()
	fan.paste(circled, (150, 150), circled)

	frames = []
	for i in range(100):
		frames.append(fan.rotate(i**1.9))

	return wand_gif(frames, durations=40)

@executor_function
def ripple_func(img):
	bg = Image.new('RGBA', (300, 300), 'black')
	img = ImageOps.flip(ImageOps.fit(Image.open(img), (300, 300)).convert('RGBA'))
	bg.paste(img, (0, 0), img)
	bg = bg.convert('RGB')

	buf = BytesIO()
	bg.save(buf, 'PNG')
	buf.seek(0)

	tex = pv.Texture(imageio.imread(buf))
	x = np.arange(-10, 10, 0.25)
	y = np.arange(-10, 10, 0.25)
	x, y = np.meshgrid(x, y)
	r = np.sqrt(x**2 + y**2)
	z = np.sin(r)

	grid = pv.StructuredGrid(x, y, z)
	grid.texture_map_to_plane(inplace=True)

	pts = grid.points.copy()
	plotter = pv.Plotter(notebook=False, off_screen=True, window_size=[300, 250])

	frames = []
	nframe = 15
	for phase in np.linspace(0, 2 * np.pi + 0.41, nframe + 1)[:nframe]:
		z = np.sin(r + phase)
		pts[:, -1] = z.ravel()

		plotter.add_mesh(grid, smooth_shading=True, texture=tex)
		plotter.update_coordinates(pts, render=False)
		plotter.mesh.compute_normals(cell_normals=False, inplace=True)

		if plotter._first_time:
			plotter._on_first_render_request()
			plotter.render()
		else:
			plotter.update()
			frames.append(Image.fromarray(plotter.image))
		plotter.clear()

	plotter.close()
	return wand_gif(frames, 60)

@executor_function
def cow_func(img):
	bg = Image.new('RGBA', (300, 300), 'black')
	img = ImageOps.fit(Image.open(img), (300, 300)).convert('RGBA')
	bg.paste(img, (0, 0), img)
	bg = bg.convert('RGB')

	buf = BytesIO()
	bg.save(buf, 'PNG')
	buf.seek(0)

	tex = pv.Texture(imageio.imread(buf))

	mesh = cow_mesh.copy(deep=False)
	mesh.texture_map_to_plane(inplace=True)

	pl = pv.Plotter(off_screen=True, window_size=[350, 300])

	camera = pv.Camera()
	camera.position = 15, 0, 15
	camera.focal_point = 0, 0, 0
	pl.camera = camera

	frames = []
	for i in np.linspace(0, 360, 50):
		rot = mesh.rotate_y(i, inplace=False)
		actor = pl.add_mesh(rot, texture=tex, smooth_shading=True)
		buf = BytesIO()
		pl.screenshot(buf)
		buf.seek(0)
		frames.append(Image.open(buf))
		pl.remove_actor(actor)
	pl.close()

	return wand_gif(frames, 50)

@executor_function
def globe_func(img):
	bg = Image.new('RGBA', (300, 300), 'black')
	img = ImageOps.fit(Image.open(img), (300, 300)).convert('RGBA')
	bg.paste(img, (0, 0), img)
	bg = bg.convert('RGB')

	buf = BytesIO()
	bg.save(buf, 'PNG')
	buf.seek(0)

	tex = pv.Texture(imageio.imread(buf))

	mesh = pv.Sphere(5).smooth()
	mesh.texture_map_to_sphere(inplace=True)

	pl = pv.Plotter(off_screen=True, window_size=[350, 300])

	camera = pv.Camera()
	camera.position = -15, 15, 0
	camera.focal_point = 0, 0, 0
	pl.camera = camera

	frames = []
	for i in np.linspace(0, 360, 30):
		rot = mesh.rotate_y(i, inplace=False)
		actor = pl.add_mesh(rot, texture=tex, smooth_shading=True, metallic=1)
		buf = BytesIO()
		pl.screenshot(buf)
		buf.seek(0)
		frames.append(Image.open(buf))
		pl.remove_actor(actor)
	pl.close()

	return wand_gif(frames, 50)

@executor_function
def cracks_func(img):
	# code adapted with changes from
	# https://github.com/Lucas-C/dotfiles_and_notes/blob/master/languages/python/img_processing/japanify.py and
	# https://github.com/Lucas-C/dotfiles_and_notes/blob/master/languages/python/img_processing/steal_colors_with_same_brightness.py

	def contrastpoints(image, j, width, threshold):
		contrast = []
		for i in range(width - 3):
			ave1 = sum(image[i + 0, j][:3]) / 3
			ave2 = sum(image[i + 1, j][:3]) / 3
			ave3 = sum(image[i + 2, j][:3]) / 3
			if abs(ave2 - ave1) > threshold and abs(ave1 - ave3) > (threshold / 2):
				contrast.append(i)
		return contrast

	def luminosity(pixel):
		if len(pixel) > 3 and not pixel[3]:
			return 0
		r, g, b = pixel[:3]
		return 0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2)
	
	img = ImageOps.contain(Image.open(img), (300, 300)).convert('RGBA')
	width, height = img.size
	im = img.load()

	for j in range(height):
		contrast = contrastpoints(im, j - 1 if j else 0, width, 20)
		m = 0
		for i in range(width):
			if m < len(contrast) and i >= contrast[m]:
				im[i, j] = (0, 0, 0)
				m += 1

	palette = {}
	pwidth, pheight = warm_palette.size
	palette_pixels = warm_palette.load()

	for j in range(pheight):
		for i in range(pwidth):
			brightness = luminosity(palette_pixels[i, j])
			palette[brightness] = palette_pixels[i, j]

	sorted_keys = sorted(palette.keys())

	for j in range(height):
		for i in range(width):
			at = bisect_left(sorted_keys, luminosity(im[i, j]))
			brightness = max(sorted_keys) if at == len(sorted_keys) else sorted_keys[at]
			im[i, j] = palette[brightness]

	buf = BytesIO()
	img.save(buf, 'PNG')
	buf.seek(0)

	return buf

@executor_function
def melt_func(img):
	img = ImageOps.contain(Image.open(img), (300, 300)).convert('RGBA')

	frames = []
	for _ in range(5):
		spike = pixelsort(img, interval_function='random', angle=90)
		frames.append(spike)

	return wand_gif(frames, 100)

@executor_function
def gameboy_camera_func(img):
	imgs = Image.open(img)

	frames = []
	durations = []
	for n, frame in enumerate(ImageSequence.Iterator(imgs)):
		if n > 50:
			break

		durations.append(frame.info.get('duration', 50))
		img = np.array(ImageOps.contain(frame, (100, 100)).convert('L'))

		for i in range(img.shape[0]):
			for j in range(img.shape[1]):
				if img[i][j] >= 236:
					img[i][j] = 255
				elif img[i][j] >= 216:
					img[i][j] = 255 - ((i%2)*(j%2)*83)
				elif img[i][j] >= 196:
					img[i][j] = 255 - (((j+i+1)%2)*83)
				elif img[i][j] >= 176:
					img[i][j] = 172 + (((i+1)%2)*(j%2)*83)
				elif img[i][j] >= 157:
					img[i][j] = 172
				elif img[i][j] >= 137:
					img[i][j] = 172 - ((i%2)*(j%2)*86)
				elif img[i][j] >= 117:
					img[i][j] = 172 - (((j+i+1)%2)*86)
				elif img[i][j] >= 97:
					img[i][j] = 86 + (((i+1)%2)*(j%2)*86)
				elif img[i][j] >= 78:
					img[i][j] = 86
				elif img[i][j] >= 58:
					img[i][j] = 86 - ((i%2)*(j%2)*86)
				elif img[i][j] >= 38:
					img[i][j] = 86 - (((j+i+1)%2)*86)
				elif img[i][j] >= 18:
					img[i][j] = 0 + (((i+1)%2)*(j%2)*86)
				else:
					img[i][j] = 0
		
		fobj = BytesIO()
		Image.fromarray(img).resize((300, 300)).save(fobj, "GIF")
		frame = Image.open(fobj)
		frames.append(frame)
	
	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=durations, disposal=0, loop=0)
	igif.seek(0)

	return igif
	
@executor_function
def fire_func(img):
	img = Image.open(img)
	colors = [
		(20, 21, 128), (33, 34, 182), (41, 53, 215), (41, 98, 232), (39, 115, 234),
		(0, 90, 255), (0, 154, 255)
	]

	frames = []
	if hasattr(img, 'n_frames') and img.n_frames > 1:
		durations = []
		for i, frame in enumerate(ImageSequence.Iterator(img)):
			if i > 50:
				break
			durations.append(frame.info.get('duration', 50))
			frame = ImageOps.contain(frame, (300, 300)).convert('RGBA')
			frame_np = cv2.cvtColor(np.array(frame), cv2.COLOR_RGBA2BGRA)
			edges = cv2.Canny(frame_np, 300, 300)
			indices = np.where(edges != [0])
			blank = np.zeros((300, 300, 4), np.uint8)
			for x, y in zip(indices[0], indices[1]):
				for i in range(random.randint(5, 35)):
					if i < 3: pct = 0.5
					elif i < 8: pct = 0.4
					elif i < 15: pct = 0.3
					elif i < 20: pct = 0.2
					else: pct = 0.1
					try:
						if random.random() < pct:
							blank[abs(x-i)][y] = *random.choice(colors), 255
					except:
						...

			_, buf = cv2.imencode(".png", blank)
			buf = BytesIO(buf)
			m = Image.open(buf)
			frame.paste(m, (0, 0), m)
			frames.append(frame)
		return wand_gif(frames, durations)
	else:
		img = ImageOps.contain(img, (300, 300)).convert('RGBA')
		img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGRA)
		edges = cv2.Canny(img_np, 300, 300)
		indices = np.where(edges != [0])
		for _ in range(5):
			frame = img.copy()
			blank = np.zeros((300, 300, 4), np.uint8)
			for x, y in zip(indices[0], indices[1]):
				for i in range(random.randint(5, 35)):
					try:
						if i < 3: pct = 0.5
						elif i < 8: pct = 0.4
						elif i < 15: pct = 0.3
						elif i < 20: pct = 0.2
						else: pct = 0.1
						if random.random() < pct:
							blank[abs(x-i)][y] = *random.choice(colors), 255
					except:
						...
			_, buf = cv2.imencode(".png", blank)
			buf = BytesIO(buf)
			m = Image.open(buf)
			frame.paste(m, (0, 0), m)
			frames.append(frame)

		return wand_gif(frames, 50)

@executor_function
def endless_func(img):
	img = Image.open(img)
	pts1 = np.float32([[0, 0], [300, 0], [0, 300], [300, 300]])
	pts2 = np.float32([[100, 200], [200, 200], [0, 301], [300, 301]])
	M = cv2.getPerspectiveTransform(pts1, pts2)

	frames = []
	durations = []
	for i, frame in enumerate(ImageSequence.Iterator(img)):
		if i > 100:
			break
		durations.append(frame.info.get('duration', 50))
		frame = cv2.cvtColor(np.array(ImageOps.contain(frame.convert('RGBA'), (300, 300))), cv2.COLOR_RGBA2BGRA)
		dst = cv2.warpPerspective(frame, M, (300, 300), borderMode=cv2.BORDER_WRAP)
		_, buf = cv2.imencode(".png", dst)
		buf = BytesIO(buf)
		frames.append(Image.open(buf))

	return wand_gif(frames, durations)

@executor_function
def bayer_func(img):
	img = Image.open(img)
	frames = []
	durations = []
	for frame in ImageSequence.Iterator(img):
		if frame.tell() > 100:
			break
		durations.append(frame.info.get('duration', 50))
		npa = np.array(ImageOps.contain(frame.convert('RGB'), (100, 100), Image.BICUBIC), dtype=np.uint8)
		w, h, _ = npa.shape
		ra = np.zeros((2*w, 2*h, 3), dtype=np.uint8)
		ra[::2, ::2, 2] = npa[:, :, 2]
		ra[1::2, ::2, 1] = npa[:, :, 1]
		ra[::2, 1::2, 1] = npa[:, :, 1]
		ra[1::2, 1::2, 0] = npa[:, :, 0]
		frames.append(ImageOps.contain(Image.fromarray(ra, "RGB"), (300, 300)))

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=durations, disposal=0, loop=0)
	igif.seek(0)

	return igif

@executor_function
def slice_func(img):
	img = ImageOps.fit(Image.open(img), (512, 512)).convert('RGBA')
	npa = np.array(img)
	frames = []
	frames.append(img)
	for i in range(1, 8):
		if i % 2 == 0:
			for x in range(512):
				w = int(512 / 2 ** i)
				if x % w // (w//2) == 0:
					npa[x] = np.roll(npa[x], w)
				else:
					npa[x] = np.roll(npa[x], -w)
			npa = np.rot90(npa)
			frames.append(Image.fromarray(npa).rotate(0))
		else:
			for x in range(512):
				w = int(512 / 2 ** i)
				if x % w // (w//2) == 0:
					npa[x] = np.roll(npa[x], w)
				else:
					npa[x] = np.roll(npa[x], -w)
			npa = np.rot90(npa, -1)
			frames.append(Image.fromarray(np.rot90(npa)).rotate(0))

	return wand_gif(frames, 1000)

@executor_function
def spikes_func(img):
	img = ImageOps.contain(Image.open(img), (300, 300)).convert('RGBA')
	w, h = img.size
	line_length = 20
	frames = []
	for _ in range(10):
		canv = Image.new('RGBA', (w, h))
		draw = ImageDraw.Draw(canv)
		for _ in range(5000):
			x1, y1 = random.randint(20, w-20), random.randint(20, h-20)
			angle = random.randint(0, 360)
			x2, y2 = x1 + line_length * math.cos(angle), y1 + line_length*math.sin(angle)
			mx, my = (x2 + x1) / 2, (y2 + y1) / 2
			if (pix := img.getpixel((mx, my)))[-1] != 0:
				draw.line([x1, y1, x2, y2], pix)
		frames.append(canv)
	return wand_gif(frames, 100)

@executor_function
def blocks_func(img):
	img = ImageOps.contain(Image.open(img), (300, 300)).convert('RGBA')
	w, h = img.size
	line_length = 20
	frames = []
	for _ in range(10):
		canv = Image.new('RGBA', (w, h))
		draw = ImageDraw.Draw(canv)
		for _ in range(5000):
			x1, y1 = random.randint(20, w-20), random.randint(20, h-20)
			angle = random.randint(0, 360)
			x2, y2 = x1 + line_length * math.cos(angle), y1 + line_length*math.sin(angle)
			mx, my = (x2 + x1) / 2, (y2 + y1) / 2
			if (pix := img.getpixel((mx, my)))[-1] != 0:
				draw.rectangle([x1, y1, x2, y2], pix)
		frames.append(canv)
	return wand_gif(frames, 100)

@executor_function
def letters_func(img):
	img = ImageOps.contain(Image.open(img), (300, 300)).convert('RGBA')
	w, h = img.size
	frames = []
	for _ in range(10):
		canv = Image.new('RGBA', (w, h))
		draw = ImageDraw.Draw(canv)
		for _ in range(1000):
			x, y = random.randint(20, w-20), random.randint(20, h-20)
			if (pix := img.getpixel((x, y)))[-1] != 0:
				draw.text([x, y], random.choice(string.ascii_letters), pix, font_arial3, 'mm')
		frames.append(canv)
	return wand_gif(frames, 100)

@executor_function
def bricks_func(img):
	img = Image.open(img)
	w, h = img.size

	frames = []
	durations = []
	for frame in ImageSequence.Iterator(img):
		if frame.tell() > 100:
			break
		durations.append(frame.info.get('duration', 50))
		frame = ImageOps.contain(frame, (400, 400)).convert('RGBA')
		canv = Image.new('RGBA', frame.size)
		draw = ImageDraw.Draw(canv)

		for i in range(h):
			for j in range(w):
				try:
					if j % 2 == 0:
						draw.rectangle((40*i, 20*j, 35+i*40, 15+j*20), frame.getpixel((40*i+10, 20*j+7)))
					else:
						draw.rectangle((40*i-20, 20*j, 35+i*40-20, 15+j*20), frame.getpixel((40*i-20+10, 20*j+7)))
				except:
					...
		frames.append(canv)

	return wand_gif(frames, durations)

@executor_function
def tiles_func(img, n_edges):
	img = ImageOps.fit(Image.open(img), (300, 300)).convert('RGBA')
	frames = []
	for r in np.linspace(0, 360//n_edges, 50):
		canv = Image.new('RGBA', (300, 300))
		draw = ImageDraw.Draw(canv)
		for i in range(15):
			for j in range(15):
				draw.regular_polygon([i*20+10, j*20+10, 10], n_edges, r, img.getpixel((i*20+10, j*20+10)), 'black')
		frames.append(canv)

	return wand_gif(frames)

@executor_function
def wiggle_func(img):
	img = ImageOps.contain(Image.open(img), (300, 300)).convert('RGBA')
	npa = np.array(img)
	rows, cols, _ = npa.shape

	frames = []
	for n in range(-100, 100, 10):
		out = np.zeros(npa.shape, np.uint8)
		for i in range(rows):
			for j in range(cols):
				x = int(np.sin(np.pi * i / rows * 3) * n)
				out[i, j] = npa[i, (j+x) % cols]
		frames.append(out)

	frames += frames[-2:0:-1]
	
	return wand_gif(frames, 30)

@executor_function
def cube_func(img):
	bg = Image.new('RGBA', (300, 300), 'black')
	img = ImageOps.fit(Image.open(img), (300, 300)).convert('RGBA')
	bg.paste(img, (0, 0), img)
	bg = bg.convert('RGB')

	buf = BytesIO()
	bg.save(buf, 'PNG')
	buf.seek(0)

	tex = pv.Texture(imageio.imread(buf))

	mesh = cube_mesh.copy(deep=False)

	pl = pv.Plotter(off_screen=True, window_size=[350, 350])

	camera = pv.Camera()
	camera.position = 3.7, 3.7, 3.7
	camera.focal_point = 0, 0, 0
	pl.camera = camera

	frames = []
	for i in np.linspace(0, 355, 50):
		rot = mesh.rotate_y(i, inplace=False)
		actor = pl.add_mesh(rot, texture=tex, smooth_shading=True)
		buf = BytesIO()
		pl.screenshot(buf)
		buf.seek(0)
		frames.append(Image.open(buf))
		pl.remove_actor(actor)
	pl.close()

	return wand_gif(frames, 50)

@executor_function
def paint_func(img):
	img = ImageOps.fit(Image.open(img), (300, 300)).convert('RGBA')
	masks = brush_mask

	frames = []
	durations = []
	for mask in ImageSequence.Iterator(masks):
		canv = Image.new('RGBA', (300, 300))
		canv.paste(img, (0, 0), mask.convert('L').resize((300, 300)))
		frames.append(canv)
		durations.append(50)

	durations[-1] = 1000
	return wand_gif(frames, durations)

@executor_function
def shine_func(img):
	img = ImageOps.contain(Image.open(img).convert('RGBA'), (300, 300))
	npa = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGRA)

	edges = cv2.Canny(npa, 300, 300)
	indices = np.where(edges != [0])
	spots = random.choices(tuple(zip(*indices)), k=100)

	s_min = 5
	s_max = 35

	N = s_max - s_min
	sizes = random.choices(range(0, N), k=100)
	
	frames = []
	for i in range(N*2-2):
		frame = img.copy()
		for (x, y), s in zip(spots, sizes):
			k = i + s
			if k < N:
				size = k
			else:
				if k < N * 2 - 1:
					size = N - k % N - 2
				else:
					size = (k + 1) % N + 1
			size += s_min
			star = flare_img.copy().resize((size, size))
			frame.paste(star, (y-size//2, x-size//2), star)
		frames.append(frame)
	
	return wand_gif(frames)

@executor_function
def neon_func(img):
	img = ImageOps.contain(Image.open(img).convert('RGBA'), (300, 300))
	npa = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGRA)
	w, h = img.size
	edges = cv2.Canny(npa, w, h)
	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
	
	mask = cv2.dilate(edges, kernel, iterations=1)
	_, buf = cv2.imencode(".png", mask)
	buf = BytesIO(buf)
	mask = Image.open(buf)

	frames = []
	for i, angle in zip(np.linspace(0, 1, 100), np.linspace(0, 8*np.pi, 100)):
		frame = img.copy()
		rgb = [int(c*255) for c in colorsys.hsv_to_rgb(i, 1.0, 1.0)] + [255]
		colored = Image.new('RGBA', img.size, tuple(rgb))
		x, y = int(5 * math.cos(angle)), int(5 * math.sin(angle))
		frame.paste(colored, (x, y), mask)
		frames.append(frame.crop((5, 5, w-5, h-5)))

	return wand_gif(frames)

@executor_function
def phone_func(img):
	w, h = 150, 238
	img = ImageOps.contain(Image.open(img).convert('RGBA'), (w, h))

	iw, ih = img.size
	canv = Image.new('RGBA', (w, h), 'white')
	canv.paste(img, (w//2-iw//2, h//2-ih//2), img)

	npa = cv2.cvtColor(np.array(canv), cv2.COLOR_RGBA2BGRA)
	pts1 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
	pts2 = np.float32([[8, 0], [w-4, 2], [0, h-2], [w-10, h+8]])
	M = cv2.getPerspectiveTransform(pts1, pts2)

	dst = cv2.warpPerspective(npa, M, (w, h))
	_, buf = cv2.imencode(".png", dst)
	buf = BytesIO(buf)
	screen = Image.open(buf)

	frames = []
	durations = []
	for i, frame in enumerate(ImageSequence.Iterator(phone_gif)):
		durations.append(frame.info.get('duration', 50))
		frame = frame.convert('RGBA')
		if i == 34:
			frame.paste(screen, (139, 27), screen)
		frames.append(frame)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=durations, disposal=0, loop=0)
	igif.seek(0)

	return igif

@executor_function
def kanye_func(img):
	img = Image.open(img)

	frames = []
	durations = []
	for i, frame in enumerate(ImageSequence.Iterator(img)):
		if i > 100:
			break
		durations.append(frame.info.get('duration', 50))

		frame = ImageOps.fit(frame.convert('RGBA'), (263, 326))
		canv = Image.new('RGBA', kanye_img.size)
		canv.paste(frame, (193, 320), frame)
		canv.paste(kanye_img, (0, 0), kanye_img)

		frames.append(ImageOps.contain(canv, (400, 400)))

	return wand_gif(frames, durations)

@executor_function
def flush_func(img):
	img = ImageOps.fit(Image.open(img).convert('RGBA'), (300, 300))
	w, h = toilet_img.size

	frames = []
	for i, j, k in zip(map(int, np.linspace(0, 360*3, 50)), map(int, np.linspace(0, 250, 50)), map(int, np.linspace(0, 200, 50))):
		img = img.resize((300-j, 300-j))
		npa = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGRA)

		result = iaa.ShearY((i, i), fit_output=True).augment_image(npa)
		_, buf = cv2.imencode(".png", result)
		buf = BytesIO(buf)
		sheared = Image.open(buf)
		sw, sh = sheared.size

		canv = Image.new('RGBA', toilet_img.size)
		canv.paste(toilet_img, (0, 0), toilet_img)
		canv.paste(sheared, (w//2-sw//2, h-sh//2-400+k), sheared)

		frames.append(canv)

	return wand_gif(frames)

#
# Utility
# #

def wheel_2(args):
	frames = []

	result = random.choice(args)
	loop = random.choice([4, 5, 6])
	if result == args[1]:
		stop = random.choice([1, 2, 3, 4, 5, 12])
		c = 'green'
	elif result == args[0]:
		stop = random.choice([6, 7, 8, 9, 10, 11])
		c = 'red'

	for _ in range(loop):
		for frame in wheel_images['wheel_2']:
			fobj = BytesIO()
			frame.save(fobj, "gif", transparency=4)
			frame = Image.open(fobj)
			frames.append(frame)

	durations = [50] * (len(frames)-15)
	durations.extend([100]*10)

	for i in range(stop):
		frame = wheel_images['wheel_2'][i]
		
		fobj = BytesIO()
		frame.save(fobj, "GIF", transparency=4)
		frame = Image.open(fobj)
		frames.append(frame)

	durations.extend([300]*(stop+5))

	last_frame = wheel_images['wheel_2'][stop-1]
	buf = BytesIO()
	last_frame.save(buf, "PNG")
	buf.seek(0)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', append_images=frames[1:], save_all=True, duration=durations)
	igif.seek(0)

	return igif, result, sum(durations), buf, c

def wheel_3(args):
	frames = []

	result = random.choice(args)
	loop = random.choice([4, 5, 6])
	if result == args[1]:
		stop = random.choice([4, 5, 6, 7])
		c = 'green'
	elif result == args[0]:
		stop = random.choice([8, 9, 10, 11])
		c = 'red'
	elif result == args[2]:
		stop = random.choice([1, 2, 3, 12])
		c = 'blue'

	for _ in range(loop):
		for frame in wheel_images['wheel_3']:
			fobj = BytesIO()
			frame.save(fobj, "gif", transparency=5)
			frame = Image.open(fobj)
			frames.append(frame)

	durations = [50] * (len(frames)-15)
	durations.extend([100]*10)

	for i in range(stop):
		frame = wheel_images['wheel_3'][i]

		fobj = BytesIO()
		frame.save(fobj, "gif", transparency=5)
		frame = Image.open(fobj)
		frames.append(frame)

	durations.extend([300]*(stop+5))

	last_frame = wheel_images['wheel_3'][stop-1]
	buf = BytesIO()
	last_frame.save(buf, "PNG")
	buf.seek(0)
	
	igif = BytesIO()
	frames[0].save(igif, format='gif', append_images=frames[1:], save_all=True, duration=durations)
	igif.seek(0)

	return igif, result, sum(durations), buf, c

def wheel_4(args):
	frames = []

	result = random.choice(args)
	loop = random.choice([4, 5, 6])
	if result == args[1]:
		stop = random.choice([7, 8, 9])
		c = 'green'
	elif result == args[0]:
		stop = random.choice([10, 11, 12])
		c = 'red'
	elif result == args[2]:
		stop = random.choice([4, 5, 6])
		c = 'blue'
	elif result == args[3]:
		stop = random.choice([1, 2, 3])
		c = 'yellow'

	for _ in range(loop):
		for frame in wheel_images['wheel_4']:
			fobj = BytesIO()
			frame.save(fobj, "gif", transparency=6)
			frame = Image.open(fobj)
			frames.append(frame)

	durations = [50] * (len(frames)-15)
	durations.extend([100]*10)

	for i in range(stop):
		frame = wheel_images['wheel_4'][i]

		fobj = BytesIO()
		frame.save(fobj, "gif", transparency=6)
		frame = Image.open(fobj)
		frames.append(frame)

	durations.extend([300]*(stop+5))

	last_frame = wheel_images['wheel_4'][stop-1]
	buf = BytesIO()
	last_frame.save(buf, "PNG")
	buf.seek(0)

	igif = BytesIO()
	frames[0].save(igif, format='gif', append_images=frames[1:], save_all=True, duration=durations)
	igif.seek(0)

	return igif, result, sum(durations), buf, c

def wheel_6(args):
	frames = []

	result = random.choice(args)
	loop = random.choice([4, 5, 6])
	if result == args[1]:
		stop = random.choice([7, 8])
		c = 'green'
	elif result == args[0]:
		stop = random.choice([9, 10])
		c = 'red'
	elif result == args[2]:
		stop = random.choice([5, 6])
		c = 'blue'
	elif result == args[3]:
		stop = random.choice([3, 4])
		c = 'yellow'
	elif result == args[4]:
		stop = random.choice([1, 2])
		c = 'orange'
	elif result == args[5]:
		stop = random.choice([11, 12])
		c = 'purple'

	for _ in range(loop):
		for frame in wheel_images['wheel_6']:
			fobj = BytesIO()
			frame.save(fobj, "gif", transparency=8)
			frame = Image.open(fobj)
			frames.append(frame)

	durations = [50] * (len(frames)-15)
	durations.extend([100]*10)

	for i in range(stop):
		frame = wheel_images['wheel_6'][i]

		fobj = BytesIO()
		frame.save(fobj, "gif", transparency=8)
		frame = Image.open(fobj)
		frames.append(frame)

	durations.extend([300]*(stop+5))

	last_frame = wheel_images['wheel_6'][stop-1]
	buf = BytesIO()
	last_frame.save(buf, "PNG")
	buf.seek(0)
	
	igif = BytesIO()
	frames[0].save(igif, format='gif', append_images=frames[1:], save_all=True, duration=durations, include_color_table=True)
	igif.seek(0)

	return igif, result, sum(durations), buf, c

@executor_function
def wheel_func(args):
	l = len(args)
	if l == 2: return wheel_2(args)
	elif l == 3: return wheel_3(args)
	elif l == 4: return wheel_4(args)
	elif l == 6: return wheel_6(args)

@executor_function
def circle_func(img, size):
	img = Image.open(img).resize((size))
	mask = Image.new('RGBA', size, (0, 0, 0, 0))
	mask_drawing = ImageDraw.Draw(mask)
	mask_drawing.ellipse((0, 0, *size), 'white')

	frames = []
	durations = []
	for i, frame in enumerate(ImageSequence.Iterator(img)):
		if i > 100:
			break

		durations.append(frame.info.get('duration', 50))
		canv = Image.new('RGBA', size, (0, 0, 0, 0))
		canv.paste(img, (0, 0), mask)
		frames.append(canv)

	return wand_gif(frames, durations)

@executor_function
def scrap_func(text):
	wrapped = TextWrapper(width=10).wrap(text.upper().strip())
	wrapped = [row.center(max(len(row) for row in wrapped), ' ') for row in wrapped]

	crop_to = (max(len(row) for row in wrapped)*210, len(wrapped)*210)
	frames = []
	for _ in range(5):
		canvas = Image.new('RGB', (2500, 2500), 'white')
		x, y = 0, 0

		for row in wrapped:
			for let in row:
				if let not in scrap_letters.keys():
					x += 150
					continue

				let_img = random.choice(scrap_letters[let])
				
				let_img.thumbnail((200, 200), Image.ANTIALIAS)
				canvas.paste(let_img, (x, y), let_img)

				x += let_img.size[0] + 20
			x = 0
			y += 220
		
		canvas = canvas.crop((0, 0, *crop_to))
		npa = np.array(canvas)
		if npa.min() == 255:
			return None

		fobj = BytesIO()
		canvas.save(fobj, "GIF", transparency=0)
		canvas = Image.open(fobj)
		frames.append(canvas)

	igif = BytesIO()
	frames[0].save(igif, format='GIF', save_all=True, append_images=frames[1:], duration=500, loop=0, disposal=2)
	igif.seek(0)
	return igif

@executor_function
def scrolling_text_func(text):
	texted = (text + ' ') * 20
	tl = font_arial4.getlength(text + ' ')

	frames = []
	for i in np.linspace(0, tl, 100):
		canv = Image.new('RGBA', (400, 100))
		draw = ImageDraw.Draw(canv)
		draw.text((20-i, 50), texted, 'white', font_arial4, 'lm')
		frames.append(canv)

	return wand_gif(frames, 50)

@executor_function
def img_to_emoji_func(image, best):
	with Image.open(image) as image4:
		im = image4.resize((best, best)).convert("RGBA")
		im = ImageOps.mirror(im)
		h = []
		x = 0

		dat = [
			(56, 56, 56), (242, 242, 242), (247, 99, 12), (0, 120, 215), (232, 18, 36), 
			(142, 86, 46), (136, 108, 228), (22, 198, 12), (255, 241, 0)
		]

		dat2 = "⬛⬜🟧🟦🟥🟫🟪🟩🟨"
		data = list(im.getdata())

		for p in data:
			x += 1
			p = list(p)

			def myFunc(e):
				r = p[0]
				g = p[1]
				b = p[2]

				er = e[0]
				eg = e[1]
				eb = e[2]

				return abs(r - er) + abs(g - eg) + abs(b - eb)

			if p[3] < 5:
				h.append("⬛")
			else:
				newlis = dat.copy()
				newlis.sort(key=myFunc)
				h.append(dat2[dat.index(newlis[0])])

			if x % im.width == 0:
				h.append("\n")

		al = [[] for _ in range(best)]
		row = 0
		for el in h:
			if el == '\n':
				row += 1
			else:
				al[row].append(el)
		
		text = '\n'.join([''.join(row[::-1]) for row in al])
		
		return text

@executor_function
def typerace_func(text):
	img = Image.new('RGB', (1200, 700), 'black')

	lines = textwrap.wrap(text, width=25)
	draw = ImageDraw.Draw(img)
	
	for i, line in enumerate(lines):
		draw.text((30, 30+80*i), line, font=tfont)

	buf = BytesIO()
	img.save(buf, 'PNG')
	buf.seek(0)

	return buf

@executor_function
def skyline_func(contributions, username, year):
	mx = [[]]
	for week in contributions:
		if week['week'] == 0:
			for _ in range(7-len(week['days'])):
				mx[week['week']].append(0)

		for day in week['days']:
			mx[week['week']].append(day['count'])

		if week['week'] == contributions[-1]['week']:
			for _ in range(7-len(week['days'])):
				mx[week['week']].append(0)
		else:
			mx.append([])

	columns = []
	for i, row in enumerate(mx, 1):
		for j, e in enumerate(row, 1):
			columns.append(pv.Box((i, i+1, j, j+1, 0 if not e else 1+e*0.5, 0)))

	merged_column = columns[0].merge(columns[1:])

	text_username = pv.Text3D(username).translate([5, -1, -1], inplace=True).rotate_x(60, inplace=True).scale([2, 2, 2], inplace=True)
	text_year = pv.Text3D(year).translate([20, -1, -1], inplace=True).rotate_x(60, inplace=True).scale([2, 2, 2], inplace=True)

	merged = merged_column.merge([text_username, text_year])

	p = pv.Plotter(off_screen=True, window_size=(450, 350))

	light_1 = pv.Light(position=(5, 3, 10), focal_point=(0, 0, 0), color='purple')
	light_2 = pv.Light(position=(5, -3, 10), focal_point=(0, 0, 0), color='orange')
	p.add_light(light_1)
	p.add_light(light_2)

	p.camera.position = (146, 20, 20)
	body = merged.scale((1.3, 1.3, 1.3), inplace=True)

	frames = []
	for i in np.linspace(0, 355, 50):
		rot = body.rotate_z(i, point=body.center, inplace=False).translate((0, 0, -10), inplace=True)
		actor = p.add_mesh(rot, color='linen', pbr=True, metallic=0.8, roughness=0.4, diffuse=0.2, specular=1, specular_power=15)
		buf = BytesIO()
		p.screenshot(buf)
		buf.seek(0)
		frames.append(Image.open(buf))
		p.remove_actor(actor)
	p.close()

	return wand_gif(frames[1:], 100)

@executor_function
def spotify_func(title, artists, cover_buf, duration_seconds, start_timestamp):
	def shorten(text, font, max_length):
		res = ''
		for c in text:
			res += c
			if font.getlength(res) > max_length:
				res = res[:-2] + '...'
				break

		return res

	cover = Image.open(cover_buf).convert('RGBA').resize((256, 256))
	color = ColorThief(cover_buf).get_color(quality=1)
	gray = np.mean((0.2989*color[0], 0.5870*color[1], 0.1140*color[2]))
	fcolor = 'white' if gray < 65 else 'black'
	
	img = Image.new('RGBA', (1392, 368), (0, 0, 0, 0))
	draw = ImageDraw.Draw(img)
	draw.rounded_rectangle((0, 0, 1392, 368), 50, color)
	shadow = Image.new('RGBA', (256, 256), (25, 25, 25, 240))
	img.paste(shadow, (60, 60), shadow)
	img.paste(cover, (56, 56), cover)
	artists_text = ', '.join(artists)

	draw.text((368, 47), shorten(title, sfont_title, 945), fcolor, font=sfont_title)
	draw.text((368, 125), shorten(artists_text, sfont_auth, 945), fcolor, font=sfont_auth)

	end_minutes, end_seconds = divmod(duration_seconds, 60)
	on_minutes, on_seconds = divmod((dt.datetime.now()-dt.datetime.fromtimestamp(start_timestamp)).seconds, 60)
	draw.text((368, 256), f"{on_minutes:02}:{on_seconds:02}", fcolor, font=sfont)
	draw.text((1200, 256), f"{end_minutes:02}:{end_seconds:02}", fcolor, font=sfont)

	fbar = Image.new('RGBA', (640, 10), (255, 255, 255, 100))
	img.paste(fbar, (530, 270), fbar)
	end_pos = int(((dt.datetime.now()-dt.datetime.fromtimestamp(start_timestamp)).seconds/duration_seconds)*640)
	bar = Image.new('RGBA', (end_pos, 10), fcolor)
	img.paste(bar, (530, 270), bar)
	draw.ellipse((530+end_pos-15, 276-15, 530+end_pos+15, 276+15), fill=fcolor)

	buf = BytesIO()
	img.save(buf, 'PNG')
	buf.seek(0)

	return buf

@executor_function
def player_func(title, seconds_played, total_seconds, thumbnail_buf, line_1, line_2):
	thumbnail = ImageOps.fit(Image.open(thumbnail_buf).convert('RGBA'), (455, 256))
	color = ColorThief(thumbnail_buf).get_color(quality=1)
	gray = np.mean((0.2989*color[0], 0.5870*color[1], 0.1140*color[2]))
	fcolor = 'white' if gray < 65 else 'black'

	img = Image.new('RGBA', (1392, 368), (0, 0, 0, 0))
	draw = ImageDraw.Draw(img)
	draw.rounded_rectangle((0, 0, 1392, 368), 50, color)
	shadow = Image.new('RGBA', thumbnail.size, (25, 25, 25, 240))
	img.paste(shadow, (60, 60), shadow)
	img.paste(thumbnail, (56, 56), thumbnail)

	draw.text((557, 50), title if len(title) <= 20 else title[:23] + '...', fcolor, font=player_bold_60)
	if line_1:
		draw.text((557, 120), line_1 if len(line_1) <= 35 else line_1[:38] + '...', fcolor, font=player_reg)
	if line_2:
		draw.text((557, 170), line_2 if len(line_2) <= 35 else line_2[:38] + '...', fcolor, font=player_reg)

	end_minutes, end_seconds = divmod(int(total_seconds), 60)
	on_minutes, on_seconds = divmod(int(seconds_played), 60)
	draw.text((615, 270), f"{on_minutes:02}:{on_seconds:02}", fcolor, anchor='mt', font=player_bold_40)
	draw.text((1255, 256), f"{end_minutes:02}:{end_seconds:02}", fcolor, font=player_bold_40)

	fbar = Image.new('RGBA', (555, 10), (255, 255, 255, 100))
	img.paste(fbar, (685, 280), fbar)
	end_pos = int(seconds_played / total_seconds * 555)
	bar = Image.new('RGBA', (end_pos, 10), fcolor)
	img.paste(bar, (685, 280), bar)
	draw.ellipse((685 + end_pos - 15, 285 - 15, 685 + end_pos + 15, 285 + 15), fill=fcolor)

	buf = BytesIO()
	img.save(buf, 'PNG')
	buf.seek(0)

	return buf
