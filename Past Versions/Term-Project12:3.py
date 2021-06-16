#################################################
# Term Project!
# By Aaron Tan ahtan@andrew.cmu.edu
# Fall 2020
#################################################

import math, copy, random, time
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

    blockAction = []

    def __init__(self, name, sprite, coords): #Initializes block data
        self.sprite = sprite
        self.state = "Solid"
        self.name = name
        (self.x0, self.y0, self.x1, self.y1) = coords

    def __repr__(self): #returns name, state and coords in tuple
        return (self.name, self.state, (self.x0, self.y0, self.x1, self.y1))
    
    def __hash__(self):
        return hash((self.name, self.x0, self.y0))
    
    def __eq__(self, other):
        return isinstance(other, Block) and self.name == other.name
    
    def isFluid(self):
        if self.state == "Non-Solid":
            return True
        else:
            return False
    
    def drawBlock(self, app, canvas): #replace with image later
        canvas.create_rectangle(self.x0, self.y0, self.x1, self.y1,
        fill = self.sprite, width = app.cellWidth, outline = "White")
    
    def doBlock(self, entity):
        pass
    
    def updateBlock(self, app):
        pass

class Air(Block): #The thing you can move though
    def __init__(self, coords):
        super().__init__("Air", "White", coords)
        self.state = "Non-Solid"

class NormalSolid(Block): #Literally does nothing
    def __init__(self, coords):
        super().__init__("Normal Solid", "Black", coords)

class upMove(Block): #Bouncy!
    def __init__(self, coords):
        super().__init__("UpMove", "Grey", coords)
    
    def doBlock(self, entity):
        super().doBlock(entity)
        entity.dy = -50
    
    def drawBlock(self, app, canvas):
        super().drawBlock(app, canvas)
        xArrowApex = (self.x0+self.x1)/2
        yArrowApex = (self.y0)
        yArrowSide = (self.y0 + self.y1)/2
        leftArrowBase = (xArrowApex + self.x0)/2
        rightArrowBase = (xArrowApex + self.x1)/2
        canvas.create_rectangle(leftArrowBase, yArrowSide, rightArrowBase,
        self.y1, fill = "Black")
        canvas.create_polygon(self.x0, yArrowSide, xArrowApex, yArrowApex,
        self.x1, yArrowSide, fill = "Black")

class Ice(Block): #Slippery!
    def __init__(self, coords):
        super().__init__("Ice", "Light Blue", coords)
    
    def doBlock(self, entity):
        super().doBlock(entity)
        if entity.dx > 0:
            entity.dx += 2
        elif entity.dx < 0:
            entity.dx -= 2

    def drawBlock(self, app, canvas):
        super().drawBlock(app, canvas)

class Vanish(Block): #Template for writing other blocks
    def __init__(self, coords):
        super().__init__("Vanish", "Green", coords)
        self.timer = 1 #seconds
        self.visible = True
    
    def doBlock(self, entity):
        super().doBlock(entity)
        if self.sprite == "Green":
            self.blockAction.append(self)
            self.initialTime = time.time()
            self.sprite = "Light Green"

    def updateBlock(self, app):
        if (time.time() - self.initialTime) > self.timer:
            if self.visible:
                self.state = "Non-Solid"
                self.sprite = "White"
                self.visible = False
                self.initialTime = time.time()
            else:
                self.state = "Green"
                self.state = "Solid"
                self.sprite = "Green"
                self.visible = True
                self.blockAction.remove(self)

    def drawBlock(self, app, canvas):
        super().drawBlock(app, canvas)

class Template(Block): #Template for writing other blocks
    def __init__(self, coords):
        super().__init__("Name", "Sprite", coords)
    
    def doBlock(self, entity):
        super().doBlock(entity)
    
    def updateBlock(self, app):
        pass
    
    def drawBlock(self, app, canvas):
        super().drawBlock(app, canvas)


##############
#Entities
##############

class Entity(object): #Initializes all entities with coords, velocities and lbs
    baseVelo = 1000
    baseAccel = 1000
    baseGrav = 500
    entityList = []
    def __init__(self, name, sprite, x, y, weight, app):
        self.entityList.append(self)
        self.name = name
        self.sprite = sprite
        self.x = x
        self.y = y
        self.weight = weight
        self.flying = False
        self.dx = 0
        self.dy = 0
        self.jump = True
        self.collision = False
        self.friction = False
        if self.weight == "Small":
            self.width = (app.height//app.rows)
            self.height =(app.width//app.cols)
            self.r = 5
        if self.weight == "Medium":
            self.width = (app.height // app.rows)
            self.height = (app.width// app.cols)*2
            self.r = 10
        if self.weight == "Large":
            self.width = (app.height//app.rows)*2
            self.height =(app.width//app.cols)*2
            self. r = 15
        self.accel = self.baseAccelPerSecond
        self.maxVelo = self.baseVeloPerSecond
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
    
    def moveEntity(self, app): #moves self
        if self.dx > self.maxVelo:
            self.dx = self.maxVelo
        elif self.dx < -self.maxVelo:
            self.dx = -self.maxVelo
        
        if not self.flying: #If entity cannot fly, applies gravity
            self.dy += self.gravity

        if friction(app, self):
            self.friction = True
        else:
            self.friction = False

        if collision(app, self):
            self.collision = True
        else:
            self.x += self.dx
            self.y += self.dy
            self.collision = False

    
    def drawEntity(self, app, canvas):
        canvas.create_oval(self.x - self.width//2,
        self.y - self.height//2, self.x + self.width//2,
        self.y + self.height//2, fill = self.sprite)

class Player(Entity): #Player Object

    def __init__(self, x, y, app):
        self.health = 20
        self.sword = True
        self.bow = True
        self.ammo = 0
        self.left = False
        self.right = False
        super().__init__("Player","Red", x, y,
            "Medium", app)
    
    def updateDimensions(self):
        self.x1 = self.x0 + app.height // app.rows
        self.y1 = self.y0 + (app.width// app.cols)*2
    
    def drawEntity(self, app, canvas):
        super().drawEntity(app, canvas)
        canvas.create_text(100, 100,
        text = f"x = {int(self.x)}, y=  {int(self.y)}, heallth:{self.health}")

class Enemy(Entity): #All Enemies of the player with AI
    enemyList = []
    def __init__ (self, name, sprite, x, y, weight, strength, app):
        super().__init__(name, sprite, x, y, weight, app)
        self.attack = strength
        self.enemyList.append(self)
    
    def moveEntity(self, app):
        super().moveEntity(app)
        
    
    def pathFind(self, app, player):
        if distance(self.x, self.y, player.x, player.y) < self.r + player.r:
            player.health -= self.attack
            player.dx += self.dx*2 #Knocks Back
            player.dy += self.dy*2 #Knocks Back

class Blob(Enemy): #Stupid Blob
    def __init__(self, x, y, app):
        name = "Blob"
        sprite = "Green"
        strength = 2
        weight = "Small"
        super().__init__(name, sprite, x, y, weight, strength, app)
        self.dxInitial = 10
        self.dx = self.dxInitial

    def pathFind(self, app, player):
        super().pathFind(app, player)
        if self.collision:
            self.dxInitial = -self.dxInitial
            self.dx = self.dxInitial
        elif self.friction:
            self.dx = self.dxInitial

class Fly(Enemy): #Stupid Fly
    def __init__(self, x, y, app):
        name = "Fly"
        sprite = "Yellow"
        strength = 2
        weight = "Small"
        super().__init__(name, sprite, x, y, weight, strength, app)
        self.dxInitial = 10
        self.dyInitial = 10
        self.dx = self.dxInitial
        self.flying = True
    
    def pathFind(self, app, player):
        super().pathFind(app, player)
        if self.collision or self.y < 0:
            self.dxInitial = -self.dxInitial
            self.dx = self.dxInitial
        elif self.friction:
            self.dx = self.dxInitial

class SmartFly(Enemy):
    def __init__(self, x, y, app):
        name = "Fly"
        sprite = "Orange"
        strength = 2
        weight = "Small"
        super().__init__(name, sprite, x, y, weight, strength, app)
        self.dxInitial = 10
        self.dx = self.dxInitial
        self.flying = True
    
    def pathFind(self, app, player):
        super().pathFind(app, player)

class Projectile(Entity): #All Projectiles of thing
    projectileList = []
    pass

################################################################################
# Model
################################################################################

def playTP(): #Defines largest 16-10 aspect ratio possible for screen
    width = 1380
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
    app.key = None
    createLevel(app)
    createEntities(app)
    pass

def createLevel(app): #generates level
    app.blockAction = Block.blockAction
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
    
    for col in range(15, app.cols-14):
        app.grid[col][30] = NormalSolid(getCellBounds(app, 30, col))
    
    app.grid[14][30] = upMove(getCellBounds(app, 30, 14))

    for col in range(app.cols-14, app.cols-1):
        app.grid[col][30] = Ice(getCellBounds(app, 30, col))
    
    for col in range(app.cols-24, app.cols-14):
        app.grid[col][25] = Vanish(getCellBounds(app, 25, col))

def createEntities(app): #generates entities
    app.entities = Entity.entityList
    app.hostiles = Enemy.enemyList
    app.projectiles = Projectile.projectileList
    app.player =  Player(app.width//2, app.height//2, app)
    Blob(app.width//4, app.height//4, app)
    Fly(app.width//4, app.height//2, app)

################################################################################
# Controller
################################################################################

def timerFired(app): #Moves in accordance to timer
    moveEntities(app)
    updateBlock(app)

def updateBlock(app):
    for block in app.blockAction:
        block.updateBlock(app)

def moveEntities(app): #Moves all entities

    for entity in app.entities:
        entity.moveEntity(app)

    for mob in app.hostiles:
        mob.pathFind(app, app.player)

    for projectile in app.projectiles:
        intersection(app, entity)
   
def keyPressed(app, event): #Key pressed, detects key pressed
    app.key == None
    if event.key == "p":
        app.player.x = app.width//2
        app.player.y = 4*app.height//5
        app.player.dy= 0
    if app.player.flying:
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
    elif event.key == "w" and app.player.jump:
        app.player.dy -= app.player.accel*2
        if app.player.dy <= -app.player.maxVelo*3:
            app.player.dy = -app.player.maxVelo*3
    elif event.key == "s" and app.player.jump:
        pass

def collision(app, entity): #Checks all possible blocks between entity and block
    dx, dy = 0, 0
    if entity.dx < 0:   xStep = -app.cellSizeX
    else:               xStep = app.cellSizeX
    if entity.dy < 0:   yStep = -app.cellSizeY
    else:               yStep = app.cellSizeY
    if entity.dx == 0:  slope, vertical = 0, True
    else:               slope, vertical = abs(entity.dy/entity.dx), False

    while abs(dx) < abs(entity.dx) or abs(dy) < abs(entity.dy):
        if abs(slope*dx) > abs(dy) or vertical: 
            dy += yStep
        else:
            dx += xStep
        if collisionBlock(app, entity, entity.x+dx, entity.y+dy, slope):
            return True
    return False

def collisionBlock(app, entity, x, y, slope): #Checks if exists entity collision
    row0, col0 = getCellOfCoords(app, x, y)
    row1, col1 = getCellOfCoords(app, x-entity.width//2, y-entity.height//2)
    row2, col2 = getCellOfCoords(app, x+entity.width//2, y+entity.height//2)
    if row2 % 1 == 0: #If bottom is on a full block, it doesn't collsion detect
        row2 = row2-1
    if col2 % 1 == 0: #If right is on a full block, it doesn't collision detect
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
                correctDisplacement(app, entity, row, col, x, y, slope)
                app.grid[col][row].doBlock(entity)
                return True
    return False

def correctDisplacement(app, entity, row, col, x, y, slope):
    '''spaces appropriate amount
    once collision is detected '''

    x0, y0, x1, y1 = getCellBounds(app, row, col)
    dx, dy = entity.dx, entity.dy
    xNew, yNew = entity.x, entity.y,
    xDiff = 0
    yDiff = 0
    if x-entity.width//2 < x1 and entity.dx < 0:
            xNew = x1 + entity.width//2
            dx = 0

    if x+entity.width//2 > x0 and entity.dx > 0:
            xNew = x0 - entity.width//2
            dx = 0

    if y-entity.height//2 < y1 and entity.dy < 0:
            yNew = y1 + entity.height//2
            dy = 0

    if y+entity.height//2 > y0 and entity.dy > 0:
            yNew = y0 - entity.height//2
            dy = 0


    '''if (abs(xNew-entity.x) * slope < abs(yNew-entity.y) or yNew > app.height):
        print(f"{entity.name} y collision")
        entity.y = yNew
        entity.dy = dy
        entity.x += entity.dx
    else:
        print(f"{entity.name} x collision")
        entity.x = xNew
        entity.dx = dx
        entity.y += entity.dy
    '''
    entity.x = xNew
    entity.y = yNew
    entity.dx = dx
    entity.dy = dy
 
    
    
    entity.dx = 0
    entity.dy = 0

def friction(app, entity): #applies friction and detects when ents on platforms
    row, col = getCellOfCoords(app, entity.x, entity.y+entity.height//2)

    if row % 1 == 0 and not app.grid[int(col)][int(row)].isFluid():
        app.grid[int(col)][int(row)].doBlock(entity)
        if entity.dy > 0: #Prevents collision if object is moving downward
            entity.dy = 0 
            entity.jump = True
        if entity.dx < 0: #Slows down player
            entity.dx += min(-entity.dx, 2)
        elif entity.dx >= 2: #Slows down player
            entity.dx -= min(entity.dx, 2)
        return True
    else:
        entity.jump = False
        return False

#General Helpers

def getCellBounds(app, row, col): #From earlier 15-112 notes, Cell with block
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

def distance(x0, y0, x1, y1): #finds distance between two points
    x = x1-x0
    y = y1-y0
    return (x**2 + y**2)**(0.5)
################################################################################
# View
################################################################################
def redrawAll(app, canvas):
    drawGrid(app, canvas)
    drawEntities(app, canvas)

def drawGrid(app, canvas):
    for row in app.grid:
        for block in row:
            block.drawBlock(app, canvas)


def drawEntities(app, canvas):
    for entity in app.entities:
        entity.drawEntity(app, canvas)

################################################################################
#Extra
################################################################################

def main():
    playTP()

if __name__ == '__main__':
    main()