import pygame
import sys
from objects import Button, Rectangle, Grid, Battleship
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,                 # screen
    GRID_SIZE, CELL_SIZE,                      # GRID
    SHIPS_SIZES, SHIP_IMAGES,                               # ship images    
    OCEAN_BLUE, WHITE, BLACK, RED, BLUE, GREEN   # colors
)

pygame.init()
pygame.mixer.init()
pygame.font.init()

# variables
deployed_ships = [] # reset the deployed ships list
ship_orientation = "horizontal"
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battleship Game")

for orientation in SHIP_IMAGES:
    for ship in SHIP_IMAGES[orientation]:
        if orientation == "horizontal":
            scaled_size = (CELL_SIZE * SHIPS_SIZES[ship], CELL_SIZE)
        else:
            scaled_size = (CELL_SIZE, CELL_SIZE * SHIPS_SIZES[ship])
        SHIP_IMAGES[orientation][ship] = pygame.transform.scale(SHIP_IMAGES[orientation][ship], scaled_size)

# Boards
red_board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
blue_board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]


RED_SHIP_CONSTANT = [
    Battleship(2, (600, 50), RED, "Destroyer"),
    Battleship(32, (600, 110), RED, "Submarine"),
    Battleship(31, (600, 170), RED, "Cruiser"),
    Battleship(4, (600, 230), RED, "Battleship"),
    Battleship(5, (600, 290), RED, "Carrier")  #TODO: fix for testing
]

BLUE_SHIP_CONSTANT = [
    Battleship(2, (400, 50), BLUE, "Destroyer"),
    Battleship(32, (400, 110), BLUE, "Submarine"),
    Battleship(31, (400, 170), BLUE, "Cruiser"),
    Battleship(4, (400, 230), BLUE, "Battleship"),
    Battleship(5, (400, 290), BLUE, "Carrier")
]
# Current player
current_player = "red"
selected_ship = None
ship_orientation = "horizontal"  # or "vertical"

# Scores
red_score = 0
blue_score = 0

round = 0

nuke = "deactive"
red_nuke = True
blue_nuke = True

GRID_LEFT_TOP_RED = (50, 50)
GRID_LEFT_TOP_BLUE = (850, 50)

red_grid = Grid(GRID_SIZE, GRID_SIZE, CELL_SIZE, GRID_LEFT_TOP_RED)
red_ships = RED_SHIP_CONSTANT.copy()

blue_grid = Grid(GRID_SIZE, GRID_SIZE, CELL_SIZE, GRID_LEFT_TOP_BLUE)
blue_ships = BLUE_SHIP_CONSTANT.copy()

selected_ship = None
deployed_ships = []
fp_setup = True   # first player setup  #TODO: TESTING
sp_setup = True   # second player setup
round_start = False   # change to true once sp_setup is complete // should be false

display_winner = True

GRID_LEFT_TOP_RED = (50, 50)
GRID_LEFT_TOP_BLUE = (850, 50)

blue_deployed = []
red_deployed = []

# Helper functions
def clear_screen(screen):
    screen.fill(OCEAN_BLUE)

def activate_nuke(screen):
    global nuke
    if nuke == "deactive":
        nuke = "active"
    else:
        nuke = "deactive"

def start_setup(grid, complete_button, rotate_button, reset_button):
    grid.insert(screen)
    complete_button.draw(screen)
    rotate_button.draw(screen)
    reset_button.draw(screen)

def draw_rect_list(screen, rect_list, color):
    for rect in rect_list:
        pygame.draw.rect(screen, color, rect)

# load sounds
intro_sound = pygame.mixer.Sound("assets/audio/goodDayToDie.mp3")
boom_sound = pygame.mixer.Sound("assets/audio/boom.mp3")
boom_sound.set_volume(1)
intro_sound.play(loops=-1)

start_game = False
quit = False
# Home page
while not start_game:
    clear_screen(screen) # fill screen with ocean blue
    play_button = Button(612, 400, 216, 100, "<PLAY>", WHITE, BLACK, WHITE, BLACK, clear_screen)
    play_button.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            start_game = True
            quit = True
        elif event.type == pygame.MOUSEBUTTONDOWN:  # check if button is down
            start_game = play_button.is_clicked(event, screen)
    
    pygame.display.update()
if not quit:
    while start_game:
        while fp_setup:   # Red player setup loop
            clear_screen(screen)  # Background color ocean blue
            complete_button = Button(600, 600, 216, 100, "<COMPLETE>", WHITE, BLACK, WHITE, BLACK, clear_screen)
            rotate_button = Button(600, 450, 160, 75, "Rotate", WHITE, BLACK, WHITE, BLACK)
            reset_button = Button(800, 450, 160, 75, "RESET", WHITE, BLACK, WHITE, BLACK)
            start_setup(red_grid, complete_button, rotate_button, reset_button) # Draw grid, red complete button, rotate button and the reset button

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    start_game = False
                    fp_setup = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # if complete_button.is_clicked(event, screen):   # TODO: For testing rem later
                    #     start_game = False
                    #     break  
                    mouse_pos = pygame.mouse.get_pos()
                    if not red_ships:
                        fp_setup = not complete_button.is_clicked(event, screen)  # Will return true if it's clicked
                        if not fp_setup:
                            red_deployed = deployed_ships
                    if rotate_button.is_clicked(event, screen):  # rotate the ships is the red_ship array
                        for ship in red_ships:
                            ship.rotate()
                        if ship_orientation == "horizontal":
                            ship_orientation = "vertical"
                        else:
                            ship_orientation = "horizontal"
                    for ship in red_ships: # select a battleship
                        if ship.rect.collidepoint(mouse_pos):
                            selected_ship = ship
                            break
                    if selected_ship:
                        # Deploy the selected ship
                        hovered_cell = red_grid.get_hovered_cell(mouse_pos, selected_ship.size, ship_orientation, selected_ship.identifier, clicked=True)
                        if hovered_cell:
                            ship_left_before = selected_ship.rect.topleft
                            selected_ship.rect.topleft = hovered_cell.topleft

                            make_none = True
                            for ship in deployed_ships:
                                if ship.rect.colliderect(selected_ship.rect):
                                    selected_ship.rect.topleft = ship_left_before
                                    make_none = False
                                    red_grid.ship_log.pop()  # To remove the appended data of a hover ship that collides with deployed ship
                                    break
                            if make_none:
                                deployed_ships.append(selected_ship)
                                red_ships.remove(selected_ship)
                                selected_ship = None
                    if reset_button.is_clicked(event, screen):
                        red_ships = RED_SHIP_CONSTANT.copy()
                        deployed_ships = []
                        for ship in red_ships:
                            ship.reset()
                        ship_orientation = "horizontal"
                        red_grid.ship_log = []

            # Draw battleships
            for ship in red_ships:
                ship.draw(screen)

            # Draw deployed ships
            for ship in deployed_ships:
                ship.draw(screen)
            
            if selected_ship is not None:  # Hover effect on grid
                mouse_pos = pygame.mouse.get_pos()
                hovered_cell = red_grid.get_hovered_cell(mouse_pos, selected_ship.size, ship_orientation, selected_ship.identifier)
                highlight_rect = Rectangle(
                        selected_ship.position[0]-5, selected_ship.position[1]-5,
                        selected_ship.rect.width+10, selected_ship.rect.height+10,
                        WHITE
                )
                highlight_rect.draw(screen, 2)
                # selected_ship.draw(screen)
                if hovered_cell:   # hover effect
                    hover_rect = hovered_cell.copy()
                    hover_rect.width = selected_ship.rect.width
                    hover_rect.height = selected_ship.rect.height
                    pygame.draw.rect(screen, RED, hover_rect, 2)

            pygame.display.flip()

        if not start_game: # break of early if quit in sp_setup
            break
        # Round transition
        deployed_ships = [] # reset the deployed ships list
        ship_orientation = "horizontal"

        while sp_setup:   # Blue player setup loop
            clear_screen(screen)  # Background color ocean blue
            complete_button = Button(400, 600, 216, 100, "<COMPLETE>", WHITE, BLACK, WHITE, BLACK, clear_screen)
            rotate_button = Button(400, 450, 160, 75, "Rotate", WHITE, BLACK, WHITE, BLACK)
            reset_button = Button(600, 450, 160, 75, "RESET", WHITE, BLACK, WHITE, BLACK)
            start_setup(blue_grid, complete_button, rotate_button, reset_button) # Draw grid, complete button, rotate button and the reset button

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    start_game = False
                    sp_setup = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if not blue_ships:
                        sp_setup = not complete_button.is_clicked(event, screen)
                        if not sp_setup:
                            round_start = True
                            blue_deployed = deployed_ships
                    if rotate_button.is_clicked(event, screen):  # rotate the ships is the red_ship array
                        for ship in blue_ships:
                            ship.rotate()
                        if ship_orientation == "horizontal":
                            ship_orientation = "vertical"
                        else:
                            ship_orientation = "horizontal"
                    for ship in blue_ships: # select a battleship
                        if ship.rect.collidepoint(mouse_pos):
                            selected_ship = ship
                            break
                    if selected_ship:
                        # Deploy the selected ship
                        hovered_cell = blue_grid.get_hovered_cell(mouse_pos, selected_ship.size, ship_orientation, selected_ship.identifier, clicked=True)
                        if hovered_cell:
                            ship_left_before = selected_ship.rect.topleft
                            selected_ship.rect.topleft = hovered_cell.topleft

                            make_none = True
                            for ship in deployed_ships:    # check for collision with deployed ships
                                if ship.rect.colliderect(selected_ship.rect):
                                    selected_ship.rect.topleft = ship_left_before   # return the ship to the original position
                                    make_none = False
                                    blue_grid.ship_log.pop()  # To remove the appended data of a hover ship that collides with deployed ship
                                    break
                            if make_none:
                                deployed_ships.append(selected_ship)
                                blue_ships.remove(selected_ship)
                                selected_ship = None
                    if reset_button.is_clicked(event, screen):
                        blue_ships = BLUE_SHIP_CONSTANT.copy()
                        deployed_ships = []
                        for ship in blue_ships:
                            ship.reset()
                        ship_orientation = "horizontal"
                        blue_grid.ship_log = []
            # Draw battleships
            for ship in blue_ships:
                ship.draw(screen)

            # Draw deployed ships
            for ship in deployed_ships:
                ship.draw(screen)
            
            if selected_ship is not None:  # Hover effect on grid
                mouse_pos = pygame.mouse.get_pos()
                hovered_cell = blue_grid.get_hovered_cell(mouse_pos, selected_ship.size, ship_orientation, selected_ship.identifier)
                highlight_rect = Rectangle(
                        selected_ship.position[0]-5, selected_ship.position[1]-5,
                        selected_ship.rect.width+10, selected_ship.rect.height+10,
                        WHITE
                )
                highlight_rect.draw(screen, 2)
                # selected_ship.draw(screen)
                if hovered_cell:   # hover effect
                    hover_rect = hovered_cell.copy()
                    hover_rect.width = selected_ship.rect.width
                    hover_rect.height = selected_ship.rect.height
                    pygame.draw.rect(screen, BLUE, hover_rect, 2)    
            pygame.display.flip()
        
        intro_sound.stop()
        if not start_game:
            break

        red_grid.ship_to_grid()
        blue_grid.ship_to_grid()

        while round_start:  # battle starts
            clear_screen(screen)
            red_grid.insert(screen)
            blue_grid.insert(screen)
            mouse_pos = pygame.mouse.get_pos()

            font = pygame.font.Font(None, 74)
            text = font.render(f"{current_player.capitalize()} turn", True, RED if current_player == "red" else BLUE)
            screen.blit(text, (600, 10))

            # nuke button blue should activate nuke mode in red grid and vice versa
            nuke_button_blue = Button(1100, 560, 200, 100, "Nuke", WHITE, BLACK, BLUE, GREEN, activate_nuke) 
            nuke_button_red = Button(50, 560, 200, 100, "Nuke", WHITE, BLACK, RED, GREEN, activate_nuke)
            nuke_highlight_red = pygame.rect.Rect(50, 680, 200, 10)    #
            nuke_highlight_blue = pygame.rect.Rect(1100, 680, 200, 10)  #
            if red_nuke:
                pygame.draw.rect(screen, GREEN, nuke_highlight_red)
            else:
                pygame.draw.rect(screen, RED, nuke_highlight_red)
            if blue_nuke:
                pygame.draw.rect(screen, GREEN, nuke_highlight_blue)
            else:
                pygame.draw.rect(screen, RED, nuke_highlight_blue)

            if round >= 1.5:
                nuke_button_blue.draw(screen)

            if round >= 2:
                nuke_button_red.draw(screen)

            # Check for win condition first
            if red_grid.round_over() or blue_grid.round_over():
                pygame.time.wait(1000)
                # Update scores
                if red_grid.round_over():
                    blue_score += 1
                else:
                    red_score += 1
                round_start = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    round_start = False
                    sp_setup = False
                    fp_setup = False
                    start_game = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if current_player == "red":
                        if nuke_button_red.is_clicked(event,screen):
                            if red_nuke:
                                nuke = "active"
                    else: # if blue
                        if nuke_button_blue.is_clicked(event, screen):
                            if blue_nuke:
                                nuke = "active"

                    if current_player == "red":
                        if nuke == "active" and red_nuke:  # nuke mode
                            if blue_grid.nuke_grid(mouse_pos):
                                nuke = "deactive"
                                red_nuke = False
                                current_player = "blue"
                                round += 0.5
                        else:  # single missiles
                            if blue_grid.single_click(mouse_pos):
                                current_player = "blue"
                                round += 0.5
                    elif current_player == "blue":
                        if nuke == "active" and blue_nuke: # nuke mode
                            if red_grid.nuke_grid(mouse_pos):
                                nuke = "deactive"
                                blue_nuke = False
                                current_player = "red"
                                round += 0.5
                        else: # single missiles
                            if red_grid.single_click(mouse_pos):
                                round += 0.5  # increment round
                                current_player = "red"
                    
            # Hover effect on grid
            if round_start:
                if current_player == "red":
                    if nuke == "active" and red_nuke:
                        red_nuke_hover = blue_grid.get_nuke_hovered_cell(mouse_pos)
                        if red_nuke_hover:
                            draw_rect_list(screen, red_nuke_hover, RED)
                    else:
                        red_hover = blue_grid.get_single_hovered_cell(mouse_pos)
                        if red_hover:
                            pygame.draw.rect(screen, RED, red_hover)

                else:  # if blue
                    if nuke == "active" and blue_nuke:
                        blue_nuke_hover = red_grid.get_nuke_hovered_cell(mouse_pos)
                        if blue_nuke_hover:
                            draw_rect_list(screen, blue_nuke_hover, BLUE)
                    else:
                        blue_hover = red_grid.get_single_hovered_cell(mouse_pos)
                        if blue_hover:
                            pygame.draw.rect(screen, BLUE, blue_hover)
            else:
                break
            
            # Redraw Eliminated Squares
            for row, col in red_grid.eliminated_squares:  # color eliminated squares for red grid
                try:
                    if red_grid.grid[row][col][0] == "A":
                        pygame.draw.rect(screen, BLACK, red_grid.rects[row][col])
                    else:
                        pygame.draw.rect(screen, GREEN, red_grid.rects[row][col])
                except TypeError:
                    pass
            for row, col in blue_grid.eliminated_squares:  # color eliminated squares for blue grid
                try:
                    if blue_grid.grid[row][col][0] == "A":
                        pygame.draw.rect(screen, BLACK, blue_grid.rects[row][col])
                    else:
                        pygame.draw.rect(screen, GREEN, blue_grid.rects[row][col])
                except TypeError:
                    pass
            pygame.display.flip()

        while display_winner:
            clear_screen(screen)
            red_grid.insert(screen)
            blue_grid.insert(screen)
            if red_score > blue_score:
                winner_text = "Red Wins!"
            elif red_score < blue_score:
                winner_text = "Blue Wins!"
            else:
                winner_text = "Draw!"
            winner_font = pygame.font.Font(None, 200)
            text_surface = winner_font.render(winner_text, True, GREEN)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            
            for ship in red_deployed:
                ship.draw(screen)
            for ship in blue_deployed:
                ship.draw(screen)

            screen.blit(text_surface, text_rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    display_winner = False
                    start_game = False
                    sp_setup = False
                    fp_setup = False
            pygame.display.flip()

pygame.quit()
sys.exit()
