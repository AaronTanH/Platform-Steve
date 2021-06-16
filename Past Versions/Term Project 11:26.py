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
    @staticmethod #Generates the base accel, velo and gravity from timer delay
    def initializeFrameRate(timerDelay):
        Entity.baseAccelPerSecond = (Entity.baseAccel/1000)*timerDelay
        Entity.baseVeloPerSecond = (Entity.baseVelo/1000)*timerDelay
        Entity.gravPerSecond = (Entity.baseGrav/1000)*timerDelay

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
    app.timerDelay = 50 #ms
    Entity.initializeFrameRate(app.timerDelay)
    app.rows = 48
    app.cols = 80
    app.margin = 10
    app.cellWidth = 1
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

    #app.grid[0] = [NormalSolid(getCellBounds(app, row, 0))
    #            for row in range(app.rows)]

    app.grid[finalCol] = [NormalSolid(getCellBounds(app, row, finalCol))
                for row in range(app.rows)]

    for col in range(app.cols):
        app.grid[col][finalRow] = NormalSolid(getCellBounds(app, finalRow, col))
################################################################################
# Controller
################################################################################

def timerFired(app):
    moveEntities(app)

def moveEntities(app): #Moves all entities
    for entity in app.entities:
        moveEntity(app, entity)

def moveEntity(app, entity): #moves arbitrary entity

    friction (app, entity)
    fall(app, entity)

    if 0 < entity.dx > entity.maxVelo: #Prevents 
        entity.dx = entity.maxVelo
    elif 0 > entity.dx < -entity.maxVelo:
        entity.dx = -entity.maxVelo
        entity.y += entity.dy

    X1 = entity.x+entity.dx
    Y1 = entity.y+entity.dy
    dx = entity.dx//5
    dy = entity.dy//5
    tests = 5
    collided = False
    for i in range(1, tests+1):
        newX = i*dx+entity.x
        newY = i*dy+entity.y
        if collision(app, entity, newX, newY):
            entity.dy, entity.x, entity.y = 0, newX-dx, newY-dy
            collided = True
    if not collided:
        entity.x, entity.y = X1, Y1
    
    
    

def friction (app, entity):
    friction = 5
    if entity.dx > 0:
        entity.dx -= entity.accel/friction
        if entity.dx < 0:      entity.dx = 0
    else:
        entity.dx += entity.accel/friction
        if entity.dx > 0:      entity.dx = 0
    

def collision(app, entity, x, y): #checks if entity is in nearby blocks
    corners = []
    corners.append(getCellOfCoords(app, x, y))
    corners.append(getCellOfCoords(app, x, y+entity.height))
    corners.append(getCellOfCoords(app, x+entity.width, y+entity.height))
    corners.append(getCellOfCoords(app, x+entity.width, y))
    corners.append(getCellOfCoords(app, x+entity.width//2, y+entity.height//2))
    for (row, col) in corners:
        if (col not in range(len(app.grid)) or
        row not in range(len(app.grid[0]))):
            return True
        elif not app.grid[col][row].isFluid():
            entity.airborne = False
            return True
    return False

def fall(app, entity): #simulates gravity
    entity.dy += Entity.gravPerSecond

def mousePressed(app, event):
    pass

def keyPressed(app, event):
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
    elif event.key == "a" and event.key == "d":
        app.player.left = False
        app.player.right = False
    
    if event.key == "w":
        pass
    elif event.key == "s":
        pass
    


def getCellBounds(app, row, col): #From earlier anims, Cell with block
    gridWidth = app.width
    gridHeight = app.height
    x0 = col*gridWidth/app.cols
    y0 = row*gridHeight/app.rows
    x1 = (col+1)*gridWidth/app.cols
    y1 = (row+1)*gridHeight/app.rows
    return (x0, y0, x1, y1)

def getCellOfCoords(app, x, y):
    col = x*app.cols/app.width
    row = y*app.rows/app.height
    return roundHalfUp(row), roundHalfUp(col)

################################################################################
# View
################################################################################
def redrawAll(app, canvas):
    drawGrid(app, canvas)
    drawEntity(app, canvas)

def drawGrid(app, canvas):
    for row in app.grid:
        for block in row:
            drawBlock(app, canvas, block)

def drawBlock(app, canvas, block): #replace with image later
    canvas.create_rectangle(block.x0, block.y0, block.x1, block.y1,
    fill = block.sprite, width = app.cellWidth, outline = "White")

def drawEntity(app, canvas):
    drawPlayer(app, canvas)

def drawPlayer(app, canvas):
    canvas.create_oval(app.player.x, app.player.y,
    app.player.x + app.player.width, app.player.y + app.player.height,
    fill = app.player.sprite)
    canvas.create_text(100, 100,
    text = f"{app.player.x} {app.player.y} {getCellOfCoords(app, app.player.x, app.player.y)}")

################################################################################
#Extra
################################################################################

def main():
    playTP()

if __name__ == '__main__':
    main()