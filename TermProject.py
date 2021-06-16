#################################################
# Term Project!
# By Aaron Tan ahtan@andrew.cmu.edu
# Fall 2020
#################################################

import math, copy, random, time
from cmu_112_graphics import *
import blocks as b
import entities as e
import ui as u

#################################################
# Helper functions
#################################################

def almostEqual(d1, d2, epsilon=10**-7): #Copied from 112 Course Notes
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

import decimal
def roundHalfUp(d): #Copied from 112 Course Notes
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

################################################################################
# Model
################################################################################

def appStarted(app):
    app.highScore = 0
    app.start = True
    restartApp(app)

def restartApp(app): #Model
    e.Entity.entityList = []
    e.Projectile.projectileList = []
    app.score = 0
    app.restart = False
    app.pause = False
    app.death = False
    app.timerDelay = 18 #ms
    e.Entity.initializeFrameRate(app.timerDelay)
    app.rows = 48
    app.cols = 80
    app.margin = 10
    app.cellWidth = 1
    app.cellSizeX = app.width//app.cols 
    app.cellSizeY = app.height//app.rows
    app.key = None
    app.difficulty = 1
    app.score = 0
    createUI(app)
    createGame(app)
    pass

def createUI(app):
    app.cursor = u.Cursor(app)

def createGame(app):
    app.stage = 0
    app.stages = []
    app.mobStages = []
    app.blockAction = b.Block.blockAction
    app.stages.append(b.generateStage(app))
    app.grid = app.stages[app.stage]
    app.grid[40][20] = b.Heart(getCellBounds(app, 20, 40))
    createEntities(app)

def createEntities(app): #generates entities
    app.entities = e.Entity.entityList
    app.projectiles = e.Projectile.projectileList
    app.player =  e.Player(app.width//2, app.height//2, app)
    app.mobStages.append(e.generateEntities(app))
    app.mobStage = app.mobStages[app.stage]

################################################################################
# Controller
################################################################################

def timerFired(app): #Moves in accordance to timer
    if app.start or app.restart or app.pause or app.death:
        return
    moveEntities(app)
    updateBlock(app)
    app.cursor.update(app)

def updateBlock(app):
    for block in app.blockAction:
        block.updateBlock(app)

def moveEntities(app): #Moves all entities

    for friendly in app.entities:
        if not friendly.dead:
            friendly.moveEntity(app)

    for mob in app.mobStage:
        if not mob.dead:
            mob.moveEntity(app)
            mob.pathFind(app, app.player)

    for projectile in app.projectiles:
        if not projectile.dead:
            projectile.intersect(app, app.mobStage)

def mouseMoved(app, event):
    x, y = minRadius(app.player.x, app.player.y, event.x, event.y, app.cursor.r)
    app.cursor.x = x
    app.cursor.y = y

def mousePressed(app, event):
    if app.start or app.restart:
        return
    p = app.player
    if p.equipped.name == "Sword": #detects just intersection when pressed
        p.equipped.intersect(app, app.mobStage)
    elif p.equipped.name == "Bow": #Creates arrow with cursor as velocity
        x, y = minRadius(app.player.x, app.player.y,
        event.x, event.y, app.cursor.r)
        dx = x - app.player.x
        dy = y - app.player.y
        e.Arrow(app, app.player, dx, dy)
    elif p.equipped.name == "Pick":
        p.equipped.intersect(app, app.mobStage)
        row, col = getCellOfCoords(app, p.equipped.x, p.equipped.y)
        row, col = int(row), int(col)
        if not app.grid[col][row].isFluid():
            p.blocks += 1
            coords = getCellBounds(app, row, col)
            app.grid[col][row] = b.Air(coords)
    elif p.equipped.name == "Block":
        p.equipped.intersect(app, app.mobStage)
        row, col = getCellOfCoords(app, p.equipped.x, p.equipped.y)
        row, col = int(row), int(col)
        if app.grid[col][row].isFluid():
            if p.blocks <= 0:
                pass
            else:
                p.blocks -= 1
                coords = getCellBounds(app, row, col)
                app.grid[col][row] = b.Normal(coords)

def keyPressed(app, event): #Key pressed, detects key pressed

    #Key state restrictions

    if event.key == "p":
        app.pause = not app.pause
    if app.start:
        app.start = False
        return
    if event.key == "r":
        restartApp(app)
        return
    if event.key == "c":
        app.death = False
    if app.pause or app.death or app.restart:
        return
    p = app.player

    #Movement

    if event.key == "a": #Left
        if p.dx > 0 and not p.slip:
            p.dx = 0
        else:
            p.dx -= p.accel*2
        p.left = True
        p.right = False

    elif event.key == "d": #Right
        if p.dx < 0 and not p.slip:
            p.dx = 0
        else:
            p.dx += p.accel*2
        p.right = True
        p.left = False

    elif event.key == "w":
        if p.flying:
            p.dy -= p.accel
            if p.dy < -p.maxVelo: p.dy = p.maxVelo
        elif p.jump:
            p.dy = -p.accel*3
            p.doubleJump = True
        elif p.doubleJump:
            p.dy = -p.accel*3
            p.doubleJump = False

    elif event.key == "s" and (not p.jump or p.flying):
        p.dy += p.accel
    elif event.key == "s" and p.jump:
        row, col = getCellOfCoords(app, p.x, p.y+p.height//2)
        if row > app.rows-2: return
        elif app.grid[int(col)][int(row)+1].isFluid():
            p.y += app.cellSizeY + p.height + 1
    
    #Equipment

    elif event.key == "1": #Sword
        app.entities.remove(p.equipped)
        p.equipped = e.Sword(app)
    elif event.key == "2": #Bow
        app.entities.remove(p.equipped)
        p.equipped = e.Bow(app)
    elif event.key == "3": #Pick
        app.entities.remove(p.equipped)
        p.equipped = e.Pick(app)
    elif event.key == "4": #Block
        app.entities.remove(p.equipped)
        p.equipped = e.Block(app)

    #Shortcuts

    elif event.key == "Right": #Moves forward a level or generates new level
        app.stage += 1
        if app.stage >= len(app.stages):
            app.difficulty += 1
            app.stages.append(b.generateStage(app))
            app.mobStages.append(e.generateEntities(app))
            app.score += 100
        app.grid = app.stages[app.stage]
        app.mobStage = app.mobStages[app.stage]

    elif event.key == "Left": #Moves back a stage if there is a thing there
        app.stage -= min(1, app.stage)
        app.grid = app.stages[app.stage]
        app.mobStage = app.mobStages[app.stage]

    elif event.key == "f": #toggles flying
        p.flying = not p.flying
    

def collision(app, entity, recurs = 0):
    if recurs >= 10:    return True
    #Checks all possible blocks between entity and block
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
        if collisionBlock(app, entity, entity.x+dx, entity.y+dy, slope, recurs):
            return True
        if entity.friction:
            row, col = getCellOfCoords(app, entity.x+dx,
            entity.y+entity.height//2)
            row, col = int(row), int(col)
            if not (0 <= row < app.rows) or not (0 <= col < app.cols):
                entity.kill(app)
                return False
            app.grid[col][row].doBlock(entity)


    return False

def collisionBlock(app, entity, x, y, slope, recurs):
    #Checks if exists entity collision
    row0, col0 = getCellOfCoords(app, x, y)
    row1, col1 = getCellOfCoords(app, x-entity.width//2, y-entity.height//2)
    row2, col2 = getCellOfCoords(app, x+entity.width//2, y+entity.height//2)
    if row2 % 1 == 0: #If bottom is on a full block, it doesn't collsion detect
        row2 = row2-1
    if col2 % 1 == 0: #If right is on a full block, it doesn't collision detect
        col2 = col2-1
    rows = [int(row0), int(row1), int(row2)]
    cols = [int(col0), int(col1), int(col2)]
    for i in range(len(rows)): #corrects height so it goes inside grid
        if rows[i] < 0:             rows[i] = 0
        elif rows[i] >= app.rows:   rows[i] = app.rows-1
    
    for j in range(len(cols)): #corrects width so it goes inside grid
        if cols[j] < 0:             cols[j] = 0
        elif cols[j] >= app.cols:   cols[j] = app.cols-1
    for row in rows:
        for col in cols:
            if not (0 <= row < app.rows) or not (0 <= col < app.cols):
                entity.kill(app)
                return False
            if not app.grid[col][row].isFluid():
                app.grid[col][row].doBlock(entity)
                correctDisplacement(app, entity, row, col, x, y, slope, recurs)
                return True
    return False

def correctDisplacement(app, entity, row, col, x, y, slope, recurs):
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
    
    if (abs(xNew-entity.x) * slope < abs(yNew-entity.y)):
        entity.y = yNew
        entity.dy = dy
        if collision(app, entity):  return True
        entity.x += entity.dx
    else:
        entity.x = xNew
        entity.dx = dx
        if friction(app, entity): return True
        if collision(app, entity, recurs + 1):  return True
        entity.y += entity.dy
    return True

def friction(app, entity):
    #applies friction and detects when ends on platforms
    row, col = getCellOfCoords(app, entity.x, entity.y+entity.height//2)
    row, col, rem = int(row), int(col), row % 1
    if not (0 <= row < app.rows) or not (0 <= col < app.cols):
                entity.kill(app)
                return False
    if rem == 0 and not app.grid[col][row].isFluid():
        app.grid[col][row].doBlock(entity)
        if entity.dy > 0: #Prevents collision if object is moving downward
            entity.dy = 0 
            entity.doubleJump = True
        if entity.dx < 0: #Slows down player
            entity.dx += min(-entity.dx, entity.friction)
        elif entity.dx >= 2: #Slows down player
            entity.dx -= min(entity.dx, entity.friction)
        entity.jump = True
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

def minRadius(x0, y0, x, y, r0):
    r = distance(x0, y0, x, y)
    if r > r0:
        size = r0/r
    else:
        size = 1
    return x0 - ((x0-x) * size), y0 - ((y0-y) * size)

################################################################################
# View
################################################################################
def redrawAll(app, canvas):
    if app.start:
        drawStart(app, canvas)
        return
    drawGrid(app, canvas)
    drawEntities(app, canvas)
    drawUI(app, canvas)
    if app.restart:
        drawRestart(app, canvas)
    elif app.pause:
        drawPause(app, canvas)
    elif app.death:
        drawDeath(app, canvas)

def drawStart(app, canvas):
    cx, cy = app.width//2, app.height//2

    canvas.create_rectangle(cx-app.width//4, cy-app.height//4, cx+app.width//4,
    cy+app.height//4, fill = "Blue", width = 10)
    
    canvas.create_text(cx, cy, text = "Welcome to 2D\nPlatform Steve",
    font = "Arial 40", fill = "White")
    canvas.create_text(cx, cy+70, text = "Press any Key to Begin",
    font = "Arial 20", fill = "White")
    pass

def drawRestart(app, canvas):
    if app.score >= app.highScore:
        text = f'''Game Over!
    You got a New High Score: {app.score}!'''
    else:
        text = f'''Uh Oh! Game Over!\nYou didn't get past{app.highScore}!
        You only got {app.score}!'''
    cx, cy = app.width//2, app.height//2
    canvas.create_rectangle(cx-app.width//4, cy-app.height//4, cx+app.width//4,
    cy+app.height//4, fill = "Blue", width = 10)
    
    canvas.create_text(cx, cy, text = text,
    font = "Arial 40", fill = "White")
    canvas.create_text(cx, cy+70, text = "Press r to Restart",
    font = "Arial 20", fill = "White")

def drawDeath(app, canvas):   
    text = f'''Current Score:{app.score}\n  High Score:{app.highScore} 
    Lives Left:{app.player.hearts}'''
    cx, cy = app.width//2, app.height//2
    canvas.create_rectangle(cx-app.width//8, cy-app.height//8, cx+app.width//8,
    cy+app.height//8, fill = "Blue", width = 10)
    
    canvas.create_text(cx, cy, text = text,
    font = "Arial 20", fill = "White")
    canvas.create_text(cx, cy+70, text = "Press c to Continue",
    font = "Arial 20", fill = "White")

def drawPause(app, canvas):
    cx, cy = app.width//2, app.height//2
    text = f'''Current Score:{app.score}\n  High Score:{app.highScore} 
    Lives Left:{app.player.hearts}'''
    canvas.create_rectangle(cx-app.width//8, cy-app.height//8, cx+app.width//8,
    cy+app.height//8, fill = "Red", width = 10)
    canvas.create_text(cx, cy+20, text = text,
    font = "Arial 20", fill = "Black")
    
    canvas.create_text(cx, cy-25, text = "Game Paused", font = "Arial 20")

def drawGrid(app, canvas):
    for row in app.grid:
        for block in row:
            block.drawBlock(app, canvas)

def drawUI(app, canvas):
    p = app.player
    app.cursor.draw(app, canvas)
    canvas.create_rectangle(10, 10, 250, 50, fill = "White", width = "5")
    canvas.create_text(120, 20,
    text = f"Ammo: {p.ammo} Blocks: {p.blocks} health: {p.health}")
    canvas.create_text(120, 40,
text = f"Equipped:{p.equipped.name} Hearts:{p.hearts} Level:{app.stage}")
    canvas.create_rectangle(app.width-250, 10, app.width-10, 50,
    fill = "White", width = "5")
    canvas.create_text(app.width-120, 30, text = f"score:{app.score}",
    font = "Arial 20")


def drawEntities(app, canvas):
    for entity in app.entities:
        if not entity.dead:
            entity.drawEntity(app, canvas)
    for mob in app.mobStage:
        if not mob.dead:
            mob.drawEntity(app, canvas)

################################################################################
#Extra
################################################################################

def main():
    runApp(width = 1380, height = 846)

if __name__ == '__main__':
    main()