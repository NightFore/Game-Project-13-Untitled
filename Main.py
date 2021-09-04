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

    if cleared_lines:
        for i in range(max(cleared_lines), 0, -1):
            for j in range(len(game.grid[i])):
                game.grid[i][j] = game.grid[i-1][j]
        for j in range(len(game.grid[0])):
            game.grid[0][j] = (0, 0, 0)


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
        self.block_pos = [[int(self.pos[0]), int(self.pos[1])]]
        self.pos.x = self.game.grid_pos[0] + self.pos[0]*self.game.block_size[0]
        self.pos.y = self.game.grid_pos[1] + self.pos[1]*self.game.block_size[1]
        self.rot = 0
        self.last_fall = pygame.time.get_ticks()
        self.update_move()
        self.update_shape()
        print(self.item)

    def draw(self):
        for block in self.block_pos:
            rect = self.rect.copy()
            rect.x = self.game.grid_pos[0] + block[0]*self.game.block_size[0]
            rect.y = self.game.grid_pos[1] + block[1]*self.game.block_size[1]
            self.game.gameDisplay.blit(self.surface, rect)

    def get_keys(self):
        for event in self.game.event:
            if event.type == pygame.KEYDOWN:
                dx, dy, rot = 0, 0, 0
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    rot = +1
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    dy = 1
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    dx = -1
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    dx = 1
                self.update_move(dx, dy, rot)

    def update_shape(self, rot=0):
        index = (self.rot + rot) % len(self.game.main_dict["shape"][self.item])
        shape = self.game.main_dict["shape"][self.item][index]
        block_pos = []
        offset_x, offset_y = None, None
        for y, line in enumerate(shape):
            for x, column in enumerate(line):
                if column == "0":
                    if offset_x is None or offset_y is None:
                        offset_x, offset_y = x, y
                    block_pos.append([self.block_pos[0][0] + x-offset_x, self.block_pos[0][1] + y-offset_y])

        verify = True
        for block in block_pos:
            if not(0 <= block[0] <= 9 and self.game.grid[block[1]][block[0]] == (0, 0, 0)):
                verify = False
        if verify:
            self.block_pos = block_pos
            self.rot = index

    def update_move(self, dx=0, dy=0, rot=0):
        move = True
        kill = False
        for block in self.block_pos:
            if block[1] + dy >= 20 or self.game.grid[block[1]+dy][block[0]] != (0, 0, 0):
                kill = True
            elif not(0 <= block[0] + dx <= 9 and self.game.grid[block[1]][block[0]+dx] == (0, 0, 0)):
                move = False
        if kill:
            for block in self.block_pos:
                self.game.grid[block[1]][block[0]] = self.color
            next_piece(self.game)
            self.kill()
        elif move:
            for block in self.block_pos:
                block[0] += dx
                block[1] += dy
        self.update_shape(rot)

    def update(self):
        self.get_keys()

        if pygame.time.get_ticks() - self.last_fall >= self.game.fall_speed:
            self.update_move(0, 1)
            self.last_fall = pygame.time.get_ticks()
