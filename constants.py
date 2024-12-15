import pygame
import os


# Screen dimensions
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 850

# Colors
WHITE =      (255, 255, 255)
BLACK =      (0  , 0  , 0  )
BLUE =       (33 , 19 , 235)
RED =        (225, 34 , 34 )
GRAY =       (200, 200, 200)
GREEN =      (0  , 255, 0  )
OCEAN_BLUE = (21 , 127, 233)
WHITE_GRAY = (240, 240, 240)
YELLOW =     (255, 255, 0  )
DARK_YELLOW =(214, 186, 24 )


GRID_SIZE = 10     # 10x10 grid
CELL_SIZE = 50     # Directly proportional to the amouont of ships 5 ships: 50

TIME_PER_TURN =  15 # in seconds

# Ship configurations
SHIPS = {
    "Carrier": 5,
    "Battleship": 4,
    "Cruiser": 31,
    "Submarine": 32,
    "Destroyer": 2
}
SHIPS_SIZES = {
    "Carrier": 5,
    "Battleship": 4,
    "Cruiser": 3,
    "Submarine": 3,
    "Destroyer": 2
}

# Load Horizontal and Vertical ship images
SHIP_IMAGES = {
    "horizontal": {
        "Destroyer": pygame.image.load(os.path.join("assets", "img", "ships","destroyer_h.png")),
        "Submarine" : pygame.image.load(os.path.join("assets", "img", "ships", "submarine_h.png")),
        "Cruiser" : pygame.image.load(os.path.join("assets", "img", "ships", "cruiser_h.png")),
        "Battleship": pygame.image.load(os.path.join("assets", "img", "ships", "battleship_h.png")),
        "Carrier": pygame.image.load(os.path.join("assets", "img", "ships", "carrier_h.png"))
    },
    "vertical": {
        "Destroyer": pygame.image.load(os.path.join("assets", "img", "ships","destroyer_v.png")),
        "Submarine" : pygame.image.load(os.path.join("assets", "img", "ships", "submarine_v.png")),
        "Cruiser" : pygame.image.load(os.path.join("assets", "img", "ships", "cruiser_v.png")),
        "Battleship": pygame.image.load(os.path.join("assets", "img", "ships", "battleship_v.png")),
        "Carrier": pygame.image.load(os.path.join("assets", "img", "ships", "carrier_v.png"))
    }
}

# Arrow images
ARROWS = {
    "red": pygame.image.load(os.path.join("assets", "img", "red arrow.png")),
    "blue": pygame.image.load(os.path.join("assets", "img", "blue arrow.png"))
}

# GRID starting positions
GRID_LEFT_TOP_RED = (50, 70)
GRID_LEFT_TOP_BLUE = (850, 70)
