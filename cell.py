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
		self.vel = Vector(1, 0).rotate(randint(0, 360))
		self.vel.scale_to_length(self.speed)
		self.vel.rotate(randint(0, 360))
		self.bestFood = Food(-10)
		self.possibleFood = []
		self.mate = None
		self.bestMate = None
		self.mateVision = 300
		self.possibleMates = []
		self.children = []
		self.parents = []
		self.taken = False
		self.priorityMargin = 2000
		self.repThreshold = 1000
		self.agingThreshold = 1000
		self.overrideWander = False
		self.dead = False
		self.ammount = 5000

		self.maxChildren = 4

		if self.appeal < 0:
			self.appeal = 0
			self.genes["appeal"] = 0

		self.size = 10

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


		nameLen = randint(4,7)
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
		foundPredator = self.findPredator()

		if not foundFood and not foundMate and not self.taken and not foundPredator:
			self.wander()

		if self.taken and self.mate and not foundPredator:
			self.reproduce(self.mate)

		if foundPredator:
			foundMate = False
			self.runAway(self.closestPredator)

		if self.hunger > 10000:
			self.repUrge = 0
			foundMate = self.taken = False
			if self.mate is not None:
				self.mate = None
			if not foundPredator:
				self.wander()
			else:
				self.runAway(self.closestPredator)

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

			if self.bestMate is not None and (not self.bestMate.taken or self.bestMate.mate == self) and len(self.parent.cells+self.parent.asexcells)<self.parent.maxCells:
				self.mate = self.bestMate
				self.mate.mate = self
				self.mate.taken = True
				self.taken = True
				self.reproduce(self.mate)

		if self.mate and self.mate.dead:
			self.mate = None

		self.repUrge+=1
		self.hunger += 1
		if self.hunger >= 3000 and self.hunger%1500==0:
			self.foodWanted+=2
		if self.hunger < 0:
			self.hunger = 0

		self.ageCounter += 1
		self.age = round(self.ageCounter/self.agingThreshold)

		if self.age > 15:
			if randint(0,1000) == 1:
				self.parent.ageDeaths += 1
				self.deathCause = "Died of old age"
				self.die()
		if self.hunger > 10000:
			self.parent.hungerDeaths += 1
			self.deathCause = "Died of hunger"
			self.die()

		parentStr = re.sub('[\[\]\']', '', str(self.parents))

		if len(self.children) > 2:
			c1 = re.sub('[\[\]\']', '', str(self.children[0:2]))
			if len(self.children) > 6:
				c2 = re.sub('[\[\]\']', '', str(self.children[2:6]))
				c3 = re.sub('[\[\]\']', '', str(self.children[6:]))
			else:
				c2 = re.sub('[\[\]\']', '', str(self.children[2:]))
		else:
			cstr = re.sub('[\[\]\']', '', str(self.children))


		self.info = [
			f"{self.name}'s statistics:",
			" - Rep type:       Sexual",
			f" - Speed:          {self.speed}",
			f" - Appeal:         {self.appeal}",
			f" - Vision:         {self.vision}",
			f" - Age:            {self.age}",
			f" - Hunger:         {self.hunger}",
			f" - Rep urge:       {self.repUrge}"
		]

		if len(self.children) > 2:
			if len(self.children) > 6:
				self.info.append(f" - Children:       {c1}")
				self.info.append(f"     {c2}")
				self.info.append(f"     {c3}")
			else:
				self.info.append(f" - Children:       {c1}")
				self.info.append(f"     {c2}")
		else:
			self.info.append(f" - Children:       {cstr}")

		self.info.append(f" - Parent:         {parentStr}")

		if self.dead:
			self.info.append(f" - {self.deathCause}")

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
			if (self.pos - r.pos).length() < self.mateVision and r != self and r.repUrge>self.repThreshold:
				self.possibleMates.append(r)
		if self.possibleMates != []:
			return True
		return False

	def findPredator(self):
		self.closestPredator = None
		for r in self.parent.asexcells:
			dist = (self.pos - r.pos).length()
			if dist < self.vision:
				if not self.closestPredator or dist < (self.pos - self.closestPredator.pos).length():
					self.closestPredator = r
		if self.closestPredator:
			return True
		return False

	def runAway(self, p):
		tmp = p.pos - self.pos
		angle = self.vel.angle_to(tmp)
		self.vel = -self.vel.rotate(angle)
		self.move()

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

	def getEaten(self, eater):
		self.deathCause = f"Eaten by {eater.name}"
		self.die()

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
				for i in range(randint(1,self.maxChildren)):
					genesA = self.genes
					genesB = mate.genes

					genomes = genesA.keys()
					genesC = {}

					for i in genomes:
						if randomBool():
							genesC[i] = genesA[i]
						else:
							genesC[i] = genesB[i]
						if randint(0, 100) < self.mutationRate:
							genesC[i] += randint(-5, 5)

					child = Cell(self.parent, self.pos+Vector(self.size, self.size), genesC)
					child.parents = [self.name, mate.name]
					self.parent.cells.append(child)
					self.children.append(child.name)
					mate.children.append(child.name)
				self.repUrge = -self.repThreshold
				self.taken = False
				self.mate = None

	def wander(self):
		self.vel = self.vel.rotate(uniform(-5, 5))
		self.move()

	def die(self):
		self.dead = True
		self.info.append(f" - {self.deathCause}")
		self.parent.deaths += 1
		if self.name not in []:
			try:
				self.parent.cells.remove(self)
			except: pass
			try:
				self.parent.dead.append(self)

			except: pass

	def move(self):
		self.pos += self.vel*self.delta
		if self.pos.x < self.size:
			self.pos.x = self.screen.size.x-self.size
		if self.pos.x > self.screen.size.x-self.size:
			self.pos.x = self.size

		if self.pos.y < self.size:
			self.pos.y = self.screen.size.y-self.size
		if self.pos.y > self.screen.size.y-self.size:
			self.pos.y = self.size

	def show(self):
		self.screen.stroke(200, 200, 0)
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

	def showName(self):
		self.screen.stroke(255, 255, 0)
		self.screen.textFont("nk57-monospace.ttf")
		self.screen.text(self.name, self.pos.x-16, self.pos.y-self.size-20)

class AsexCell():
	def __init__(self, parent, pos, genes):
		self.parent = parent
		self.pos = pos
		self.genes = genes
		self.screen = self.parent.enviroment
		self.simulation = self.parent.simulation

		self.get_name()

		self.vision = self.genes["vision"]
		self.speed = self.genes["speed"]

		self.hunger = 0
		self.vel = Vector(1, 0).rotate(randint(0, 360))
		self.vel.scale_to_length(self.speed)
		self.vel.rotate(randint(0, 360))
		self.bestFood = Food(-10)
		self.possibleFood = []
		self.children = []
		self.parents = []
		self.priorityMargin = 3000
		self.repThreshold = 4000
		self.dead = False
		self.mass = 2500
		self.ageCounter = 0
		self.age = 0
		self.agingThreshold = 1000
		self.divided = False

		self.sizeReduction = 500


		self.size = round(self.mass / self.sizeReduction)

		self.highlight = False

	def get_name(self):
		consonants = list("wrtypsdfghjklzxcvbnm")
		vowels = list("aeiou")
		letters = consonants+vowels


		nameLen = randint(4,7)
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

		for i in self.parent.cellNames.keys():
			if i != self and i == self.name:
				self.get_name()
		for i in self.parent.cellNamesDead.keys():
			if i != self and i == self.name:
				self.get_name()

	def live(self, delta):
		self.delta = delta

		foundFood = self.findFood()

		if foundFood:
			self.bestFood = Food(-10)
			for f in self.possibleFood:
				if f.ammount > self.bestFood.ammount:
					self.bestFood = f

			if (self.hunger > 2500 and not isinstance(self.bestFood, Cell)) or self.hunger <= 2500:
				tmp = self.bestFood.pos - self.pos
				angle = self.vel.angle_to(tmp)
				self.vel = self.vel.rotate(angle)
				self.move()
				if (self.pos - self.bestFood.pos).length() < self.size:
					self.eat(self.bestFood)

		else:
			self.wander()

		self.size = round(self.mass / self.sizeReduction)

		if self.mass >= 10000 and len(self.parent.cells+self.parent.asexcells)<self.parent.maxCells:
			self.reproduce()

		self.hunger += 1
		if self.hunger > 5000:
			self.parent.hungerDeaths += 1
			self.deathCause = "hunger"
			self.die()

		self.parentStr = re.sub('[\[\]\']', '', str(self.parents))
		self.childrenStr = re.sub('[\[\]\']', '', str(self.children))

		self.ageCounter += 1
		self.age = round(self.ageCounter/self.agingThreshold)

		self.info = [
			f"{self.name}'s statistics:",
			" - Rep type:       Asexual",
			f" - Speed:          {self.speed}",
			f" - Vision:         {self.vision}",
			f" - Age:            {self.age}",
			f" - Hunger:         {self.hunger}",
			f" - Mass:           {self.mass}",
			f" - Children:       {self.childrenStr}",
			f" - Parent:         {self.parentStr}"
		]

		if self.dead:
			self.info.append(f" - Dead")

		if self.divided:
			self.info.append(f" - Divided")

	def findFood(self):
		self.possibleFood = []
		for f in self.parent.food:
			if (self.pos - (f.pos)).length() < self.vision:
				self.possibleFood.append(f)
		if self.possibleFood != []:
			return True
		else:
			for c in self.parent.cells:
				if (self.pos - (c.pos)).length() < self.vision:
					self.possibleFood.append(c)
			if self.possibleFood != []:
				return True
		return False

	def eat(self, food):
		if isinstance(food, Food):
			tmp = food.copy()
			tmp.ammount -= self.hunger
			self.hunger -= food.ammount
			if self.hunger < 0:
				self.hunger = 0
			self.parent.food.remove(food)
		else:
			self.mass += 5000
			food.getEaten(self)

	def reproduce(self):
		self.mutationRate = self.parent.mutationSlider.mark
		genomes = self.genes.keys()

		for n in range(2):
			newGenes = self.genes
			for i in genomes:
				if randint(0,100) < self.mutationRate:
					newGenes[i] += randint(-5, 5)
			child = AsexCell(self.parent, self.pos+Vector(int(30*n), int(30*n)), newGenes)
			child.mass = round(self.mass/2)
			child.parents = [self.name]
			self.children.append(child.name)
			self.parent.asexcells.append(child)

		self.parent.asexcells.remove(self)
		self.parent.cellNamesDead[self.name] = self
		self.divided = True

	def wander(self):
		self.vel = self.vel.rotate(uniform(-5, 5))
		self.move()

	def die(self):
		self.dead = True
		self.parent.deaths += 1
		if self.name not in []:
			try:
				self.parent.asexcells.remove(self)
				self.parent.dead.append(self)
			except: pass

	def move(self):
		self.pos += self.vel*self.delta
		if self.pos.x < self.size:
			self.pos.x = self.screen.size.x-self.size
		if self.pos.x > self.screen.size.x-self.size:
			self.pos.x = self.size

		if self.pos.y < self.size:
			self.pos.y = self.screen.size.y-self.size
		if self.pos.y > self.screen.size.y-self.size:
			self.pos.y = self.size

	def show(self):
		self.screen.stroke(255, 100, 255)
		self.screen.strokeWeight(self.size)
		self.screen.point(self.pos.x, self.pos.y)

		if self.highlight:
			self.screen.strokeWeight(4)
			self.screen.noFill()
			self.screen.stroke(100,100,255)
			self.screen.circle(self.pos.x, self.pos.y, self.size+10)

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

	def showName(self):
		self.screen.stroke(255, 255, 0)
		self.screen.textFont("nk57-monospace.ttf")
		self.screen.text(self.name, self.pos.x-16, self.pos.y-self.size-20)
