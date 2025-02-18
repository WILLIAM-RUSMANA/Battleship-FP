import pygame
from constants import GRID_SIZE, CELL_SIZE, WHITE_GRAY, SHIP_IMAGES, RED, GREEN, SHIPS

pygame.mixer.init()
boom_sound = pygame.mixer.Sound("assets/audio/BOOM.mp3")
pew_sound = pygame.mixer.Sound("assets/audio/pew pew.mp3")

class Rectangle(object):     # 
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, screen, weight=None) -> None:
        if weight is not None:    # for non full fill rectangles
            pygame.draw.rect(screen, self.color, self.rect, weight)
        else:                     # for full fill rectangles
            pygame.draw.rect(screen, self.color, self.rect)

class Timer_display(Rectangle):    # Child of Rectangle for displaying real time game duration
    def __init__(self, x, y, width, height, color, text_color=GREEN, font_size=60):
        super().__init__(x, y, width, height, color)
        self.font = pygame.font.Font(None, font_size)
        self.text_color = text_color
    
    def draw(self, screen, current_time) -> None:  # Draw timer with red or green color
        current_time_str = str(current_time)
        if current_time <= 3:  # Color text RED when timer is less than or equal to 3
            text_surf = self.font.render(current_time_str, True, RED)
        else:   # Color text as self.text_color
            text_surf = self.font.render(current_time_str, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

class Button(Rectangle):     # Child of Rectangle that serves as a button with text and hover color change
    def __init__(self, x, y, width, height, text, text_color, color, hover_color, text_hover_color, action = None):
        super().__init__(x, y, width, height, color)
        self.text = text
        self.font = pygame.font.Font(None, 36)
        self.text_color = text_color
        self.hover_color = hover_color
        self.action = action
        self.text_hover_color = text_hover_color

    def draw(self, screen) -> None:    # Draws button and check for collision for hover effect
        mouse_pos = pygame.mouse.get_pos()  # get mouse position
        text_surf = None
        if self.rect.collidepoint(mouse_pos):  # checks for collison with mouse pos
            pygame.draw.rect(screen, self.hover_color, self.rect)
            text_surf = self.font.render(self.text, True, self.text_hover_color)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
            text_surf = self.font.render(self.text, True, self.text_color)
        
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event, screen) -> bool:   # Check if button is clicked
        if self.rect.collidepoint(event.pos):   # check if button down is on button
            if self.action is not None:
                self.action(screen)
            return True
        return False

class Grid(object):
    def __init__(self, rows, cols, cell_size, top_left, color=WHITE_GRAY):
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.top_left = top_left
        self.color = color
        self.rects = [
            [pygame.Rect(
                (top_left[0] + x * cell_size), (top_left[1] + y * cell_size), cell_size, cell_size
            )
            for x in range(cols)]
            for y in range(rows)
        ]
        self.ship_log = []  # put where ships are at
        self.eliminated_squares = []
        self.ship_health = {
            "Carrier": 5,
            "Battleship": 4,  #TODO: fix for testing
            "Cruiser": 3,   # 31
            "Submarine": 3, # 32 
            "Destroyer": 2
        }

    def reset(self):  # reset the class variables 
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.ship_log = []
        self.eliminated_squares = []
        self.ship_health = {
            "Carrier": 5,
            "Battleship": 4,  #TODO: fix for testing
            "Cruiser": 3,   # 31
            "Submarine": 3, # 32 
            "Destroyer": 2
        }
    def insert(self, screen):  #  Draw grid on screen
        for row in self.rects:
            for rect in row:
                pygame.draw.rect(screen, self.color, rect, 1)
    
    # Getter method for setup phase that returns hovered Rect object, and appends data to ship_log when clicked
    def get_hovered_cell(self, mouse_pos, size_selected, orientation, identifier = None,clicked = False) -> pygame.Rect:
        # only gets when MOUSEBUTTONDOWN
        if orientation == "horizontal":
            for row in range(self.rows):
                for i in range(self.cols):
                    if self.rects[row][i].collidepoint(mouse_pos):
                        if GRID_SIZE < i + size_selected:
                            adjusted_pos = GRID_SIZE-size_selected
                            if clicked:
                                self.ship_log.append((adjusted_pos, row, size_selected, "horizontal", identifier))  # append grid's x, y, ship_size, orientation
                            return self.rects[row][adjusted_pos]
                        if clicked:
                            self.ship_log.append((i, row, size_selected, "horizontal", identifier)) 
                        return self.rects[row][i]
            return None
        else:   # if vertical
            for row in range(self.rows):
                for i in range(self.cols):
                    if self.rects[row][i].collidepoint(mouse_pos):
                        if GRID_SIZE < row + size_selected:
                            adjusted_pos = GRID_SIZE-size_selected
                            if clicked:
                                self.ship_log.append((i, adjusted_pos, size_selected, "vertical", identifier))  # Store as (x, y)
                            return self.rects[adjusted_pos][i]
                        if clicked:
                            self.ship_log.append((i, row, size_selected, "vertical", identifier))  # Store as (x, y)
                        return self.rects[row][i]
            return None
    
    # Method for battle phase that returns Rect object to display hover effect
    def get_single_hovered_cell(self, mouse_pos)->pygame.Rect:   # The hover function for game play
        for row in range(self.rows):
            for col in range(self.cols):
                if self.rects[row][col].collidepoint(mouse_pos):
                    return self.rects[row][col]
        return None
    
    # Method for battle phase that returns a list of Rect objects to display hover effect
    def get_nuke_hovered_cell(self, mouse_pos)->list[pygame.Rect]:
        for y in range(self.rows):
            for x in range(self.cols):
                if self.rects[y][x].collidepoint(mouse_pos):
                    y_y, x_x = y, x
                    if x + 3 >= GRID_SIZE:   # should accept for 7 and above
                        x_x = GRID_SIZE - 4
                    if y + 3 >= GRID_SIZE:
                        y_y = GRID_SIZE - 4
                    rects = []
                    for yy in range(y_y, y_y + 4):
                        for xx in range(x_x, x_x + 4):
                            rects.append(self.rects[yy][xx])
                    return rects
        return None
    
    # Method for returning x, y based on mouse position
    def get_x_y(self, mouse_pos):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.rects[row][col].collidepoint(mouse_pos):
                    return col, row
        return None
    
    # Method for appending eliminated Rects onto eliminated_squares list and return bool for player turn state
    def remove(self, row_index, col_index, nuke = False):  # y, x
        if self.grid[row_index][col_index] == 0:   # empty grid but valid hit
            if not nuke:  # play normal shot sound
                pew_sound.play()
            else:   # play nuke sound
                boom_sound.play()
            self.grid[row_index][col_index] = "X"
            self.eliminated_squares.append((row_index, col_index))
            return True # Will change player turn
        elif isinstance(self.grid[row_index][col_index], str):   # check if it's a string type
            if self.grid[row_index][col_index][0] == "A":  # Already destroyed ship
                return False   # invalidates click
            elif self.grid[row_index][col_index] == "X":   # empty grid
                return False   # makes click invalid
            elif self.grid[row_index][col_index] == "A": 
                return False # Invalidates click
            return False
        else:  # valid hits
            self.eliminated_squares.append((row_index, col_index))
            self.hit_ship(self.grid[row_index][col_index])
            self.grid[row_index][col_index] = "A" + str(self.grid[row_index][col_index])  # hit something
            boom_sound.play()  # boom sound if valid hit
            return False # to loop again if something is hit by single shots
    
    # Method to find row index and col index of clicked Rect, call remove method and return bool for player change state:
    #  False-> Stay Current  True -> Change  
    def single_click(self, mouse_pos) -> bool:
        for row_index, row in enumerate(self.rects):
            for col_index, rect in enumerate(row):
                if rect.collidepoint(mouse_pos):
                    elimination_stat = self.remove(row_index, col_index)  # False could also mean yes but something is hit so go again
                    if elimination_stat:
                        return True
        return False
     
    # Method to gdt rows and cols of selected Rects using nuke, remove the selected Rects using remove method, and return bool success state
    def nuke_grid(self, mouse_pos) -> bool:
        xy = self.get_x_y(mouse_pos)
        if xy:
            x, y = xy
        else:
            return False  # To terminate early because no valid Rects are selected
        
        if x + 3 >= GRID_SIZE:   # 7 and above will be accepted
            x = 6
        if y + 3 >= GRID_SIZE:
            y = 6
        for y_y in range(y, y + 4):
            for x_x in range(x, x+4):
                self.remove(y_y,x_x, True)

        return True

    # Method to insert ship identifiers on 2D list ship_log
    def ship_to_grid(self):
        for ship in self.ship_log:
            x, y, ship_size, orientation, identifier = ship
            try:
                if orientation == "horizontal":
                    for i in range(ship_size):
                        self.grid[y][x + i] = identifier
                elif orientation == "vertical":
                    for i in range(ship_size):
                        self.grid[y + i][x] = identifier
            except Exception as e:
                print(f"Error processing ship data ship_to_grid: {e}")
                print(f"ERROR: {e}")

    # Method to decrease ship_health by taking in ship_identifier as input
    def hit_ship(self, ship_identifier) -> None:
        if ship_identifier == 5:
            self.ship_health["Carrier"] -= 1
        elif ship_identifier == 4:
            self.ship_health["Battleship"] -= 1
        elif ship_identifier == 31:
            self.ship_health["Cruiser"] -= 1
        elif ship_identifier == 32:
            self.ship_health["Submarine"] -= 1
        elif ship_identifier == 2:
            self.ship_health["Destroyer"] -= 1
    
    # Method to return bool that ends game when health is 0
    # True -> end game    False -> continue
    def round_over(self):
        total_health = 0
        for ship in self.ship_health:
            total_health += self.ship_health[ship]
        if total_health == 0:
            return True
        return False
    
class Battleship:  # used in setup phase and winner display phase
    def __init__(self, identifier, horizontal_position, color, ship_type) -> None:
        self.ship_type = ship_type
        self.identifier = identifier
        self.horizontal_position = horizontal_position
        self.vertical_position = (self.horizontal_position[0]-50+self.horizontal_position[1], 100)
        self.color = color
        if self.identifier > 30:
            self.size = 3
        else:
            self.size = self.identifier
        self.rect = pygame.Rect(horizontal_position, (self.size * CELL_SIZE, CELL_SIZE))
        self.orientation = "horizontal"
        self.position = horizontal_position

    # Method to draw Rect and insert ship image on top of it
    def draw(self, screen) -> None:
        # Use image instead of rectangle
        pygame.draw.rect(screen, self.color, self.rect)
        ship_name = list(SHIPS.keys()) [list(SHIPS.values()).index(self.identifier)]  # Turn ship keys into list then use the index of the value to find it's index
        image = SHIP_IMAGES[self.orientation][ship_name]
        screen.blit(image, self.rect)
    
    # Method to rotate Rect object's attributes by changing it's width and height attribute; class varaibles orientation and position
    def rotate(self):
        if self.orientation == "horizontal":
            self.orientation = "vertical"
            self.position = self.vertical_position
            self.rect = pygame.Rect(self.vertical_position, (CELL_SIZE, self.size * CELL_SIZE))
        else:
            self.orientation = "horizontal"
            self.position = self.horizontal_position
            self.rect = pygame.Rect(self.horizontal_position, (self.size * CELL_SIZE, CELL_SIZE))

    # Method to return Rect object to their default position
    def reset(self):
        self.position = self.horizontal_position
        self.vertical_position = (self.horizontal_position[0]-50+self.horizontal_position[1], 100)
        self.orientation = "horizontal"
        self.rect = pygame.Rect(self.horizontal_position, (self.size * CELL_SIZE, CELL_SIZE))

