import pygame
import time

__INPUT_FILE__ = '.\input.txt'
__MARGIN_TOP__ = 45
__MARGIN_LEFT__ = 45
__AUTOFILL_DELAY__ = 125

class Game:
    #Default board to fall back to, in case something goes wrong with user input
    defult_board = [
        [0, 1, 0, 9, 0, 0, 0, 8, 0],
        [5, 7, 0, 2, 0, 8, 9, 0, 1],
        [6, 8, 9, 0, 7, 1, 0, 0, 5],
        [7, 0, 0, 1, 0, 6, 5, 9, 0],
        [9, 0, 0, 0, 2, 3, 7, 1, 4],
        [8, 4, 0, 7, 0, 0, 0, 3, 6],
        [2, 9, 0, 0, 1, 0, 0, 4, 3],
        [0, 6, 0, 3, 8, 0, 1, 5, 9],
        [1, 0, 8, 0, 9, 0, 6, 0, 2]
    ]

    board = [[0 for i in range(9)] for i in range(9)]

    #Initialize the game window and all parameters required
    def __init__(self):
        self.window = pygame.display.set_mode((630, 800))
        pygame.display.set_caption('Sudoku Solver')
        
        self.readFromFile()
        self.rows = 9
        self.cols = 9
        self.width = 540
        self.height = 600
        self.selected = None
        self.model = None
        self.drawwrong = False
        self.cubes = [[Cube(self.board[i][j], i, j, self.width, self.height) for j in range(self.cols)] for i in range(self.rows)]
        self.update_model()
        pygame.font.init()

        self.starttime = time.time()
        self.running = True

    #Function to attempt to read input from input file
    def readFromFile(self):
        try:
            success = True
            inputboard = []
            with open(__INPUT_FILE__) as file:
                for l in file:
                    line = l.split()
                    inputline = []
                    for i in line:
                        if(int(i) < 0 or int(i) > 9):
                            success = False
                            break
                        inputline.append(int(i))
                    inputboard.append(inputline)
                self.board = inputboard
            if(len(inputboard) != 9 or len(inputboard[0]) != 9):
                success = False
            if(not success):
                print('Invalid input in the input file\nDefaulting to build-in input value')
                self.board = self.defult_board
                    
        except IOError:
            print(f'Could not open file \'{__INPUT_FILE__}\'\nDefaulting to build-in input value')
            self.board = self.defult_board


    #Function to handle keyboard inputs
    def KeyboardHandler(self):
        key = None
        for event in pygame.event.get():
            #pygame.QUIT event is generated when the Cross icon is pressesd
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F4:
                    self.running = False
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9
                if event.key == pygame.K_DELETE:
                    self.clear()
                    key = None

                if event.key == pygame.K_SPACE:
                    self.solve_gui()

                if event.key == pygame.K_RETURN:
                    i, j = self.selected
                    if self.cubes[i][j].temp != 0:
                        if self.place(self.cubes[i][j].temp):
                            print(f"Placed at [{i}][{j}]")
                        else:
                            self.drawwrong = True
                            self.wrongstart = time.time()
                            print(f"Cannot place at [{i}][{j}]")
                        key = None

                        if self.is_finished():
                            print("Game over")

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = self.click(pos)
                if clicked:
                    self.select(clicked[0], clicked[1])
                    key = None

        if self.selected and key != None:
            self.sketch(key)

    #Function for main game loop
    def RunGame(self):
        self.KeyboardHandler()
        self.redraw_window(time.time()-self.starttime)
        pygame.display.update()

    #Function to draw the grid and the time for every background buffer update
    def redraw_window(self, currtime):
        self.window.fill((255,255,255))
        # Draw time
        fnt = pygame.font.SysFont("Verdana", 40)
        text = fnt.render("Time: " + format_time(currtime), 1, (0,0,0))
        wrongtext = fnt.render("Wrong move!", 2, (200,40,40))
        self.window.blit(text, (320, 560 + __MARGIN_TOP__))
        if(self.drawwrong):
            if(time.time()-self.wrongstart > 1):
                self.drawwrong = False
            self.window.blit(wrongtext, (__MARGIN_LEFT__, 560 + __MARGIN_TOP__))
        # Draw grid and board
        self.draw()
    
    #Function to update the model grid from the current values in the cubes
    def update_model(self):
        self.model = [[self.cubes[i][j].value for j in range(self.cols)] for i in range(self.rows)]

    #Function to solve the sudoku in the model grid
    def solve(self):
        li,pos,flag = find_empty(self.model)
        if flag == 0:
            return True
        if not pos:
            return False
        row,col = pos
        for i in li:
            if valid(self.model, i, (row, col)):
                self.model[row][col] = i
                if self.solve():
                    return True
                self.model[row][col] = 0
        return False

    #Function to place a number in the gui grid
    def place(self, val):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set(val)
            self.update_model()
            #Check in number is safe
            if valid(self.model, val, (row,col)) and self.solve():
                return True
            else:
                self.cubes[row][col].set(0)
                self.cubes[row][col].set_temp(0)
                self.update_model()
                return False

    #Function to write temporary value to a cell
    def sketch(self, val):
        row, col = self.selected
        self.cubes[row][col].set_temp(val)

    #Function to draw the sudoku grid
    def draw(self):
        # Draw Grid Lines
        gap = self.width / 9
        for i in range(self.rows+1):
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(self.window, (0,0,0), (__MARGIN_LEFT__, i*gap + __MARGIN_TOP__), (self.width + __MARGIN_LEFT__, i*gap  + __MARGIN_TOP__), thick)
            pygame.draw.line(self.window, (0, 0, 0), (i * gap + __MARGIN_LEFT__,  __MARGIN_TOP__), (i * gap + __MARGIN_LEFT__, self.height-14), thick)

        # Draw Cubes
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].draw(self.window)

    #Function to select cube once user has clicked on a box
    def select(self, row, col):
        # Reset all other
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].selected = False

        self.cubes[row][col].selected = True
        self.selected = (row, col)

    #Function to clear the board
    def clear(self):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set_temp(0)

    #Function to return the coordinates of the square the user clicked on 
    def click(self, pos):
        if (pos[0] < (self.width + __MARGIN_LEFT__) and pos[0] > (__MARGIN_LEFT__)) and ((pos[1] < self.height + __MARGIN_TOP__) and (pos[1] > __MARGIN_TOP__)):
            gap = (self.width) / 9
            x = (pos[0]-__MARGIN_LEFT__) // gap
            y = (pos[1]-__MARGIN_TOP__) // gap
            return (int(y),int(x))
        else:
            return None

    #Function to check if we've reached final game state
    def is_finished(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cubes[i][j].value == 0:
                    return False
        return True

    #Function to solve sudoku using backtacking on the main game grid
    def solve_gui(self):
        li,pos,flag = find_empty(self.model)

        if flag == 0:
            return True

        if not pos:
            return False
        
        row,col = pos

        for i in li:
            if valid(self.model, i, (row, col)):
                self.model[row][col] = i
                self.cubes[row][col].set(i)
                self.cubes[row][col].draw_change(self.window, True)
                self.update_model()
                pygame.display.update()
                pygame.time.delay(__AUTOFILL_DELAY__)
                if self.solve_gui():
                    return True

        return False

class Cube:
    rows = 9
    cols = 9

    def __init__(self, value, row, col, width, height):
        self.value = value
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    def draw(self, window):
        fnt = pygame.font.SysFont("Verdana", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        if self.temp != 0 and self.value == 0:
            text = fnt.render(str(self.temp), 1, (128,128,128))
            window.blit(text, (x+5 + __MARGIN_LEFT__, y+5 + __MARGIN_TOP__))
        elif not(self.value == 0):
            text = fnt.render(str(self.value), 1, (0, 0, 0))
            window.blit(text, (x + (gap/2 - text.get_width()/2) + __MARGIN_LEFT__, y + (gap/2 - text.get_height()/2) + __MARGIN_TOP__))

        if self.selected:
            pygame.draw.rect(window, (255,0,0), (x + __MARGIN_LEFT__,y + __MARGIN_TOP__, gap ,gap), 3)

    def draw_change(self, window, g=True):
        fnt = pygame.font.SysFont("Verdana", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        pygame.draw.rect(window, (255, 255, 255), (x + __MARGIN_LEFT__, y + __MARGIN_TOP__, gap, gap), 0)

        text = fnt.render(str(self.value), 1, (0, 0, 0))
        window.blit(text, (x + (gap / 2 - text.get_width() / 2) + __MARGIN_LEFT__, y + (gap / 2 - text.get_height() / 2) + __MARGIN_TOP__))
        if g:
            pygame.draw.rect(window, (0, 255, 0), (x + __MARGIN_LEFT__, y + __MARGIN_TOP__, gap, gap ), 3)
        else:
            pygame.draw.rect(window, (255, 0, 0), (x, y, gap, gap), 3)

    def set(self, val):
        self.value = val

    def set_temp(self, val):
        self.temp = val

#Function to find the best number to put at (i, j)
def best(board,i,j):
    full = {0,1,2,3,4,5,6,7,8,9}
    excluded = {0}
    for row in range(len(board)):
        excluded.add(board[row][j])

    for col in range(len(board)):
        excluded.add(board[i][col])

    i -= i%3
    j -= j%3

    for row in range(int(len(board)/3)):
        for col in range(int(len(board)/3)):
            excluded.add(board[i+row][j+col])

    left = full.difference(excluded)
    return left


def find_empty(board):
    minv = 10
    minn = set()
    pos = ()
    flag = 0
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 0:
                flag = 1
                numbers = best(board,i,j)
                if(minv > len(numbers) and len(numbers) > 0):
                    minv = len(numbers)
                    minn = numbers
                    pos = (i,j)


    if(minv == 10):
        return (None,None,flag)

    return (minn,pos,flag)

#Function to check if move is safe
def valid(bo, num, pos):
    # Check row
    for i in range(len(bo[0])):
        if bo[pos[0]][i] == num and pos[1] != i:
            return False

    # Check column
    for i in range(len(bo)):
        if bo[i][pos[1]] == num and pos[0] != i:
            return False

    # Check box
    box_x = pos[1] // 3
    box_y = pos[0] // 3

    for i in range(box_y*3, box_y*3 + 3):
        for j in range(box_x * 3, box_x*3 + 3):
            if bo[i][j] == num and (i,j) != pos:
                return False

    return True

#Function to display time
def format_time(secs):
    sec = int(secs%60)
    minute = int(secs//60)
    hour = minute//60
    
    str_min = str(minute)
    str_sec = str(sec)

    if(minute < 10):
        str_min = '0' + str(minute)
    if(sec < 10):
        str_sec = '0' + str(sec)
    mat = " " + str_min + ":" + str_sec
    return mat

#Main game function
def game_main():
    game = Game()
    #Game loop
    while game.running:
        game.RunGame()
        

if __name__ == '__main__':
    game_main()