import pygame
import random
from pygame.locals import *
from os import path

from Camera import *
from ScaledGame import *

from Class import *
from Function import *
from Settings import *


class Game:
    def __init__(self, main):
        self.main = main
        self.tetrominoes = pygame.sprite.Group()
        self.game_dict = self.main.main_dict["game"]
        self.settings_dict = self.game_dict["settings"]
        self.shape_dict = self.game_dict["shape"]
        self.play_width = self.settings_dict["play_width"]
        self.play_height = self.settings_dict["play_height"]
        self.block_size = self.settings_dict["block_size"]
        self.block_border_size = self.settings_dict["block_border_size"]
        self.block_surface = pygame.Surface(self.block_size)
        self.block_surface_rect = (self.block_border_size[0], self.block_border_size[1], self.block_size[0] - 2 * self.block_border_size[0], self.block_size[1] - 2 * self.block_border_size[1])

    def new_game(self):
        self.line_count = 0
        self.start_level = 0
        self.level = self.start_level
        self.score = 0
        self.grid = create_grid()
        self.grid_pos = ((screen_size[0] - self.play_width) / 2, screen_size[1] - self.play_height)
        self.Next_Piece = Next_Piece(self.main, self.game_dict, self.tetrominoes, data="next_piece", item=self.get_shape())
        self.new_piece()

    def new_piece(self, move_tap=False, last_dir=0, hard_drop_check=True):
        for tetromino in self.tetrominoes:
            tetromino.kill()
        self.Player = Tetromino(self.main, self.game_dict, self.tetrominoes, data="tetromino", item=self.Next_Piece.item)
        self.Next_Piece = Next_Piece(self.main, self.game_dict, self.tetrominoes, data="next_piece", item=self.get_shape())
        self.Player.move_tap = move_tap
        self.Player.last_dir = last_dir
        self.Player.hard_drop_check = hard_drop_check

    def get_shape(self):
        return random.choice(list(self.shape_dict))

    def clear_line(self):
        cleared_lines = []
        for i in range(len(self.grid)):
            clear = True
            for j in range(len(self.grid[i])):
                if self.grid[i][j] == (0, 0, 0):
                    clear = False
            if clear:
                cleared_lines.append(i)

        if cleared_lines:
            self.line_count += len(cleared_lines)
            if self.line_count >= min((self.level + 1) * 10, 100 + (self.level - min(15, self.start_level)) * 10):
                self.level = min(self.level + 1, len(self.game_dict["level"]))

            if len(cleared_lines) == 1:
                pygame.mixer.Sound.play(self.main.sound_effects["single"])
                self.score += 40 * (self.level + 1)
            if len(cleared_lines) == 2:
                pygame.mixer.Sound.play(self.main.sound_effects["double"])
                self.score += 100 * (self.level + 1)
            if len(cleared_lines) == 3:
                pygame.mixer.Sound.play(self.main.sound_effects["triple"])
                self.score += 300 * (self.level + 1)
            if len(cleared_lines) == 4:
                pygame.mixer.Sound.play(self.main.sound_effects["tetris"])
                self.score += 1200 * (self.level + 1)

            for i in range(max(cleared_lines), len(cleared_lines) - 1, -1):
                for j in range(len(self.grid[i])):
                    self.grid[i][j] = self.grid[i - len(cleared_lines)][j]
            for i in range(len(cleared_lines)):
                for j in range(len(self.grid[0])):
                    self.grid[i][j] = (0, 0, 0)

    def draw_grid(self):
        pygame.draw.rect(self.main.gameDisplay, (0, 0, 0), (self.grid_pos[0], self.grid_pos[1], self.play_width, self.play_height))

        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                dx, dy = j * self.block_size[0], i * self.block_size[1]
                self.block_surface = init_surface(self.block_surface, self.block_surface_rect, self.grid[i][j], (150, 150, 150))
                self.main.gameDisplay.blit(self.block_surface, (self.grid_pos[0] + dx, self.grid_pos[1] + dy))

    def draw(self):
        self.draw_grid()
        self.main.draw_text("Score: %d" % self.score, self.main.font_dict["LiberationSerif"], WHITE, (160, 520), align="center")
        self.main.draw_text("Lines: %d" % self.line_count, self.main.font_dict["LiberationSerif"], WHITE, (160, 590), align="center")
        self.main.draw_text("Level: %d" % self.level, self.main.font_dict["LiberationSerif"], WHITE, (160, 660), align="center")

    def update(self):
        pass

class Tetromino(pygame.sprite.Sprite):
    def __init__(self, main, dict, group=None, data=None, item=None, parent=None, variable=None, action=None):
        # Initialization -------------- #
        init_sprite_2(self, main, dict, group, data, item, parent, variable, action)
        self.surface = init_surface(self.surface, self.surface_rect, self.color, self.border_color)
        self.init()

    def init(self):
        # Settings
        self.settings = self.game.settings_dict
        self.shapes = self.game.shape_dict[self.item]
        self.block_pos = [[int(self.pos[0]), int(self.pos[1])]]
        self.offset = -2, -2

        # Ghost Piece
        self.ghost_pos = self.block_pos
        self.ghost_surface = pygame.Surface.copy(self.surface)
        self.ghost_surface.set_alpha(150)

        # dx
        self.last_dir = 0
        self.tap_delay = self.settings["tap_delay"]
        self.das_delay = self.settings["das_delay"]
        self.last_das = self.das_delay
        self.tap_check = False

        # dy
        self.drop_delay = self.settings["drop_delay"]
        self.last_drop = self.drop_delay
        self.fall_delay = self.game.game_dict["level"][self.game.level]
        self.last_fall = self.fall_delay
        self.hard_drop_check = True
        self.lock_check = True

        # rot
        self.block_rot = -1
        self.block_center = 0
        self.rot_check = True

        # Initializing shape
        self.update_move(rot=1)
        self.update_move(ghost=True)

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
                    if self.lock_check:
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
            self.tap_check = False
            self.last_dir = 0
        self.update_move(rot=rot)
        self.update_move(dx=dx)
        self.update_move(dy=dy)

        self.ghost_pos = self.block_pos
        for _ in range(20):
            self.update_move(dy=1, pos=self.ghost_pos, ghost=True)

    def update_move(self, dx=0, dy=0, rot=0, pos=None, ghost=False):
        move, move_check, lock_check, rot_check = False, True, False, True
        if pos is None:
            pos = self.block_pos
        block_pos = []
        block_rot = (self.block_rot + rot) % len(self.shapes)
        block_center = 0
        shape = self.shapes[block_rot]
        for y, line in enumerate(shape):
            for x, column in enumerate(line):
                if column == "0" or column == "X":
                    block_pos.append([pos[self.block_center][0] + self.offset[0] + x + dx, pos[self.block_center][1] + self.offset[1] + y + dy])
                if column == "X":
                    block_center = len(block_pos) - 1

        for block in block_pos:
            if not (0 <= block[0] <= 9 and block[1] <= 19) or 0 <= block[1] and self.game.grid[block[1]][block[0]] != (0, 0, 0):
                move_check, lock_check, rot_check = not (dx != 0), dy != 0, not (rot != 0)

        if lock_check and (not move_check or not rot_check):
            self.update_move(dy=dy)
        elif lock_check:
            if not ghost:
                pygame.mixer.Sound.play(self.main.sound_effects["lock"])
                self.lock_check = False
                for block in pos:
                    self.game.grid[block[1]][block[0]] = self.color
                self.game.clear_line()
                self.game.new_piece(self.tap_check, self.last_dir, self.hard_drop_check)
        elif move_check and rot_check:
            if dx != 0:
                if not self.tap_check or self.last_dir != dx:
                    pygame.mixer.Sound.play(self.main.sound_effects["tap"])
                    move = True
                    self.last_das = self.tap_delay
                    self.last_dir = dx
                    self.tap_check = True
                elif self.last_das <= 0:
                    pygame.mixer.Sound.play(self.main.sound_effects["das"])
                    move = True
                    self.last_das = self.das_delay
            if dy != 0 and (self.last_drop <= 0 or ghost):
                move = True
                self.last_drop = self.drop_delay
                self.last_fall = self.fall_delay
            if rot != 0:
                pygame.mixer.Sound.play(self.main.sound_effects["rotate"])
                move = True
                self.block_center = block_center
                self.block_rot = block_rot
                self.rot_check = False
        if move:
            if not ghost:
                self.block_pos = block_pos
            else:
                self.ghost_pos = block_pos

    def draw(self):
        for block in self.block_pos:
            rect = self.rect.copy()
            rect.x = self.game.grid_pos[0] + block[0] * self.game.block_size[0]
            rect.y = self.game.grid_pos[1] + block[1] * self.game.block_size[1]
            self.main.gameDisplay.blit(self.surface, rect)

        for block in self.ghost_pos:
            rect = self.rect.copy()
            rect.x = self.game.grid_pos[0] + block[0] * self.game.block_size[0]
            rect.y = self.game.grid_pos[1] + block[1] * self.game.block_size[1]
            self.main.gameDisplay.blit(self.ghost_surface, rect)

    def update(self):
        self.get_keys()

class Next_Piece(pygame.sprite.Sprite):
    def __init__(self, main, dict, group=None, data=None, item=None, parent=None, variable=None, action=None):
        # Initialization -------------- #
        init_sprite_2(self, main, dict, group, data, item, parent, variable, action)
        self.surface = init_surface(self.surface, self.surface_rect, self.color, self.border_color)
        self.init()

    def init(self):
        self.shape = self.game.shape_dict[self.item][0]
        len_x, len_y = len(self.shape[0]), len(self.shape)
        x_min, x_max = len_x, 0
        y_min, y_max = len_y, 0

        self.block_pos = []
        for y, line in enumerate(self.shape):
            for x, column in enumerate(line):
                if column == "0" or column == "X":
                    self.block_pos.append([x, y])
                    x_min, x_max = min(x_min, x), max(x_max, x)
                    y_min, y_max = min(y_min, y), max(y_max, y)
        width = (abs(x_min - x_max) + 1) * self.game.block_size[0]
        height = (abs(y_min - y_max) + 1) * self.game.block_size[1]

        block_surface = self.surface
        self.surface = pygame.Surface((width, height))
        self.rect = self.main.align_rect(self.surface, int(self.pos[0]), int(self.pos[1] + self.game.block_size[1]/2), self.center)
        for block in self.block_pos:
            rect = self.rect.copy()
            rect.x = (block[0]-x_min) * self.game.block_size[0]
            rect.y = (block[1]-y_min) * self.game.block_size[1]
            self.surface.blit(block_surface, rect)

        box_width, box_height = len_x * self.game.block_size[0], len_y * self.game.block_size[1]
        self.box_surface = pygame.Surface((box_width, box_height))
        self.box_rect = self.main.align_rect(self.box_surface, int(self.pos[0]), int(self.pos[1]), self.center)
        self.box_surface_rect = (6, 6, box_width - 2*6, box_height - 2*6)
        self.box_surface = init_surface(self.box_surface, self.box_surface_rect, (0, 0, 0), (150, 150, 150))

    def draw(self):
        self.main.gameDisplay.blit(self.box_surface, self.box_rect)
        self.main.gameDisplay.blit(self.surface, self.rect)
        self.main.draw_text("NEXT", self.main.font_dict["LiberationSerif"], WHITE, (self.pos[0], self.pos[1] - self.game.block_size[1]), align="s")

    def update(self):
        pass


def init_menu(main, menu, clear=True):
    menu_dict = main.main_dict["menu"][menu]
    if clear:
        clear_menu(main)

    main.update_music(main.music_dict[menu_dict["music"]])
    main.update_background(main.background_dict[menu_dict["background"]])

    for button in main.button_dict[menu]:
        Button(main, main.button_dict, main.buttons, data=menu, item=button)

def clear_menu(main):
    for sprite in main.all_sprites:
        sprite.kill()

def main_menu(main, menu):
    init_menu(main, menu)
    main.game.new_game()

def pause_menu(main, menu):
    main.paused = not main.paused

MAIN_DICT = {
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
        "tap": "se_maoudamashii_system_14.ogg",
        "das": "se_maoudamashii_system_21.ogg",
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
    "font": {
        "LiberationSerif": {"ttf": "LiberationSerif-Regular.ttf", "size": 40}
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
    "button": {
        "type": {
            "type_1": {
                "align": "nw", "size": (280, 50),
                "border": True, "border_size": (5, 5), "border_color": BLACK,
                "font": "LiberationSerif", "font_color": WHITE,
                "inactive_color": LIGHT_SKY_BLUE, "active_color": DARK_SKY_BLUE,
                "sound_active": None, "sound_action": None},
        },
        "main_menu": {
            "new_game": {"type": "type_1", "pos": (20, 20), "text": "New Game", "action": "sprite.game.game.new_game"},
            "load_game": {"type": "type_1", "pos": (20, 90), "text": "WIP"},
            "options": {"type": "type_1", "pos": (20, 160), "text": "WIP"},
            "exit": {"type": "type_1", "pos": (20, 230), "text": "Exit", "action": "sprite.game.quit_game"},
        },
    },
    "game": {
        "settings": {
            "play_width": 300, "play_height": 600, "block_size": (30, 30), "block_border_size": (2, 2),
            "tap_delay": 16, "das_delay": 6, "drop_delay": 2},
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
        "next_piece": {
            "settings": {"pos": (885, 400), "align": "center", "size": (30, 30), "border_size": (6, 6)},
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
                   '..X0..',
                   '.00...',
                   '.....'],
                  ['.....',
                   '..0..',
                   '..X0.',
                   '...0.',
                   '.....']],
            "Z": [['.....',
                   '.....',
                   '.0X..',
                   '..00.',
                   '.....'],
                  ['.....',
                   '...0.',
                   '..X0.',
                   '..0..',
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
        "level": [48, 43, 38, 33, 28, 23, 18, 13, 8, 6, 5, 5, 5, 4, 4, 4, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    },
}
