#################################################
# Term Project!
# By Aaron Tan ahtan@andrew.cmu.edu
# Fall 2020
#################################################

import math, copy, random, pygame

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

class App(object):
    def __init__(self, x = 0, y = 0, title = None):
        self.width, self.height, title = x, y, title
###############
#Blocks
###############
class Block(object): #Blocks Superclass for all the levels
    def __init__(self, name, state, sprite, coords):
        self.sprite = sprite
        self.state = state
        self.name = name
        (self.x0, self.y0, self.x1, self.y1) = coords
        self.width = self.x1-self.x0
        self.height = self.y1-self.y0
    def __repr__(self):
        return (self.name, self.state, self.x, self.y)
    
    def __hash__(self):
        return hash((self.name, self.state, self.x, self.y))
    
    def __eq__(self, other):
        return isinstance(other, Block) and self.name == other.name
    
    def color(self):
        if self.sprite == "White":      return (255, 255, 255)
        elif self.sprite == "Black":    return (0, 0, 0)
        elif self.sprite == "Red":      return (255, 0, 0)
        else:                           return (255, 0, 255)
    
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

class Entity(object):
    baseVelo = 400
    baseAccel = 500
    baseGrav = 50
    def __init__(self, name, sprite, x, y, weight, airBorne, app):
        self.name = name
        self.sprite = sprite
        self.x0 = x
        self.y0 = y
        self.weight = weight
        self.airBorne = airBorne
        self.dx = 0
        self.dy = 0

        if self.weight == "Medium":
            self.x1 = self.x0 + (app.height // app.rows)
            self.y1 = self.y0 + (app.width// app.cols)*2
            self.jump = self.baseAccel

        self.width = self.x1-self.x0
        self.height = self.y1-self.y0
    def __repr__(self):
        pass
    def __hash__(self):
        pass
    def __eq__(self):
        pass

    def color(self):
        if self.sprite == "White":      return (255, 255, 255)
        elif self.sprite == "Black":    return (0, 0, 0)
        elif self.sprite == "Red":      return (255, 0, 0)
        else:                           return (255, 0, 255)

    @staticmethod
    def initializeFrameRate(timerDelay):
        Entity.baseAccelPerSecond = (Entity.baseAccel/1000)*timerDelay
        Entity.baseVeloPerSecond = (Entity.baseVelo/1000)*timerDelay
        Entity.gravPerSecond = (Entity.baseGrav/1000)*timerDelay

class Player(Entity):

    def __init__(self, x, y, app):
        self.lives = 3
        self.sword = True
        self.gun = True
        self.ammo = 0
        self.jump = False
        self.left = False
        self.right = False
        super().__init__("Player", "Red", x, y, "Medium", False, app)
        self.accel = Entity.baseAccelPerSecond
        self.maxVelo = Entity.baseVeloPerSecond
    
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
    app = App()
    app.height = height
    app.width = width
    pygame.display.set_caption("Tech Demo")

    return appStarted(app)

def appStarted(app): #Model
    app.win = pygame.display.set_mode((app.width, app.height))
    app.gameOver = False
    app.timerDelay = 16 #ms
    Entity.initializeFrameRate(app.timerDelay)
    app.rows = 48
    app.cols = 80
    app.margin = 0
    app.cellWidth = 0
    app.player =  Player(app.width//2, app.height//2, app)
    createLevel(app)
    pygame.time.delay(app.timerDelay)
    return app

def createLevel(app): #generates level

    app.grid = [[Air(getCellBounds(app, row, col))
                for row in range(app.rows)] for col in range(app.cols)]
    finalCol = app.cols-1
    finalRow = app.rows-1
    app.grid[0] = [NormalSolid(getCellBounds(app, row, 0))
                for row in range(app.rows)]
    app.grid[finalCol] = [NormalSolid(getCellBounds(app, row, finalCol))
                for row in range(app.rows)]
    for col in range(app.cols):
        app.grid[col][finalRow] = NormalSolid(getCellBounds(app, finalRow, col))

################################################################################
# Controller
################################################################################

def timerFired(app, keys):
    movePlayer(app, keys)

def movePlayer(app, keys): #moves player
    if app.player.dx > app.player.maxVelo:
        app.player.dx = app.player.maxVelo
    elif app.player.dx < -app.player.maxVelo:
        app.player.dx = -app.player.maxVelo
        
    app.player.x0 += app.player.dx
    app.player.x1 += app.player.dx
    fall(app, app.player)
    if collision(app, app.player):
        app.player.x0 -= app.player.dx
        app.player.x1 -= app.player.dx
        app.player.dx = 0
    if app.player.airBorne:
        pass
    elif ((not keys[pygame.K_a] and app.player.dx < 0 or
    not keys[pygame.K_d] and app.player.dx > 0) or
    keys[pygame.K_a] and keys[pygame.K_d]):
        friction (app, app.player)

def friction (app, entity):
    if entity.dx > 0:
        entity.dx -= entity.accel
        if entity.dx < 0:      entity.dx = 0
    else:
        entity.dx += entity.accel
        if entity.dx > 0:      entity.dx = 0
    

def collision(app, entity): #checks if entity is in nearby blocks
    corners = []
    corners.append(getCellOfCoords(app, entity.x0, entity.y0))
    corners.append(getCellOfCoords(app, entity.x0, entity.y1))
    corners.append(getCellOfCoords(app, entity.x1, entity.y0))
    corners.append(getCellOfCoords(app, entity.x1, entity.y1))
    for (row, col) in corners:
        if not app.grid[row][col].isFluid():
            return True
    return False
    


    pass

def fall(app, entity): #simulates gravity
    entity.dy += Entity.gravPerSecond
    entity.y0 += entity.dy
    entity.y1 += entity.dy
    if collision(app, entity):
        entity.y0 -= entity.dy
        entity.y1 -= entity.dy
        entity.dy = 0

    pass

def mousePressed(app):
    pass

def keyPressed(app, keys):
    if app.player.airBorne:
        pass
    elif keys[pygame.K_a] and keys[pygame.K_d]:
        app.player.left = False
        app.player.right = False
    elif keys[pygame.K_a] and app.player.dx > -app.player.maxVelo: #Left
        app.player.dx -= app.player.accel
        app.player.left = True
        app.player.right = False
    elif keys[pygame.K_d] and app.player.dx > -app.player.maxVelo: #Right
        app.player.dx += app.player.accel
        app.player.right = True
        app.player.left = False
    
    if keys[pygame.K_w]:
        app.player.dy = -10
    elif keys[pygame.K_s]:
        pass
    


def getCellBounds(app, row, col): #From earlier anims, Cell with block
    gridWidth = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    x0 = col*gridWidth/app.cols + app.margin
    y0 = row*gridHeight/app.rows + app.margin
    x1 = (col+1)*gridWidth/app.cols + app.margin
    y1 = (row+1)*gridHeight/app.rows + app.margin
    return (x0, y0, x1+1, y1+1)

def getCellOfCoords(app, x, y):
    col = (x-app.margin)*app.rows/app.width
    row = (y-app.margin)*app.rows/app.height
    return roundHalfUp(row), roundHalfUp(col)-1

################################################################################
# View
################################################################################
def redrawAll(app):
    drawGrid(app)
    drawEntity(app)

    pygame.display.update()

def drawGrid(app):
    for row in app.grid:
        for block in row:
            drawBlock(app, block)

def drawBlock(app, block): #replace with image later

    pygame.draw.rect(app.win, block.color(), (block.x0, block.y0, block.width,
    block.height))

def drawEntity(app):
    drawPlayer(app)

def drawPlayer(app):
    pygame.draw.ellipse(app.win, app.player.color(),
    (app.player.x0, app.player.y0, app.player.width, app.player.height))

################################################################################
#Extra
################################################################################

def main():
    app = playTP()
    while not app.gameOver:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app.gameOver = True
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pos()
        keyPressed(app, keys)
        timerFired(app, keys)

        redrawAll(app)

main()
pygame.quit()