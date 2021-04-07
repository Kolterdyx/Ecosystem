from additional import *
from food import *

class Cell:
	@dispatch(object, Vector, dict)
	def __init__(self, parent, pos, genes):
		self.parent = parent
		self.pos = pos
		self.genes = genes
		self.screen = self.parent.enviroment
		self.simulation = self.parent.simulation

		self.get_name()

		self.vision = self.genes["vision"]
		self.speed = self.genes["speed"]
		self.appeal = self.genes["appeal"]

		self.repUrge = 0
		self.age = 0
		self.ageCounter = 0
		self.hunger = 0
		self.foodWanted = 0
		self.vel = Vector(1, 0).rotate(random(360))
		self.vel.scale_to_length(self.speed)
		self.vel.rotate(random(360))
		self.bestFood = Food(-10)
		self.possibleFood = []
		self.mate = None
		self.bestMate = None
		self.mateVision = 300
		self.possibleMates = []
		self.children = []
		self.parents = []
		self.taken = False
		self.priorityMargin = 3000
		self.repThreshold = 4000
		self.agingThreshold = 1000
		self.overrideWander = False
		self.dead = False

		if self.appeal < 0:
			self.appeal = 0
			self.genes["appeal"] = 0

		self.size = 5

		self.highlight = False

	@dispatch(int)
	def __init__(self, appeal):
		self.appeal = -10
		self.mate = None
		self.taken = False
		self.repUrge = 0

	def get_name(self):
		consonants = list("wrtypsdfghjklzxcvbnm")
		vowels = list("aeiou")
		letters = consonants+vowels


		nameLen = random(4,7)
		self.name = [None]*nameLen
		for i in range(nameLen):
			if i<1:
				self.name[i] = choice(letters)
			else:
				l = self.name[i-1]
				if l in consonants:
					self.name[i] = choice(vowels)
				elif l in vowels:
					if randomBool():
						if i>1 and self.name[i-2] not in vowels:
							tmp = list("aeiou")
							tmp.remove(l)
							self.name[i] = choice(tmp)
						else:
							self.name[i] = choice(consonants)
					else:
						self.name[i] = choice(consonants)

		self.name[0] = self.name[0].upper()
		self.name.remove(None) if None in self.name else None
		self.name = "".join(self.name)

		for i in self.parent.cells:
			if i != self and i.name == self.name:
				self.get_name()
		for i in self.parent.dead:
			if i != self and i.name == self.name:
				self.get_name()

	def live(self, delta):
		self.delta = delta

		foundFood = self.findFood()
		foundMate = self.findMate() if (self.repUrge > self.repThreshold and not self.taken) else False

		if not foundFood and not foundMate and not self.taken:
			self.wander()

		if self.taken and self.mate:
			self.reproduce(self.mate)

		if self.hunger > 10000:
			self.repUrge = 0
			foundMate = self.taken = False
			if self.mate is not None:
				self.mate = None
			self.wander()

		if foundFood and not (self.mate and self.hunger < 5000):
			self.bestFood = Food(-10)
			for f in self.possibleFood:
				if f.ammount > self.bestFood.ammount:
					self.bestFood = f
			tmp = self.bestFood.pos - self.pos
			angle = self.vel.angle_to(tmp)
			self.vel = self.vel.rotate(angle)
			self.move()
			if (self.pos - self.bestFood.pos).length() < self.size:
				self.eat(self.bestFood)


		if foundMate:
			self.bestMate = None
			for r in self.possibleMates:
				if self.bestMate:
					if r.appeal > self.bestMate.appeal:
						self.bestMate = r
				else:
					self.bestMate = r if r!= self else None

			if self.bestMate is not None and (not self.bestMate.taken or self.bestMate.mate == self):
				self.mate = self.bestMate
				self.mate.mate = self
				self.mate.taken = True
				self.taken = True
				self.reproduce(self.mate)

		if self.age>4:
			self.size = 10
			self.repUrge+=1
		self.hunger += 1
		if self.hunger >= 3000 and self.hunger%1500==0:
			self.foodWanted+=2
		if self.hunger < 0:
			self.hunger = 0

		self.ageCounter += 1
		self.age = round(self.ageCounter/self.agingThreshold)

		if self.age > 50:
			if random(0,1000) == 1:
				self.parent.ageDeaths += 1
				self.deathCause = "old age"
				self.die()
		if self.hunger > 20000:
			self.parent.hungerDeaths += 1
			self.deathCause = "hunger"
			self.die()

	def findFood(self):
		self.possibleFood = []
		if self.foodWanted > 0:
			for f in self.parent.food:
				if (self.pos - (f.pos)).length() < self.vision:
					self.possibleFood.append(f)
			if self.possibleFood != []:
				return True
		return False

	def findMate(self):
		self.possibleMates = []
		for r in self.parent.cells:
			if (self.pos - r.pos).length() < self.mateVision and r != self and r.age > 4 and r.repUrge>self.repThreshold:
				self.possibleMates.append(r)
		if self.possibleMates != []:
			return True
		return False

	def eat(self, food):
		tmp = food.copy()
		tmp.ammount -= self.hunger
		self.hunger -= food.ammount
		if tmp.ammount <= 0:
			self.parent.food.remove(food)
		else:
			food.ammount = tmp.ammount
		if self.hunger == 0:
			self.foodWanted = 0
		else:
			self.foodWanted -= 1

	def reproduce(self, mate):
		self.mutationRate = self.parent.mutationSlider.mark
		if self.taken and self.mate:
			tmp = self.mate.pos - self.pos
			angle = self.vel.angle_to(tmp)
			self.vel = self.vel.rotate(angle)
			self.move()

			if (self.mate.pos - self.pos).length() < self.size:
				mate.repUrge = -self.repThreshold
				mate.mate = None
				mate.taken = False
				if self.age > 4:
					genesA = self.genes
					genesB = mate.genes

					genomes = genesA.keys()
					genesC = {}

					for i in genomes:
						if randomBool():
							genesC[i] = genesA[i]
						else:
							genesC[i] = genesB[i]
						if random(100) < self.mutationRate:
							genesC[i] += random(-5, 5)

					child = Cell(self.parent, self.pos+Vector(self.size, self.size), genesC)
					child.parents = [self.name, mate.name]
					self.parent.cells.append(child)
					self.children.append(child.name)
					mate.children.append(child.name)
					self.repUrge = -self.repThreshold
					self.taken = False
					self.mate = None

	def wander(self):
		self.vel = self.vel.rotate(randf(-5, 5))
		self.move()

	def die(self):
		self.dead = True
		self.parent.deaths += 1
		if self.name not in []:
			self.parent.cells.remove(self)
			self.parent.dead.append(self)

	def move(self):
		self.pos += self.vel*self.delta
		if self.pos.x < 0 or self.pos.x > self.screen.size.x:
			self.vel.x = -self.vel.x

		if self.pos.y < 0 or self.pos.y > self.screen.size.y:
			self.vel.y = -self.vel.y

	def show(self):
		self.screen.stroke(200, 200, 100)
		if self.name in ["Lucía", "Mauro", "Adolfo", "Ciro"]:
			self.screen.stroke(100, 100, 255)
		self.screen.strokeWeight(self.size)
		self.screen.point(self.pos.x, self.pos.y)

		if self.highlight:
			self.screen.strokeWeight(4)
			self.screen.noFill()
			self.screen.stroke(100,100,255)
			self.screen.circle(self.pos.x, self.pos.y, self.size+10)

		if self.mate and self.parent.showMatingLine:
			tmp = (self.mate.pos - self.pos)/2
			self.screen.line(self.pos.x, self.pos.y, self.pos.x+tmp.x, self.pos.y+tmp.y)

	def debug(self):

		self.screen.stroke(255, 255, 0)
		self.screen.strokeWeight(2)
		self.screen.noFill()
		# self.screen.circle(self.pos.x, self.pos.y, self.vision)
		self.screen.stroke(255,10,10)
		# self.screen.circle(self.pos.x, self.pos.y, self.mateVision)
		tmp = self.vel.normalize()
		tmp.scale_to_length(self.size)
		self.screen.stroke(100, 100, 100)
		self.screen.line(self.pos.x, self.pos.y, self.pos.x+tmp.x, self.pos.y+tmp.y)
		self.screen.stroke(255, 255, 0)

		info = [
			self.name
		]

		self.screen.stroke(255, 255, 0)
		self.screen.textFont("nk57-monospace.ttf")
		for i in range(len(info)):
			self.screen.text(info[i], self.pos.x-16, self.pos.y-30-i*15)
