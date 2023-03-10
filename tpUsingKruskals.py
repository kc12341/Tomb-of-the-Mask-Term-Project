# Name: Kyle Chen
# Andrew ID: kylechen
# Term Project: Tomb of the Mask

from cmu_112_graphics import *
import random

# this code was modified from my tetris project
# all images used were screenshots taken from https://arcadespot.com/game/tomb-of-the-mask-online/
# and https://tomb-of-the-mask.fandom.com/wiki/Tomb_of_the_Mask_Wiki
# the other files were where I tested the separate algorithms and aspects of the code

# this type of enemy will just travel to random locations in its vicinity
class Bat:
    def __init__(self, startRow, startCol, direction, index):
        self.collision = False
        self.color = 'cyan'
        # this will be the actual row of the enemy
        self.row = startRow
        self.col = startCol
        self.direction = direction
        self.index = index
    
    def move(self):
        if self.collision == False:
            if self.index % 2 == 0:
                self.row += self.direction
            else:
                self.col += self.direction

class Chaser:
    def __init__(self, startRow, startCol):
        self.collision = False
        self.color = 'cyan'
        self.row = startRow
        self.col = startCol
        
    def move(self, n, path):
        self.path = path[::-1]
        if self.collision == False:
            (self.row, self.col) = self.path[n] # n is the index

# can add in different types of enemies later, like enemies that shoot projectiles

def gameDimensions():
    # if you want to play on bigger dimensions then you can change the 
    # rows, cols, cellSize, margin
    rows = 21
    cols = 14
    cellSize = 25
    margin = 25

    return (rows, cols, cellSize, margin)

def mazeDimensions(app):
    rows = (app.rows * 2) + 7 # we're adding 7 rows at the bottom for where the player will start
    cols = app.cols
    return (rows, cols)

# the following model-to-view and view-to-model codes were taken and modified from
# the CMU 112 website

# for drawing the board
def getCellBounds(app, row, col):  
    x0 = app.margin + (col * app.cellSize)
    x1 = app.margin + (col+1) * app.cellSize
    y0 = app.margin + row * app.cellSize
    y1 = app.margin + (row+1) * app.cellSize
    return (x0, y0, x1, y1)

def getCell(app, x, y):
    row = int((y - app.margin) / app.cellSize)
    col = int((x - app.margin) / app.cellSize)
    return (row, col)

def appStarted(app):
    # load all the images here
    app.image1 = app.loadImage('images/sprite.png')
    app.player = app.scaleImage(app.image1, 1/15)
    app.homeImage = app.loadImage('images/homeScreen.png')
    app.homeScreen = app.scaleImage(app.homeImage, 1/10)
    app.coinImage = app.loadImage('images/coins.png')
    app.coin = app.scaleImage(app.coinImage, 1/20)
    app.shield = app.loadImage('images/shield.png')
    app.magnet = app.loadImage('images/magnet.png')
    app.coinAddict = app.loadImage('images/coinAddict.png')
    app.scoreBooster = app.loadImage('images/scoreBooster.png')

    # the following spritesheet was made by https://www.codeandweb.com/free-sprite-sheet-packer
    # using screenshots from the game
    app.spritestripImage = app.loadImage('images/spritesheet.png')
    app.spritestrip = app.scaleImage(app.spritestripImage, 1/2)

    # the following sprite code was taken from the CMU 112 Website (Animations 4 lecture)
    app.sprites = [ ]
    for i in range(2):
        # each sprite should be 28 x 28
        sprite = app.spritestrip.crop((1+28*i, 0, 28+28*i, 28))
        app.sprites.append(sprite)
    app.spriteCounter = 0 

    # shop and power up information
    app.shop = False
    app.shieldActive = False
    app.magnetActive = False
    app.coinAddictActive = False
    app.scoreBoosterActive = False
    app.scoreBoost = 0
    app.cost = 10

    # game dimensions
    (app.rows, app.cols, app.cellSize, app.margin) = gameDimensions()

    # this stores the maze and the player space at the beginning of the maze
    (app.totalMazeRows, app.totalMazeCols) = mazeDimensions(app)

    # this stores the dimensions of only the maze
    (app.mazeRows, app.mazeCols) = (app.totalMazeRows - 7, app.totalMazeCols)

    # initialize the player's position at the center of the screen
    (app.playerRow, app.playerCol) = (app.rows // 2 , app.cols // 2)
    (app.drow, app.dcol) = (0, 0)
    # player position with respect to the maze
    app.currMazeRow = app.mazeRows + 6

    # timer information
    app.totalTime = 0
    app.timerDelay = 100
    app.difficulty = 10
    
    # CURRENCY INFORMATION
    app.coinPos = set()
    app.newCoinPos = set()
    app.checkMagnet = []
    app.coins = 410

    # MOVEMENT INFORMATION
    app.scrollY = ((app.totalMazeRows + app.rows) // (app.totalMazeRows // app.rows)) * app.cellSize
    app.rowScrollY = (app.totalMazeRows + app.rows) // (app.totalMazeRows // app.rows)

    # maze information
    (app.leftBorder, app.topBorder, topx1, topy1) = getCellBounds(app, 0, 0)
    (endx0, endy0, app.rightBorder, app.bottomBorder) = getCellBounds(app, app.mazeRows, app.mazeCols)
    app.emptyColor = 'black'
    app.mazeColor = '#' + ''.join(random.choice('ABCDEF0123456') for i in range(6))
    app.board = [([app.emptyColor] * app.cols) for i in range(app.rows)]

    app.walls = set()
    app.newWalls = set()
    app.maze = []
    app.wallsToRemove = []

    # enemy information
    app.enemies = set()
    getWalls(app, 0, app.mazeRows // 2)
    generateMaze(app)

    # points need to be generate after maze has been generated so that it can
    # properly avoid walls
    app.pointPath = set(pathfinder(app, app.mazeRows, app.mazeCols // 2, 0, app.cols // 2))
    app.newPointPath = set() # for the sideScroll function
    pointConverter(app)
    app.bestScore = None
    app.score = 0

    # lose conditions
    app.currLavaRow = (app.rows - 1) + app.rowScrollY
    makeLava(app)

    # enemy chaser information
    app.enemies = set()
    generateEnemy(app)
    adjust(app)
    app.path = pathfinder(app, app.chaser.row, app.chaser.col, app.playerRow, app.playerCol)
    app.iterations = 0

    app.play = False 
    app.gameOver = False
    app.complete = False

# new level makes it so that it generates a new maze rather than restarting the
# entire game
def newLevel(app, score, difficulty):
    # this stores the maze and the player space at the beginning of the maze
    (app.totalMazeRows, app.totalMazeCols) = mazeDimensions(app)

    # this stores the dimensions of only the maze
    (app.mazeRows, app.mazeCols) = (app.totalMazeRows - 7, app.totalMazeCols)

    # initialize the player's position at the center of the screen
    (app.playerRow, app.playerCol) = (app.rows // 2 , app.cols // 2)
    (app.drow, app.dcol) = (0, 0)
    # player position with respect to the maze
    app.currMazeRow = app.mazeRows + 6

    # timer information
    app.totalTime = 0
    app.timerDelay = 100
    if app.difficulty > 2:
        app.difficulty = difficulty - 1
    
    # maze information
    (app.leftBorder, app.topBorder, topx1, topy1) = getCellBounds(app, 0, 0)
    (endx0, endy0, app.rightBorder, app.bottomBorder) = getCellBounds(app, app.mazeRows, app.mazeCols)
    app.score = score
    app.bestScore = None
    app.scrollY = ((app.totalMazeRows + app.rows) // (app.totalMazeRows // app.rows)) * app.cellSize
    app.rowScrollY = (app.totalMazeRows + app.rows) // (app.totalMazeRows // app.rows)

    app.emptyColor = 'black'
    app.mazeColor = '#' + ''.join(random.choice('ABCDEF0123456') for i in range(6))
    app.board = [([app.emptyColor] * app.cols) for i in range(app.rows)]
    # app.endGoal = 

    app.walls = set()
    app.newWalls = set()
    app.maze = []
    app.wallsToRemove = []
    getWalls(app, 0, app.mazeRows // 2)
    generateMaze(app)

    # points need to be generate after maze has been generated so that it can
    # properly avoid walls
    app.pointPath = set(pathfinder(app, app.mazeRows, app.mazeCols // 2, 0, app.cols // 2))
    app.newPointPath = set() # for the sideScroll function
    pointConverter(app)
    
    app.currLavaRow = (app.rows - 1) + app.rowScrollY
    makeLava(app)

    # enemy chaser information
    app.enemies = set()
    generateEnemy(app)
    app.path = pathfinder(app, app.chaser.row, app.chaser.col, app.playerRow, app.playerCol)
    app.iterations = 0
    adjust(app)

    app.shop = False
    app.play = True
    app.gameOver = False
    app.complete = False

# restart is for after you lose and want to return to the home page for the shop
def restart(app, score, bestScore, coins):
    # game dimensions
    (app.rows, app.cols, app.cellSize, app.margin) = gameDimensions()

    # this stores the maze and the player space at the beginning of the maze
    (app.totalMazeRows, app.totalMazeCols) = mazeDimensions(app)

    # this stores the dimensions of only the maze
    (app.mazeRows, app.mazeCols) = (app.totalMazeRows - 7, app.totalMazeCols)

    # initialize the player's position at the center of the screen
    (app.playerRow, app.playerCol) = (app.rows // 2 , app.cols // 2)
    (app.drow, app.dcol) = (0, 0)
    # player position with respect to the maze
    app.currMazeRow = app.mazeRows + 6

    # timer information
    app.totalTime = 0
    app.timerDelay = 100
    app.difficulty = 10
    
    # CURRENCY INFORMATION
    app.coinPos = set()
    app.newCoinPos = set()
    app.coins = coins

    # MOVEMENT INFORMATION
    app.scrollY = ((app.totalMazeRows + app.rows) // (app.totalMazeRows // app.rows)) * app.cellSize
    app.rowScrollY = (app.totalMazeRows + app.rows) // (app.totalMazeRows // app.rows)

    # maze information
    (app.leftBorder, app.topBorder, topx1, topy1) = getCellBounds(app, 0, 0)
    (endx0, endy0, app.rightBorder, app.bottomBorder) = getCellBounds(app, app.mazeRows, app.mazeCols)
    app.emptyColor = 'black'
    app.mazeColor = '#' + ''.join(random.choice('ABCDEF0123456') for i in range(6))
    app.board = [([app.emptyColor] * app.cols) for i in range(app.rows)]

    app.walls = set()
    app.newWalls = set()
    app.maze = []
    app.wallsToRemove = []
    getWalls(app, 0, app.mazeRows // 2)

    # enemy information
    app.enemies = set()
    generateMaze(app)

    # points need to be generate after maze has been generated so that it can
    # properly avoid walls
    app.pointPath = set(pathfinder(app, app.mazeRows, app.mazeCols // 2, 0, app.cols // 2))
    app.newPointPath = set() # for the sideScroll function
    pointConverter(app)
    app.score = score
    app.bestScore = bestScore
    
    app.currLavaRow = (app.rows - 1) + app.rowScrollY
    makeLava(app)

    adjust(app)
    app.path = pathfinder(app, app.chaser.row, app.chaser.col, app.playerRow, app.playerCol)
    app.iterations = 0

    app.play = False 
    app.gameOver = False
    app.complete = False

    # shop and power up information
    app.shop = False
    app.shieldActive = False
    app.magnetActive = False
    app.coinAddictActive = False
    app.scoreBoosterActive = False
    app.cost = 10

def startScreen(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = 'black')
    canvas.create_text(app.width // 2, app.height * 0.25, text = f'Best Score: {app.bestScore}')
    canvas.create_text(app.width // 2, app.height * 0.2, text = 'TOMB OF THE MASK', font='Lato 20')
    canvas.create_text(app.width // 2, app.height * 0.7, text = 'Click to play.')
    canvas.create_image(app.width // 2, app.height // 2, image=ImageTk.PhotoImage(app.homeScreen))
    
    # will draw the platform
    (x0, y0, x1, y1) = getCellBounds(app, app.mazeRows + 3, app.mazeCols // 2)
    canvas.create_rectangle(x0 - app.cellSize, y0 - app.cellSize, x1 + app.cellSize, y1 + app.cellSize)

    # shop button
    canvas.create_rectangle(app.margin, app.height * 0.9, app.width - app.margin, app.height - app.margin)
    canvas.create_text(app.width // 2, app.height * 0.93, text = 'Shop')

def shop(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = 'black')
    canvas.create_text(app.width // 2, app.margin, text=f'coins: {app.coins}')
    canvas.create_rectangle (app.width * 0.1, app.margin // 2, app.width * 0.25, app.margin * 1.5)
    canvas.create_text(app.width * 0.18, app.margin, text=f'Back')

    # shield
    canvas.create_rectangle(app.margin, app.margin * 2, app.width // 2, app.height // 2,
    outline = 'white')   
    canvas.create_text(app.width * 0.285, app.height * 0.1, text='Shield')
    canvas.create_image(app.width * 0.285, app.height * 0.25, image=ImageTk.PhotoImage(app.shield))
    canvas.create_text(app.width * 0.285, app.height * 0.4, text='Protect yourself \n' +
    'from death once.')
    canvas.create_rectangle(app.margin * 1.5, app.height * 0.43, app.width * 0.48, app.height * 0.48)
    canvas.create_text(app.width * 0.28, app.height * 0.455, text=f'Upgrade: {app.cost} coins')

    # magnet
    canvas.create_rectangle(app.width // 2, app.margin * 2, app.width - app.margin, app.height // 2,
    outline = 'white')
    canvas.create_text(app.width * 0.715, app.height * 0.1, text='Magnet')
    canvas.create_image(app.width * 0.715, app.height * 0.25, image=ImageTk.PhotoImage(app.magnet))
    canvas.create_text(app.width * 0.715, app.height * 0.4, text='Attract all nearby \n' +
    'points and coins.')
    canvas.create_rectangle(app.width * 0.52, app.height * 0.43, app.width * 0.92, app.height * 0.48)
    canvas.create_text(app.width * 0.72, app.height * 0.455, text=f'Upgrade: {app.cost * 10} coins')

    # coin addict
    canvas.create_rectangle(app.margin, app.height // 2, app.width // 2, app.height - app.margin * 2,
    outline = 'white')
    canvas.create_text(app.width * 0.285, app.height * 0.52, text='Coin Addict')
    canvas.create_image(app.width * 0.285, app.height * 0.67, image=ImageTk.PhotoImage(app.coinAddict))
    canvas.create_text(app.width * 0.285, app.height * 0.825, text='Turns points into \n' +
    'coins for one round.')
    canvas.create_rectangle(app.margin * 1.5, app.height * 0.85, app.width * 0.48, app.height * 0.9)
    canvas.create_text(app.width * 0.28, app.height * 0.875, text=f'Upgrade: {app.cost * 10} coins')
    
    # score multiplier
    canvas.create_rectangle(app.width // 2, app.height // 2, app.width - app.margin, app.height - app.margin * 2,
    outline = 'white') 
    canvas.create_text(app.width * 0.715, app.height * 0.52, text='Score Multiplier')
    canvas.create_image(app.width * 0.715, app.height * 0.67, image=ImageTk.PhotoImage(app.scoreBooster))
    canvas.create_text(app.width * 0.715, app.height * 0.825, text='Adds five to your score \n' +
    'for each point.')
    canvas.create_rectangle(app.width * 0.52, app.height * 0.85, app.width * 0.92, app.height * 0.9)
    canvas.create_text(app.width * 0.72, app.height * 0.875, text=f'Upgrade: {app.cost * 20} coins')

def drawBoard(app, canvas):
    for row in range(app.rows):
        for col in range(app.cols):
            drawCell(app, canvas, row, col, app.board[row][col]) # replace emptyColor
            # with the block color/empty color later once we generate maze

# I want to make the draw cell so that it will randomly choose a design for 
# the level, ie random color and random block design
def drawCell(app, canvas, row, col, color):
    (x0, y0, x1, y1) = getCellBounds(app, row, col)
    canvas.create_rectangle(x0, y0, x1, y1, fill = color, 
    outline = color)

def pointConverter(app):
    for (row, col) in app.pointPath:
        if (row, col) == (app.playerRow, app.playerCol):
            continue
        (x0, y0, x1, y1) = getCellBounds(app, row, col)
        x0 += 0.45 * app.cellSize
        y0 += 0.45 * app.cellSize
        x1 -= 0.45 * app.cellSize
        y1 -= 0.45 * app.cellSize
        app.newPointPath.add((x0, y0, x1, y1))

    app.pointPath = set()

    for point in app.newPointPath:
        app.pointPath.add(point)
    app.newPointPath = set()


# COIN HELPERS 
def generateCoins(app):
    # 10 coins per level
    for coin in range(10):
        row = random.randint(0, app.mazeRows)
        col = random.randint(0, app.mazeCols)
        app.coinPos.add((row, col))

    # coinAddict Active
    if app.coinAddictActive == True:
        for point in app.pointPath:
            (x0, y0, x1, y1) = point
            (row, col) = getCell(app, x0 + app.cellSize // 2, y0 + app.cellSize // 2)
            app.coinPos.add((row, col))
    
def getCoins(app):
    # magnet Active
    if app.magnetActive == True:
        possibleMoves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        for (drow, dcol) in possibleMoves:
            newRow = app.playerRow + drow
            newCol = app.playerCol + dcol
            if (newRow, newCol) in app.coinPos:
                app.coinPos.remove((newRow, newCol))
                app.coins += 1
    else:
        if (app.playerRow, app.playerCol) in app.coinPos:
            app.coinPos.remove((app.playerRow, app.playerCol))
            app.coins += 1

def drawCoins(app, canvas):
    for (row, col) in app.coinPos:
        if row < 0 or row >= app.rows or col < 0 or col >= app.cols:
            continue
        (x0, y0, x1, y1) = getCellBounds(app, row, col)
        canvas.create_image(x0 + 0.5 * app.cellSize, y0 + 0.5 * app.cellSize,
        image=ImageTk.PhotoImage(app.coin))


# POINT HELPERS
def drawPoints(app, canvas):
    for point in app.pointPath:
        (x0, y0, x1, y1) = point
        canvas.create_rectangle(x0, y0, x1, y1, fill = 'yellow')

def getPoints(app):
    (x0, y0, x1, y1) = getCellBounds(app, app.playerRow, app.playerCol)
    x0 += 0.45 * app.cellSize
    y0 += 0.45 * app.cellSize
    x1 -= 0.45 * app.cellSize
    y1 -= 0.45 * app.cellSize
    if app.magnetActive != True:
        if (x0, y0, x1, y1) in app.pointPath:
            app.pointPath.remove((x0, y0, x1, y1))
            app.score += (1 + app.scoreBoost)
    else:
        # magnet will check the 3 x 3 grid around the player and get the points and coins
        possibleMoves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        for (drow, dcol) in possibleMoves:
            newx0 = x0 + app.cellSize * dcol
            newy0 = y0 + app.cellSize * drow
            newx1 = x1 + app.cellSize * dcol
            newy1 = y1 + app.cellSize * drow
            if (newx0, newy0, newx1, newy1) in app.pointPath:
                app.pointPath.remove((newx0, newy0, newx1, newy1))
                app.score += (1 + app.scoreBoost)

def drawPlayer(app, canvas):
    (x0, y0, x1, y1) = getCellBounds(app, app.playerRow, app.playerCol)
    imageWidth, imageHeight = app.player.size
    (cx, cy) = (x0 + imageWidth // 2, y0 + imageHeight // 2)
    canvas.create_image(cx, cy, image=ImageTk.PhotoImage(app.player))
    if app.shieldActive == True:
        canvas.create_oval(cx - app.cellSize * 0.5, cy - app.cellSize * 0.5, cx + app.cellSize * 0.5,
        cy + app.cellSize * 0.5, outline = 'white', width = 3)
    
    if app.magnetActive == True:
        canvas.create_rectangle(x0 - app.cellSize, y0 - app.cellSize,
        x1 + app.cellSize, y1 + app.cellSize, outline = 'white')

# MAZE HELPERS
def getWalls(app, startRow, endRow):
    app.walls = set(app.walls)

    # we're only generating one quadrant of walls (quadrant 2)
    (midx0, midy0, midx1, midy1) = getCellBounds(app, endRow - 1, (app.mazeCols // 2) - 1)
    for row in range(startRow, endRow):
        for col in range(app.mazeCols // 2):
            app.maze.append({(row, col)}) # creates distinct sets while getting walls
            (x0, y0, x1, y1) = getCellBounds(app, row, col)
            
            if x0 != midx1 and x1 != midx1:
                app.walls.add((x1, y0, x1, y1)) # right wall
            
            if y1 != midy1:
                app.walls.add((x0, y1, x1, y1)) # bottom wall

            if y0 == y1 == app.topBorder:
                pass
            else:
                app.walls.add((x0, y0, x1, y0)) # top wall

            app.walls.add((x0, y0, x0, y1)) # left wall
            
    
    # turn it into a list now that we don't have dupes
    app.walls = list(app.walls)
    random.shuffle(app.walls) 
     
def drawMaze(app, canvas):
    (a, b, c, bottomBorder) = getCellBounds(app, app.rows - 1, app.cols - 1)
    # add the platform the player will stand on
    for wall in app.walls:
        (x0, y0, x1, y1) = wall
        if y0 <= app.topBorder or y1 > bottomBorder:
            continue
        canvas.create_line(x0, y0, x1, y1, fill = app.mazeColor, width = 4)

def makePlatform(app):
    (x0, y0, x1, y1) = getCellBounds(app, app.mazeRows + 3, app.mazeCols // 2)
    app.walls.append((x0, y1, x1, y1))
    app.walls.append((x0 - app.cellSize, y1, x0, y1))
    app.walls.append((x1, y1, x1 + app.cellSize, y1))
    app.walls.append((x0 - app.cellSize, y1, x0 - app.cellSize, y1 + app.cellSize))
    app.walls.append((x1 + app.cellSize, y1, x1 + app.cellSize, y1 + app.cellSize))

    app.walls.append((x0, y1 + app.cellSize, x1, y1 + app.cellSize))
    app.walls.append((x0 - app.cellSize, y1 + app.cellSize, x0, y1 + app.cellSize))
    app.walls.append((x1, y1 + app.cellSize, x1 + app.cellSize, y1 + app.cellSize)) 


def generateMaze(app):
    makeCaverns(app)
    generateMazeHelper(app)
    mirrorAcrossY(app)
    mirrorAcrossX(app)
    generateCoins(app)
    generateEnemy(app)
    makePlatform(app)
    

def makeCaverns(app):
    row1 = random.randint(0, app.mazeRows // 2)
    row2 = random.randint(0, app.mazeRows // 2)
    while not 3 < abs(row1 - row2) < 5:
        row1 = random.randint(0, app.mazeRows // 2)
        row2 = random.randint(0, app.mazeRows // 2)
    if row1 < row2:
        (x0, y0, x1, y1) = getCellBounds(app, row1, 0)
        (nx0, ny0, nx1, ny1) = getCellBounds(app, row2, app.cols)
        for wall in app.walls:
            (wx0, wy0, wx1, wy1) = wall
            if wx0 == wx1 == app.leftBorder:
                continue
            elif y0 < wy0 < ny1: 
                app.walls.remove(wall)
    else:
        (x0, y0, x1, y1) = getCellBounds(app, row2, 0)
        (nx0, ny0, nx1, ny1) = getCellBounds(app, row1, app.cols - 1)
        for wall in app.walls:
            (wx0, wy0, wx1, wy1) = wall
            if wx0 == wx1 == app.leftBorder:
                continue
            if y0 < wy0 < ny1 and (x0 != app.leftBorder or x1 != app.rightBorder):
                app.walls.remove(wall)

def adjust(app):
    for wall in app.walls:
        (x0, y0, x1, y1) = wall
        y0 -= app.scrollY
        y1 -= app.scrollY
        app.newWalls.add((x0, y0, x1, y1))
    
    for point in app.pointPath:
        (x0, y0, x1, y1) = point
        y0 -= app.scrollY
        y1 -= app.scrollY
        app.newPointPath.add((x0, y0, x1, y1))

    for (row, col) in app.coinPos:
        row -= app.rowScrollY
        app.newCoinPos.add((row, col))
    
    app.walls = []
    app.pointPath = set()
    app.coinPos = set()

    for wall in app.newWalls:
        app.walls.append(wall)
    
    for point in app.newPointPath:
        app.pointPath.add(point)
    
    for enemy in app.enemies:
        enemy.row -= app.rowScrollY

    for coin in app.newCoinPos:
        app.coinPos.add(coin)
        
    app.currLavaRow -= app.rowScrollY   
    makeLava(app)

    app.newWalls = set()
    app.newPointPath = set()
    app.newCoinPos = set()
        
# the following code was modified from the pseudocode for Kruskal's Algorithm
# on Wikipedia, found here:
# https://en.wikipedia.org/wiki/Maze_generation_algorithm
def generateMazeHelper(app):
    for wall in app.walls:
        (x0, y0, x1, y1) = wall
        # this will check if the chosen wall is a maze border
        if (x0 == x1 == app.leftBorder):
            continue

        # for vertical walls
        elif x0 == x1:
            (row1, col1) = getCell(app, x0 - app.cellSize // 2, y0 + app.cellSize // 2) # left cell
            (row2, col2) = getCell(app, x0 + app.cellSize // 2, y0 + app.cellSize // 2) # right cell
            if cellsConnected(app, (row1, col1), (row2, col2)):
                continue
            app.wallsToRemove.append(wall)

        elif y0 == y1: # for horizontal walls
            (row1, col1) = getCell(app, x0 + app.cellSize // 2, y0 - app.cellSize // 2) # top cell
            (row2, col2) = getCell(app, x0 + app.cellSize // 2, y0 + app.cellSize // 2) # bottom cell
            if cellsConnected(app, (row1, col1), (row2, col2)):
                continue
            app.wallsToRemove.append(wall)

    for wall in app.wallsToRemove:
        app.walls.remove(wall)

    currLength = len(app.walls) // 2
    while len(app.walls) > currLength:
        index = random.randint(0, len(app.walls) - 1)
        (x0, y0, x1, y1) = app.walls[index] 
        if (x0 == x1 == app.leftBorder):
            continue
        app.walls.pop(index)
    
    for extraEdges in range(3):
        path = None
        while path == None:
            path = pathfinder(app, app.mazeRows // 2, random.randint(0, app.mazeCols // 2), 0, app.mazeCols // 2)
        path.reverse()
        for cell in range(len(path)):
            currCell = path[cell]
            if currCell == path[-1]: 
                continue
            nextCell = path[cell + 1]
            if existsWall(app, currCell, nextCell):
                (x0, y0, x1, y1) = getWall(app, currCell, nextCell)
                app.walls.remove((x0, y0, x1, y1))

def cellsConnected(app, cell1, cell2):
    for mazeCell in app.maze:
        if cell1 in mazeCell and cell2 in mazeCell:
            return True
        elif cell1 in mazeCell:
            withCell1 = mazeCell
        elif cell2 in mazeCell:
            withCell2 = mazeCell

    app.maze.remove(withCell1)
    app.maze.remove(withCell2)
    for elem in withCell2:
        withCell1.add(elem)
    app.maze.append(withCell1)
    return False        

def mirrorAcrossY(app):
    for wall in app.walls:
        (x0, y0, x1, y1) = wall
        app.newWalls.add((app.rightBorder - x1, y0, app.rightBorder - x0, y1))
    
    for wall in app.newWalls:
        app.walls.append(wall)
    
    app.newWalls = set()

def mirrorAcrossX(app):
    mazeBottomBorder = app.mazeRows * app.cellSize
    for wall in app.walls:
        (x0, y0, x1, y1) = wall
        if y0 == y1 == app.margin:
            continue
        app.newWalls.add((x0, mazeBottomBorder - y1, x1, mazeBottomBorder - y0))
    
    for wall in app.newWalls:
        app.walls.append(wall)
    
    app.newWalls = set()

# LOSE CONDITION HELPERS
def makeSpike(app):
    for i in range(2):
        row = random.randint(0, app.rows - 1)
        col = random.randint(0, app.cols - 1)
        app.board[row][col] = 'cyan' 

def generateEnemy(app):

    app.bat = Bat(random.randint(0, app.mazeRows - 1), random.randint(0, app.mazeCols - 1), 1, 1) 
    app.enemies.add(app.bat)
    app.bat2 = Bat(random.randint(0, app.mazeRows - 1), random.randint(0, app.mazeCols - 1), 1, 2)
    app.enemies.add(app.bat2)
    app.bat3 = Bat(random.randint(0, app.mazeRows - 1), random.randint(0, app.mazeCols - 1), 1, 1) 
    app.enemies.add(app.bat3)
    app.bat4 = Bat(random.randint(0, app.mazeRows - 1), random.randint(0, app.mazeCols - 1), 1, 2)  
    app.enemies.add(app.bat4)

    app.chaser = Chaser(random.randint(0, app.mazeRows - 1), random.randint(0, app.mazeCols - 1))
    app.enemies.add(app.chaser)

def drawEnemies(app, canvas):
    for enemy in app.enemies:
        (row, col) = (enemy.row, enemy.col)
        if row >= app.rows:
            continue
        (x0, y0, x1, y1) = getCellBounds(app, enemy.row, enemy.col)
        sprite = app.sprites[app.spriteCounter]
        canvas.create_image(x0 + app.cellSize // 2, y0 + app.cellSize // 2, image=ImageTk.PhotoImage(sprite))

def makeLava(app):
    for row in range(app.currLavaRow, app.rows):
        for col in range(app.cols):
            app.board[row][col] = 'cyan'
    
    if app.currLavaRow >= app.rows:
        for col in range(app.cols):
            app.board[app.rows - 1][col] = app.emptyColor
        return

    for row in range(0, app.currLavaRow):
        for col in range(app.cols):
            app.board[row][col] = app.emptyColor
        
def isCollision(app):
    for enemy in app.enemies:
        if (enemy.row, enemy.col) == (app.playerRow, app.playerCol):
            return True
    

# the template of this BFS algorithm was taken and modified from the 
# 112 tp student guide for pathfinding

# will return a list of tuples that will map point A to point B
def pathfinder(app, startRow, startCol, targetRow, targetCol):
    toVisit = [(startRow, startCol)]
    visited = set()
    visited.add((startRow, startCol))
    pathToTake = dict()
    newRow = None
    newCol = None
    while toVisit != []:
        (currRow, currCol) = toVisit[0]
        toVisit.pop(0)
        if (currRow, currCol) == (targetRow, targetCol):
            # pathToTake[(targetRow, targetCol)] = (currRow, currCol)
            path = [(currRow, currCol)]
            while (currRow, currCol) != (startRow, startCol):
                (prevRow, prevCol) = pathToTake[(currRow, currCol)]
                path.append((prevRow, prevCol))
                (currRow, currCol) = (prevRow, prevCol)
            return path
        possibleMoves = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        random.shuffle(possibleMoves)
        for (drow, dcol) in possibleMoves:
            newRow = currRow + drow
            newCol = currCol + dcol
    
            if (0 <= newRow < app.totalMazeRows and 0 <= newCol < app.totalMazeCols and 
            (newRow, newCol) not in visited  
            and not existsWall(app, (currRow, currCol), (newRow, newCol))):
                neighbor = (newRow, newCol)
                visited.add(neighbor)
                toVisit.append(neighbor)
                pathToTake[neighbor] = (currRow, currCol)
    return None  

def timerFired(app):
    if app.gameOver == True or app.play == False:
        return

    app.totalTime += app.timerDelay
    app.spriteCounter = (1 + app.spriteCounter) % len(app.sprites)
    
    if app.totalTime % (app.timerDelay * app.difficulty) == 0:
        app.currLavaRow -= 1
        makeLava(app)

    if movePlayerLegal(app, app.drow, app.dcol):
        app.playerRow += app.drow
        app.playerCol += app.dcol
        getCoins(app)
        getPoints(app)

    if app.playerRow != app.rows // 2:
        app.scrollY = (app.playerRow - (app.rows // 2)) * app.cellSize
        app.rowScrollY = (app.playerRow - (app.rows // 2))
        sideScroll(app)
        
    for enemy in app.enemies:
        if isinstance(enemy, Bat):
            if enemy.index % 2 == 1:
                if (existsWall(app, (enemy.row, enemy.col), (enemy.row, enemy.col + enemy.direction))
                or enemy.col + enemy.direction >= app.mazeCols or enemy.col + enemy.direction < 0):
                    enemy.direction *= -1
                enemy.move()
            else:
                if (existsWall(app, (enemy.row, enemy.col), (enemy.row + enemy.direction, enemy.col))
                or enemy.row + enemy.direction >= app.mazeRows or enemy.row + enemy.direction < 0):
                    enemy.direction *= -1
                enemy.move()

        elif isinstance(enemy, Chaser):
            if enemy.row < 0 or enemy.row >= app.rows:
                pass
            else:
                path = pathfinder(app, app.chaser.row, app.chaser.col, app.playerRow, app.playerCol)
 
                if app.path != path:
                    app.iterations = 1
                    app.path = path
                
                if path == None:
                    path = pathfinder(app, app.chaser.row, app.chaser.col, app.playerRow, app.playerCol)

                if app.totalTime % (app.timerDelay * app.difficulty) == 0:
                    enemy.move(app.iterations, app.path)
                    app.iterations += 1

    if gameOver(app):
        app.gameOver = True
        return
    
    if completeLevel(app):
        newLevel(app, app.score, app.difficulty)


# MOVEMENT HELPERS
def keyPressed(app, event):
    # app.sound.start()
    if event.key == 'Left':
        app.drow = 0
        app.dcol = -1
    elif event.key == 'Down':
        app.drow = 1
        app.dcol = 0 
    elif event.key == 'Right':
        app.drow = 0
        app.dcol = 1
    elif event.key == 'Up':
        app.drow = -1
        app.dcol = 0
    elif event.key == 'r':
        restart(app, app.score, app.bestScore, app.coins)

def movePlayerLegal(app, drow, dcol):
    newRow = app.playerRow + drow
    newCol = app.playerCol + dcol
    # bug here, causing player to not travel all the way to the end of the maze
    if newRow < 0 or newRow >= app.mazeRows or newCol < 0 or newCol >= app.mazeCols:
        return False
    elif existsWall(app, (app.playerRow, app.playerCol), (newRow, newCol)):
        return False

    return True

# similar to existsWall function except returns the wall itself instead of bool
def getWall(app, currCell, newCell):
    (newRow, newCol) = newCell
    (currRow, currCol) = currCell

    (newx0, newy0, newx1, newy1) = getCellBounds(app, newRow, newCol)
    (x0, y0, x1, y1) = getCellBounds(app, currRow, currCol)

    # for vertical walls
    if y0 == newy0:
        if (x0, y0, newx1, newy1) in app.walls:
            return (x0, y0, newx1, newy1)
        elif (newx0, newy0, x1, y1) in app.walls: 
            return (newx0, newy0, x1, y1)
        
    # for horizontal walls
    elif x0 == newx0: 
        if (newx0, newy0, x1, y1) in app.walls:
            return (newx0, newy0, x1, y1)
        elif (x0, y0, newx1, newy1) in app.walls:
            return (x0, y0, newx1, newy1)

def existsWall(app, currCell, newCell):
    (newRow, newCol) = newCell
    (currRow, currCol) = currCell

    (newx0, newy0, newx1, newy1) = getCellBounds(app, newRow, newCol)
    (x0, y0, x1, y1) = getCellBounds(app, currRow, currCol)

    # the following logic is similar to what can be found in the maze generator
    # where we need to case on whether we encounter a vertical or horizontal wall
    
    # for vertical walls
    if y0 == newy0:
        # this accounts for going left and right
        if ((x0, y0, newx1, newy1) in app.walls or 
            (newx0, newy0, x1, y1) in app.walls): 
            return True
        return False
    
    # for horizontal walls
    elif x0 == newx0: 
        if ((newx0, newy0, x1, y1) in app.walls or
            (x0, y0, newx1, newy1) in app.walls):
            return True
        return False
    
# things to move: the mazeBlockCells, the points, the player
def sideScroll(app):
    app.playerRow = app.rows // 2
    adjust(app)

def mousePressed(app, event):
    mouseX = event.x
    mouseY = event.y
    if (app.play == False and app.margin < mouseX < app.width - app.margin and 
    app.height * 0.9 < mouseY < app.height - app.margin):
        app.shop = True
    
    elif app.shop == True:
        # buy shield
        if ((app.margin * 1.5 < mouseX < app.width * 0.43 and 
        app.height * 0.43 < mouseY < app.height * 0.48) and app.shieldActive == False 
        and app.coins >= app.cost):
            app.shieldActive = True
            app.coins -= app.cost
        
        # buy magnet
        elif (app.width * 0.52 < mouseX < app.width * 0.92 and
        app.height * 0.43 < mouseY < app.height  * 0.48 and 
        app.coins >= app.cost * 10 and app.magnetActive == False):
            app.magnetActive = True
            app.coins -= (app.cost * 10)
        
        elif (app.margin * 1.5 < mouseX < app.width * 0.48 and 
        app.height * 0.85 < mouseY < app.height * 0.9 and 
        app.coins >= app.cost * 10 and app.coinAddictActive == False):
            app.coinAddictActive = True
            generateCoins(app)
            app.coins -= (app.cost * 10)

        elif (app.width * 0.52 < mouseX < app.width * 0.92 and
        app.height * 0.85 < mouseY < app.height * 0.9 and
        app.coins >= app.cost * 20 and app.scoreBoosterActive == False):
            app.scoreBoosterActive = True
            app.scoreBoost = 5
            app.coins -= (app.cost * 20)

        if (app.width * 0.1 < mouseX < app.width * 0.25 and 
        app.margin // 2 < mouseY < app.margin * 1.5):
            app.shop = False

    elif app.play == False and app.shop == False:
        app.play = True


# GAME CONDITION HELPERS
def completeLevel(app):
    (x0, y0, x1, y1) = getCellBounds(app, app.playerRow, app.playerCol)
    for wall in app.walls:
        (wx0, wy0, wx1, wy1) = wall
        if y1 > wy1:
            return False
    return True

def gameOver(app):
    if app.shieldActive == False:
        if isCollision(app):
            app.gameOver = True
        
        if app.currLavaRow == app.playerRow:
            app.gameOver = True
    else:
        if isCollision(app):
            app.shieldActive = False
        
        if app.currLavaRow == app.playerRow:
            app.shieldActive = False
    
    app.bestScore = app.score
    return 

def redrawAll(app, canvas):
    if app.play == False and app.shop == False:
        startScreen(app, canvas)
    elif app.shop == True:
        shop(app, canvas)
    else:
        canvas.create_rectangle(0, 0, app.width, app.height, fill = 'black')
        drawBoard(app, canvas)
        drawPoints(app, canvas)
        drawPlayer(app, canvas)
        drawMaze(app, canvas)
        drawEnemies(app, canvas)
        drawCoins(app, canvas)
        canvas.create_text(app.width // 2, app.margin * 2, text=f'score: {app.score}')
        canvas.create_text(app.width // 9, app.margin * 2, text=f'coins: {app.coins}')
        # side borders
        canvas.create_line(app.margin, app.margin, app.margin, 
        app.height - app.margin, fill = app.mazeColor, width = 4)
        canvas.create_line(app.width - app.margin, app.margin, 
        app.width - app.margin, app.height - app.margin, fill = app.mazeColor, width = 4)
        if app.gameOver == True:
            canvas.create_text(app.width // 2, app.height // 2, text='Game Over! \n' 'Press r to restart.',
            fill = 'white')

runApp(width=400, height=600)

