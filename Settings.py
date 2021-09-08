import pygame
from os import path

"""
    Settings
"""
project_title = "Untitled"
screen_size = WIDTH, HEIGHT = 1280, 720
FPS = 60
default_volume = 5
default_sound_volume = 75

"""
    Colors
"""
BLACK = 0, 0, 0
WHITE = 255, 255, 255

RED = 255, 0, 0
GREEN = 0, 255, 0
GREEN_2 = 0, 200, 0
GREEN_3 = 0, 145, 0
BLUE = 0, 0, 255

YELLOW = 255, 255, 0
MAGENTA = 255, 0, 255
CYAN = 0, 255, 255

LIGHT_SKY_BLUE = 140, 205, 245
DARK_SKY_BLUE = 15, 160, 240

"""
    Game Settings
"""
GAME_DICT = {
    "background": {
        "background_image": None,
        "background_color": DARK_SKY_BLUE,
    },

    "HUD": {
    },

    "font": {
    },

    "color": {
    }
}

MUSIC_DICT = {
    "main_menu": "Tetris_theme.ogg"
}

FONT_DICT = {
}

UI_DICT = {
}

BUTTON_DICT = {
}