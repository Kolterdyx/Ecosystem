from cell import *
from food import *
from additional import *
from threading import Thread
import subprocess
import sys
import csv

# Uncomment for a fixed simulation
# random.seed(0)

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

    @dispatch(float, float)
    def offset(self, xoff, yoff):
        self.offset_vec = Vector(round(xoff), round(yoff))
        self.pos += self.offset_vec
        self.pos.x = int(self.pos.x)
        self.pos.y = int(self.pos.y)
    @dispatch(int, int)
    def offset(self, xoff, yoff):
        self.offset_vec = Vector(round(xoff), round(yoff))
        self.pos += self.offset_vec
        self.pos.x = int(self.pos.x)
        self.pos.y = int(self.pos.y)
    @dispatch(Vector)
    def offset(self, off):
        self.offset_vec = off
        self.pos += self.offset_vec
        self.pos.x = int(self.pos.x)
        self.pos.y = int(self.pos.y)

    def resize(self, nw, nh):
        self.size = Vector(nw, nh)

    def resetPos(self):
        self.pos = Vector(0,0)
        self.rect.topleft = self.pos
        self.scaled_rect.topleft = self.pos

    def zoom(self, mult):
        if not self.p1:
            mousepos = Vector(pg.mouse.get_pos())
            brdist = mousepos  - self.parent.simulation.pos - self.pos - self.scaled_rect.size
            tldist = mousepos  - self.parent.simulation.pos - self.pos
            a = brdist - tldist
            b = tldist - brdist

            self.scaled_rect = pg.Rect(self.pos, (round(self.osize.x*mult), round(self.osize.y*mult)))
            if self.scale != mult:
                newbrdist = mousepos  - self.parent.simulation.pos - self.pos - self.scaled_rect.size
                diff = Vector(round(self.osize.x*mult), round(self.osize.y*mult))
                off = -(brdist-newbrdist)/2
                self.offset(off)
                newtldist = mousepos  - self.parent.simulation.pos - self.pos
                off = (Vector(self.scaled_rect.size)/2 - newtldist) * mult/2
                if self.scale-mult > 0:
                    off *= -1
                self.offset(off)

                self.scale = mult
            self.scaled_image = pg.transform.smoothscale(self.image, self.scaled_rect.size)

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
                self.offset(off)

            self.pos.x = int(self.pos.x)
            self.pos.y = int(self.pos.y)

            self.rect.topleft = self.pos
            self.scaled_rect.topleft = self.pos


class Screen:

    def __init__(self, screen):
        self.screen = screen
        self.startTime = time.time()

        self.graphs = subprocess.Popen("python data_visualizer.py")

        self.simId = 0
        self.data = {}
        self.fieldnames = [
            "simID",
            "step",
            "total_ammount",
            "total_peak_ammount",
            "cell_ammount",
            "cell_peak_ammount",
            "asexcell_ammount",
            "asexcell_peak_ammount",
            "food_ammount"
        ]
        with open('data.csv', 'w') as csv_file:
            self.csv_writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            self.csv_writer.writeheader()
        self.registerFreq = 25

        self.minZoom = 0

        self.timeStep = 0
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
        self.maxCells = 1000000
        self.initialFood = 100

        self.extinctions = 0
        self.record = 0

        self.foodGenRate = 62

        self.deaths = 0
        self.hungerDeaths = 0
        self.ageDeaths = 0

        self.cells = []
        self.asexcells = []
        self.food = []
        self.dead = []
        self.cellNames = {}
        self.cellNamesDead = {}

        self.pauseTime = False

        self.canvasSize = Vector(width-self.marginLeft-self.marginRight, height-self.marginTop-self.marginBottom)
        self.enviroment = Enviroment(self, 0, 0, self.canvasSize.x*4, self.canvasSize.y*4)
        self.simulation = Canvas(self.marginLeft, self.marginTop, self.canvasSize.x, self.canvasSize.y)


        self.children = 0
        self.adults = 0

        for i in range(self.initialCells):
            self.addCell()
            self.addAsexCell()

        for i in range(self.initialFood):
            self.addFood()

        # self.cells[0].name = "Mauro"
        # self.cells[1].name = "Lucía"
        # self.cells[2].name = "Ciro"
        # self.cells[3].name = "Adolfo"

        self.guiFontSize = 12


        self.info = []
        self.cellNames = {}

        self.debugTarget = self.cells[0]

        self.showMatingLine = False

        self.zoom = self.minZoom = round(self.simulation.size.x / self.enviroment.size.x, 2)
        self.enviroment.zoom(self.zoom)
        self.enviroment.resetPos()

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

        self.resetViewButton = Button(self)
        self.resetViewButton.set_label("Reset view")
        self.resetViewButton.func = self.resetView
        self.resetViewButton.width = 160
        self.resetViewButton.height = 40

        self.pauseButton = Button(self)
        self.pauseButton.set_label("Pause")
        self.pauseButton.func = self.pause
        self.pauseButton.width = 160
        self.pauseButton.height = 40

        self.saveButton = Button(self)
        self.saveButton.set_label("Save data")
        self.saveButton.func = self.saveData
        self.saveButton.width = 160
        self.saveButton.height = 40



        self.widgets = [
            self.restartButton,
            self.mutationSlider,
            self.foodRateSlider,
            self.debugTargetEntry,
            self.maxFrameRateEntry,
            self.showNameToggle,
            self.showMatingToggle,
            self.hideSimulation,
            self.resetViewButton,
            self.pauseButton,
            self.saveButton
        ]

        for i in range(len(self.widgets)):
            self.widgets[i].move(20, 16+self.marginTop+(round(self.guiFontSize*3.57)*(i-1)))

        self.restartButton.move(int(width/2-self.restartButton.width/2), int(height-self.marginBottom/2-self.restartButton.height/2))
        self.resetViewButton.move(int(width/2-self.resetViewButton.width/2-self.resetViewButton.width-20), int(height-self.marginBottom/2-self.resetViewButton.height/2))
        self.pauseButton.move(int(width/2-self.pauseButton.width/2+self.pauseButton.width+20), int(height-self.marginBottom/2-self.pauseButton.height/2))

        for w in self.widgets:
            w.set_font_color((255,255,0))
            w.set_font_size(self.guiFontSize)
            w.set_font("nk57-monospace.ttf")
            w.bg_color = (60, 60, 60)
            w.border_width = 1
            w.border_color = (255, 255, 0)

    def restartSim(self):
        self.simId += 1
        self.startTime = time.time()
        self.timeStep = 0
        self.cells = []
        self.asexcells = []
        self.cellNames = {}
        self.cellNamesDead = {}
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
        for i in range(self.initialFood):
            self.addFood()

        self.cellNames = {}
        self.cellNamesDead = {}

        self.setDebugTarget()

    def resetView(self):
        self.zoom = self.minZoom = round(self.simulation.size.x / self.enviroment.size.x, 2)
        self.enviroment.zoom(self.zoom)
        self.enviroment.resetPos()

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
                self.fastest = None
                self.avSpeed = 0
                self.mostAppeal = None
                self.avAppeal = 0
                self.mostMass = None
                self.avMass = 0
                self.mostVision = None
                self.avVision = 0
                self.cellNames = {}
                for r in self.cells:
                    self.cellNames[r.name] = r
                    self.avSpeed += r.speed
                    self.avAppeal += r.appeal
                    self.avVision += r.vision

                    if r.age>4:
                        self.adults+=1
                    else:
                        self.children+=1

                    if not self.mostAppeal or r.appeal > self.mostAppeal.appeal:
                        self.mostAppeal = r

                for r in self.asexcells:
                    self.cellNames[r.name] = r

                    self.avMass += r.mass

                    if not self.mostMass or r.mass > self.mostMass.mass:
                        self.mostMass = r

                for r in self.cells+self.asexcells:
                    r.live(self.delta)

                    if not self.fastest or r.speed > self.fastest.speed:
                        self.fastest = r
                    if not self.mostVision or r.vision > self.mostVision.vision:
                        self.mostVision = r

                for r in self.dead:
                    self.cellNamesDead[r.name] = r


                self.avSpeed = round(self.avSpeed / len(self.cells) if self.cells else 0, 3)
                self.avAppeal = round(self.avAppeal / len(self.cells) if self.cells else 0, 3)
                self.avVision = round(self.avVision / len(self.cells) if self.cells else 0, 3)
                self.avMass = round(self.avMass / len(self.asexcells) if self.asexcells else 0, 3)


                if self.timeStep%self.foodGenRate==0:
                    self.addFood()

                self.timeStep+=1
                self.time = round(time.time() - self.startTime, 2)

            self.foodGenRate = self.foodRateSlider.max-self.foodRateSlider.mark + 1


            if len(self.cellNames) > self.record:
                self.record = len(self.cellNames)

            if len(self.cellNames)<2:
                self.cells = []
                self.asexcells = []
                self.food = []
                self.extinctions+=1
                self.simId += 1
                self.speciesDuration = time.time() - self.lastExtinction
                self.timeStepSpeciesDuration = self.timeStep-self.lastExtinctionTimeStep
                self.lastExtinction = time.time()
                self.lastExtinctionTimeStep = self.timeStep
                for i in range(self.initialCells):
                    self.addCell()
                for i in range(self.initialFood):
                    self.addFood()


            if self.deaths:
                self.ageDeathsPercent = self.ageDeaths / self.deaths * 100
                self.hungerDeathsPercent = self.hungerDeaths / self.deaths * 100

            spacer = ["------------------------------"]
            hours, minutes, seconds = formatSeconds(self.time)
            self.info = [
                "Time:              {}h {}m {:.2f}s".format(hours, minutes, seconds),
                f"Time step:         {self.timeStep}",
                "Food:              "+str(len(self.food)),
                "Current FPS:       "+str(self.fps),
                "Max frame rate:    "+str(self.maxFrameRate),
                *spacer,
                "Deaths:            "+str(self.deaths),
                "Extinctions:       "+str(self.extinctions),
                "Last run:          {}h {}m {:.2f}s".format(*formatSeconds(self.speciesDuration)),
                f"                   {self.timeStepSpeciesDuration} time steps",
                *spacer,
                "Peak ammount:      "+str(self.record),
                f"Ammount:           {len(self.cellNames)} total",
                f" - Sexual:         {len(self.cells)} ({round(len(self.cells)/len(self.cellNames)*100) if len(self.cellNames)>0 else 0}%)",
                f" - Asexual:        {len(self.asexcells)} ({round(len(self.asexcells)/len(self.cellNames)*100) if len(self.cellNames)>0 else 0}%)",
                *spacer,
                f"Highest speed:     {self.fastest.speed if len(self.cells+self.asexcells) else None} ({self.fastest.name if self.cells+self.asexcells else None})",
                "Av. speed:         "+str(self.avSpeed),
                f"Highest vision:    {self.mostVision.vision if len(self.cells+self.asexcells) else None} ({self.mostVision.name if self.cells+self.asexcells else None})",
                "Av. vision:        "+str(self.avVision),
                f"Highest appeal:    {self.mostAppeal.appeal if self.cells else 0} ({self.mostAppeal.name if self.cells else None})",
                "Av. appeal:        "+str(self.avAppeal),
                f"Highest mass:      {self.mostMass.mass if self.asexcells else 0} ({self.mostMass.name if self.asexcells else None})",
                "Av. mass:          "+str(self.avMass),
                *spacer

            ]


            if self.debugTarget:

                for i in self.debugTarget.info:
                    self.info.append(i)
            else:
                self.info.append("No target selected")

            self.minZoom = round(self.simulation.size.x / self.enviroment.size.x, 2)

            self.zoom = round(self.zoom, 2)

            self.enviroment.update()

            self.showNames = self.showNameToggle.checked
            self.showMatingLine = self.showMatingToggle.checked


            self.registerData()

    def registerData(self):
        if self.timeStep%self.registerFreq==0:
            self.data["simID"] = self.simId
            self.data["step"] = int(self.timeStep/self.registerFreq)
            self.data["total_ammount"] = len(self.cells)+len(self.asexcells)
            self.data["total_peak_ammount"] = self.record
            self.data["cell_ammount"] = len(self.cells)
            self.data["cell_peak_ammount"] = 0
            self.data["asexcell_ammount"] = len(self.asexcells)
            self.data["asexcell_peak_ammount"] = 0
            self.data["food_ammount"] = len(self.food)

            self.saveData()

    def saveData(self):
        self.pauseTime = True
        with open("data.csv", "a") as f:
            csv_writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            csv_writer.writerow(self.data)
        self.pauseTime = False

    def draw(self):
        background(100)
        self.simulation.background(50)
        self.enviroment.background(0)

        if not self.hideSimulation.checked:
            for f in self.food:
                f.show()

            for r in self.cells+self.asexcells:
                r.show()

                if self.showNames:
                    r.showName()

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
        if self.debugTargetEntry.text in self.cellNames.keys():
            self.debugTarget = self.cellNames[self.debugTargetEntry.text]
            self.debugTarget.highlight = True
            if self.debugTarget != oldDebugTarget and oldDebugTarget:
                oldDebugTarget.highlight = False
        elif self.debugTargetEntry.text in self.cellNamesDead.keys():
            self.debugTarget = self.cellNamesDead[self.debugTargetEntry.text]
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

    def pause(self):
        self.pauseTime = not self.pauseTime
        self.pauseButton.set_label("Unpause" if self.pauseTime else "Pause")

    def addFood(self):
        self.food.append(Food(self, Vector(randint(self.enviroment.pos.x, self.enviroment.size.x), randint(self.enviroment.pos.y, self.enviroment.size.y))))

    def addCell(self):
        self.cells.append(Cell(self,
                                Vector(randint(self.enviroment.pos.x, self.enviroment.size.x), randint(self.enviroment.pos.y, self.enviroment.size.y)),
                                {
                                    "vision": randint(100, 150),
                                    "speed": randint(20,50),
                                    "appeal": randint(0, 100)
                                }))

    def addAsexCell(self):
        self.asexcells.append(AsexCell(self,
                                Vector(randint(self.enviroment.pos.x, self.enviroment.size.x), randint(self.enviroment.pos.y, self.enviroment.size.y)),
                                {
                                    "vision": randint(100, 150),
                                    "speed": randint(20,50)
                                }))

    def events(self):
        for event in pg.event.get():
            self.enviroment.event = event
            if event.type == pg.QUIT:
                # self.saveData()
                self.graphs.terminate()
                self.killUpdateThread = True
                self.updateThread.join()
                raise SystemExit
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    # self.saveData()
                    self.graphs.terminate()
                    self.killUpdateThread = True
                    self.updateThread.join()
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
