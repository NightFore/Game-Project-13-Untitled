import pygame
import random
from pygame.locals import *
from os import path

from Camera import *
from ScaledGame import *

from Class import *
from Function import *
from Settings import *
from Menu import *


def init_main(game):
    game.main_dict = MAIN_DICT
    game.data_dict = game.main_dict["main"]
    game.play_width = game.data_dict["play_width"]
    game.play_height = game.data_dict["play_height"]
    game.block_size = game.data_dict["block_size"]
    game.block_border_size = game.data_dict["block_border_size"]
    game.fall_speed = game.data_dict["fall_speed"]

    game.grid = create_grid({})
    game.grid_pos = ((screen_size[0]-game.play_width)/2, screen_size[1]-game.play_height)
    game.block_surface = pygame.Surface(game.block_size)
    game.block_surface_rect = (game.block_border_size[0], game.block_border_size[1], game.block_size[0] - 2*game.block_border_size[0], game.block_size[1] - 2*game.block_border_size[1])

    game.tetrominoes = pygame.sprite.Group()
    game.test_1 = Tetromino(game, game.main_dict, game.tetrominoes, data="tetromino", item=get_shape(game))

def create_grid(locked_pos={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                c = locked_pos[(j, i)]
                grid[i][j] = c
    return grid

def draw_grid(game):
    pygame.draw.rect(game.gameDisplay, (0, 0, 0), (game.grid_pos[0], game.grid_pos[1], game.play_width, game.play_height))

    for i in range(len(game.grid)):
        for j in range(len(game.grid[i])):
            dx, dy = j*game.block_size[0], i*game.block_size[1]
            game.block_surface = init_surface(game.block_surface, game.block_surface_rect, game.grid[i][j], (150, 150, 150))
            game.gameDisplay.blit(game.block_surface, (game.grid_pos[0] + dx, game.grid_pos[1] + dy))

def next_piece(game):
    clear_line(game)
    game.test_1 = Tetromino(game, game.main_dict, game.tetrominoes, data="tetromino", item=get_shape(game))

def clear_line(game):
    cleared_lines = []
    for i in range(len(game.grid)):
        clear = True
        for j in range(len(game.grid[i])):
            if game.grid[i][j] == (0, 0, 0):
                clear = False
        if clear:
            cleared_lines.append(i)

    if clear:
        for i in cleared_lines:
            for j in range(len(game.grid[i])):
                game.grid[i][j] = (0, 0, 0)

        for i in range(max(cleared_lines), 1, -1):
            print(i)
            for j in range(len(game.grid[i])):
                game.grid[i][j] = game.grid[i-1][j]
        print(cleared_lines)


def get_shape(game):
    return random.choice(list(game.main_dict["shape"]))

MAIN_DICT = {
    "main": {
        "play_width": 300, "play_height": 600, "block_size": (30, 30), "block_border_size": (2, 2), "fall_speed": 2000
    },

    "tetromino": {
        "settings": {"pos": (4, 0), "align": "nw", "size": (30, 30), "border_size": (6, 6)},
        "I": {"color": (1, 240, 241), "border_color": (0, 222, 221)},
        "J": {"color": (1, 1, 238), "border_color": (6, 8, 165)},
        "L": {"color": (240, 160, 0), "border_color": (220, 145, 0)},
        "O": {"color": (240, 241, 0), "border_color": (213, 213, 0)},
        "S": {"color": (0, 241, 0), "border_color": (0, 218, 0)},
        "T": {"color": (160, 0, 243), "border_color": (147, 0, 219)},
        "Z": {"color": (238, 2, 0), "border_color": (215, 0, 0)},
    },

    "shape": {
        "S": [['.....',
               '......',
               '..00..',
               '.00...',
               '.....'],
              ['.....',
               '..0..',
               '..00.',
               '...0.',
               '.....']],
        "Z": [['.....',
               '.....',
               '.00..',
               '..00.',
               '.....'],
              ['.....',
               '..0..',
               '.00..',
               '.0...',
               '.....']],
        "I": [['..0..',
               '..0..',
               '..0..',
               '..0..',
               '.....'],
              ['.....',
               '0000.',
               '.....',
               '.....',
               '.....']],
        "O": [['.....',
               '.....',
               '.00..',
               '.00..',
               '.....']],
        "J": [['.....',
               '.0...',
               '.000.',
               '.....',
               '.....'],
              ['.....',
               '..00.',
               '..0..',
               '..0..',
               '.....'],
              ['.....',
               '.....',
               '.000.',
               '...0.',
               '.....'],
              ['.....',
               '..0..',
               '..0..',
               '.00..',
               '.....']],
        "L": [['.....',
               '...0.',
               '.000.',
               '.....',
               '.....'],
              ['.....',
               '..0..',
               '..0..',
               '..00.',
               '.....'],
              ['.....',
               '.....',
               '.000.',
               '.0...',
               '.....'],
              ['.....',
               '.00..',
               '..0..',
               '..0..',
               '.....']],
        "T": [['.....',
               '..0..',
               '.000.',
               '.....',
               '.....'],
              ['.....',
               '..0..',
               '..00.',
               '..0..',
               '.....'],
              ['.....',
               '.....',
               '.000.',
               '..0..',
               '.....'],
              ['.....',
               '..0..',
               '.00..',
               '..0..',
               '.....']]
    }
}






class Tetromino(pygame.sprite.Sprite):
    def __init__(self, game, dict, group=None, data=None, item=None, parent=None, variable=None, action=None):
        # Initialization -------------- #
        init_sprite_2(self, game, dict, group, data, item, parent, variable, action)
        self.surface = init_surface(self.surface, self.surface_rect, self.color, self.border_color)
        self.init()

    def init(self):
        self.block_pos = [int(self.pos[0]), int(self.pos[1])]
        self.pos.x = self.game.grid_pos[0] + self.block_pos[0]*self.game.block_size[0]
        self.pos.y = self.game.grid_pos[1] + self.block_pos[1]*self.game.block_size[1]
        self.update_move(0, 0)
        self.last_fall = pygame.time.get_ticks()

        print(self.item)

    def draw(self):
        self.game.gameDisplay.blit(self.surface, self.rect)

    def get_keys(self):
        for event in self.game.event:
            if event.type == pygame.KEYDOWN:
                dx, dy = 0, 0
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    dy = -1
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    dy = 1
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    dx = -1
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    dx = 1
                self.update_move(dx, dy)

    def update_move(self, dx, dy):
        if self.verify_move(dx, dy):
            update_move(self, dx*self.game.block_size[0], dy*self.game.block_size[1])

    def verify_move(self, dx=0, dy=0):
        move = False
        if self.block_pos[1] + dy >= 20 or self.game.grid[self.block_pos[1]+dy][self.block_pos[0]] != (0, 0, 0):
            self.game.grid[self.block_pos[1]][self.block_pos[0]] = self.color
            next_piece(self.game)
            self.kill()
        elif 0 <= self.block_pos[0] + dx <= 9 and 0 <= self.block_pos[1] + dy < 20 and self.game.grid[self.block_pos[1]][self.block_pos[0]+dx] == (0, 0, 0):
            self.block_pos[0] += dx
            self.block_pos[1] += dy
            move = True
        return move

    def update(self):
        self.get_keys()

        if pygame.time.get_ticks() - self.last_fall >= self.game.fall_speed:
            self.update_move(0, 1)
            self.last_fall = pygame.time.get_ticks()
