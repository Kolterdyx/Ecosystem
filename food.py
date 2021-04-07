from additional import *
from multipledispatch import dispatch

class Food:
	@dispatch(object, Vector)
	def __init__(self, parent, pos):
		self.parent = parent
		self.pos = pos
		self.ammount = random(1000, 5000)

		self.screen = self.parent.enviroment

		self.size = 2.5

	@dispatch(int)
	def __init__(self, amm):
		self.ammount = amm
		self.pos = Vector(-1000000000000000, -1000000000000000)

	def copy(self):
		return Food(self.ammount)

	def show(self):
		self.screen.stroke(255)
		self.screen.strokeWeight(round(self.size*self.ammount/3000)+1)
		self.screen.point(self.pos.x-self.size/2, self.pos.y-self.size/2)
