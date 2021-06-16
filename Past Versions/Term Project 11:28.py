#################################################
# Term Project!
# By Aaron Tan ahtan@andrew.cmu.edu
# Fall 2020
#################################################

import math, copy, random
from cmu_112_graphics import *

#################################################
# Helper functions
#################################################

def almostEqual(d1, d2, epsilon=10**-7):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

import decimal
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

################################################################################
# Classes
################################################################################

###############
#Blocks
###############
class Block(object): #Blocks Superclass for all the levels
    def __init__(self, name, state, sprite, coords): #Initializes block data
        self.sprite = sprite
        self.state = state
        self.name = name
        (self.x0, self.y0, self.x1, self.y1) = coords

    def __repr__(self): #returns name, state and coords in tuple
        return (self.name, self.state, (self.x0, self.y0, self.x1, self.y1))
    
    def __hash__(self):
        return hash((self.name, self.state, self.x0, self.y0))
    
    def __eq__(self, other):
        return isinstance(other, Block) and self.name == other.name
    
    def isFluid(self):
        if self.state == "Non-Solid":
            return True
        else:
            return False

class Air(Block):
    def __init__(self, coords):
        super().__init__("Air", "Non-Solid", "White", coords)

class NormalSolid(Block):
    def __init__(self, coords):
        super().__init__("Normal Solid", "Solid", "Black", coords)
    
    def doBlock(self, entity):
        return

class upMove(Block):
    def __init__(self, coords):
        super()._init__("up move", "Solid", "Black", coords)
    
    def doBlock(self, entity):
        entity.dx = -10
        return
##############
#Entities
##############

class Entity(object): #Initializes all entities with coords, velocities and lbs
    baseVelo = 1000
    baseAccel = 1000
    baseGrav = 500
    entityList = []
    def __init__(self, name, sprite, x, y, weight, airBorne, app):
        self.entityList.append(self)
        self.name = name
        self.sprite = sprite
        self.x = x
        self.y = y
        self.weight = weight
        self.airBorne = airBorne
        self.dx = 0
        self.dy = 0
        if self.weight == "Medium":
            self.width = (app.height // app.rows)
            self.height = (app.width// app.cols)*2
            self.jump = self.baseAccel
    def __repr__(self):
        pass
    def __hash__(self):
        pass
    def __eq__(self):
        pass

    def getBounds(self):
        return (self.x-self.width//2, self.y-self.height//2,
        self.x+self.width//2, self.x+self.height//2)

    @staticmethod #Generates the base accel, velo and gravity from timer delay
    def initializeFrameRate(timerDelay):
        Entity.baseAccelPerSecond = (Entity.baseAccel/1000)*timerDelay
        Entity.baseVeloPerSecond = (Entity.baseVelo/1000)*timerDelay
        Entity.gravity = (Entity.baseGrav/1000)*timerDelay

class Player(Entity): #Player Object

    def __init__(self, x, y, app):
        self.lives = 3
        self.sword = True
        self.gun = True
        self.ammo = 0
        self.jump = False
        self.left = False
        self.right = False
        super().__init__("Player", "Red", x, y, "Medium", False, app)
        self.accel = self.baseAccelPerSecond
        self.maxVelo = self.baseVeloPerSecond
    
    def updateDimensions(self):
        self.x1 = self.x0 + app.height // app.rows
        self.y1 = self.y0 + (app.width// app.cols)*2

################################################################################
# Model
################################################################################

def playTP(): #Defines largest 16-10 aspect ratio possible for screen
    width = 1391
    height = 846
    aspectRatio = 5/3
    if width < aspectRatio*height: #if too high redefines height
        height = roundHalfUp(width//aspectRatio)
    else: #If too wide redefines width
        width = roundHalfUp(aspectRatio*height)
    runApp(width = width, height = height)

def appStarted(app): #Model
    app.timerDelay = 18 #ms
    Entity.initializeFrameRate(app.timerDelay)
    app.rows = 48
    app.cols = 80
    app.margin = 10
    app.cellWidth = 1
    app.cellSizeX = app.width//app.cols 
    app.cellSizeY = app.height//app.rows
    app.player =  Player(app.width//2, app.height//2, app)
    app.key = None
    app.entities = Entity.entityList
    createLevel(app)
    pass

def createLevel(app): #generates level
    finalCol = app.cols-1
    finalRow = app.rows-1

    app.grid = [[Air(getCellBounds(app, row, col))
                for row in range(app.rows)] for col in range(app.cols)]

    app.grid[0] = [NormalSolid(getCellBounds(app, row, 0))
                for row in range(app.rows)]

    app.grid[finalCol] = [NormalSolid(getCellBounds(app, row, finalCol))
                for row in range(app.rows)]

    for col in range(app.cols):
        app.grid[col][finalRow] = NormalSolid(getCellBounds(app, finalRow, col))
    
    for col in range(15, app.cols-5):
        app.grid[col][30] = NormalSolid(getCellBounds(app, 30, col))
    
################################################################################
# Controller
################################################################################

def timerFired(app): #Moves in accordance to timer
    moveEntities(app)

def moveEntities(app): #Moves all entities
    for entity in app.entities:
        moveEntity(app, entity)

def moveEntity(app, entity): #moves arbitrary entity
    if entity.dx > entity.maxVelo:
        entity.dx = entity.maxVelo
    elif entity.dx < -entity.maxVelo:
        entity.dx = -entity.maxVelo
    entity.dy += entity.gravity
    if not collision(app, entity):
        entity.x += entity.dx
        entity.y += entity.dy
   
def keyPressed(app, event): #Key pressed, detects key pressed
    app.key == None
    if event.key == "p":
        app.player.x = app.width//2
        app.player.y = 4*app.height//5
        app.player.dy= 0
    if app.player.airBorne:
        pass
    elif event.key == "a": #Left
        app.player.dx -= app.player.accel*2
        app.player.left = True
        app.player.right = False
        app.key = "a"
    elif event.key == "d": #Right
        app.player.dx += app.player.accel*2
        app.player.right = True
        app.player.left = False
        app.key == "d"
    elif event.key == "w":
        app.player.dy -= app.player.accel*2
    elif event.key == "s":
        app.player.dy += app.player.accel*2

def getCellBounds(app, row, col): #From earlier anims, Cell with block
    gridWidth = app.width
    gridHeight = app.height
    x0 = col*gridWidth/app.cols
    y0 = row*gridHeight/app.rows
    x1 = (col+1)*gridWidth/app.cols
    y1 = (row+1)*gridHeight/app.rows
    return (x0, y0, x1, y1)

def getCellOfCoords(app, x, y): #Gets cell from coords
    col = x*app.cols/app.width
    row = y*app.rows/app.height
    return row, col

def collision(app, entity): #Checks all possible blocks between entity and block
    dx, dy = 0, 0
    if entity.dx < 0:   xStep = -app.cellSizeX
    else:               xStep = app.cellSizeX
    if entity.dy < 0:   yStep = -app.cellSizeY
    else:               yStep = app.cellSizeY
    if entity.dx == 0:  slope, vertical = 0, True
    else:               slope, vertical = entity.dy/entity.dx, False

    while abs(dx) < abs(entity.dx) or abs(dy) < abs(entity.dy):
        if abs(slope*dx) > abs(dy) or vertical: 
            dy += yStep
        else:
            dx += xStep
        if collisionBlock(app, entity, entity.x+dx, entity.y+dy):   return True
    
    return False


def collisionBlock(app, entity, x, y): #Checks if exists collision of entity
    row0, col0 = getCellOfCoords(app, x, y)
    row1, col1 = getCellOfCoords(app, x-entity.width//2, y-entity.height//2)
    row2, col2 = getCellOfCoords(app, x+entity.width//2, y+entity.height//2)
    if row2 % 1 == 0:
        row2 = row2-1
    if col2 % 1 == 0:
        col2 = col2-1
    rows = [int(row0), int(row1), int(row2)]
    cols = [int(col0), int(col1), int(col2)]

    for row in rows:
        for col in cols:
            if row < 0:             row = 0
            elif row >= app.rows:   row = app.rows=1
            if col < 0:             col = 0
            elif col >= app.cols:   col = app.cols=1

            if not app.grid[col][row].isFluid():
                correctDisplacement(app, entity, row, col, x, y)
                print(entity.x, entity.y)
                return True
    return False


def correctDisplacement(app, entity, row, col, x, y):
    '''spaces appropriate amount
    once collision is detected '''

    x0, y0, x1, y1 = getCellBounds(app, row, col)
    dx, dy = entity.dx, entity.dy
    xNew0, xNew1, yNew0, yNew1 = entity.x, entity.x, entity.y, entity.y
    xDiff = 0
    yDiff = 0
    if x-entity.width//2 < x1 and entity.dx != 0:
            xNew0 = x1 + entity.width//2
            
            dx = 0

    if x+entity.width//2 > x0 and entity.dx != 0:
            xNew1 = x0 - entity.width//2
            dx = 0

    if y-entity.height//2 < y1 and entity.dy != 0:
            yNew0 = y1 + entity.height//2
            dy = 0

    if y+entity.height//2 > y0 and entity.dy != 0:
            yNew1 = y0 - entity.height//2
            dy = 0

    if entity.dx < 0:
        entity.x = xNew0
    else:
        entity.x = xNew1
    if entity.dy < 0:
        entity.y = yNew0
    else:
        entity.y = yNew1
    entity.dx = dx
    entity.dy = dy
    
    


def checkInBound(app, row0, col0, row1, col1):
    pass

################################################################################
# View
################################################################################
def redrawAll(app, canvas):
    drawGrid(app, canvas)
    drawEntities(app, canvas)

def drawGrid(app, canvas):
    for row in app.grid:
        for block in row:
            drawBlock(app, canvas, block)

def drawBlock(app, canvas, block): #replace with image later
    canvas.create_rectangle(block.x0, block.y0, block.x1, block.y1,
    fill = block.sprite, width = app.cellWidth, outline = "White")

def drawEntities(app, canvas):
    for entity in app.entities:
        drawEntity(app, canvas, entity)

def drawEntity(app, canvas, entity):
    canvas.create_oval(entity.x - entity.width//2, entity.y - entity.height//2,
    entity.x + entity.width//2, entity.y + entity.height//2,
    fill = entity.sprite)
    canvas.create_text(100, 100,
    text = f"{entity.x} {entity.y} {getCellOfCoords(app, entity.x, entity.y)}")

################################################################################
#Extra
################################################################################

def main():
    playTP()

if __name__ == '__main__':
    main()