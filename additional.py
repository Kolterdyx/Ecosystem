from random import randint, uniform as randf, choice
import pygame as pg
import pgui
from pgui import Button, Entry, Slider, CheckBox
import time
import math

Vector = pg.math.Vector2

pg.init()

false = False
true = True

width = 1200
height = 900

screen = pg.display.set_mode((width, height))
weight = 1
color = (255, 255, 255)
noFill = True


class Canvas:
	def __init__(self, x, y, w, h):
		self.pos = Vector(x, y)
		self.size = Vector(w, h)
		self.width = w
		self.height = h

		self.rect = pg.Rect(self.pos, self.size)
		self.image = pg.Surface(self.size)

		self.weight = 1
		self.color = (255, 255, 255)
		self.hollow = True

		self.font = pg.font.SysFont("Monospace", 12)

	def show(self):
		screen.blit(self.image, self.rect)

	def border(self, width, r=0, g=0, b=0):
		strokeWeight(width)
		stroke(r) if not (g or b) else stroke(r,g,b)
		line(self.pos.x, self.pos.y, self.pos.x+self.width, self.pos.y)
		line(self.pos.x, self.pos.y, self.pos.x, self.pos.y+self.height)
		line(self.pos.x+self.width, self.pos.y, self.pos.x+self.width, self.pos.y+self.height)
		line(self.pos.x, self.pos.y+self.height, self.pos.x+self.width, self.pos.y+self.height)

	def circle(self, x, y, radius):
		if self.hollow:
			pg.draw.ellipse(self.image, self.color, (x-radius, y-radius, radius*2, radius*2), self.weight)
		else:
			pg.draw.ellipse(self.image, self.color, (x-radius, y-radius, radius*2, radius*2))

	def background(self, r, g=False, b=False):
		if not g and not b:
			self.image.fill((r,r,r))
		else:
			self.image.fill((r,g,b))

	def stroke(self, r, g=False, b=False):
		if not g and not b:
			self.color = (r, r, r)
		else:
			self.color = (r, g, b)

	def strokeWeight(self, i):
		self.weight = i

	def point(self, x, y):
		self.circle(x, y, self.weight)

	def noFill(self):
		self.hollow = True

	def fill(self):
		self.hollow = False

	def line(self, x1, y1, x2, y2):
		pg.draw.line(self.image, self.color, (x1, y1), (x2, y2), self.weight)

	def rect(self, x, y, w, h):
		if self.hollow:
			pg.draw.rect(self.image, self.color, (x, y, w, h), self.weight)
		else:
			pg.draw.rect(self.image, self.color, (x, y, w, h))


	def text(self, message, x, y):
		text = self.font.render(message, True, self.color)
		rect = text.get_rect(topleft=(x, y))
		self.image.blit(text, rect)


############################################## GLOBAL FUNCTIONS #########################################################

def circle(x, y, radius):
	global noFill
	if noFill:
		pg.draw.ellipse(screen, color, (x-radius, y-radius, radius*2, radius*2), weight)
	else:
		pg.draw.ellipse(screen, color, (x-radius, y-radius, radius*2, radius*2))

def background(r, g=False, b=False):
	if not g and not b:
		screen.fill((r,r,r))
	else:
		screen.fill((r,g,b))

def stroke(r, g=False, b=False):
	global color
	if not g and not b:
		color = (r, r, r)
	else:
		color = (r, g, b)
def random(a, b=None):
	if b:
		return randint(a, b)
	else:
		return randint(0, a)

def strokeWeight(i):
	global weight
	weight = i

def point(x, y):
	global weight
	circle(x, y, weight)
def noFill():
	global noFill
	noFill = True

def fill():
	global noFill
	noFill = False

def line(x1, y1, x2, y2):
	pg.draw.line(screen, color, (x1, y1), (x2, y2), weight)

def rect(x, y, w, h):
	if noFill:
		pg.draw.rect(screen, color, (x, y, w, h), weight)
	else:
		pg.draw.rect(screen, color, (x, y, w, h))

fonts = {}
for i in range(10, 72, 2):
	fonts[i] = pg.font.SysFont("Monospace", i)
font = fonts[12]
def textSize(i):
	global font, fonts
	if i in fonts.keys():
		font = fonts[i]

def text(message, x, y):
	global color, font
	text = font.render(message,True,color)
	rect = text.get_rect(topleft=(x, y))
	screen.blit(text, rect)

def randomBool():
	return random(1) > 0.5

#################################### PERLIN NOISE ####################################
def noise(x=randf(-1,1), y=randf(-1,1), z=randf(-1,1)):
	X = int(x) & 255				  # FIND UNIT CUBE THAT
	Y = int(y) & 255				  # CONTAINS POINT.
	Z = int(z) & 255
	x -= int(x)								# FIND RELATIVE X,Y,Z
	y -= int(y)								# OF POINT IN CUBE.
	z -= int(z)
	u = fade(x)								# COMPUTE FADE CURVES
	v = fade(y)								# FOR EACH OF X,Y,Z.
	w = fade(z)
	A = p[X  ]+Y; AA = p[A]+Z; AB = p[A+1]+Z	  # HASH COORDINATES OF
	B = p[X+1]+Y; BA = p[B]+Z; BB = p[B+1]+Z	  # THE 8 CUBE CORNERS,

	return lerp(w, lerp(v, lerp(u, grad(p[AA  ], x  , y  , z   ),  # AND ADD
								   grad(p[BA  ], x-1, y  , z   )), # BLENDED
						   lerp(u, grad(p[AB  ], x  , y-1, z   ),  # RESULTS
								   grad(p[BB  ], x-1, y-1, z   ))),# FROM  8
				   lerp(v, lerp(u, grad(p[AA+1], x  , y  , z-1 ),  # CORNERS
								   grad(p[BA+1], x-1, y  , z-1 )), # OF CUBE
						   lerp(u, grad(p[AB+1], x  , y-1, z-1 ),
								   grad(p[BB+1], x-1, y-1, z-1 ))))

def fade(t):
	return t ** 3 * (t * (t * 6 - 15) + 10)

def lerp(t, a, b):
	return a + t * (b - a)

def grad(hash, x, y, z):
	h = hash & 15					  # CONVERT LO 4 BITS OF HASH CODE
	u = x if h<8 else y				# INTO 12 GRADIENT DIRECTIONS.
	v = y if h<4 else (x if h in (12, 14) else z)
	return (u if (h&1) == 0 else -u) + (v if (h&2) == 0 else -v)

p = [None] * 512
permutation = [151,160,137,91,90,15,
   131,13,201,95,96,53,194,233,7,225,140,36,103,30,69,142,8,99,37,240,21,10,23,
   190, 6,148,247,120,234,75,0,26,197,62,94,252,219,203,117,35,11,32,57,177,33,
   88,237,149,56,87,174,20,125,136,171,168, 68,175,74,165,71,134,139,48,27,166,
   77,146,158,231,83,111,229,122,60,211,133,230,220,105,92,41,55,46,245,40,244,
   102,143,54, 65,25,63,161, 1,216,80,73,209,76,132,187,208, 89,18,169,200,196,
   135,130,116,188,159,86,164,100,109,198,173,186, 3,64,52,217,226,250,124,123,
   5,202,38,147,118,126,255,82,85,212,207,206,59,227,47,16,58,17,182,189,28,42,
   223,183,170,213,119,248,152, 2,44,154,163, 70,221,153,101,155,167, 43,172,9,
   129,22,39,253, 19,98,108,110,79,113,224,232,178,185, 112,104,218,246,97,228,
   251,34,242,193,238,210,144,12,191,179,162,241, 81,51,145,235,249,14,239,107,
   49,192,214, 31,181,199,106,157,184, 84,204,176,115,121,50,45,127, 4,150,254,
   138,236,205,93,222,114,67,29,24,72,243,141,128,195,78,66,215,61,156,180]
for i in range(256):
	p[256+i] = p[i] = permutation[i]

if __name__ == '__main__':
	print("%1.17f" % perlin_noise(3.14, 42, 7))
