#Aaron Tan
#AndrewID: ahtan
#15-112 TP Blocks File
import math, copy, random, time
class Block(object): #Blocks Superclass for all the levels

    blockAction = []
    types = set() #Creates set of blocks

    def __init__(self, name, sprite, coords): #Initializes block data
        self.sprite = sprite
        self.state = "Solid"
        self.name = name
        (self.x0, self.y0, self.x1, self.y1) = coords
        self.coords = coords
        self.cooldown = 1
        self.warm = True

    def __repr__(self): #returns name, state and coords in tuple
        return (self.name, self.state, (self.x0, self.y0, self.x1, self.y1))
    
    def __hash__(self):
        return hash((self.name, self.x0, self.y0))
    
    def __eq__(self, other):
        return isinstance(other, Block) and self.name == other.name
    
    def isFluid(self):
        if self.state == "Gas" or self.state == "Liquid":
            return True
        else:
            return False
    
    def drawBlock(self, app, canvas): #replace with image later
        canvas.create_rectangle(self.x0, self.y0, self.x1, self.y1,
        fill = self.sprite, width = app.cellWidth, outline = "White")
    
    def doBlock(self, entity):
        if self.warm: #provides cooldown to prevent excessive activation
            self.blockAction.append(self)
            self.initialTime = time.time()
            self.warm = False
        else:
            return
    
    def updateBlock(self, app):
        if (time.time() - self.initialTime) > self.cooldown:
            self.blockAction.remove(self)
            self.warm = True

class Air(Block): #The thing you can move though
    Block.types.add("Air")
    def __init__(self, coords):
        super().__init__("Air", "White", coords)
        self.state = "Gas"

class Normal(Block): #Literally does nothing
    Block.types.add("Normal")
    def __init__(self, coords):
        super().__init__("Normal", "Black", coords)

class Normal1(Block): #Literally does nothing
    Block.types.add("Normal1")
    def __init__(self, coords):
        super().__init__("Normal", "Light Grey", coords)

class Lava(Block): #Literally does nothing
    Block.types.add("Lava")
    def __init__(self, coords):
        super().__init__("Normal", "Orange", coords)
    
    def doBlock(self, entity):
        if self.warm:
            entity.health -= 2
        super().doBlock(entity)

class upMove(Block): #Bouncy!
    Block.types.add("upMove")
    def __init__(self, coords):
        super().__init__("UpMove", "Light Grey", coords)
    
    def doBlock(self, entity):
        super().doBlock(entity)
        entity.ddy -= entity.accel//2
    
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

class downMove(Block): #Bouncy!
    Block.types.add("downMove")
    def __init__(self, coords):
        super().__init__("downMove", "Light Grey", coords)
    
    def doBlock(self, entity):
        super().doBlock(entity)
        entity.ddy += entity.accel//2
        #entity.ddy = entity.accel*5
    
    def drawBlock(self, app, canvas):
        super().drawBlock(app, canvas)
        xArrowApex = (self.x0+self.x1)/2
        yArrowApex = (self.y1)
        yArrowSide = (self.y0 + self.y1)/2
        leftArrowBase = (xArrowApex + self.x0)/2
        rightArrowBase = (xArrowApex + self.x1)/2
        canvas.create_rectangle(leftArrowBase, yArrowSide, rightArrowBase,
        self.y0, fill = "Black")
        canvas.create_polygon(self.x0, yArrowSide, xArrowApex, yArrowApex,
        self.x1, yArrowSide, fill = "Black")

class leftMove(Block): #Bouncy!
    Block.types.add("leftMove")
    def __init__(self, coords):
        super().__init__("leftMove", "Light Grey", coords)
    
    def doBlock(self, entity):
        super().doBlock(entity)
        entity.ddx -= entity.accel//2
    
    def drawBlock(self, app, canvas):
        super().drawBlock(app, canvas)
        yArrowApex = (self.y0+self.y1)/2
        xArrowApex = (self.x0)
        xArrowSide = (self.x0 + self.x1)/2
        topArrowBase = (yArrowApex + self.y0)/2
        botArrowBase = (yArrowApex + self.y1)/2
        canvas.create_rectangle(xArrowSide, topArrowBase,
        self.x1, botArrowBase, fill = "Black")
        canvas.create_polygon(xArrowSide, self.y0, xArrowApex, yArrowApex,
        xArrowSide, self.y1, fill = "Black")

class rightMove(Block): #Bouncy!
    Block.types.add("rightMove")
    def __init__(self, coords):
        super().__init__("leftMove", "Light Grey", coords)
    
    def doBlock(self, entity):
        super().doBlock(entity)
        entity.ddx += entity.accel//2
    
    def drawBlock(self, app, canvas):
        super().drawBlock(app, canvas)
        yArrowApex = (self.y0+self.y1)/2
        xArrowApex = (self.x1)
        xArrowSide = (self.x0 + self.x1)/2
        topArrowBase = (yArrowApex + self.y0)/2
        botArrowBase = (yArrowApex + self.y1)/2
        canvas.create_rectangle(xArrowSide, topArrowBase,
        self.x0, botArrowBase, fill = "Black")
        canvas.create_polygon(xArrowSide, self.y0, xArrowApex, yArrowApex,
        xArrowSide, self.y1, fill = "Black")

class Ice(Block): #Slippery!
    Block.types.add("Ice")
    def __init__(self, coords):
        super().__init__("Ice", "Light Blue", coords)
    
    def doBlock(self, entity):
        entity.slip = True
        super().doBlock(entity)
        if entity.dx > 0:
            entity.dx += entity.friction
        elif entity.dx < 0:
            entity.dx -= entity.friction
        

    def drawBlock(self, app, canvas):
        super().drawBlock(app, canvas)

class Vanish(Block): #Template for writing other blocks
    Block.types.add("Vanish")
    def __init__(self, coords):
        super().__init__("Vanish", "Green", coords)
        self.timer = 1 #seconds
        self.visible = True
    
    def doBlock(self, entity):
        if self.sprite == "Green":
            self.blockAction.append(self)
            self.initialTime = time.time()
            self.sprite = "Light Green"

    def updateBlock(self, app):
        if (time.time() - self.initialTime) > self.timer:
            if self.visible:
                self.state = "Gas"
                self.sprite = "White"
                self.visible = False
                self.initialTime = time.time()
                self.timer = 3
            else:
                self.state = "Green"
                self.state = "Solid"
                self.sprite = "Green"
                self.visible = True
                self.blockAction.remove(self)
                self.timer = 1

    def drawBlock(self, app, canvas):
        super().drawBlock(app, canvas)

class Crumble(Block): #Template for writing other blocks
    Block.types.add("Crumble")
    def __init__(self, coords):
        super().__init__("Crumble", "Grey", coords)
        self.strength = random.randint(2, 10)
    
    def doBlock(self, entity):
        super().doBlock(entity)
        if entity.y + entity.height//2 == self.y0:
            return
        if entity.dx >= entity.maxVelo-5:
            self.strength -= 2
        else:
            self.strength -= 1
        if entity.dy >= entity.maxVelo-5:
            self.strength -= 2
        else:
            self.strength -= 1
        if self.strength <= 0:
            self.state = "Gas"
            self.sprite = "White"

    
    def updateBlock(self, app):
        pass
    
    def drawBlock(self, app, canvas):
        super().drawBlock(app, canvas)
    
class Brick(Block): #Template for writing other blocks
    Block.types.add("Brick")
    def __init__(self, coords):
        super().__init__("Brick", "Brown", coords)
    
    def doBlock(self, entity):
        super().doBlock(entity)
        if entity.dy < 0 and entity.y > self.y1:
            self.state = "Gas"
            self.sprite = "White"

    def updateBlock(self, app):
        pass
    
    def drawBlock(self, app, canvas):
        super().drawBlock(app, canvas)

class Heart(Block): #Adds Health
    Block.types.add("Heart")
    def __init__(self, coords):
        super().__init__("Heart", "Red", coords)
    
    def doBlock(self, entity):
        super().doBlock(entity)
        if entity.dy < 0 and entity.y > self.y1 and not self.sprite == "Black":
            self.state = "Normal"
            self.sprite = "Black"
            entity.health += 10
            try:
                entity.hearts += 1
            except:
                passFly
    
    def updateBlock(self, app):
        pass
    
    def drawBlock(self, app, canvas):
        super().drawBlock(app, canvas)

class Ammo(Block): #Adds Ammo
    Block.types.add("Ammo")
    def __init__(self, coords):
        super().__init__("Ammo", "Blue", coords)
    
    def doBlock(self, entity):
        super().doBlock(entity)
        if entity.dy < 0 and entity.y > self.y1 and not self.state == "Normal":
            self.state = "Normal"
            self.sprite = "Black"
            try:
                entity.ammo += 10
            except:
                pass
    
    def updateBlock(self, app):
        pass
    
    def drawBlock(self, app, canvas):
        super().drawBlock(app, canvas)

class Fly(Block): #Lets player fly
    Block.types.add("Fly")
    def __init__(self, coords):
        super().__init__("Fly", "Yellow", coords)
        self.timer = 10
    
    def doBlock(self, entity):
        super().doBlock(entity)
        if ((entity.dy < 0 and entity.y > self.y1)
        and (not self.state == "Black" and entity.name == "Player")):
            self.state = "Normal"
            self.sprite = "Black"
            entity.health += 10
            self.initialTime = time.time()
            entity.flying = True
            entity.jump = False
    
    def updateBlock(self, app):
        if time.time() - self.initialTime > self.timer:
            app.player.flying = False
    
    def drawBlock(self, app, canvas):
        super().drawBlock(app, canvas)

class Template(Block): #Template for writing other blocks
    #Block.types.add("")
    def __init__(self, coords):
        super().__init__("Name", "Sprite", coords)
    
    def doBlock(self, entity):
        super().doBlock(entity)
    
    def updateBlock(self, app):
        pass
    
    def drawBlock(self, app, canvas):
        super().drawBlock(app, canvas)

################################################################################
#Auxillary Block Function 
################################################################################
def pickBlockType(include = Block.types, exclude = {}): #Picks blocktype
    validTypes = []
    for block in include:
        if block not in exclude and block in include:
            validTypes.append(block)
    total = len(validTypes)
    if len(validTypes) == 0: return
    
    i = random.randint(0, total-1)
    if validTypes[i] == None:
        return "Air"
    return validTypes[i]

def generateBlock(name, coords): #Generates block given name and coords

    if name == "Air":
        return Air(coords)
    elif name == "Normal":
        return Normal(coords)
    elif name == "Normal1":
        return Normal1(coords)
    elif name == "Lava":
        return Lava(coords)
    elif name == "upMove":
        return upMove(coords)
    elif name == "downMove":
        return downMove(coords)
    elif name == "leftMove":
        return leftMove(coords)
    elif name == "rightMove":
        return rightMove(coords)
    elif name == "Ice":
        return Ice(coords)
    elif name == "Vanish":
        return Vanish(coords)
    elif name == "Crumble":
        return Crumble(coords)
    elif name == "Brick":
        return Brick(coords)
    elif name == "Heart":
        return Heart(coords)
    elif name == "Ammo":
        return Ammo(coords)
    elif name == "Fly":
        return Fly(coords)
    else:
        return Air(coords)
    ''' #future expansions
    elif name == "":
        return (coords)
    elif name == "":
        return (coords)
    elif name == "":
        return (coords)
    elif name == "":
        return (coords)
    elif name == "":
        return (coords)
    elif name == "":
        return (coords)
    '''

def generatePlat(app):
    pass

def generateFloor(app, L, col0, col1, row, block):
    for col in range(col0, col1):
        L[col][row] = generateBlock(block, getCellBounds(app, row, col))

def generateStair(L, x0, y0, x1, y1):
    pass

def generateWall(app, L, col, row0, row1, block):
    for row in range(row0, row1-1):
        L[col][row] = generateBlock(block, getCellBounds(app, row, col))

def generateObstacle():
    pass

def generateStage(app):
    grid = [[Air(getCellBounds(app, row, col))
                for row in range(app.rows)] for col in range(app.cols)]
    
    rows = app.rows
    row = random.randint(5,8)
    previousCol = 0
    while row < rows: #Creates Floors
        block = pickBlockType(exclude = {"Air", "Ammo", "Heart", "Fly",
        "upMove", "downMove"})
        length = random.randint(5, app.cols//2)
        placement = random.randint(0, app.cols-length-1)
        generateFloor(app, grid, placement, placement+length, row, block)
        if (length//2 + placement) - previousCol > 10:
            row += random.randint(0,5)
    
    cols = app.cols
    col = random.randint(1,3)
    while col < cols: #Creates Walls
        block = pickBlockType(exclude = {"Air", "Ammo", "Heart", "Fly",
        "rightMove", "leftMove", "Lava"})
        length = random.randint(5, app.rows//2)
        placement = random.randint(0, app.rows-length-1)
        generateWall(app, grid, col, placement, placement+length, block)
        col += random.randint(5,8)

    while row < rows: #Adds air spaces to increase maneuverability
        length = random.randint(5, app.cols//4)
        placement = random.randint(0, app.cols-length-1)
        generateFloor(app, grid, placement, placement+length, row, "Air")
        generateFloor(app, grid, placement, placement+length, row+1, "Air")
        row += random.randint(0,5)
    
    while col < cols: #Creates Air spaces to increase movement
        length = random.randint(5, app.rows//2)
        placement = random.randint(0, app.rows-length-1)
        generateWall(app, grid, col, placement, placement+length, "Air")
        generateWall(app, grid, col+1, placement, placement+length, "Air")
        generateWall(app, grid, col+2, placement, placement+length, "Air")
        col += random.randint(8,15)
    
    for i in range(3): #Adds powerups
        block = pickBlockType(include = {"Ammo", "Heart", "Fly"})
        row = random.randint(0, app.rows-1)
        col = random.randint(0, app.cols-1)
        grid[col][row] = generateBlock(block, getCellBounds(app, row, col))
    
    grid[0][app.rows-1] = Normal(getCellBounds(app, app.rows-1, 0))
    grid[app.cols-1][app.rows-1] = Normal(getCellBounds(app, 
    app.rows-1, app.cols-1))
      
    return grid

def getCellBounds(app, row, col): #From earlier 15-112 notes, Cell with block
    gridWidth = app.width
    gridHeight = app.height
    x0 = col*gridWidth/app.cols
    y0 = row*gridHeight/app.rows
    x1 = (col+1)*gridWidth/app.cols
    y1 = (row+1)*gridHeight/app.rows
    return (x0, y0, x1, y1)