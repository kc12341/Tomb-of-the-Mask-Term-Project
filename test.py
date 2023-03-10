from cmu_112_graphics import *
import random, pygame, copy

# the code regarding pygame was taken and modified from the CMU-112 website
# this code was modified from my tetris project

class Player:
    def __init__(self):
        self.alive = True

# this type of enemy will just travel to random locations in its vicinity
class WanderingEnemy:
    def __init__(self, startRow, startCol):
        self.collision = False
        self.color = 'cyan'
        # this will be the actual row of the enemy
        self.row = startRow
        self.col = startCol

        # this will just be to keep a constant area where the enemy wanders around
        self.startRow = startRow
        self.startCol = startCol
        self.range = 2
    
    def move(self):
        if self.collision == False:
            (currRow, currCol) = (self.startRow, self.startCol)
            self.row = random.randint(currRow, currRow + self.range)
            self.col = random.randint(currCol, currCol + self.range)

class ProjectileEnemy:
    def __init__(self, startRow, startCol):
        self.collision = False
        #self.color = color of the maze, it will just have a different block design

class ChasingEnemy:
    def __init__(self, startRow, startCol, path):
        self.collision = False
        self.color = 'cyan'
        self.row = startRow
        self.col = startCol
        self.path = path[::-1]
    
    def move(self, n, path):
        self.path = path[::-1]
        if self.collision == False:
            (self.row, self.col) = self.path[n] # n is the index

class Sound(object):
    def __init__(self, path):
        self.path = path
        pygame.mixer.music.load(path)

    # Returns True if the sound is currently playing
    def isPlaying(self):
        return bool(pygame.mixer.music.get_busy())

    # Loops = number of times to loop the sound.
    # If loops = 1 or 1, play it once.
    # If loops > 1, play it loops + 1 times.
    # If loops = -1, loop forever.
    def start(self, loops=1):
        self.loops = loops
        pygame.mixer.music.play(loops=loops)

    # Stops the current sound from playing
    def stop(self):
        pygame.mixer.music.stop()

def gameDimensions():
    # if you want to play on bigger dimensions then you can change the 
    # rows, cols, cellSize, margin
    # original dimensions used were rows 40, cols 24
    rows = 21
    cols = 10
    cellSize = 25
    margin = 25
    return (rows, cols, cellSize, margin)

# for drawing the terrain
def getCellBounds(app, row, col):  
    x0 = app.margin + (col * app.cellSize)
    x1 = app.margin + (col+1) * app.cellSize
    y0 = app.margin + row * app.cellSize
    y1 = app.margin + (row+1) * app.cellSize
    return (x0, y0, x1, y1)

def getCell(app, x, y):
    cellWidth  = app.width / app.cols
    cellHeight = app.height / app.rows
    # Note: we have to use int() here and not just // because
    # row and col cannot be floats and if any of x, y, app.margin,
    # cellWidth or cellHeight are floats, // would still produce floats.
    row = int(y / cellHeight)
    col = int(x / cellWidth)
    return (row, col)


def appStarted(app):
    # I'll load in the image later, for now I'll experiment on a rectangle
    # app.image1 = app.loadImage('images/sprite.png')
    # app.player = app.scaleImage(app.image1, 1/10)
    
    # game dimensions
    (app.rows, app.cols, app.cellSize, app.margin) = gameDimensions()

    # initialize the player's position at the center of the screen
    (app.playerRow, app.playerCol) = (app.rows // 2, app.cols // 2)
    
    # maze information
    # where the maze starts generating from
    (app.mazeRow, app.mazeCol) = (app.playerRow, app.playerCol) 
    app.score = 0
    app.scrollY = 0
    app.emptyColor = 'black'
    app.mazeColor = '#' + ''.join(random.choice('ABCDEF0123456') for i in range(6))
    app.board = [([app.mazeColor] * app.cols) for i in range(app.rows)]
    app.timerDelay = 1000 

    # points need to be generate after maze has been generated so that it can
    # properly avoid walls
    app.pointPath = set()
    app.mazeBlockCells = [(app.playerRow, app.playerCol)] # maze starts at playerPos

    app.newPointPath = set() # for the sideScroll function
    app.newMazeBlockCells = [] # for the sideScroll function
    app.visited = set()
    # app.currPos = [(app.mazeRow, app.mazeCol)]
    generateMazeHelper(app, app.visited, app.mazeBlockCells)
    generateMaze(app)

    # enemy chaser information
    app.path = pathfinder(app, 0, app.cols - 1, app.playerRow, app.playerCol)
    app.iterations = 0

    # generateMaze(app)
    app.enemies = set()
    generateEnemy(app)

    # make player after all of these
    # makePlayer(app)

    # sound effects
    pygame.mixer.init()
    app.sound = Sound("button.mp3")
    app.gameOver = False

def instructionScreen(app):
    pass

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

def drawPoints(app, canvas):
    for (row, col) in app.pointPath:
        if (row, col) == (app.playerRow, app.playerCol) or row < 0 or col < 0:
            continue
        (x0, y0, x1, y1) = getCellBounds(app, row, col)
        canvas.create_rectangle(x0 + 0.33 * app.cellSize, y0 + 0.33 * app.cellSize, 
        x1 - 0.33 * app.cellSize, y1 - 0.33 * app.cellSize, fill = 'yellow') # change to player color next

def getPoints(app):
    if (app.playerRow, app.playerCol) in app.pointPath:
        app.pointPath.remove((app.playerRow, app.playerCol))
        app.score += 1

def drawPlayer(app, canvas):
    (x0, y0, x1, y1) = getCellBounds(app, app.playerRow, app.playerCol)
    canvas.create_rectangle(x0, y0, x1, y1, fill = 'yellow')

def makePlayer(app):
    app.board[app.playerRow][app.playerCol] = 'yellow'

def generateMaze(app):
    for mazeCell in app.mazeBlockCells:
        (row, col) = mazeCell
        if row < 0 or col < 0 or row >= app.rows or col >= app.cols:
            continue
        app.board[row][col] = app.emptyColor 

# the following code was modified from the pseudocode on Wikipedia, found here:
# https://en.wikipedia.org/wiki/Maze_generation_algorithm
def generateMazeHelper(app, visited, mazeCells):
    # if len(visited) == app.rows * app.cols:
        # return app.board
    (row, col) = mazeCells[-1]
    if row == 0:
        return mazeCells
    else:
        (currRow, currCol) = mazeCells[-1]
        visited.add((currRow, currCol)) # repetitive but we can get back to this
        app.pointPath.add((currRow, currCol))
        # if app.scrollY < app.rows // 2:
        #     possibleMoves = [(-1, 0), (0, 1), (0, -1)] # removed down option if it's above half
        # else:
        #     possibleMoves = [(0, 1), (-1, 0), (0, -1), (1, 0)]
        possibleMoves = [(0, 1), (-1, 0), (0, -1)] # removed down option if it's above half
        random.shuffle(possibleMoves)
        for (drow, dcol) in possibleMoves:
            newRow = currRow + drow
            newCol = currCol + dcol
            # print(f'(newRow, newCol) = ({newRow, newCol})')
            if (0 <= newRow < app.rows and 0 <= newCol < app.cols and 
            (newRow, newCol) not in visited):
                # visited.add((newRow, newCol))
                # print(f'visited = {visited}')
                # currPos.append((newRow, newCol))
                # find a way to carve path
                # need to draw a rectangle over the wall to "carve" the path
                mazeCells.append((newRow, newCol))

                # mazeCells.add((newX0, newX1, newY0, newY1))
                # print(f'mazeCells = {mazeCells}')
                
                result = generateMazeHelper(app, visited, mazeCells)
                if result != None:
                    # return app.board
                    return mazeCells
                mazeCells.pop()
        return None
    # makeSpike(app)

def makeSpike(app):
    for i in range(2):
        row = random.randint(0, app.rows - 1)
        col = random.randint(0, app.cols - 1)
        app.board[row][col] = 'cyan' 

def generateEnemy(app):
    app.bat = WanderingEnemy(0, 0) # this enemy class will just go to some random 
    # point within their vicinity and if you collide with them you die
    # for simplicity, let's start with the "vicinity" being the entire board
    app.enemies.add(app.bat)
    app.chaser = ChasingEnemy(0, app.cols - 1, app.path)
    app.enemies.add(app.chaser)

def isCollision(app):
    for enemy in app.enemies:
        if (enemy.row, enemy.col) == (app.playerRow, app.playerCol):
            return True
    
# the template of this BFS algorithm was taken and modified from the 
# 112 tp student guide for pathfinding

# this will return a list of tuples containing the cells that will be emptyColor
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
        for (drow, dcol) in possibleMoves:
            newRow = currRow + drow
            newCol = currCol + dcol
            if (0 <= newRow < app.rows and 0 <= newCol < app.cols and 
            (newRow, newCol) not in visited 
            and app.board[newRow][newCol] != 'cyan'):
            #and app.board[newRow][newCol] != app.mazeColor 
                neighbor = (newRow, newCol)
                visited.add(neighbor)
                toVisit.append(neighbor)
                pathToTake[neighbor] = (currRow, currCol)
    return None        

def timerFired(app):
    return 
    if app.gameOver == True:
        return
    
    app.board[app.bat.row][app.bat.col] = app.emptyColor
    app.bat.move()
    app.board[app.bat.row][app.bat.col] = app.bat.color

    app.path = pathfinder(app, app.chaser.row, app.chaser.col, app.playerRow, app.playerCol)
    app.board[app.chaser.row][app.chaser.col] = app.emptyColor   

    # the mod is causing the skip in cells, can debug this later
    app.chaser.move(app.iterations % len(app.path), app.path)
    app.board[app.chaser.row][app.chaser.col] = app.chaser.color
    app.iterations += 1

    if isCollision(app):
        app.gameOver = True
        return

def keyPressed(app, event):
    # app.sound.start()
    if event.key == 'Left':
        movePlayer(app, 0, -1)
        makePlayer(app)
    elif event.key == 'Down':
        movePlayer(app, 1, 0)
        makePlayer(app)
    elif event.key == 'Right':
        movePlayer(app, 0, 1)
        makePlayer(app)
    elif event.key == 'Up':
        movePlayer(app, -1, 0)
        makePlayer(app)

# will move the sprite in the respective direction until it hits an obstacle
def movePlayer(app, drow, dcol):
    if app.gameOver == True:
        return
    while movePlayerLegal(app, drow, dcol):
        if ((app.bat.row, app.bat.col) == (app.playerRow, app.playerCol)
        or (app.chaser.row, app.chaser.col) == (app.playerRow, app.playerCol)
        or app.board[app.playerRow][app.playerCol] == 'cyan'):
            app.bat.collision = True
            app.chaser.collision = True
            app.gameOver = True
            return
        getPoints(app)
        # makePlayer(app)
        app.board[app.playerRow][app.playerCol] = app.emptyColor
        app.playerRow += drow
        app.playerCol += dcol
        makePlayer(app)

        # we want to scroll while the player is moving so that they can see
        # the map coming up
        
        # this case is when player is above half of the rows, so need to scroll up;
        # ie the maze goes down
        # player below half of the rows, so need to scroll down; ie maze goes up
        if app.playerRow != app.rows // 2:
            app.scrollY = (app.rows // 2) - app.playerRow
            sideScroll(app)
        
def movePlayerLegal(app, drow, dcol):
    newRow = app.playerRow + drow
    newCol = app.playerCol + dcol
    if (newRow < 0 or newRow >= app.rows or newCol < 0 or newCol >= app.cols
    or app.board[newRow][newCol] == app.mazeColor):
        return False
    return True

# things to move: the mazeBlockCells, the points, the player
def sideScroll(app):
    app.playerRow = app.rows // 2

    for point in app.pointPath:
        (row, col) = point
        if row >= app.rows:
            continue
        app.board[row][col] = app.emptyColor
        row += app.scrollY
        app.newPointPath.add((row, col))

    app.pointPath = app.newPointPath
    app.newPointPath = set()

    for mazeCell in app.mazeBlockCells:
        (row, col) = mazeCell
        app.board[row][col] = app.mazeColor
        row += app.scrollY
        if row >= app.rows:
            continue
        app.newMazeBlockCells.append((row, col))

    app.mazeBlockCells = copy.copy(app.newMazeBlockCells)
    app.visited = set(app.mazeBlockCells)
    app.newMazeBlockCells = []
    # print(f'before: {app.mazeBlockCells}')
    # print(f'mazeCells is {app.mazeBlockCells}')
    generateMazeHelper(app, app.visited, app.mazeBlockCells)
    # print(f'after: {app.mazeBlockCells}')
    # print(f'visited is {app.visited}')

    generateMaze(app)
    

def redrawAll(app, canvas):
    drawBoard(app, canvas)
    drawPoints(app, canvas)
    drawPlayer(app, canvas)
    # canvas.create_image(app.playerRow, app.playerCol, image=ImageTk.PhotoImage(app.player))
    canvas.create_text(app.width // 2, app.height // 2, text=f'score = {app.score}')
    if app.gameOver == True:
        canvas.create_text(app.width // 2, app.height // 2, text='Game Over!',
        fill = 'white')

runApp(width=410, height=660)

