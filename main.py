import pygame
import sys
from objects import Button, Rectangle, Grid, Battleship, Timer_display
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,                                    # screen
    GRID_SIZE, CELL_SIZE, GRID_LEFT_TOP_RED, GRID_LEFT_TOP_BLUE,    # GRID
    SHIPS_SIZES, SHIP_IMAGES,                                       # ship images    
    OCEAN_BLUE, WHITE, BLACK, RED, BLUE, GREEN, YELLOW, GRAY,       # colors
    TIME_PER_TURN,
    ARROWS
)


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    pygame.font.init()

    ship_orientation = "horizontal"  # or "vertical"
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Battleship Game")

    # rescale images of ships and arrows
    for orientation in SHIP_IMAGES:
        for ship in SHIP_IMAGES[orientation]:
            if orientation == "horizontal":
                scaled_size = (CELL_SIZE * SHIPS_SIZES[ship], CELL_SIZE)
            else:
                scaled_size = (CELL_SIZE, CELL_SIZE * SHIPS_SIZES[ship])
            SHIP_IMAGES[orientation][ship] = pygame.transform.scale(SHIP_IMAGES[orientation][ship], scaled_size)
    ARROWS["red"] = pygame.transform.scale(ARROWS["red"], (150, 150))
    ARROWS["blue"] = pygame.transform.scale(ARROWS["blue"], (150, 150))

    # constants for default ship positions
    RED_SHIP_CONSTANT = [
        Battleship(2, (600, 70), RED, "Destroyer"),
        Battleship(32, (600, 130), RED, "Submarine"),
        Battleship(31, (600, 190), RED, "Cruiser"),
        Battleship(4, (600, 250), RED, "Battleship"),
        Battleship(5, (600, 310), RED, "Carrier")  
    ]
    BLUE_SHIP_CONSTANT = [
        Battleship(2, (400, 70), BLUE, "Destroyer"),
        Battleship(32, (400, 130), BLUE, "Submarine"),
        Battleship(31, (400, 190), BLUE, "Cruiser"),
        Battleship(4, (400, 250), BLUE, "Battleship"),
        Battleship(5, (400, 310), BLUE, "Carrier")
    ]
    # Current player
    current_player = "red"
    selected_ship = None


    # Scores
    red_score = 0
    blue_score = 0

    # turn change counter incremented by 0.5
    round = 0



    # Initialize grids and ships
    red_grid = Grid(GRID_SIZE, GRID_SIZE, CELL_SIZE, GRID_LEFT_TOP_RED)
    red_ships = RED_SHIP_CONSTANT.copy()

    blue_grid = Grid(GRID_SIZE, GRID_SIZE, CELL_SIZE, GRID_LEFT_TOP_BLUE)
    blue_ships = BLUE_SHIP_CONSTANT.copy()

    # variables
    deployed_ships = [] # list of ships placed on grid

    selected_ship = None
    deployed_ships = []
    fp_setup = True   # first player setup  
    sp_setup = True   # second player setup
    round_start = False   # change to true once sp_setup is complete // should be false

    display_winner = True

    blue_deployed = []
    red_deployed = []

    # Nuke default state
    nuke = "deactive"
    red_nuke = True
    blue_nuke = True

    # Helper functions
    def clear_screen(screen) -> None:
        screen.fill(OCEAN_BLUE)

    def activate_nuke(screen) -> None:
        # activate and deactive nuke accordingly
        global nuke
        if nuke == "deactive":
            nuke = "active"
        else:
            nuke = "deactive"

    def start_setup(grid: Grid, complete_button: Button, rotate_button: Button, reset_button: Button) -> None:
        # For setup phase, inserts grid, complete button, rotate button and reset button
        grid.insert(screen)
        complete_button.draw(screen)
        rotate_button.draw(screen)
        reset_button.draw(screen)

    def draw_rect_list(screen, rect_list, color:tuple[int, int, int]) -> None:
        # for hover effect
        for rect in rect_list:
            pygame.draw.rect(screen, color, rect)

    def next_game_reset() -> None:  # reset variables for another game
        global start_game, display_winner, fp_setup, sp_setup, round_start, nuke,red_nuke, blue_nuke, red_score, blue_score, round, red_ships, blue_ships, red_deployed, blue_deployed, deployed_ships, current_player
        start_game = True
        display_winner = False  # break from current loop
        fp_setup = True
        sp_setup = True
        round_start = False
        nuke = "deactive"
        red_nuke = True
        blue_nuke = True
        red_score = 0
        blue_score = 0
        round = 0
        red_ships = RED_SHIP_CONSTANT.copy()
        blue_ships = BLUE_SHIP_CONSTANT.copy()
        red_deployed = []
        blue_deployed = []
        deployed_ships = []
        current_player = "red"

    # load sounds
    intro_sound = pygame.mixer.Sound("assets/audio/goodDayToDie.mp3")
    ocean_sound = pygame.mixer.Sound("assets/audio/ocean.mp3")
    champion_sound = pygame.mixer.Sound("assets/audio/champion.mp3")
    draw_sound = pygame.mixer.Sound("assets/audio/draw.mp3")
    click_sound = pygame.mixer.Sound("assets/audio/release.mp3")
    beep_sound = pygame.mixer.Sound("assets/audio/beep.mp3")

    intro_sound.play(loops=-1)  # play good day to die in a loop

    start_game = False
    quit = False
    # Home page
    while not start_game:
        clear_screen(screen) # fill screen with ocean blue
        home_ship = pygame.image.load("assets/img/home ship.png")
        home_ship = pygame.transform.scale(home_ship, (400, 400))
        screen.blit(home_ship, home_ship.get_rect(center=(SCREEN_WIDTH/2, 350)))
        play_button = Button(612, 500, 216, 100, "<PLAY>", YELLOW, BLACK, YELLOW, BLACK, clear_screen)
        play_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                start_game = True
                quit = True
            elif event.type == pygame.MOUSEBUTTONDOWN:  # check if button is down
                start_game = play_button.is_clicked(event, screen)
                if start_game:
                    click_sound.play()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    click_sound.play()
                    start_game = True
        
        pygame.display.update()
    intro_sound.stop()

    if not quit:
        while start_game:
            intro_sound.play(loops=-1)
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
                        mouse_pos = pygame.mouse.get_pos()
                        if not red_ships:  # check if all ships are deployed
                            fp_setup = not complete_button.is_clicked(event, screen)  # Will return true if clicked
                            if not fp_setup: # if first player setup is complete
                                click_sound.play()
                                red_deployed = deployed_ships  # copy deployed ships for later
                        if rotate_button.is_clicked(event, screen):  # return true if rotate button is clicked
                            click_sound.play()
                            for ship in red_ships:
                                ship.rotate()  # rotate the ships is the red_ship array
                            # change ship orienation accoridngly
                            if ship_orientation == "horizontal":
                                ship_orientation = "vertical"
                            else:
                                ship_orientation = "horizontal"
                        for ship in red_ships: # loop to check if a ship is clicked
                            if ship.rect.collidepoint(mouse_pos):
                                selected_ship = ship  # select a ship
                                click_sound.play()
                                break
                        if selected_ship:  # if a ship is already selected
                            # Deploy the selected ship
                            hovered_cell = red_grid.get_hovered_cell(mouse_pos, selected_ship.size, ship_orientation, selected_ship.identifier, clicked=True)
                            if hovered_cell:
                                click_sound.play()
                                ship_left_before = selected_ship.rect.topleft
                                selected_ship.rect.topleft = hovered_cell.topleft

                                deploy_success = True
                                for ship in deployed_ships:  # check for collision with deployed ships
                                    if ship.rect.colliderect(selected_ship.rect):
                                        selected_ship.rect.topleft = ship_left_before  # return the ship to the original position
                                        deploy_success = False   # Falsify deploy state
                                        red_grid.ship_log.pop()  # Remove the appended data from ship_log
                                        break
                                if deploy_success: # move ship to deployed ships and make selected ship None again if deployment is successful
                                    deployed_ships.append(selected_ship)
                                    red_ships.remove(selected_ship)
                                    selected_ship = None
                        if reset_button.is_clicked(event, screen):
                            click_sound.play()
                            red_ships = RED_SHIP_CONSTANT.copy()  # reset red ships
                            deployed_ships = []  # remove all deployed ships
                            for ship in red_ships:
                                ship.reset()  # reset all ships to their default position
                            ship_orientation = "horizontal"
                            red_grid.ship_log = []
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            click_sound.play()
                            if not red_ships: # check if all ships are deployed
                                fp_setup = False
                                red_deployed = deployed_ships
                            

                # Draw ships in their default positions
                for ship in red_ships:
                    ship.draw(screen)

                # Draw deployed ships
                for ship in deployed_ships:
                    ship.draw(screen)
                
                # TODO: continue comments
                
                if selected_ship is not None:  # Hover effect on grid
                    mouse_pos = pygame.mouse.get_pos()
                    hovered_cell = red_grid.get_hovered_cell(mouse_pos, selected_ship.size, ship_orientation, selected_ship.identifier)
                    highlight_rect = Rectangle(
                            selected_ship.position[0]-5, selected_ship.position[1]-5,
                            selected_ship.rect.width+10, selected_ship.rect.height+10,
                            WHITE
                    )
                    highlight_rect.draw(screen, 2)
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
                        round_start = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        if not blue_ships:
                            sp_setup = not complete_button.is_clicked(event, screen)
                            if not sp_setup:
                                click_sound.play()
                                round_start = True
                                blue_deployed = deployed_ships
                        if rotate_button.is_clicked(event, screen):  # rotate the ships is the red_ship array
                            click_sound.play()
                            for ship in blue_ships:
                                ship.rotate()
                            if ship_orientation == "horizontal":
                                ship_orientation = "vertical"
                            else:
                                ship_orientation = "horizontal"
                        for ship in blue_ships: # select a battleship
                            if ship.rect.collidepoint(mouse_pos):
                                click_sound.play()
                                selected_ship = ship
                                break
                        if selected_ship:
                            # Deploy the selected ship
                            hovered_cell = blue_grid.get_hovered_cell(mouse_pos, selected_ship.size, ship_orientation, selected_ship.identifier, clicked=True)
                            if hovered_cell:
                                click_sound.play()
                                ship_left_before = selected_ship.rect.topleft
                                selected_ship.rect.topleft = hovered_cell.topleft

                                deploy_success = True
                                for ship in deployed_ships:    # check for collision with deployed ships
                                    if ship.rect.colliderect(selected_ship.rect):
                                        selected_ship.rect.topleft = ship_left_before   # return the ship to the original position
                                        deploy_success = False    # cancels deployment to not append to deployed ships
                                        blue_grid.ship_log.pop()  # To remove the appended data of a hover ship that collides with deployed ship
                                        break
                                if deploy_success:
                                    deployed_ships.append(selected_ship)
                                    blue_ships.remove(selected_ship)
                                    selected_ship = None
                        if reset_button.is_clicked(event, screen):
                            click_sound.play()
                            blue_ships = BLUE_SHIP_CONSTANT.copy()
                            deployed_ships = []
                            for ship in blue_ships:
                                ship.reset()
                            ship_orientation = "horizontal"
                            blue_grid.ship_log = []
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            click_sound.play()
                            if not blue_ships:
                                sp_setup = False
                                round_start = True
                                blue_deployed = deployed_ships
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

            red_grid.ship_to_grid() # insert ships identifers into 2d array (grid)
            blue_grid.ship_to_grid() # insert ships identifers into 2d array (grid)

            # Round transition
            deployed_ships = [] # reset the deployed ships list
            ship_orientation = "horizontal"

            if round_start:
                turn_start_time = pygame.time.get_ticks() # Get the initial time (ms)
                red_timer = TIME_PER_TURN
                blue_timer = TIME_PER_TURN
                game_start_time = pygame.time.get_ticks()

            minutes = 0
            ocean_sound.play(loops=-1)

            while round_start:  # battle starts
                clear_screen(screen)
                red_grid.insert(screen)
                blue_grid.insert(screen)
                mouse_pos = pygame.mouse.get_pos()

                font = pygame.font.Font(None, 74)
                text = font.render(f"{current_player.capitalize()} turn", True, RED if current_player == "red" else BLUE)
                screen.blit(text, (600, 10))

                font_game_time = pygame.font.Font(None, 30)
                font_game_time_ms = pygame.font.Font(None, 50)
                game_time_display = (pygame.time.get_ticks() - game_start_time) / 1000
                if game_time_display >= 60:
                    minutes += 1
                    game_start_time = pygame.time.get_ticks()  # reset the start time
                game_time_text = font_game_time_ms.render(f"{minutes:02d}:{int(game_time_display):02d}", True, GREEN)
                time_text = font_game_time.render("TIME", True, BLACK)

                screen.blit(game_time_text, (665,90))
                screen.blit(time_text, (685, 70))

                passed_time = (pygame.time.get_ticks() - turn_start_time) / 1000 # make into seconds
                if current_player == "red":
                    display_red_timer = red_timer - passed_time
                    display_blue_timer = blue_timer # (float)
                elif current_player == "blue":
                    display_blue_timer = blue_timer - passed_time
                    display_red_timer = red_timer # (float)

                if display_red_timer <= 0:
                    current_player = "blue"
                    red_timer = TIME_PER_TURN
                    turn_start_time = pygame.time.get_ticks()
                    round += 0.5
                    nuke = "deactive"
                elif display_blue_timer <= 0:
                    current_player = "red"
                    blue_timer = TIME_PER_TURN
                    turn_start_time = pygame.time.get_ticks()
                    round += 0.5
                    nuke = "deactive"
                
                red_timer_display = Timer_display(50, 30, 30, 10, RED)
                blue_timer_display = Timer_display(1300, 30, 30, 10, BLUE)

                red_timer_display.draw(screen, int(display_red_timer))
                blue_timer_display.draw(screen, int(display_blue_timer))

                # nuke button blue should activate nuke mode in red grid and vice versa

                nuke_status_red = pygame.rect.Rect(50, 700, 200, 10)    #
                nuke_status_blue = pygame.rect.Rect(1150, 700, 200, 10)  #
                if red_nuke:
                    pygame.draw.rect(screen, GREEN, nuke_status_red)
                else:
                    pygame.draw.rect(screen, RED, nuke_status_red)
                if blue_nuke:
                    pygame.draw.rect(screen, GREEN, nuke_status_blue)
                else:
                    pygame.draw.rect(screen, RED, nuke_status_blue)

                if current_player == "red":
                    screen.blit(ARROWS["red"], (625, 280))
                else:
                    screen.blit(ARROWS["blue"], (625, 280))

                # Nuke buttons
                if round >= 1.5:
                    nuke_button_blue = Button(1150, 600, 200, 100, "Nuke", WHITE, BLACK, BLUE, GREEN, activate_nuke) 
                    nuke_button_blue.draw(screen)
                else: # If nuke not ready yet
                    gray_nuke_blue = Rectangle(1150, 600, 200, 100, GRAY)
                    gray_nuke_blue.draw(screen)

                if round >= 2:
                    nuke_button_red = Button(50, 600, 200, 100, "Nuke", WHITE, BLACK, RED, GREEN, activate_nuke)
                    nuke_button_red.draw(screen)
                else:
                    gray_nuke_red = Rectangle(50, 600, 200, 100, GRAY)
                    gray_nuke_red.draw(screen)

                # Check for win condition first
                if red_grid.round_over() or blue_grid.round_over():
                    pygame.time.wait(1000)
                    # Update scores
                    if red_grid.round_over():
                        blue_score += 1
                    else:
                        red_score += 1
                    round_start = False
                    display_winner = True

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        round_start = False
                        sp_setup = False
                        fp_setup = False
                        start_game = False
                        display_winner = True
                    
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # Check if nuke button is clicked
                        if round >= 2:
                            if current_player == "red":
                                if nuke_button_red.is_clicked(event,screen):
                                    if red_nuke:
                                        beep_sound.play()

                        if round >= 1.5:
                            if current_player == "blue":
                                if nuke_button_blue.is_clicked(event, screen):
                                    if blue_nuke:
                                        beep_sound.play()

                        # Check for single missiles and nuke mode
                        if current_player == "red":
                            if nuke == "active" and red_nuke:  # nuke mode
                                if blue_grid.nuke_grid(mouse_pos):
                                    nuke = "deactive"
                                    red_nuke = False
                                    current_player = "blue"
                                    red_timer -= passed_time
                                    red_timer = TIME_PER_TURN
                                    turn_start_time = pygame.time.get_ticks() # reset turn start timer
                                    round += 0.5
                            else:  # single missiles
                                if blue_grid.single_click(mouse_pos):
                                    current_player = "blue"
                                    red_timer -= passed_time
                                    red_timer = TIME_PER_TURN
                                    turn_start_time = pygame.time.get_ticks()
                                    round += 0.5
                        elif current_player == "blue":
                            if nuke == "active" and blue_nuke: # nuke mode
                                if red_grid.nuke_grid(mouse_pos):
                                    nuke = "deactive"
                                    blue_nuke = False
                                    current_player = "red"
                                    blue_timer -= passed_time
                                    blue_timer = TIME_PER_TURN
                                    turn_start_time = pygame.time.get_ticks() # reset turn start timer
                                    round += 0.5
                            else: # single missiles
                                if red_grid.single_click(mouse_pos):
                                    round += 0.5  # increment round
                                    current_player = "red"
                                    blue_timer -= passed_time
                                    blue_timer = TIME_PER_TURN
                                    turn_start_time = pygame.time.get_ticks() # reset turn start timer


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
            
            ocean_sound.stop()
            red_grid.reset()
            blue_grid.reset()

            if red_score > blue_score or blue_score > red_score: # if one of them win
                champion_sound.play(loops=-1)
            else: # if draw
                draw_sound.play(loops=-1)

            while display_winner:
                clear_screen(screen)

                red_grid.insert(screen)
                blue_grid.insert(screen)
                for ship in red_deployed:
                    ship.draw(screen)
                for ship in blue_deployed:
                    ship.draw(screen)
                
                play_again_button = Button(590, 650, 220, 100, "PLAY AGAIN", YELLOW, BLACK, YELLOW, BLACK)
                font = pygame.font.Font(None, 30)
                font2 = pygame.font.Font(None, 60)

                play_again_instruction = font.render("-Press Space or Click Button to Play another game-", True, GREEN)
                play_again_instruction_rect = play_again_instruction.get_rect(center=(SCREEN_WIDTH/2, 500))
                screen.blit(play_again_instruction, play_again_instruction_rect)

                game_time_render = font2.render(f"{minutes:02d}:{int(game_time_display):02d}", True, BLACK)
                game_time_render_rect = game_time_render.get_rect(center=(SCREEN_WIDTH/2, 100))
                screen.blit(game_time_render, game_time_render_rect)
                
                play_again_button.draw(screen)

                if red_score > blue_score:
                    winner_text = "Red Wins!"
                elif red_score < blue_score:
                    winner_text = "Blue Wins!"
                else:
                    winner_text = "Draw!"
                winner_font = pygame.font.Font(None, 200)

                text_surface = winner_font.render(winner_text, True, GREEN)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
                screen.blit(text_surface, text_rect)


                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        display_winner = False
                        start_game = False
                        sp_setup = False
                        fp_setup = False

                    # Play again conditional
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            next_game_reset()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if play_again_button.is_clicked(event, screen):
                            next_game_reset()
                for ship in red_ships:
                    ship.reset()
                for ship in blue_ships:
                    ship.reset()
                pygame.display.flip()
            champion_sound.stop()
            draw_sound.stop()


    pygame.quit()
    sys.exit()

