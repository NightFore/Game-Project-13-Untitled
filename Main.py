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
    game.se_dict = game.main_dict["sound"]
    game.shape_dict = game.main_dict["shape"]

    game.play_width = game.data_dict["play_width"]
    game.play_height = game.data_dict["play_height"]
    game.block_size = game.data_dict["block_size"]
    game.block_border_size = game.data_dict["block_border_size"]
    game.fall_speed = game.data_dict["fall_speed"]

    game.sounds_effects = {}
    for sounds in game.se_dict:
        game.sounds_effects[sounds] = pygame.mixer.Sound(path.join(game.se_folder, game.se_dict[sounds]))

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

def next_piece(sprite, game):
    clear_line(game)
    sprite.kill()
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
        for i in range(max(cleared_lines), len(cleared_lines)-1, -1):
            print(i)
            for j in range(len(game.grid[i])):
                game.grid[i][j] = game.grid[i-len(cleared_lines)][j]
        for i in range(len(cleared_lines)):
            for j in range(len(game.grid[0])):
                game.grid[i][j] = (0, 0, 0)
        if len(cleared_lines) == 1:
            pygame.mixer.Sound.play(game.sounds_effects["single"])
        if len(cleared_lines) == 2:
            pygame.mixer.Sound.play(game.sounds_effects["double"])
        if len(cleared_lines) == 3:
            pygame.mixer.Sound.play(game.sounds_effects["triple"])
        if len(cleared_lines) == 4:
            pygame.mixer.Sound.play(game.sounds_effects["tetris"])

def get_shape(game):
    return random.choice(list(game.shape_dict))

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

    "sound": {
        "move_tap": "se_maoudamashii_system_14.ogg",
        "move_das": "se_maoudamashii_system_21.ogg",
        "rotate": "se_maoudamashii_system_17.ogg",
        "collide": "se_maoudamashii_noise_16.ogg",
        "lock": "se_maoudamashii_fight_07.ogg",
        "single": "se_maoudamashii_retro_04.ogg",
        "double": "se_maoudamashii_retro_03.ogg",
        "triple": "se_maoudamashii_retro_07.ogg",
        "tetris": "se_maoudamashii_retro_14.ogg",
        "level_up": "se_maoudamashii_retro_15.ogg",
        "pause": "se_maoudamashii_retro_08.ogg",
    },

    "shape": {
        "S": [['.....',
               '..00..',
               '.0X...',
               '......',
               '.....'],
              ['.....',
               '..0..',
               '..X0.',
               '...0.',
               '.....']],
        "Z": [['.....',
               '.00..',
               '..X0.',
               '.....',
               '.....'],
              ['.....',
               '..0..',
               '.0X..',
               '.0...',
               '.....']],
        "I": [['.....',
               '.....',
               '00X0.',
               '.....',
               '.....'],
              ['..0..',
               '..0..',
               '..X..',
               '..0..',
               '.....']],
        "O": [['.....',
               '..00.',
               '..X0.',
               '.....',
               '.....']],
        "J": [['.....',
               '.0...',
               '.0X0.',
               '.....',
               '.....'],
              ['.....',
               '..00.',
               '..X..',
               '..0..',
               '.....'],
              ['.....',
               '.....',
               '.0X0.',
               '...0.',
               '.....'],
              ['.....',
               '..0..',
               '..X..',
               '.00..',
               '.....']],
        "L": [['.....',
               '...0.',
               '.0X0.',
               '.....',
               '.....'],
              ['.....',
               '..0..',
               '..X..',
               '..00.',
               '.....'],
              ['.....',
               '.....',
               '.0X0.',
               '.0...',
               '.....'],
              ['.....',
               '.00..',
               '..X..',
               '..0..',
               '.....']],
        "T": [['.....',
               '..0..',
               '.0X0.',
               '.....',
               '.....'],
              ['.....',
               '..0..',
               '..X0.',
               '..0..',
               '.....'],
              ['.....',
               '.....',
               '.0X0.',
               '..0..',
               '.....'],
              ['.....',
               '..0..',
               '.0X..',
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
        self.shapes = self.game.shape_dict[self.item]
        self.block_pos = [[int(self.pos[0]), int(self.pos[1])]]
        self.block_rot = 0
        self.block_center = 0
        self.offset = -2, -2
        self.pos.x = self.game.grid_pos[0] + self.pos[0]*self.game.block_size[0]
        self.pos.y = self.game.grid_pos[1] + self.pos[1]*self.game.block_size[1]
        self.last_fall = pygame.time.get_ticks()
        self.update_test_2()
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
                self.update_test_2(dx, dy, rot)

    def update_test(self, dx=0, dy=0, rot=0):
        dx_check, dy_check, rot_check = True, True, True
        for block in self.block_pos:
            if not(0 <= block[0] + dx <= 9 and block[1] + dy <= 19 and self.game.grid[block[1]+dy][block[0]+dx] == (0, 0, 0)):
                dx_check, dy_check = not(dx != 0), not(dy != 0)
        if not dy_check:
            for block in self.block_pos:
                self.game.grid[block[1]][block[0]] = self.color
            next_piece(self, self.game)
        elif dx_check:
            for block in self.block_pos:
                block[0] += dx
                block[1] += dy
            if dy != 0:
                self.last_fall = pygame.time.get_ticks()

        self.update_shape(rot)

    def update_test_2(self, dx=0, dy=0, rot=0):
        dx_check, dy_check, rot_check = True, True, True
        block_pos = []
        for block in self.block_pos:
            block_pos.append(block[:])
        for block in block_pos:
            block[0], block[1] = block[0] + dx, block[1] + dy
            if not(0 <= block[0] <= 9 and block[1] <= 19) or 0 <= block[1] and self.game.grid[block[1]][block[0]] != (0, 0, 0):
                dx_check, dy_check = not(dx != 0), not(dy != 0)
        if not dy_check:
            for block in self.block_pos:
                self.game.grid[block[1]][block[0]] = self.color
            next_piece(self, self.game)
            pygame.mixer.Sound.play(self.game.sounds_effects["lock"])
        elif dx_check:
            self.block_pos = block_pos
            if dx != 0:
                pygame.mixer.Sound.play(self.game.sounds_effects["move_das"])
            if dy != 0:
                self.last_fall = pygame.time.get_ticks()

        block_pos = []
        block_rot = (self.block_rot + rot) % len(self.shapes)
        block_center = 0
        shape = self.shapes[block_rot]
        for y, line in enumerate(shape):
            for x, column in enumerate(line):
                if column == "0" or column == "X":
                    block_pos.append([self.block_pos[self.block_center][0] + self.offset[0] + x, self.block_pos[self.block_center][1] + self.offset[1] + y])
                if column == "X":
                    block_center = len(block_pos) - 1

        for block in block_pos:
            if not(0 <= block[0] <= 9) or block[1] >= 20 or block[1] >= 0 and self.game.grid[block[1]][block[0]] != (0, 0, 0):
                rot_check = False
        if rot_check:
            self.block_pos = block_pos
            self.block_center = block_center
            self.block_rot = block_rot
            if rot != 0:
                pygame.mixer.Sound.play(self.game.sounds_effects["rotate"])


    def update_move(self, dx=0, dy=0, rot=0):
        kill = False
        move = True
        for block in self.block_pos:
            if block[1] + dy >= 20 or block[1] >= 0 and self.game.grid[block[1]+dy][block[0]] != (0, 0, 0):
                kill = True
            elif not(0 <= block[0] + dx <= 9) or block[1] >= 0 and self.game.grid[block[1]][block[0]+dx] != (0, 0, 0):
                move = False
        dx_check, dy_check, rot_check = True, True, True
        for block in self.block_pos:
            if not(0 <= block[0] + dx <= 9 and block[1] + dy <= 19 and self.game.grid[block[1]+dy][block[0]+dx] == (0, 0, 0)):
                dy_check = not(dy != 0)
                dx_check = not(dx != 0)
        print(dx_check == move and not dy_check == kill)
        move, kill = dx_check, not dy_check
        if kill:
            for block in self.block_pos:
                self.game.grid[block[1]][block[0]] = self.color
            next_piece(self, self.game)
        elif move:
            for block in self.block_pos:
                block[0] += dx
                block[1] += dy
            if dy != 0:
                self.last_fall = pygame.time.get_ticks()

        self.update_shape(rot)

    def update_shape(self, rot=0):
        block_pos = []
        block_rot = (self.block_rot + rot) % len(self.shapes)
        block_center = 0
        shape = self.shapes[block_rot]
        for y, line in enumerate(shape):
            for x, column in enumerate(line):
                if column == "0" or column == "X":
                    block_pos.append([self.block_pos[self.block_center][0] + self.offset[0] + x, self.block_pos[self.block_center][1] + self.offset[1] + y])
                if column == "X":
                    block_center = len(block_pos) - 1

        verify = True
        for block in block_pos:
            if not(0 <= block[0] <= 9) or block[1] >= 20 or block[1] >= 0 and self.game.grid[block[1]][block[0]] != (0, 0, 0):
                verify = False
        if verify:
            self.block_pos = block_pos
            self.block_center = block_center
            self.block_rot = block_rot

        pygame.mixer.Sound.play(self.game.sounds_effects["move_das"])

    def update(self):
        self.get_keys()

        if pygame.time.get_ticks() - self.last_fall >= self.game.fall_speed:
            self.update_test_2(0, 1)
            self.last_fall = pygame.time.get_ticks()
