import sys, time
import pygame
from minesweeper import Minesweeper

pygame.init()
info = pygame.display.Info()

# constants
FPS = 60
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
CELL_SIZE = 30
MENU_HEIGHT = 100
# Make the board as big as possible
BOARD_SIZE = ((SCREEN_WIDTH // CELL_SIZE) * CELL_SIZE, ((SCREEN_HEIGHT - MENU_HEIGHT) // CELL_SIZE) * CELL_SIZE)
MINE_COUNT = 125

# If True, the game will attempt to automatically reveal safe cells and flag mines.
solve = False

# Board setup
Row_Count, Col_Count = BOARD_SIZE[0] // CELL_SIZE, BOARD_SIZE[1] // CELL_SIZE
# x and y offset to leave some spaces to edges of the screen
x_offset = (SCREEN_WIDTH - BOARD_SIZE[0]) / 2
y_offset = (SCREEN_HEIGHT - BOARD_SIZE[1] + MENU_HEIGHT) / 2

# Game Setup
minesweeper = Minesweeper((Row_Count, Col_Count), MINE_COUNT)
first_click = True
last_click = None
lost = False
win = False
start_time = 0
timer = False
last_time = 0
board = minesweeper.board
player_board = minesweeper.player_board

# screen setup
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
pygame.display.set_caption('Minesweeper')
clock = pygame.time.Clock()

def load_images():
    '''Loads all required images.'''
    images = {}
    path = 'images/'
    file_names = [0, 1, 2, 3, 4, 5, 6, 7, 8, 'flag', 'wrong_flag', 'bomb', 'clicked_bomb', 'unknown']
    for name in file_names:
        image = pygame.image.load(f'{path}{name}.png').convert()
        image = pygame.transform.scale(image,(CELL_SIZE,CELL_SIZE)) #scale the image to cell size
        images.update({name:image})

    return images

def draw(board, player_board, images, lost, last_click):
    '''Draws the board on screen.'''
    for row_i in range(Row_Count):
        for col_i in  range(Col_Count):
            player_cell = player_board[row_i][col_i]
            cell = board[row_i][col_i]

            if cell == 'B':
                image = images['clicked_bomb']

            if player_cell == '?':
                image = images['unknown']
            elif player_cell == 'f':
                image = images['flag']
            else:
                image = images[player_cell]

            if lost: # Show all bombs and wrong flags at end of the game
                if cell == 'b' and player_cell != 'f':
                    image = images['bomb']
                elif cell != 'b' and player_cell == 'f':
                    image = images['wrong_flag']

                if last_click == (row_i, col_i):
                    image = images['clicked_bomb']

            size = (row_i * CELL_SIZE+ x_offset, col_i * CELL_SIZE + y_offset)
            screen.blit(image, size, image.get_rect())

font = pygame.font.Font(None,100)

def draw_menu(remaining_mines, start_time, timer, last_time): #everything about this function hurts my eyes
    '''Draws the timer and the remaining mine counter.'''
    # Mine count
    text = font.render(str(remaining_mines).zfill(3), True, 'red')
    pygame.draw.rect(screen, 'black', [x_offset, y_offset - MENU_HEIGHT, 150, 75])#mine count
    screen.blit(text, (2 * x_offset + 5, y_offset - MENU_HEIGHT), text.get_rect())

    # Timer
    pygame.draw.rect(screen, 'black', [SCREEN_WIDTH - x_offset - 150, y_offset - MENU_HEIGHT, 150, 75])
    if timer:
        time_text = str(round(time.time() - start_time)).zfill(3)
    else:
        time_text = str(round(last_time - start_time)).zfill(3) # Show the last_time if game has ended
    text = font.render(time_text,True,'red')
    screen.blit(text, (SCREEN_WIDTH - x_offset - 135, y_offset - MENU_HEIGHT),text.get_rect())

# Load the images
images = load_images()

# main loop 
while True:
    # event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.key == pygame.K_SPACE: # Reset the game
                lost = False
                minesweeper = Minesweeper((Row_Count, Col_Count), MINE_COUNT)
                first_click = True
                last_click = None
                timer = False
                last_time = 0
                start_time = 0

        if event.type == pygame.MOUSEBUTTONDOWN: # Mouse events
                x, y = pygame.mouse.get_pos()
                # Get the row and column using x and y values
                row, col = round((x - x_offset) // CELL_SIZE), round((y - y_offset) // CELL_SIZE)

                if 0 <= row < Row_Count and 0 <= col < Col_Count and not lost: # Check for boundaries 
                    if event.button == 1:  # Left mouse button
                        if first_click:
                            minesweeper.place_mines(row, col)
                            first_click = False
                            timer = True
                            start_time = time.time()
                            minesweeper.reveal(row, col)
                            player_board[row][col] = 0  # Sometimes first cell doesn't update and remains unknown

                         # Check if the player has lost the game
                        if minesweeper.reveal(row, col) == 'lost' and player_board[row][col] != 'f':
                            if board[row][col] == 'b':
                                last_click = (row, col)
                            lost = True
                            timer = False

                    elif event.button == 3 and not first_click:  # Right mouse button
                        minesweeper.flag(row, col)

    board = minesweeper.board
    player_board = minesweeper.player_board
    remaining_mines = minesweeper.get_remaining_mines(MINE_COUNT)

    if timer: # Update the last_time. last_time is used when game ends
        last_time = time.time()

    if minesweeper.is_win(): # Stop the timer if player has won the game
        timer = False

    if solve and not first_click:
        minesweeper.solve()

    # Update the screen
    screen.fill('white')

    draw(board, player_board, images, lost, last_click)
    draw_menu(remaining_mines, start_time, timer, last_time)

    pygame.display.flip()
    clock.tick(FPS)
