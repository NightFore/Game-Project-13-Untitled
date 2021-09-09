import pygame
import random
from pygame.locals import *
from os import path

from Camera import *
from ScaledGame import *

from Class import *
from Function import *
from Settings import *


def init_main(game):
    game.shape_dict = game.main_dict["shape"]
    game.play_width = game.game_dict["play_width"]
    game.play_height = game.game_dict["play_height"]
    game.block_size = game.game_dict["block_size"]
    game.block_border_size = game.game_dict["block_border_size"]
    game.fall_speed = game.game_dict["fall_speed"]

    game.grid = create_grid({})
    game.grid_pos = ((screen_size[0]-game.play_width)/2, screen_size[1]-game.play_height)
    game.block_surface = pygame.Surface(game.block_size)
    game.block_surface_rect = (game.block_border_size[0], game.block_border_size[1], game.block_size[0] - 2*game.block_border_size[0], game.block_size[1] - 2*game.block_border_size[1])

    game.tetrominoes = pygame.sprite.Group()

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
            for j in range(len(game.grid[i])):
                game.grid[i][j] = game.grid[i-len(cleared_lines)][j]
        for i in range(len(cleared_lines)):
            for j in range(len(game.grid[0])):
                game.grid[i][j] = (0, 0, 0)
        if len(cleared_lines) == 1:
            pygame.mixer.Sound.play(game.sound_effects["single"])
        if len(cleared_lines) == 2:
            pygame.mixer.Sound.play(game.sound_effects["double"])
        if len(cleared_lines) == 3:
            pygame.mixer.Sound.play(game.sound_effects["triple"])
        if len(cleared_lines) == 4:
            pygame.mixer.Sound.play(game.sound_effects["tetris"])

def new_piece(game, move_tap=False, last_dir=0, hard_drop_check=True):
    Player = Tetromino(game, game.main_dict, game.tetrominoes, data="tetromino", item=get_shape(game))
    Player.move_tap = move_tap
    Player.last_dir = last_dir
    Player.hard_drop_check = hard_drop_check

def get_shape(game):
    return random.choice(list(game.shape_dict))

class Tetromino(pygame.sprite.Sprite):
    def __init__(self, game, dict, group=None, data=None, item=None, parent=None, variable=None, action=None):
        # Initialization -------------- #
        init_sprite_2(self, game, dict, group, data, item, parent, variable, action)
        self.surface = init_surface(self.surface, self.surface_rect, self.color, self.border_color)
        self.init()

    def init(self):
        self.move_tap = False
        self.last_dir = 0
        self.init_das_delay = 16
        self.das_delay = 6
        self.last_das = self.das_delay
        self.drop_delay = 2
        self.last_drop = self.drop_delay
        self.fall_delay = 30
        self.last_fall = self.fall_delay
        self.hard_drop_check = True
        self.drop_check = True

        self.shapes = self.game.shape_dict[self.item]
        self.block_pos = [[int(self.pos[0]), int(self.pos[1])]]
        self.block_rot = -1
        self.block_center = 0
        self.rot_check = True
        self.offset = -2, -2
        self.update_move(rot=1)
        print("Shape: %s" % self.item)

    def draw(self):
        for block in self.block_pos:
            rect = self.rect.copy()
            rect.x = self.game.grid_pos[0] + block[0]*self.game.block_size[0]
            rect.y = self.game.grid_pos[1] + block[1]*self.game.block_size[1]
            self.game.gameDisplay.blit(self.surface, rect)

    def get_keys(self):
        dx, dy, rot = 0, 0, 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            rot = self.rot_check
        else:
            self.rot_check = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s] and dx == 0:
            dy = 1
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and (self.last_dir == -1 or self.last_dir == 0):
            dx = -1
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and (self.last_dir == 1 or self.last_dir == 0):
            dx = 1
        if keys[pygame.K_SPACE]:
            if self.hard_drop_check:
                self.hard_drop_check = False
                for _ in range(20):
                    if self.drop_check:
                        self.last_drop = 0
                        self.update_move(dy=1)
        else:
            self.hard_drop_check = True

        self.last_das -= 1
        self.last_drop -= 1
        self.last_fall -= 1
        if self.last_fall <= 0:
            self.last_fall = self.fall_delay
            self.last_drop = 0
            dy = 1
        if dx == 0:
            self.move_tap = False
            self.last_dir = 0
        self.update_move(dx, dy, rot)

    def update_move(self, dx=0, dy=0, rot=0):
        move_check, lock_check, rot_check = True, True, True
        block_pos = []
        block_rot = (self.block_rot + rot) % len(self.shapes)
        block_center = 0
        shape = self.shapes[block_rot]
        for y, line in enumerate(shape):
            for x, column in enumerate(line):
                if column == "0" or column == "X":
                    block_pos.append([self.block_pos[self.block_center][0] + self.offset[0] + x + dx, self.block_pos[self.block_center][1] + self.offset[1] + y + dy])
                if column == "X":
                    block_center = len(block_pos) - 1

        for block in block_pos:
            if not(0 <= block[0] <= 9 and block[1] <= 19) or 0 <= block[1] and self.game.grid[block[1]][block[0]] != (0, 0, 0):
                move_check, lock_check, rot_check = not(dx != 0), not(dy != 0), not(rot != 0)

        if not lock_check and (not move_check or not rot_check):
            self.update_move(dy=dy)
        elif not lock_check:
            pygame.mixer.Sound.play(self.game.sound_effects["lock"])
            for block in self.block_pos:
                self.game.grid[block[1]][block[0]] = self.color
            clear_line(self.game)
            new_piece(self.game, self.move_tap, self.last_dir, self.hard_drop_check)
            self.drop_check = False
            self.kill()
        elif move_check and rot_check:
            if dx != 0 and dy != 0:
                self.update_move(dy=dy)
                self.update_move(dx=dx)
            else:
                if dx != 0:
                    if not self.move_tap or self.last_dir != dx:
                        pygame.mixer.Sound.play(self.game.sound_effects["move_tap"])
                        self.block_pos = block_pos
                        self.last_das = self.init_das_delay
                        self.last_dir = dx
                        self.move_tap = True
                    elif self.last_das <= 0:
                        pygame.mixer.Sound.play(self.game.sound_effects["move_das"])
                        self.block_pos = block_pos
                        self.last_das = self.das_delay
                if dy != 0:
                    if self.last_drop <= 0:
                        self.block_pos = block_pos
                        self.last_drop = self.drop_delay
                        self.last_fall = self.fall_delay
            if rot != 0:
                pygame.mixer.Sound.play(self.game.sound_effects["rotate"])
                self.block_pos = block_pos
                self.block_center = block_center
                self.block_rot = block_rot
                self.rot_check = False

    def update(self):
        self.get_keys()



def init_menu(game, menu, clear=True):
    menu_dict = game.main_dict["menu"][menu]
    if clear:
        clear_menu(game)

    game.update_music(game.music_dict[menu_dict["music"]])
    game.update_background(game.background_dict[menu_dict["background"]])

def clear_menu(game):
    for sprite in game.all_sprites:
        sprite.kill()

def main_menu(game, menu):
    init_menu(game, menu)
    new_piece(game)

def pause_menu(game, menu):
    game.paused = not game.paused

MAIN_DICT = {
    "game": {
        "play_width": 300, "play_height": 600, "block_size": (30, 30), "block_border_size": (2, 2), "fall_speed": 2000
    },
    "menu": {
        "main_menu": {
            "call": main_menu,
            "background": "default",
            "music": "default",
            "ui": {},
            "button": {},
        },
        "pause_menu": {
            "call": pause_menu,
        },
    },
    "background": {
        "default": {
            "color": DARK_SKY_BLUE,
            "image": None,
        },
    },
    "music": {
        "default": "Tetris_theme.ogg",
    },
    "sound": {
        "move_tap": "se_maoudamashii_system_14.ogg",
        "move_das": "se_maoudamashii_system_21.ogg",
        "rotate": "se_maoudamashii_system_17.ogg",
        "collide": "se_maoudamashii_noise_16.ogg",
        "lock": "se_maoudamashii_system_14.ogg",  ### Change se_maoudamashii_fight_07
        "single": "se_maoudamashii_retro_04.ogg",
        "double": "se_maoudamashii_retro_04.ogg",  # se_maoudamashii_retro_03
        "triple": "se_maoudamashii_retro_04.ogg",  # se_maoudamashii_retro_07
        "tetris": "se_maoudamashii_retro_04.ogg",  # se_maoudamashii_retro_14
        "level_up": "se_maoudamashii_retro_15.ogg",
        "pause": "se_maoudamashii_retro_08.ogg",
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
    },
}
