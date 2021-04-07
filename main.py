from cell import *
from food import *
from additional import *
from threading import Thread
import re

class Enviroment(Canvas):
	def __init__(self, parent, x, y, w, h):
		self.parent = parent
		self.opos = Vector(x, y)
		self.osize = Vector(w, h)
		Canvas.__init__(self, x, y, w, h)

		self.scale = 1

		self.scaled_image = self.image.copy()
		self.scaled_rect = self.rect.copy()
		self.event = None

		self.offset_vec = Vector(0,0)
		self.dist = self.pos

		self.p1, p2, p3 = pg.mouse.get_pressed()
		self.initialPauseTime = 0
		self.pausedTime = 0
		self.startCountingPause = True

	def offset(self, xoff, yoff):
		self.offset_vec = Vector(round(xoff), round(yoff))
		self.pos += self.offset_vec

	def resize(self, nw, nh):
		self.size = Vector(nw, nh)

	def zoom(self, mult):
		if not self.p1:
			self.scale = mult
			self.scaled_image = pg.transform.smoothscale(self.image, (round(self.osize.x*mult), round(self.osize.y*mult)))
			self.scaled_rect = pg.Rect(self.pos, self.scaled_image.get_size())

	def update(self):
		mousepos = Vector(pg.mouse.get_pos())
		if self.parent.simulation.rect.collidepoint(mousepos):
			relative_mousepos = mousepos - self.parent.simulation.pos - self.pos
			self.p1, p2, p3 = pg.mouse.get_pressed()
			if not self.p1:
				self.dist = -relative_mousepos
				if self.parent.pauseTime:
					self.parent.pauseTime = False
					self.parent.startTime += self.pausedTime
					self.initialPauseTime = 0
					self.startCountingPause = True
			if self.p1:
				self.parent.pauseTime = True
				if self.startCountingPause:
					self.initialPauseTime = time.time()
					self.startCountingPause = False
				else:
					self.pausedTime = time.time() - self.initialPauseTime
				off = relative_mousepos + self.dist
				self.offset(off.x, off.y)


			self.rect.topleft = self.pos
			self.scaled_rect.topleft = self.pos


class Screen:

	def __init__(self, screen):
		self.screen = screen
		self.startTime = time.time()

		self.minZoom = 0

		self.timer = 0
		self.time = 0
		self.maxFrameRate = 40
		self.fps = 40
		self.dt = time.time()
		self.delta = 0
		self.lastDelta = self.delta

		self.showNames = False

		self.marginLeft = 260
		self.marginRight = 260
		self.marginTop = 60
		self.marginBottom = 100

		self.initialCells = 16
		self.initialFood = 100

		self.extinctions = 0
		self.record = 0

		self.foodGenRate = 62

		self.deaths = 0
		self.hungerDeaths = 0
		self.ageDeaths = 0

		self.cells = []
		self.food = []
		self.dead = []
		self.rNames = {}
		self.rNamesDead = {}

		self.pauseTime = False

		self.canvasSize = Vector(width-self.marginLeft-self.marginRight, height-self.marginTop-self.marginBottom)
		self.enviroment = Enviroment(self, 0, 0, self.canvasSize.x*4, self.canvasSize.y*4)
		self.simulation = Canvas(self.marginLeft, self.marginTop, self.canvasSize.x, self.canvasSize.y)

		self.children = 0
		self.adults = 0

		for i in range(self.initialCells):
			self.addCell()
			self.cells[i].ageCounter = 5000

		for i in range(self.initialFood):
			self.addFood()

		# self.cells[0].name = "Mauro"
		# self.cells[1].name = "Lucía"
		# self.cells[2].name = "Ciro"
		# self.cells[3].name = "Adolfo"

		self.guiFontSize = 12


		self.info = []
		self.rNames = {}

		self.debugTarget = self.cells[0]

		self.showMatingLine = False

		self.zoom = self.minZoom = round(self.simulation.size.x / self.enviroment.size.x, 2)

		self.ageDeathsPercent = 0
		self.hungerDeathsPercent = 0

		self.speciesDuration = 0
		self.timeStepSpeciesDuration = 0
		self.lastExtinction = time.time()
		self.lastExtinctionTimeStep = 0

		self.create_widgets()

		self.killUpdateThread = False
		self.updateThread = Thread(target=self.update)
		self.debugTargetDead = False

		self.clock = pg.time.Clock()
		pg.display.set_caption("Cell simulation")
		self.setDebugTarget()

	def create_widgets(self):
		self.restartButton = Button(self, func=self.restartSim)
		self.restartButton.width = 160
		self.restartButton.height = 40
		self.restartButton.move(int(width/2-self.restartButton.width/2), int(height-self.marginBottom/2-self.restartButton.height/2))
		self.restartButton.set_label("Restart simulation")

		self.mutationSlider = Slider(self)
		self.mutationSlider.pointer_border_width = 1
		self.mutationSlider.pointer_border_color = (255, 255, 0)
		self.mutationSlider.set_label("Mutation rate: 50%")
		self.mutationSlider.set_mark(50)

		self.debugTargetEntry = Entry(self)
		self.debugTargetEntry.set_label("Debug target:")
		self.debugTargetEntry.label_padding = 5
		self.debugTargetEntry.func = self.setDebugTarget

		self.showNameToggle = CheckBox(self)
		self.showNameToggle.set_label("Show names:")
		self.showNameToggle.check_color = (255, 255, 0)

		self.foodRateSlider = Slider(self)
		self.foodRateSlider.pointer_border_width = 1
		self.foodRateSlider.pointer_border_color = (255, 255, 0)
		self.foodRateSlider.move(20, 200+self.marginTop)
		self.foodRateSlider.max = 499
		self.foodRateSlider.set_label("Food generation rate: 250")
		self.foodRateSlider.set_mark(self.foodRateSlider.max-self.foodGenRate)

		self.showMatingToggle = CheckBox(self)
		self.showMatingToggle.set_label("Show mating lines:")
		self.showMatingToggle.check_color = (255, 255, 0)

		self.hideSimulation = CheckBox(self)
		self.hideSimulation.set_label("Hide simulation:")
		self.hideSimulation.check_color = (255, 255, 0)

		self.maxFrameRateEntry = Entry(self)
		self.maxFrameRateEntry.set_label("Maximum frame rate: 40")
		self.maxFrameRateEntry.label_padding = 5
		self.maxFrameRateEntry.func = self.setMaxFrameRate
		self.maxFrameRateEntry.allowed_characters = "1234567890"



		self.widgets = [
			self.restartButton,
			self.mutationSlider,
			self.foodRateSlider,
			self.debugTargetEntry,
			self.maxFrameRateEntry,
			self.showNameToggle,
			self.showMatingToggle,
			self.hideSimulation
		]

		for i in range(1, len(self.widgets)):
			self.widgets[i].move(20, 16+self.marginTop+(round(self.guiFontSize*3.57)*(i-1)))

		for w in self.widgets:
			w.set_font_color((255,255,0))
			w.set_font_size(self.guiFontSize)
			w.set_font("nk57-monospace.ttf")
			w.bg_color = (60, 60, 60)
			w.border_width = 1
			w.border_color = (255, 255, 0)

	def restartSim(self):
		self.startTime = time.time()
		self.cells = []
		self.food = []
		self.dead = []
		self.extinctions = 0
		self.deaths = 0
		self.hungerDeaths = 0
		self.ageDeaths = 0
		self.children = 0
		self.adults = 0
		for i in range(self.initialCells):
			self.addCell()
			self.cells[i].ageCounter = 5000
		for i in range(self.initialFood):
			self.addFood()

		self.rNames = {}
		self.rNamesDead = {}

		self.setDebugTarget()

	def update(self):
		while True:
			if self.killUpdateThread:
				break
			if self.maxFrameRate:
				time.sleep(1000/self.maxFrameRate/1000)

			self.lastDelta = self.dt
			self.delta = time.time()-self.lastDelta
			if self.delta > 0:
				self.fps = round(1000/self.delta*0.001)
			else:
				self.fps = 0 if self.maxFrameRate > 0 else "Infinite"
			self.dt = time.time()

			if not self.pauseTime:
				self.adults = 0
				self.children = 0
				self.fastest = None
				self.avSpeed = 0
				self.mostAppeal = None
				self.avAppeal = 0
				self.mostVision = None
				self.avVision = 0
				self.rNames = {}
				for r in self.cells:
					r.live(self.delta)
					self.rNames[r.name] = r
					self.avSpeed += r.speed
					self.avAppeal += r.appeal
					self.avVision += r.vision

					if r.age>4:
						self.adults+=1
					else:
						self.children+=1

					if not self.fastest or r.speed > self.fastest.speed:
						self.fastest = r
					if not self.mostAppeal or r.appeal > self.mostAppeal.appeal:
						self.mostAppeal = r
					if not self.mostVision or r.vision > self.mostVision.vision:
						self.mostVision = r

				self.rNamesDead = {}
				for r in self.dead:
					self.rNamesDead[r.name] = r


				self.avSpeed /= len(self.cells)
				self.avSpeed = round(self.avSpeed, 3)
				self.avAppeal /= len(self.cells)
				self.avAppeal = round(self.avAppeal, 3)
				self.avVision /= len(self.cells)
				self.avVision = round(self.avVision, 3)


				if self.timer%self.foodGenRate==0:
					self.addFood()

				self.timer+=1
				self.time = round(time.time() - self.startTime, 2)

			self.foodGenRate = self.foodRateSlider.max-self.foodRateSlider.mark + 1


			if len(self.cells) > self.record:
				self.record = len(self.cells)

			if len(self.cells)<2:
				self.cells = []
				self.food = []
				self.extinctions+=1
				self.speciesDuration = time.time() - self.lastExtinction
				self.timeStepSpeciesDuration = self.timer-self.lastExtinctionTimeStep
				self.lastExtinction = time.time()
				self.lastExtinctionTimeStep = self.timer
				for i in range(self.initialCells):
					self.addCell()
				for i in range(self.initialFood):
					self.addFood()


			if self.deaths:
				self.ageDeathsPercent = self.ageDeaths / self.deaths * 100
				self.hungerDeathsPercent = self.hungerDeaths / self.deaths * 100

			if self.debugTarget:
				debugTargetParents = re.sub('[\[\]\']', '', str(self.debugTarget.parents))

				debugTargetChildren1 = None
				debugTargetChildren2 = None
				debugTargetChildren3 = None
				if len(self.debugTarget.children) > 2:
					debugTargetChildren1 = re.sub('[\[\]\']', '', str(self.debugTarget.children[0:2]))
					if len(self.debugTarget.children) > 4:
						debugTargetChildren2 = re.sub('[\[\]\']', '', str(self.debugTarget.children[2:4]))
						debugTargetChildren3 = re.sub('[\[\]\']', '', str(self.debugTarget.children[4:]))
					else:
						debugTargetChildren2 = re.sub('[\[\]\']', '', str(self.debugTarget.children[2:]))
				else:
					debugTargetChildrenStr = re.sub('[\[\]\']', '', str(self.debugTarget.children))

			spacer = ("","------------------------------","")
			hours, minutes, seconds = formatSeconds(self.time)
			self.info = [
				"Time:              {}h {}m {:.2f}s".format(hours, minutes, seconds),
				"Food:              "+str(len(self.food)),
				"Current FPS:       "+str(self.fps),
				"Max frame rate:    "+str(self.maxFrameRate),
				*spacer,
				"Deaths:            "+str(self.deaths),
				f"Age deaths:        {self.ageDeaths} ({round(self.ageDeathsPercent, 2)}%)",
				f"Hunger deaths:     {self.hungerDeaths} ({round(self.hungerDeathsPercent, 2)}%)",
				"Extinctions:       "+str(self.extinctions),
				"Last run:          {}h {}m {:.2f}s".format(*formatSeconds(self.speciesDuration)),
				f"                   {self.timeStepSpeciesDuration} time steps",
				*spacer,
				"Peak ammount:      "+str(self.record),
				"Ammount:           "+str(len(self.cells)),
				"Adults:            "+str(self.adults),
				"Children:          "+str(self.children),
				f"Highest speed:     {self.fastest.speed} ({self.fastest.name})",
				"Av. speed:         "+str(self.avSpeed),
				f"Highest appeal:    {self.mostAppeal.appeal} ({self.mostAppeal.name})",
				"Av. appeal:        "+str(self.avAppeal),
				f"Highest vision:    {self.mostVision.vision} ({self.mostVision.name})",
				"Av. vision:        "+str(self.avVision),
				*spacer
			]


			if self.debugTarget:
				self.debugTargetInfo = [
					f"{self.debugTarget.name}'s statistics:",
					f" - Speed:          {self.debugTarget.speed}",
					f" - Appeal:         {self.debugTarget.appeal}",
					f" - Vision:         {self.debugTarget.vision}",
					f" - Age:            {self.debugTarget.age}",
					f" - Hunger:         {self.debugTarget.hunger}",
					f" - Rep urge:       {self.debugTarget.repUrge}",
					f" - Mate:           {self.debugTarget.mate.name if self.debugTarget.mate else None}"
				]

				if len(self.debugTarget.children) < 3:
					self.debugTargetInfo.append(f" - Children:    {debugTargetChildrenStr}")
				elif len(self.debugTarget.children) > 2:
					self.debugTargetInfo.append(f" - Children:    {debugTargetChildren1}")
					self.debugTargetInfo.append(f"                {debugTargetChildren2}")
					if len(self.debugTarget.children) > 4:
						self.debugTargetInfo.append(f"                {debugTargetChildren3}")

				self.debugTargetInfo.append(f" - Parents:     {debugTargetParents}")

				if self.debugTarget.dead:
					self.debugTargetInfo.append(f" - Died of {self.debugTarget.deathCause}")

				for i in self.debugTargetInfo:
					self.info.append(i)
			else:
				self.info.append("No target selected")

			self.minZoom = round(self.simulation.size.x / self.enviroment.size.x, 2)

			self.zoom = round(self.zoom, 2)

			self.enviroment.update()

			self.showNames = self.showNameToggle.checked
			self.showMatingLine = self.showMatingToggle.checked

	def draw(self):
		background(100)
		self.simulation.background(50)
		self.enviroment.background(0)

		if not self.hideSimulation.checked:
			for f in self.food:
				f.show()

			for r in self.cells:
				r.show()
				if self.showNames:
					r.debug()

			self.enviroment.zoom(self.zoom)
			self.simulation.image.blit(self.enviroment.scaled_image, self.enviroment.scaled_rect)
		self.simulation.show()
		self.simulation.border(2, *(255, 255, 0))

		stroke(255,255,0)
		textSize(self.guiFontSize)
		textFont("nk57-monospace.ttf")
		for i, v in enumerate(self.info):
			text(v, width-self.marginRight+20, i*self.guiFontSize*1.5+self.marginTop)

		self.mutationSlider.set_label(f"Mutation rate: {self.mutationSlider.mark}%")
		self.foodRateSlider.set_label(f"Food generation rate: {self.foodRateSlider.mark+1}")
		self.maxFrameRateEntry.set_label(f"Maximum frame rate: {self.maxFrameRate}")
		for w in self.widgets:
			w.update()


		pg.display.flip()

	def setDebugTarget(self):
		oldDebugTarget = self.debugTarget
		if self.debugTargetEntry.text in self.rNames.keys():
			self.debugTarget = self.rNames[self.debugTargetEntry.text]
			self.debugTarget.highlight = True
			if self.debugTarget != oldDebugTarget and oldDebugTarget:
				oldDebugTarget.highlight = False
		elif self.debugTargetEntry.text in self.rNamesDead.keys():
			self.debugTarget = self.rNamesDead[self.debugTargetEntry.text]
			self.debugTarget.highlight = True
			if self.debugTarget != oldDebugTarget and oldDebugTarget:
				oldDebugTarget.highlight = False
		else:
			if self.debugTarget:
				self.debugTarget.highlight = False
			self.debugTarget = None

		self.debugTargetEntry.clear()

	def setMaxFrameRate(self):
		self.maxFrameRate = int(self.maxFrameRateEntry.text) if self.maxFrameRateEntry.text else 0
		self.maxFrameRateEntry.clear()

	def addFood(self):
		self.food.append(Food(self, Vector(random(self.enviroment.pos.x, self.enviroment.size.x), random(self.enviroment.pos.y, self.enviroment.size.y))))

	def addCell(self):
		self.cells.append(Cell(self,
										Vector(random(self.enviroment.pos.x, self.enviroment.size.x), random(self.enviroment.pos.y, self.enviroment.size.y)),
										{
											"vision": random(100, 150),
											"speed": random(20,50),
											"appeal": random(0, 100)
										}))

	def events(self):
		for event in pg.event.get():
			self.enviroment.event = event
			if event.type == pg.QUIT:
				self.killUpdateThread = True
				self.updateThread.join()
				# self.drawThread.join()
				raise SystemExit
			elif event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					self.killUpdateThread = True
					self.updateThread.join()
					# self.drawThread.join()
					raise SystemExit

			elif event.type == pg.MOUSEWHEEL:
				mousepos = Vector(pg.mouse.get_pos())
				if mousepos.x > self.simulation.pos.x and mousepos.x < self.simulation.pos.x+self.simulation.width and mousepos.y > self.simulation.pos.y and mousepos.y < self.simulation.pos.y+self.simulation.height:
					if event.y > 0:
						self.zoom += 0.05
					else:
						self.zoom -= 0.05 if self.zoom >= self.minZoom else 0

s = Screen(screen)

s.updateThread.start()

while True:
	s.events()
	s.draw()
