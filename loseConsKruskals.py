from cmu_112_graphics import *
import random, pygame

# the code regarding pygame was taken and modified from the CMU-112 website
# this code was modified from my tetris project
# all images used were screenshots taken from https://arcadespot.com/game/tomb-of-the-mask-online/

class Player:
    def __init__(self):
        self.alive = True

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

        # this will just be to keep a constant area where the enemy wanders around
        # self.startRow = startRow
        # self.startCol = startCol
        # self.range = 2
    
    def move(self):
        if self.collision == False:
            if self.index % 2 == 0:
                self.row += self.direction
            else:
                self.col += self.direction

class ProjectileEnemy:
    def __init__(self, startRow, startCol):
        self.collision = False
        #self.color = color of the maze, it will just have a different block design

class ChasingEnemy:
    def __init__(self, startRow, startCol):
        self.collision = False
        self.color = 'cyan'
        self.row = startRow
        self.col = startCol
    
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
    # rows = 11
    # cols = 8
    # cellSize = 25
    # margin = 25
    rows = 21
    cols = 14
    cellSize = 25
    margin = 25

    return (rows, cols, cellSize, margin)

def mazeDimensions(app):
    rows = (app.rows * 2) + 7 # we're adding 7 rows at the bottom for where the player will start
    cols = app.cols
    # rows = 10 + 7 # we're adding 7 rows at the bottom for where the player will start
    # cols = 4
    return (rows, cols)

# for drawing the terrain
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
    # I'll load in the image later, for now I'll experiment on a rectangle
    app.image1 = app.loadImage('images/sprite.png')
    app.player = app.scaleImage(app.image1, 1/15)
    app.homeImage = app.loadImage('images/homeScreen.png')
    app.homeScreen = app.scaleImage(app.homeImage, 1/10)
    

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
    
    # maze information
    (app.leftBorder, app.topBorder, topx1, topy1) = getCellBounds(app, 0, 0)
    (endx0, endy0, app.rightBorder, app.bottomBorder) = getCellBounds(app, app.mazeRows, app.mazeCols)
    app.score = 0
    app.scrollY = ((app.totalMazeRows + app.rows) // (app.totalMazeRows // app.rows)) * app.cellSize
    app.rowScrollY = (app.totalMazeRows + app.rows) // (app.totalMazeRows // app.rows)

    print(f'rowScroll: {app.rowScrollY}')

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
    # app.pointPath2 = set(pathfinder(app, app.mazeRows, app.mazeCols // 2, 0, app.cols // 2))
    # print(app.pointPath)
    # print(app.pointPath2)

    app.newPointPath = set() # for the sideScroll function
    pointConverter(app)
    
    app.currLavaRow = (app.rows - 1) + app.rowScrollY
    makeLava(app)

    # enemy chaser information
    app.enemies = set()
    generateEnemy(app)
    adjust(app)
    app.path = pathfinder(app, app.chaser.row, app.chaser.col, app.playerRow, app.playerCol)
    app.iterations = 0

    # sound effects
    pygame.mixer.init()
    app.sound = Sound("button.mp3")
    app.play = False 
    app.gameOver = False
    app.complete = False

def newLevel(app, score, difficulty):
    app.image1 = app.loadImage('images/sprite.png')
    app.player = app.scaleImage(app.image1, 1/15)

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
    app.difficulty = difficulty // 2
    
    # maze information
    (app.leftBorder, app.topBorder, topx1, topy1) = getCellBounds(app, 0, 0)
    (endx0, endy0, app.rightBorder, app.bottomBorder) = getCellBounds(app, app.mazeRows, app.mazeCols)
    app.score = score
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
    # app.pointPath2 = set(pathfinder(app, app.mazeRows, app.mazeCols // 2, 0, app.cols // 2))
    # print(app.pointPath)
    # print(app.pointPath2)

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

    # sound effects
    pygame.mixer.init()
    app.sound = Sound("button.mp3")
    app.play = True
    app.gameOver = False
    app.complete = False

def startScreen(app, canvas):
    canvas.create_image(app.width // 2, app.height // 2, image=ImageTk.PhotoImage(app.homeScreen))

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

# pointPath stored as a list of (row, col) tuples, I think it would be smarter
# to store it as (x0, y0, x1, y1) because of our adjuster function
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
    if (x0, y0, x1, y1) in app.pointPath:
        app.pointPath.remove((x0, y0, x1, y1))
        app.score += 1

def drawPlayer(app, canvas):
    (x0, y0, x1, y1) = getCellBounds(app, app.playerRow, app.playerCol)
    imageWidth, imageHeight = app.player.size
    canvas.create_image(x0 + imageWidth // 2, y0 + imageHeight // 2, image=ImageTk.PhotoImage(app.player))

    # canvas.create_rectangle(x0, y0, x1, y1, fill = 'yellow')

def makePlayer(app):
    app.board[app.playerRow][app.playerCol] = 'yellow' 

# def generateMaze(app):
#     for mazeCell in app.mazeBlockCells:
#         (row, col) = mazeCell
#         app.board[row][col] = app.emptyColor 

# have more openings in maze
# generate the entire maze and then sidescroll through it.
def getWalls(app, startRow, endRow):
    app.walls = set(app.walls)

    # we're only generating one quadrant of walls (quadrant 2)
    (midx0, midy0, midx1, midy1) = getCellBounds(app, endRow - 1, (app.mazeCols // 2) - 1)
    for row in range(startRow, endRow):
        # if row > app.playerRow:
        #     # we only want to create the maze above the player position
        #     # so when the maze is below the player we only want the side border
        #     (x0, y0, x1, y1) = getCellBounds(app, row, 0)
        #     (a0, b0, a1, b1) = getCellBounds(app, row, app.cols - 1)
        #     app.walls.add(((x0, y0, x0, y1)))
        #     app.walls.add((a1, b0, a1, b1))
        #     continue
        for col in range(app.mazeCols // 2):
            app.maze.append({(row, col)}) # creates distinct sets while getting walls
            (x0, y0, x1, y1) = getCellBounds(app, row, col)
            
            if x0 != midx1 and x1 != midx1:
                app.walls.add((x1, y0, x1, y1)) # right wall
            
            if y1 != midy1:
                app.walls.add((x0, y1, x1, y1)) # bottom wall

            app.walls.add((x0, y0, x1, y0)) # top wall
            app.walls.add((x0, y0, x0, y1)) # left wall
            
    
    # turn it into a list now that we don't have dupes
    app.walls = list(app.walls)
    random.shuffle(app.walls) 
     
# def drawMaze(app, canvas, startRow, endRow):
#     (boardLeftBorder, boardTopBorder, c, d) = getCellBounds(app, startRow, 0)
#     (a, b, boardRightBorder, boardBottomBorder)= getCellBounds(app, endRow, app.cols)
#     print(boardTopBorder, boardBottomBorder)
#     for wall in app.walls:
#         (x0, y0, x1, y1) = wall
#         if (boardTopBorder < y1 < boardBottomBorder):
#             canvas.create_line(x0, y0, x1, y1, fill = app.mazeColor, width = 4)

# def drawMaze(app, canvas):
#     (boardLeftBorder, boardTopBorder, c, d) = getCellBounds(app, 0, 0)
#     (a, b, boardRightBorder, boardBottomBorder)= getCellBounds(app, app.rows, app.cols)
#     print(boardTopBorder, boardBottomBorder)
#     for wall in app.walls:
#         (x0, y0, x1, y1) = wall
#         if (boardTopBorder < y1 < boardBottomBorder):
#             canvas.create_line(x0, y0, x1, y1, fill = app.mazeColor, width = 4)

def drawMaze(app, canvas):
    (a, b, c, bottomBorder) = getCellBounds(app, app.rows - 1, app.cols - 1)
    # add the platform the player will stand on
    for wall in app.walls:
        (x0, y0, x1, y1) = wall
        if y0 <= app.topBorder or y1 > bottomBorder:
            continue
        canvas.create_line(x0, y0, x1, y1, fill = app.mazeColor, width = 4)

def makePlatform(app):
    (x0, y0, x1, y1) = getCellBounds(app, app.mazeRows, app.mazeCols // 2)
    app.walls.append((x0, y1, x1, y1))
    app.walls.append((x0 - app.cellSize, y1, x0, y1))
    app.walls.append((x1, y1, x1 + app.cellSize, y1))
    app.walls.append((x0 - app.cellSize, y1, x0 - app.cellSize, y1 + app.cellSize))
    app.walls.append((x1 + app.cellSize, y1, x1 + app.cellSize, y1 + app.cellSize))

    app.walls.append((x0, y1 + app.cellSize, x1, y1 + app.cellSize))
    app.walls.append((x0 - app.cellSize, y1 + app.cellSize, x0, y1 + app.cellSize))
    app.walls.append((x1, y1 + app.cellSize, x1 + app.cellSize, y1 + app.cellSize)) 

# now work on increasing space within the maze

def generateMaze(app):
    makeCaverns(app)
    generateMazeHelper(app)
    # app.board[0][app.mazeCols // 2] = 'yellow'
    # maybe we can add generateEnemy in here too
    mirrorAcrossY(app)
    mirrorAcrossX(app)
    makePlatform(app)
    

    # while mazeSolver(app, app.playerRow, app.playerCol, 0, app.cols // 2) == None:
    #     print('ah')
    #     app.walls = set()
    #     getWalls(app, 0, app.mazeRows // 2)
        
    #     generateMazeHelper(app)
    #     # while len(app.walls) != 10:
    #     #     if len(app.walls) < 25: break
    #     #     index = random.randint(0, len(app.walls) - 1)
    #     #     x = app.walls.pop(index)
    #     mirrorAcrossY(app)
    #     mirrorAcrossX(app)

    # print(app.walls)

# this is the issue
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


    app.walls = []
    app.pointPath = set()
    for wall in app.newWalls:
        app.walls.append(wall)
    
    for point in app.newPointPath:
        app.pointPath.add(point)
    
    for enemy in app.enemies:
        enemy.row -= app.rowScrollY

    app.currLavaRow -= app.rowScrollY   
    makeLava(app)

    app.newWalls = set()
    app.newPointPath = set()
        
# the following code was modified from the pseudocode for Kruskal's Algorithm
# on Wikipedia, found here:
# https://en.wikipedia.org/wiki/Maze_generation_algorithm
def generateMazeHelper(app):
    # (topx0, topy0, x1, y1) = getCellBounds(app, 0, 0)
    # (x0, y0, bottomx1, bottomy1) = getCellBounds(app, app.rows - 1, app.cols - 1)
    for wall in app.walls:
        (x0, y0, x1, y1) = wall
        # print(f'wall: {wall}')
        # this will check if the chosen wall is a maze border
        # if (y0 == y1 == app.topBorder or x0 == x1 == app.leftBorder or 
        # y0 == y1 == app.bottomBorder or x0 == x1 == app.rightBorder):
        #     continue
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
            # if row1 == app.playerRow:
            #     continue
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
        # nonetype nonsubscriptable but that's because the cells we found do not
        # exist yet, so we need to find a way to just get the walls or something
        # like that
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
    # print(cell1, cell2)
    # print(app.maze)
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


def makeSpike(app):
    for i in range(2):
        row = random.randint(0, app.rows - 1)
        col = random.randint(0, app.cols - 1)
        app.board[row][col] = 'cyan' 

def generateEnemy(app):
    # i = random.randint(0, 2)
    app.bat = Bat(random.randint(0, app.mazeRows), random.randint(0, app.mazeCols), 1, 1) 
    app.enemies.add(app.bat)
    # app.chaser = ChasingEnemy(random.randint(0, app.mazeRows), random.randint(0, app.mazeCols))
    app.chaser = ChasingEnemy(app.rowScrollY, 0)
    # app.path = pathfinder(app, app.chaser.row, app.chaser.col, app.playerRow, app.playerCol)
    app.enemies.add(app.chaser)

def drawEnemies(app, canvas):
    for enemy in app.enemies:
        (row, col) = (enemy.row, enemy.col)
        if row >= app.rows:
            continue
        (x0, y0, x1, y1) = getCellBounds(app, enemy.row, enemy.col)
        canvas.create_rectangle(x0, y0, x1, y1, fill = 'cyan')

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
            # and app.board[newRow][newCol] != app.mazeColor 
            # and app.board[newRow][newCol] != 'cyan' 
            
                neighbor = (newRow, newCol)
                visited.add(neighbor)
                toVisit.append(neighbor)
                pathToTake[neighbor] = (currRow, currCol)
    return None  
      
# bug in mazeSolver, you should solve this
# the premise is that this is supposed to mimic player movement, and if
# it isn't able to solve the maze then it should return None. Otherwise,
# it gives a path that it took to solve the maze, which we will use as the pointPath
def mazeSolver(app, startRow, startCol, targetRow, targetCol):
    toVisit = [(startRow, startCol)]
    visited = set()
    visited.add((startRow, startCol))
    pathToTake = dict()
    newRow = None
    newCol = None
    while toVisit != []:
        # print(toVisit[0])
        (currRow, currCol) = toVisit[0]
        toVisit.pop(0)
        # print(toVisit)
        if (currRow, currCol) == (targetRow, targetCol):
            # pathToTake[(targetRow, targetCol)] = (currRow, currCol)
            path = [(currRow, currCol)]
            while (currRow, currCol) != (startRow, startCol):
                (prevRow, prevCol) = pathToTake[(currRow, currCol)]
                path.append((prevRow, prevCol))
                (currRow, currCol) = (prevRow, prevCol)
            # print(path)
            return path
        possibleMoves = [(-1, 0), (0, -1), (0, 1), (1, 0)]
        for (drow, dcol) in possibleMoves:
            originalRow = currRow
            originalCol = currCol
            # print(originalRow, originalCol)
            newRow = currRow + drow
            newCol = currCol + dcol
            # if 0 <= newRow < app.rows and 0 <= newCol < app.cols:
                # print(newRow, newCol)
                # if existsWall(app, (currRow, currCol), (newRow, newCol)):
                #     pass
                # else:
                # and not existsWall(app, (currRow, currCol), (newRow, newCol))
            while (0 <= newRow < app.rows and 0 <= newCol < app.cols
            and not existsWall(app, (currRow, currCol), (newRow, newCol))):
                currRow += drow
                currCol += dcol
                newRow = currRow + drow
                newCol = currCol + dcol

            # the while function yields an illegal position so we need to adjust
            if newRow < 0 or newRow >= app.rows:
                # currRow -= drow
                newRow -= drow
            
            if newCol < 0 or newCol >= app.cols:
                # currCol -= dcol
                newCol -= dcol

            # print(f'curr: ({currRow}, {currCol}), new: ({newRow}, {newCol})')
                
                # print((currRow, currCol), (newRow, newCol))
                # newRow -= drow
                # newCol -= dcol
                # print(f'newRow, newCol = ({newRow}, {newCol})')
            if ((newRow, newCol) not in visited):
                nextMove = (newRow, newCol)
                visited.add(nextMove)
                # print(f'before: {toVisit}')
                toVisit.append(nextMove)
                # print(f'after: {toVisit}')

                pathToTake[nextMove] = (originalRow, originalCol) 
            # print(toVisit)
            # print(pathToTake)
    return None        

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
    
def timerFired(app):
    if app.gameOver == True or app.play == False:
        return

    app.totalTime += app.timerDelay
    
    if app.totalTime % (app.timerDelay * app.difficulty) == 0:
        app.currLavaRow -= 1
        makeLava(app)

    if movePlayerLegal(app, app.drow, app.dcol):
        app.playerRow += app.drow
        app.playerCol += app.dcol
        getPoints(app)

    if app.playerRow != app.rows // 2:
        app.scrollY = (app.playerRow - (app.rows // 2)) * app.cellSize
        app.rowScrollY = (app.playerRow - (app.rows // 2))
        sideScroll(app)

    # app.board[app.bat.row][app.bat.col] = app.emptyColor
    # if app.bat.index % 2 == 0:
    #     if existsWall(app, (app.bat.row, app.bat.col), (app.bat.row + app.bat.direction, app.bat.col)):
    #         app.bat.direction *= -1
    #     app.bat.move()
    # else:
        
    if (existsWall(app, (app.bat.row, app.bat.col), (app.bat.row, app.bat.col + app.bat.direction))
    or app.bat.col + app.bat.direction >= app.cols or app.bat.col + app.bat.direction < 0):
        app.bat.direction *= -1
    app.bat.move()
    # print(app.bat.row, app.bat.col)

    if app.chaser.row >= app.rows:
        pass
    else:
        path = pathfinder(app, app.chaser.row, app.chaser.col, app.playerRow, app.playerCol)
        if app.path != path:
            app.iterations = 1
            app.path = path

        if app.totalTime % (app.timerDelay * app.difficulty) == 0:
            app.chaser.move(app.iterations, app.path)
            app.iterations += 1

    if gameOver(app):
        app.gameOver = True
        return
    
    if completeLevel(app):
        newLevel(app, app.score, app.difficulty)
    
 

    # app.board[app.bat.row][app.bat.col] = app.bat.color

    # app.board[app.chaser.row][app.chaser.col] = app.emptyColor   

    # # the mod is causing the skip in cells, can debug this later
    # app.chaser.move(app.iterations % len(app.path), app.path)
    # app.board[app.chaser.row][app.chaser.col] = app.chaser.color
    # app.iterations += 1



def keyPressed(app, event):
    # app.sound.start()
    if event.key == 'Left':
        app.drow = 0
        app.dcol = -1
        # movePlayer(app, 0, -1)
        # makePlayer(app)
    elif event.key == 'Down':
        app.drow = 1
        app.dcol = 0 
        # movePlayer(app, 1, 0)
        # makePlayer(app)
    elif event.key == 'Right':
        app.drow = 0
        app.dcol = 1
        # movePlayer(app, 0, 1)
        # makePlayer(app)
    elif event.key == 'Up':
        app.drow = -1
        app.dcol = 0
        # movePlayer(app, -1, 0)
        # makePlayer(app)
    elif event.key == 'r':
        appStarted(app)

# will move the sprite in the respective direction until it hits an obstacle
def movePlayer(app, drow, dcol):
    if app.gameOver == True:
        return
    while movePlayerLegal(app, drow, dcol):
        # if ((app.bat.row, app.bat.col) == (app.playerRow, app.playerCol)
        # or (app.chaser.row, app.chaser.col) == (app.playerRow, app.playerCol)
        # or app.board[app.playerRow][app.playerCol] == 'cyan'):
        #     app.bat.collision = True
        #     app.chaser.collision = True
        #     app.gameOver = True
        #     return
        # getPoints(app)
        # app.board[app.playerRow][app.playerCol] = app.emptyColor
        app.playerRow += drow
        app.playerCol += dcol
        # makePlayer(app)

        # we want to scroll while the player is moving so that they can see
        # the map coming up
        
        # this case is when player is above half of the rows, so need to scroll up;
        # ie the maze goes down
        # player below half of the rows, so need to scroll down; ie maze goes up
    if app.playerRow != app.rows // 2:
        app.scrollY = (app.playerRow - (app.rows // 2)) * app.cellSize
        app.rowScrollY = (app.rows // 2) - app.playerRow
        sideScroll(app)


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
        # print(f'possible walls: {(x0, y0, newx1, newy1)}, {(newx0, newy0, x1, y1)}')
        # print(app.walls)
        # this accounts for going left and right
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
        # print(f'possible walls: {(x0, y0, newx1, newy1)}, {(newx0, newy0, x1, y1)}')
        # print(app.walls)
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
    # app.currMazeRow += app.scrollY
    adjust(app)
    # for point in app.pointPath:
    #     (row, col) = point
    #     app.board[row][col] = app.emptyColor
    #     row += app.scrollY
    #     app.newPointPath.add((row, col))

    # app.pointPath = app.newPointPath
    # app.newPointPath = set()

    # for wall in app.walls:
    #     (x0, y0, x1, y1) = wall
    #     y0 += app.scrollY * app.cellSize
    #     y1 += app.scrollY * app.cellSize
    #     app.wallsToRemove.append((x0, y0, x1, y1))

    # app.walls = copy.copy(app.wallsToRemove)
    # app.wallsToRemove = []
    # if app.scrollY > 0:
    #     getWalls(app, 0, app.scrollY)

    # generateMazeHelper(app, app.newWalls)

def mousePressed(app, event):
    app.play = True

def completeLevel(app):
    (x0, y0, x1, y1) = getCellBounds(app, app.playerRow, app.playerCol)
    for wall in app.walls:
        (wx0, wy0, wx1, wy1) = wall
        if y1 > wy1:
            return False
    return True

def gameOver(app):
    if isCollision(app):
        app.gameOver = True
        return
    
    if app.currLavaRow == app.playerRow:
        app.gameOver = True
        return

def redrawAll(app, canvas):
    if app.play == False:
        canvas.create_rectangle(0, 0, app.width, app.height, fill = 'black')
        startScreen(app, canvas)
    else:
        canvas.create_rectangle(0, 0, app.width, app.height, fill = 'black')
        drawBoard(app, canvas)
        drawPoints(app, canvas)
        drawPlayer(app, canvas)
        # drawMaze(app, canvas, app.currMazeRow, app.currMazeRow + app.rows)
        drawMaze(app, canvas)
        drawEnemies(app, canvas)
        canvas.create_text(app.width // 2, app.margin * 2, text=f'score = {app.score}')
        # side borders
        canvas.create_line(app.margin, app.margin, app.margin, 
        app.height - app.margin, fill = app.mazeColor, width = 4)
        canvas.create_line(app.width - app.margin, app.margin, 
        app.width - app.margin, app.height - app.margin, fill = app.mazeColor, width = 4)
        if app.gameOver == True:
            canvas.create_text(app.width // 2, app.height // 2, text='Game Over!',
            fill = 'white')

runApp(width=400, height=660)

