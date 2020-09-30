import pygame
import time
pygame.font.init()


class Grid:
    board = [
        [0, 0, 2, 0, 9, 1, 0, 3, 0],
        [0, 0, 0, 2, 0, 6, 1, 0, 7],
        [0, 7, 0, 0, 3, 0, 9, 0, 0],
        [7, 0, 3, 0, 6, 0, 8, 0, 0],
        [0, 6, 5, 1, 0, 7, 2, 9, 0],
        [0, 0, 9, 0, 2, 0, 7, 0, 4],
        [0, 0, 1, 0, 7, 0, 0, 8, 0],
        [2, 0, 4, 6, 0, 8, 0, 0, 0],
        [0, 8, 0, 9, 5, 0, 3, 0, 0]
    ]

    def __init__(self, rows, cols, width, height, screen):
        self.rows = rows
        self.cols = cols
        self.cubes = [[Cube(self.board[i][j], i, j, width, height)
                       for j in range(cols)] for i in range(rows)]
        self.width = width
        self.height = height
        self.model = None
        self.update_model()
        self.selected = None
        self.screen = screen

    def update_model(self):
        self.model = [[self.cubes[i][j].value for j in range(
            self.cols)] for i in range(self.rows)]

    def place(self, val):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set(val)
            self.update_model()

            if valid(self.model, val, (row, col)) and self.solve():
                return True
            else:
                self.cubes[row][col].set(0)
                self.cubes[row][col].set_temp(0)
                self.update_model()
                return False

    # sketch the temporary value inserted into a cube
    def sketch(self, val):
        row, col = self.selected
        self.cubes[row][col].set_temp(val)

    def draw(self):
        # Draw Grid Lines
        gap = self.width / 9
        for i in range(self.rows+1):
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(self.screen, (0, 0, 0), (0, int(i*gap)),
                             (self.width, int(i*gap)), thick)
            pygame.draw.line(self.screen, (0, 0, 0), (int(i * gap), 0),
                             (int(i * gap), self.height), thick)

        # Draw Cubes
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].draw(self.screen)

    def select(self, row, col):
        # Reset all other
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].selected = False

        self.cubes[row][col].selected = True
        self.selected = (row, col)

    def clear(self):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set_temp(0)

    def delete(self):
        row, col = self.selected
        if self.cubes[row][col].value != 0:
            self.cubes[row][col].set(0)

    def click(self, pos):
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / 9
            x = pos[0] // gap
            y = pos[1] // gap
            return (int(y), int(x))
        else:
            return None

    def is_finished(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cubes[i][j].value == 0:
                    return False
        return True

    def solve(self):
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, col = find

        for i in range(1, 10):
            if valid(self.model, i, (row, col)):
                self.model[row][col] = i

                if self.solve():
                    return True

                self.model[row][col] = 0

        return False

    def solve_gui(self):
        self.update_model()
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, col = find

        for i in range(1, 10):
            if valid(self.model, i, (row, col)):
                self.model[row][col] = i
                self.cubes[row][col].set(i)
                self.cubes[row][col].draw_change(self.screen, True)
                self.update_model()
                pygame.display.update()
                pygame.time.delay(20)

                if self.solve_gui():
                    return True

                self.model[row][col] = 0
                self.cubes[row][col].set(0)
                self.update_model()
                self.cubes[row][col].draw_change(self.screen, False)
                pygame.display.update()
                pygame.time.delay(20)

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

    def draw(self, screen):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        if self.temp != 0 and self.value == 0:
            text = fnt.render(str(self.temp), 1, (128, 128, 128))
            screen.blit(text, (x+5, y+5))
        elif not(self.value == 0):
            text = fnt.render(str(self.value), 1, (0, 0, 0))
            screen.blit(text, (int(x) + int(gap/2 - text.get_width()/2),
                               int(y) + int(gap/2 - text.get_height()/2)))

        if self.selected:
            pygame.draw.rect(screen, (255, 0, 0),
                             (int(x), int(y), int(gap), int(gap)), 4)

    def draw_change(self, screen, g=True):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        pygame.draw.rect(screen, (255, 255, 255),
                         (int(x), int(y), int(gap), int(gap)), 0)

        text = fnt.render(str(self.value), 1, (0, 0, 0))
        screen.blit(text, (int(x) + int(gap / 2 - text.get_width() / 2),
                           int(y) + int(gap / 2 - text.get_height() / 2)))
        if g:
            pygame.draw.rect(screen, (0, 255, 0),
                             (int(x), int(y), int(gap), int(gap)), 3)
        else:
            pygame.draw.rect(screen, (255, 0, 0),
                             (int(x), int(y), int(gap), int(gap)), 3)

    def set(self, val):
        self.value = val

    def set_temp(self, val):
        self.temp = val


def find_empty(bo):
    for i in range(len(bo)):
        for j in range(len(bo[0])):
            if bo[i][j] == 0:
                return (i, j)  # row, col

    return None


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
            if bo[i][j] == num and (i, j) != pos:
                return False

    return True


def redraw_window(screen, board, time, strikes):
    screen.fill((255, 255, 255))
    # Draw time
    fnt = pygame.font.SysFont("comicsans", 40)
    text = fnt.render("Time: " + format_time(time), 1, (255, 0, 0))
    screen.blit(text, (380, 560))
    # Draw Strikes
    # Draw instruction
    # text = fnt.render("Press D to reset the board", 1, (0, 0, 0))
    # screen.blit(text, (0, 560))
    # text = fnt.render(
    #     "Press Spacebar to auto solve the board", 1, (0, 0, 0))
    # screen.blit(text, (0, 580))
    # text = fnt.render(
    #     "Press Backspace to remove temporary number", 1, (0, 0, 0))
    # screen.blit(text, (0, 600))
    text = fnt.render("X " * strikes, 1, (255, 0, 0))
    screen.blit(text, (20, 560))
    # Draw grid and board
    board.draw()


def end_window(screen, board, time, strikes):
    screen.fill((255, 255, 255))
    # Draw time
    fnt = pygame.font.SysFont("comicsans", 40)
    text = fnt.render("Time: " + format_time(time), 1, (255, 0, 0))
    screen.blit(text, (380, 560))
    # Game over
    text = fnt.render("Game over", 1, (255, 0, 0))
    screen.blit(text, (20, 560))
    # Draw grid and board
    board.draw()


def format_time(secs):
    sec = secs % 60
    minute = secs//60
    if sec < 10:
        mat = " " + str(minute) + ":0" + str(sec)
    else:
        mat = " " + str(minute) + ":" + str(sec)
    return mat


def main():
    screen = pygame.display.set_mode((540, 600))
    # Title and Icon
    pygame.display.set_caption("Sudoku")
    icon = pygame.image.load('sudoku.png')
    pygame.display.set_icon(icon)
    board = Grid(9, 9, 540, 540, screen)
    key = None
    run = True
    start = time.time()
    end = False
    strikes = 0

    # Game Loop
    while run:

        play_time = round(time.time() - start)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
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
                # If Backspace is pressed, delete temp value
                if event.key == pygame.K_BACKSPACE:
                    board.clear()
                    key = None
                # If Delete is pressed, delete entered & temp value
                if event.key == pygame.K_DELETE:
                    board.delete()
                    board.clear()
                    key = None
                # If R is pressed reset the board to default
                if event.key == pygame.K_r:
                    board = Grid(9, 9, 540, 540, screen)
                # If SPACE is pressed, auto solve the board and go to end game
                if event.key == pygame.K_SPACE:
                    board.solve_gui()
                    end = True
                    run = False

                if event.key == pygame.K_RETURN:
                    i, j = board.selected
                    if board.cubes[i][j].temp != 0:
                        if board.place(board.cubes[i][j].temp):
                            continue
                        else:
                            strikes += 1
                        key = None

                        if board.is_finished():
                            run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None

        if board.selected and key != None:
            board.sketch(key)
        # If 3 strikes, game over
        if strikes == 3:
            run = False
            end = True
        redraw_window(screen, board, play_time, strikes)
        pygame.display.update()

    end_time = round(time.time() - start)

    while end:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None

        if board.selected and key != None:
            board.sketch(key)

        end_window(screen, board, end_time, strikes)
        pygame.display.update()


main()
pygame.quit()
