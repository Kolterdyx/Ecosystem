from rabbit import *
from food import *
from additional import *

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

		self.offsetting = False

	def offset(self, xoff, yoff):
		self.pos.x = round(xoff*self.scale)
		self.pos.y = round(yoff*self.scale)
		self.rect.topleft = self.pos

	def resize(self, nw, nh):
		self.size = Vector(nw, nh)

	def zoom(self, mult):
		self.scale = mult
		self.scaled_image = pg.transform.smoothscale(self.image, (round(self.osize.x*mult), round(self.osize.y*mult)))
		self.scaled_rect = pg.Rect(self.pos, self.scaled_image.get_size())

	def update(self):
		if self.offsetting:
			pass


class Screen:

	def __init__(self, screen):
		self.screen = screen
		self.startTime = time.time()

		self.timer = 0
		self.time = 0
		self.debug = False

		self.marginLeft = 320
		self.marginRight = 320
		self.marginTop = 60
		self.marginBottom = 60

		self.initialRabbits = 8
		self.initialFood = 100

		self.extinctions = 0
		self.record = 0

		self.foodGenRate = 250

		self.deaths = 0
		self.hungerDeaths = 0
		self.ageDeaths = 0

		self.rabbits = []
		self.food = []

		self.canvasSize = Vector(width-self.marginLeft-self.marginRight, height-self.marginTop-self.marginBottom)
		self.enviroment = Enviroment(self, 0, 0, self.canvasSize.x*2, self.canvasSize.y*2)
		self.simulation = Canvas(self.marginLeft, self.marginTop, self.canvasSize.x, self.canvasSize.y)

		self.children = 0
		self.adults = 0

		for i in range(self.initialRabbits):
			self.addRabbit()

		# self.rabbits[0].name = "Mauro"
		# self.rabbits[1].name = "Lucía"
		# self.rabbits[2].name = "Ciro"
		# self.rabbits[3].name = "Adolfo"


		self.info = []

		self.zoom = 1

		self.ageDeathsPercent = 0
		self.hungerDeathsPercent = 0


		for i in range(self.initialFood):
			self.addFood()

		self.create_widgets()

	def create_widgets(self):
		self.restartButton = Button(self, func=self.restartSim)
		self.restartButton.move(x=20, y=height-self.marginBottom-self.restartButton.height)
		self.restartButton.set_font_color((255,255,0))
		self.restartButton.border_width = 2
		self.restartButton.border_color = (255, 255, 0)
		self.restartButton.bg_color = (60, 60, 60)
		self.restartButton.set_label("Restart")

		self.mutationSlider = Slider(self)
		self.mutationSlider.border_width = 1
		self.mutationSlider.border_color = (255, 255, 0)
		self.mutationSlider.pointer_border_width = 1
		self.mutationSlider.pointer_border_color = (255, 255, 0)
		self.mutationSlider.bg_color = (60, 60, 60)
		self.mutationSlider.move(20, 16+self.marginTop)
		self.mutationSlider.set_font("Monotype")
		self.mutationSlider.set_font_color((255,255,0))
		self.mutationSlider.set_font_size(16)
		self.mutationSlider.set_label("Mutation rate: 50%")
		self.mutationSlider.set_mark(50)

		self.toggleDebug = CheckBox(self)
		self.toggleDebug.bg_color = (60, 60, 60)
		self.toggleDebug.set_font("Monotype")
		self.toggleDebug.set_font_color((255,255,0))
		self.toggleDebug.set_font_size(16)
		self.toggleDebug.set_label(" Debugging")
		self.toggleDebug.check_color = (255,255,0)
		self.toggleDebug.border_color = (255,255,0)
		self.toggleDebug.border_width = 1
		self.toggleDebug.label_side = "left"
		self.toggleDebug.move(112, 120)

		self.xoffSlider = Slider(self)
		self.xoffSlider.border_width = 1
		self.xoffSlider.border_color = (255, 255, 0)
		self.xoffSlider.pointer_border_width = 1
		self.xoffSlider.pointer_border_color = (255, 255, 0)
		self.xoffSlider.bg_color = (60, 60, 60)
		self.xoffSlider.move(20, 200+self.marginTop)
		self.xoffSlider.set_font("Monotype")
		self.xoffSlider.set_font_color((255,255,0))
		self.xoffSlider.set_font_size(16)
		self.xoffSlider.set_label("X Offset: 0")
		self.xoffSlider.max = int(self.enviroment.size.x - self.simulation.size.x)

		self.yoffSlider = Slider(self)
		self.yoffSlider.border_width = 1
		self.yoffSlider.border_color = (255, 255, 0)
		self.yoffSlider.pointer_border_width = 1
		self.yoffSlider.pointer_border_color = (255, 255, 0)
		self.yoffSlider.bg_color = (60, 60, 60)
		self.yoffSlider.move(20, 260+self.marginTop)
		self.yoffSlider.set_font("Monotype")
		self.yoffSlider.set_font_color((255,255,0))
		self.yoffSlider.set_font_size(16)
		self.yoffSlider.set_label("Y Offset: 0")
		self.yoffSlider.max = int(self.enviroment.size.y - self.simulation.size.y)



		self.widgets = [
			self.restartButton,
			self.mutationSlider,
			self.toggleDebug,
			self.xoffSlider,
			self.yoffSlider
		]

	def restartSim(self):
		self.startTime = time.time()
		self.rabbits = []
		self.food = []
		self.initialRabbits = 4
		self.initialFood = 30
		self.extinctions = 0
		self.record = 0
		self.foodGenRate = 250
		self.deaths = 0
		self.hungerDeaths = 0
		self.ageDeaths = 0
		self.canvasSize = Vector(width-self.marginLeft-self.marginRight, height-self.marginTop-self.marginBottom)
		self.simulation = Canvas(self.marginLeft, self.marginTop, self.canvasSize.x, self.canvasSize.y)
		self.children = 0
		self.adults = 0
		for i in range(self.initialRabbits):
			self.addRabbit()
		for i in range(self.initialFood):
			self.addFood()

	def update(self):
		self.adults = 0
		self.children = 0
		self.fastest = None
		self.avSpeed = 0
		self.mostAppeal = None
		self.avAppeal = 0
		self.mostVision = None
		self.avVision = 0
		for r in self.rabbits:
			r.live()

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

		self.avSpeed /= len(self.rabbits)
		self.avSpeed = round(self.avSpeed, 3)
		self.avAppeal /= len(self.rabbits)
		self.avAppeal = round(self.avAppeal, 3)
		self.avVision /= len(self.rabbits)
		self.avVision = round(self.avVision, 3)


		if self.timer%self.foodGenRate==0:
			self.addFood()

		if len(self.rabbits) > self.record:
			self.record = len(self.rabbits)

		if len(self.rabbits)<2:
			self.rabbits = []
			self.extinctions+=1
			for i in range(self.initialRabbits):
				self.addRabbit()

		self.timer+=1
		self.time = round(time.time() - self.startTime, 2)

		if self.deaths:
			self.ageDeathsPercent = self.ageDeaths / self.deaths * 100
			self.hungerDeathsPercent = self.hungerDeaths / self.deaths * 100

		spacer = "----------------------------"
		self.info = [
			"Time(s):        "+str(self.time),
			"Food:           "+str(len(self.food)),
			spacer,
			"Deaths:         "+str(self.deaths),
			f"Age deaths:     {self.ageDeaths} ({round(self.ageDeathsPercent, 2)}%)",
			f"Hunger deaths:  {self.hungerDeaths} ({round(self.hungerDeathsPercent, 2)}%)",
			"Extinctions:    "+str(self.extinctions),
			spacer,
			"Peak ammount:   "+str(self.record),
			"Ammount:        "+str(len(self.rabbits)),
			"Adults:         "+str(self.adults),
			"Children:       "+str(self.children),
			f"Highest speed:  {self.fastest.speed} ({self.fastest.name})",
			"Av. speed:      "+str(self.avSpeed),
			f"Highest appeal: {self.mostAppeal.appeal} ({self.mostAppeal.name})",
			"Av. appeal:     "+str(self.avAppeal),
			f"Highest vision: {self.mostVision.vision} ({self.mostVision.name})",
			"Av. vision:     "+str(self.avVision)
		]

		self.mutationSlider.set_label(f"Mutation rate: {self.mutationSlider.mark}%")
		self.xoffSlider.set_label(f"X Offset: {int(self.xoffSlider.mark)}")
		self.yoffSlider.set_label(f"Y Offset: {int(self.yoffSlider.mark)}")


		self.enviroment.offset(-self.xoffSlider.mark, -self.yoffSlider.mark)



	def draw(self):
		background(100)
		self.simulation.background(50)
		self.enviroment.background(0)


		for f in self.food:
			f.show()

		for r in self.rabbits:
			r.show()
			if self.debug:
				r.debug()

		self.enviroment.zoom(self.zoom)
		self.simulation.image.blit(self.enviroment.scaled_image, self.enviroment.rect)
		self.simulation.show()
		self.simulation.border(2, *(255, 255, 0))

		stroke(255,255,0)
		textSize(16)
		for i in range(len(self.info)):
			text(self.info[i], width-self.marginRight+20, i*20+self.marginTop)

		for w in self.widgets:
			w.update()


		pg.display.flip()

	def addFood(self):
		self.food.append(Food(self, Vector(random(self.enviroment.pos.x, self.enviroment.size.x), random(self.enviroment.pos.y, self.enviroment.size.y))))
	def addRabbit(self):
		self.rabbits.append(Rabbit(self,
										Vector(random(self.enviroment.pos.x, self.enviroment.size.x), random(self.enviroment.pos.y, self.enviroment.size.y)),
										{
											"vision": random(100, 150),
											"speed": random(20,40),
											"appeal": random(0, 100)
										}))
	def events(self):
		for event in pg.event.get():
			self.enviroment.event = event
			if event.type == pg.QUIT:
				raise SystemExit
			elif event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					raise SystemExit
				if event.key == pg.K_d:
					self.debug = not self.debug

			elif event.type == pg.MOUSEWHEEL:
				mousepos = Vector(pg.mouse.get_pos())
				if mousepos.x > self.simulation.pos.x and mousepos.x < self.simulation.pos.x+self.simulation.width and mousepos.y > self.simulation.pos.y and mousepos.y < self.simulation.pos.y+self.simulation.height:
					if event.y > 0:
						self.zoom += 0.05
					else:
						self.zoom -= 0.05 if self.zoom >= 0.05 else 0

			elif event.type == pg.MOUSEBUTTONDOWN:
				mousepos = Vector(pg.mouse.get_pos()) - self.enviroment.pos - Vector(self.marginLeft, self.marginTop)
				if mousepos.x < self.enviroment.scaled_rect.width and mousepos.x > 0 and mousepos.y < self.enviroment.scaled_rect.height and mousepos.y > 0:
					self.enviroment.offsetting = True

			elif event.type == pg.MOUSEBUTTONUP:
				mousepos = Vector(pg.mouse.get_pos()) - self.enviroment.pos - Vector(self.marginLeft, self.marginTop)
				if mousepos.x < self.enviroment.scaled_rect.width and mousepos.x > 0 and mousepos.y < self.enviroment.scaled_rect.height and mousepos.y > 0:
					self.enviroment.offsetting = False



s = Screen(screen)
while 1:
	s.events()
	s.update()
	s.draw()
