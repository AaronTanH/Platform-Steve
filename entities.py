#Aaron Tan
#AndrewID: ahtan
#15-112 TP Entities File
import math, copy, random, time
from TermProject import *
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
        self.ddx = 0
        self.ddy = 0
        self.jump = True
        self.collision = False
        self.friction = False
        self.friction = 2
        self.slip = True
        self.dead = False
        if self.weight == "Projectile":
            self.width = (app.height//app.rows)//3
            self.height = (app.width//app.cols)//3
            self.r = 5
            self.health = 5
        if self.weight == "Small":
            self.width = (app.height//app.rows)
            self.height =(app.width//app.cols)
            self.r = 5
            self.health = 5*app.difficulty
        if self.weight == "Medium":
            self.width = (app.height // app.rows)
            self.height = (app.width// app.cols)*2
            self.r = 10
            self.health = 10*app.difficulty
        if self.weight == "Large":
            self.width = (app.height//app.rows)*2
            self.height =(app.width//app.cols)*2
            self.r = 15
            self.health = 15*app.difficulty
        self.accel = self.baseAccelPerSecond
        self.normalVelo = self.baseVeloPerSecond
        self.maxVelo = self.normalVelo
    def __repr__(self):
        return f"{self.name}, {self.sprite}, {(self.x, self.y)}"
    def __hash__(self):
        return hash((self.name, self.x, self.y))
    def __eq__(self, other):
        return self.name == other.name

    def getBounds(self):
        return (self.x-self.width//2, self.y-self.height//2,
        self.x+self.width//2, self.x+self.height//2)

    @staticmethod #Generates the base accel, velo and gravity from timer delay
    def initializeFrameRate(timerDelay):
        Entity.baseAccelPerSecond = (Entity.baseAccel/1000)*timerDelay
        Entity.baseVeloPerSecond = (Entity.baseVelo/1000)*timerDelay
        Entity.gravity = (Entity.baseGrav/1000)*timerDelay

    def moveEntity(self, app): #moves self, checks for conditions to kill
        self.dx += self.ddx
        self.dy += self.ddy
        self.ddx = 0
        self.ddy = 0

        if (not (0 <= self.x < app.width) or not #If not in bounds or gonna die
        (0 <= self.y < app.height)) or self.health <= 0:
            self.kill(app)

        if self.dx > self.maxVelo:
            self.dx = self.maxVelo
        elif self.dx < -self.maxVelo:
            self.dx = -self.maxVelo
        
        if not self.flying: #If entity cannot fly, applies gravity
            self.dy += self.gravity
        else:
            self.x += self.dx
            self.y += self.dy
            return
        self.slip = False
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
    
    def kill(self, app): #Kills if it exits frame
        self.dead = True

    
    def drawEntity(self, app, canvas):
        canvas.create_oval(self.x - self.width//2,
        self.y - self.height//2, self.x + self.width//2,
        self.y + self.height//2, fill = self.sprite)

################################################################################

class Player(Entity): #Player Object

    def __init__(self, x, y, app):
        super().__init__("Player","Red", x, y,
            "Medium", app)
        self.hearts = 3
        self.health = 20
        self.ammo = 10
        self.blocks = 0
        self.left = False
        self.right = False
        self.root = False
        self.silence = False
        self.doubleJump = False 
        self.equipped = Sword(app)
    
    def updateDimensions(self):
        self.x1 = self.x0 + app.height // app.rows
        self.y1 = self.y0 + (app.width// app.cols)*2
    
    def moveEntity(self, app):
        super().moveEntity(app)
        x, y = minRadius(self.x, self.y,
        app.cursor.x, app.cursor.y, app.cursor.r)
        app.cursor.x = x
        app.cursor.y = y
        if self.health <= 0:
            self.kill(app)
    
    def kill(self, app): #Kills if it exits frame
            if ((self.y < 0 or self.y > app.height) or (self.health <= 0) or
            (self.x <= 0 and app.stage == 0)): #If it goes out of bounds
                self.hearts -= 1
                self.y, self.x = app.height//2, app.width//2
                self.health = 20
                self.dy = 0
                self.dx = 0
                app.death = True
                
            elif self.x <= 0: #Goes back if there is another dude
                app.stage -= 1
                app.grid = app.stages[app.stage]
                app.mobStage = app.mobStages[app.stage]
                self.x = app.width-5
                return

            elif self.x >= app.width and app.stage == len(app.stages)-1:
                app.stage += 1
                app.difficulty += 1
                app.stages.append(b.generateStage(app))
                app.mobStages.append(e.generateEntities(app))
                app.grid = app.stages[app.stage]
                app.mobStage = app.mobStages[app.stage]
                app.score += 100
                self.x = 5
                return

            elif self.x >= app.width:
                app.stage += 1
                app.grid = app.stages[app.stage]
                app.mobStage = app.mobStages[app.stage]
                self.x = 5
                return
            
            if self.hearts <= 0:
                app.restart = True
                if app.score >= app.highScore:
                    app.highScore = app.score

################################################################################

class Enemy(Entity): #All Enemies of the player with AI
    def __init__ (self, name, sprite, x, y, weight, strength, app):
        super().__init__(name, sprite, x, y, weight, app)
        self.attack = strength
        if self in self.entityList:
            self.entityList.remove(self)
    
    def moveEntity(self, app):
        super().moveEntity(app)

    def pathFind(self, app, player):
        if distance(self.x, self.y, player.x, player.y) < self.r + player.r:
            player.health -= self.attack
            player.dx = 2*(self.dx - player.dx)#Knocks Back
            player.dy = 2*(self.dy - player.dy)#Knocks Back
    
    def kill(self, app):
        super().kill(app)
        app.score += 5*app.difficulty

class Blob(Enemy): #Stupid Blob
    def __init__(self, x, y, app):
        name = "Blob"
        sprite = "Green"
        strength = 2*app.difficulty
        weight = "Small"
        super().__init__(name, sprite, x, y, weight, strength, app)
        self.dxInitial = 10
        self.dx = self.dxInitial

    def pathFind(self, app, player):
        super().pathFind(app, player)
        if self.collision and self.dx == 0:
            self.dxInitial = -self.dxInitial
            self.dx = self.dxInitial
        elif self.friction and self.dx < 0:
            self.dx = max(self.dx-2, -abs(self.dxInitial))
        elif self.friction and self.dx > 0:
            self.dx = min(self.dx+2, abs(self.dxInitial))
        else:
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
        if not (self.width+10 <= self.x <= app.width-self.width-10):
            self.dxInitial = -self.dxInitial
            self.dx = self.dxInitial
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
        self.direction = "Up"
    
    def pathFind(self, app, player):
        super().pathFind(app, player)
        if abs(self.y-player.y) < 20:
            pass
        elif self.y < player.y:
            self.dy = 10
        else:
            self.dy = -10
        if abs(self.x-player.x) < self.r + player.r:
            pass
        elif self.x < player.x:
            self.dx = 10
        else:
            self.dx = -10

################################################################################
  
class Projectile(Entity): #All Projectiles of thing
    projectileList = []
    def __init__(self, name, sprite, x, y, app):
        self.projectileList.append(self)
        super().__init__(name, sprite, x, y, "Projectile", app)
        self.damage = 5+3*app.difficulty
        self.flying = True
        self.owner = None
    
    def intersect(self, app, L):
        for entity in L:
            x = entity.x-self.x
            y = entity.y-self.y
            if self.owner == entity.name:
                pass
            if isinstance(entity, Projectile):
                pass
            elif (x**2 + y**2)**(0.5) < self.r+entity.r:
                entity.health -= self.damage
                self.health -= self.damage

class Sword(Projectile):
    def __init__(self, app):
        self.x = app.cursor.x
        self.y = app.cursor.y
        app.cursor.r = 75
        super().__init__("Sword", "Grey", self.x, self.y, app)
        self.projectileList.remove(self)
        self.health = 1000
        self.damage = 10
        self.r = 10
        self.animated = False
        self.timer = 1
        self.owner = "Player"
    
    def moveEntity(self, app): #Moves sword in relation to player, updates info
        self.x = app.cursor.x
        self.y = app.cursor.y
    
        if self.animated and time.time() + self.pressed > self.timer:
            self.animated = False
    
    def intersect(self, app, L): # adds timer when mouse pressed
        super().intersect(app, L)
        self.animated = True
        self.pressed = time.time()

    def drawEntity(self, app, canvas):
        if self.animated:
            canvas.create_line(self.x+app.player.height//4, self.y,
            self.x-app.player.height//4, self.y, fill = self.sprite, width = 3)
        else:
            canvas.create_line(self.x, self.y-app.player.height//4, self.x,
            self.y + app.player.height//4, fill = self.sprite, width = 3)

class Bow(Projectile):
    def __init__(self, app):
        app.cursor.r = 75
        entity = app.player
        self.y = entity.y
        if entity.left:
            self.x = entity.x - entity.width
        elif entity.right:
            self.x = entity.x + entity.width
        else:
            self.x = entity.x
            self.y = entity.y + entity.height
        super().__init__("Bow", "Grey", self.x, self.y, app)
        self.health = 1000
        self.damage = 10
        self.r = 0
        self.owner = "Player"
    
    def moveEntity(self, app):
        if app.player.left:
            self.x = app.player.x - app.player.width
            self.y = app.player.y
        elif app.player.right:
            self.x = app.player.x + app.player.width
            self.y = app.player.y
        else:
            self.x = app.player.x
            self.y = app.player.y + app.player.height
    
    def intersect(self, app, L): # adds timer when mouse pressed
        self.animated = True
        self.pressed = time.time()
    
    def drawEntity(self, app, canvas):
        canvas.create_line(self.x, self.y-app.player.height//4,
        self.x, self.y + app.player.height//4, fill = self.sprite)
        canvas.create_oval(app.cursor.x-2, app.cursor.y-2, app.cursor.x+2,
        app.cursor.y+2, fill = "Black")

class Arrow(Projectile): #Creates an arrow centered on player
    def __init__(self, app, entity, dx, dy):
        self.x = entity.x
        self.y = entity.y
        super().__init__("Arrow", "Black", self.x, self.y, app)
        self.owner = "Player"
        self.flying = False
        self.maxVelo = self.maxVelo*5
        self.dx = dx
        self.dy = dy
        self.r = 50
        self.length = 10
        angle = math.atan(dy/dx)
        self.xLength = self.length*math.cos(angle)//2
        self.yLength = self.length*math.sin(angle)//2
        self.direction = 1
        self.friction = False
        self.collision = False

    def moveEntity(self, app): #Makes maxVelo include y direction
        if self.friction or self.collision:
            self.kill(app)
        speed = (self.dx**2 + self.dy**2)**0.5
        if speed > self.maxVelo:
            self.dx = self.dx * self.maxVelo / speed
            self.dy = self.dy * self.maxVelo / speed
        super().moveEntity(app)
        if self.dx < 0:
            self.direction *= -1
        if self.dy < 0:
            self.direction *= -1
        if self.dx == 0:
            angle = math.pi/4
        else:
            angle = math.atan(self.dy/self.dx)
        self.xLength = self.length*math.cos(angle)//2
        self.yLength = self.direction*self.length*math.sin(angle)//2

    def drawEntity(self, app, canvas):
        canvas.create_line(self.x - self.xLength, self.y - self.yLength,
        self.x + self.xLength, self.y + self.yLength, fill=self.sprite, width=2)



class Pick(Projectile):
    def __init__(self, app):
        self.x = app.cursor.x
        self.y = app.cursor.y
        app.cursor.r = 100
        super().__init__("Pick", "Black", self.x, self.y, app)
        self.projectileList.remove(self)
        self.health = 1000
        self.damage = 10
        self.r = 10
        self.animated = False
        self.timer = 1
        self.owner = "Player"
    
    def kill(app):
        return
    
    def moveEntity(self, app): #Moves sword in relation to player, updates info
        self.x = app.cursor.x
        self.y = app.cursor.y
        
        if self.animated and time.time() + self.pressed > self.timer:
            self.animated = False
    
    def intersect(self, app, L): # adds timer when mouse pressed
        self.animated = True
        self.pressed = time.time()

    def drawEntity(self, app, canvas):
        canvas.create_line(self.x, self.y-app.player.height//4,
        self.x, self.y + app.player.height//4, fill = self.sprite, width = 2)
        canvas.create_line(self.x+5, self.y-app.player.height//4,
        self.x-5, self.y-app.player.height//4, fill = self.sprite, width = 5)

class Block(Projectile):
    def __init__(self, app):
        self.x = app.cursor.x
        self.y = app.cursor.y
        app.cursor.r = 100
        super().__init__("Block", "Black", self.x, self.y, app)
        self.projectileList.remove(self)
        self.health = 1000
        self.damage = 10
        self.r = 10
        self.animated = False
        self.timer = 1
        self.owner = "Player"
    
    def kill(app):
        return
    
    def moveEntity(self, app): #Moves sword in relation to player, updates info
        self.x = app.cursor.x
        self.y = app.cursor.y
        
        if self.animated and time.time() + self.pressed > self.timer:
            self.animated = False
    
    def intersect(self, app, L): #Ignores Intersect
        pass

    def drawEntity(self, app, canvas): #Draws Entity
        if app.player.blocks > 0:
            canvas.create_rectangle(self.x - app.player.width//4,
            self.y - app.player.height//8, self.x + app.player.width//4,
            self.y + app.player.height//8, fill = self.sprite, width = 2)
        else:
            canvas.create_rectangle(self.x - app.player.width//4,
            self.y - app.player.height//8, self.x + app.player.width//4,
            self.y + app.player.height//8, fill = "White", width = 2)

def smartFind(entity, app, player):
    if entity.y+entity.height//2 == player.y+player.height//2:
        pass

def findEmptyBlock(app): #Finds Empty Block
    while True:
        row = random.randint(0, app.rows-10)
        col = random.randint(0, app.cols-1)
        if app.grid[col][row].isFluid():
            x0, y0, x1, y1 = getCellBounds(app, row, col)
            return (x1 + x0)/2, (y1 + y0)/2

def generateEntities(app): #Generates Entities
    L = []
    for i in range(int(app.difficulty**0.5)):
        x, y = findEmptyBlock(app)
        L.append(Blob(x, y, app))
    for i in range(int(app.difficulty**0.5)):
        x, y = findEmptyBlock(app)
        L.append(Fly(x, y, app))
    for i in range(int(app.difficulty**0.5)//2):
        x, y = findEmptyBlock(app)
        L.append(SmartFly(x, y, app))
    return L