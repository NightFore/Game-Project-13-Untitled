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
        print(self.line_count, (self.level + 1) * 10, 100 + (self.level - min(15, self.start_level)) * 10)
        print(self.level, self.score, self.Player.fall_delay)
        print()


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
        self.move_tap = False
        self.last_dir = 0
        self.init_das_delay = 16
        self.das_delay = 6
        self.last_das = self.das_delay
        self.drop_delay = 2
        self.last_drop = self.drop_delay
        self.fall_delay = self.game.game_dict["level"][self.game.level]
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

    def draw(self):
        for block in self.block_pos:
            rect = self.rect.copy()
            rect.x = self.game.grid_pos[0] + block[0] * self.game.block_size[0]
            rect.y = self.game.grid_pos[1] + block[1] * self.game.block_size[1]
            self.main.gameDisplay.blit(self.surface, rect)

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
            if not (0 <= block[0] <= 9 and block[1] <= 19) or 0 <= block[1] and self.game.grid[block[1]][block[0]] != (0, 0, 0):
                move_check, lock_check, rot_check = not (dx != 0), not (dy != 0), not (rot != 0)

        if not lock_check and (not move_check or not rot_check):
            self.update_move(dy=dy)
        elif not lock_check:
            pygame.mixer.Sound.play(self.main.sound_effects["lock"])
            self.drop_check = False
            for block in self.block_pos:
                self.game.grid[block[1]][block[0]] = self.color
            self.game.clear_line()
            self.game.new_piece(self.move_tap, self.last_dir, self.hard_drop_check)
        elif move_check and rot_check:
            if dx != 0 and dy != 0:
                self.update_move(dy=dy)
                self.update_move(dx=dx)
            else:
                if dx != 0:
                    if not self.move_tap or self.last_dir != dx:
                        pygame.mixer.Sound.play(self.main.sound_effects["move_tap"])
                        self.block_pos = block_pos
                        self.last_das = self.init_das_delay
                        self.last_dir = dx
                        self.move_tap = True
                    elif self.last_das <= 0:
                        pygame.mixer.Sound.play(self.main.sound_effects["move_das"])
                        self.block_pos = block_pos
                        self.last_das = self.das_delay
                if dy != 0:
                    if self.last_drop <= 0:
                        self.block_pos = block_pos
                        self.last_drop = self.drop_delay
                        self.last_fall = self.fall_delay
            if rot != 0:
                pygame.mixer.Sound.play(self.main.sound_effects["rotate"])
                self.block_pos = block_pos
                self.block_center = block_center
                self.block_rot = block_rot
                self.rot_check = False

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
        x_max, x_min = 0, len(self.shape[0])
        y_max, y_min = 0, len(self.shape)

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
        self.rect = self.main.align_rect(self.surface, int(self.pos[0]), int(self.pos[1]), self.center)
        for block in self.block_pos:
            rect = self.rect.copy()
            rect.x = (block[0]-x_min) * self.game.block_size[0]
            rect.y = (block[1]-y_min) * self.game.block_size[1]
            self.surface.blit(block_surface, rect)

    def draw(self):
        self.main.gameDisplay.blit(self.surface, self.rect)

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
        "settings": {"play_width": 300, "play_height": 600, "block_size": (30, 30), "block_border_size": (2, 2)},
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
            "settings": {"pos": (1000, 350), "align": "center", "size": (30, 30), "border_size": (6, 6)},
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
        "level": [48, 43, 38, 33, 28, 23, 18, 13, 8, 6, 5, 5, 5, 4, 4, 4, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    },
}
