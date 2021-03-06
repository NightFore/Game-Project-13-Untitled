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
        self.select_level_buttons = pygame.sprite.Group()
        self.game_dict = self.main.main_dict["game"]
        self.settings_dict = self.game_dict["settings"]
        self.shape_dict = self.game_dict["shape"]
        self.play_width = self.settings_dict["play_width"]
        self.play_height = self.settings_dict["play_height"]
        self.block_size = self.settings_dict["block_size"]
        self.block_border_size = self.settings_dict["block_border_size"]
        self.block_surface = pygame.Surface(self.block_size)
        self.block_surface_rect = (self.block_border_size[0], self.block_border_size[1], self.block_size[0] - 2 * self.block_border_size[0], self.block_size[1] - 2 * self.block_border_size[1])
        self.grid_pos = ((screen_size[0] - self.play_width) / 2, screen_size[1] - self.play_height)

    def new_game(self, start_level=0):
        self.score = 0
        self.line_count = 0
        self.start_level, self.level = start_level, start_level
        self.last_dx = 0
        self.are = 0
        self.grid = create_grid()
        self.Next_Piece = Next_Piece(self.main, self.tetrominoes, self.game_dict, data="next_piece", item=self.get_shape())
        self.new_piece()

    def init_select_level(self):
        if self.select_level_buttons:
            self.clear_select_level()
        else:
            settings = self.main.main_dict["button"]["settings"]["icon"]
            pos = (5, 230)
            size, border_size = settings["size"], settings["border_size"]
            for index in range(len(self.game_dict["level"])):
                index_x, index_y = index % 10, index // 10
                button = Button(self.main, self.select_level_buttons, self.main.button_dict, data="select_level", item="default", variable=index, action=self.select_level)
                update_sprite_rect(button, pos[0] + (size[0] - border_size[0]/2) * index_x, pos[1] + (size[1] - border_size[1]/2) * index_y)
                init_sprite_text(button, "%i" % index)

    def select_level(self, level):
        self.clear_select_level()
        self.new_game(level)

    def clear_select_level(self):
        for button in self.select_level_buttons:
            button.kill()

    def new_piece(self):
        for tetromino in self.tetrominoes:
            tetromino.kill()
        self.Player = Tetromino(self.main, self.tetrominoes, self.game_dict, data="tetromino", item=self.Next_Piece.item)
        self.Next_Piece = Next_Piece(self.main, self.tetrominoes, self.game_dict, data="next_piece", item=self.get_shape())
        self.Player.last_dx = self.last_dx

    def get_shape(self):
        return random.choice(list(self.shape_dict))

    def draw_grid(self):
        pygame.draw.rect(self.main.gameDisplay, (0, 0, 0), (self.grid_pos[0], self.grid_pos[1], self.play_width, self.play_height))

        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                dx, dy = j * self.block_size[0], i * self.block_size[1]
                self.block_surface = init_surface(self.block_surface, self.block_surface_rect, self.grid[i][j], (150, 150, 150))
                self.main.gameDisplay.blit(self.block_surface, (self.grid_pos[0] + dx, self.grid_pos[1] + dy))

    def clear_line(self, sprite):
        """
        are: Entry delay / Appearance delay / Spawn delay
        are_lock = 10~18 (10 + 2 for every 4 lines above 2)
        are_clear = 17~20 (16 + frame counter % 5)
        """

        # Initialization
        self.last_dx = sprite.last_dx
        height = 0
        for block in sprite.block_pos:
            self.grid[block[1]][block[0]] = sprite.color
            height = max(height, block[1]+1)
        self.are_lock = 10 + 2 * ((20 - (height - 2)) // 4)

        # Cleared lines
        self.cleared_lines = []
        for i in range(len(self.grid)):
            clear = True
            for j in range(len(self.grid[i])):
                if self.grid[i][j] == (0, 0, 0):
                    clear = False
            if clear:
                self.cleared_lines.append(i)

        if self.cleared_lines:
            self.are_clear = 16 + pygame.time.get_ticks() % 5

            # Level Up
            self.line_count += len(self.cleared_lines)
            if self.line_count >= min((self.level + 1) * 10, 100 + (self.level - min(15, self.start_level)) * 10):
                self.level = min(self.level + 1, len(self.game_dict["level"]))

            # Score
            if len(self.cleared_lines) == 1:
                pygame.mixer.Sound.play(self.main.sound_effects["single"])
                self.score += 40 * (self.level + 1)
            elif len(self.cleared_lines) == 2:
                pygame.mixer.Sound.play(self.main.sound_effects["double"])
                self.score += 100 * (self.level + 1)
            elif len(self.cleared_lines) == 3:
                pygame.mixer.Sound.play(self.main.sound_effects["triple"])
                self.score += 300 * (self.level + 1)
            elif len(self.cleared_lines) == 4:
                pygame.mixer.Sound.play(self.main.sound_effects["tetris"])
                self.score += 1200 * (self.level + 1)
        else:
            self.are_clear = 0

        self.are = self.are_lock + self.are_clear
        sprite.kill()

    def clear_animation(self):
        """
        0 <= col <= 9: Clear and move each line column by column
        index: Increment by one when the index of the line to be moved is a line to clear
        """

        if self.cleared_lines:
            col = self.are - self.are_lock
            if 0 <= col <= 9:
                index = 1
                for i in range(max(self.cleared_lines), max(self.cleared_lines) - min(self.cleared_lines), -1):
                    while i - index in self.cleared_lines:
                        index += 1
                    if i - index >= 0:
                        self.grid[i][col] = self.grid[i - index][col]
                    else:
                        self.grid[i][col] = (0, 0, 0)
            if col == 10:
                for i in range(len(self.cleared_lines)):
                    for j in range(len(self.grid[0])):
                        self.grid[i][j] = (0, 0, 0)



    def get_keys(self):
        keys = pygame.key.get_pressed()
        self.last_dx = -(keys[pygame.K_LEFT] or keys[pygame.K_a]) or (keys[pygame.K_RIGHT] or keys[pygame.K_d])

    def draw(self):
        self.draw_grid()
        self.main.draw_text("Score: %d" % self.score, self.main.font_dict["LiberationSerif"], WHITE, (160, 520), align="center")
        self.main.draw_text("Lines: %d" % self.line_count, self.main.font_dict["LiberationSerif"], WHITE, (160, 590), align="center")
        self.main.draw_text("Level: %d" % self.level, self.main.font_dict["LiberationSerif"], WHITE, (160, 660), align="center")

    def update(self):
        if self.are > 0:
            self.are -= 1
            self.get_keys()
            self.clear_animation()
            if self.are <= 0:
                self.new_piece()


class Tetromino(pygame.sprite.Sprite):
    def __init__(self, main, group, dict, data, item, parent=None, variable=None, action=None):
        # Initialization -------------- #
        init_sprite(self, main, group, dict, data, item, parent, variable, action)

    def init(self):
        init_sprite_surface(self)
        self.block_surface = init_surface(self.surface, self.surface_rect, self.color, self.border_color)

    def load(self):
        # Settings
        self.shapes = self.game.shape_dict[self.item]

        # dx
        self.tap_delay = self.settings["tap_delay"]
        self.das_delay = self.settings["das_delay"]

        # dy
        self.drop_delay = self.settings["drop_delay"]
        self.fall_delay = self.game.game_dict["level"][self.game.level]

    def new(self):
        # Settings
        self.block_pos = [[int(self.pos[0]), int(self.pos[1])]]
        self.offset = -2, -2

        # dx
        self.last_dx = 0
        self.last_move = self.das_delay
        self.tap_check = True

        # dy
        self.last_drop = self.drop_delay
        self.last_fall = self.fall_delay
        self.hard_drop_check = True
        self.drop_check = True

        # rot
        self.block_rot = 0
        self.block_center = 0
        self.rot_check = True

        # Initializing Block
        self.init_shape = True
        self.update_move()
        self.init_shape = False

        # Initializing Ghost
        self.ghost_pos = self.block_pos
        self.ghost_surface = pygame.Surface.copy(self.block_surface)
        self.ghost_surface.set_alpha(125)
        self.ghost_check = True

    def get_keys(self):
        # Initialization
        keys = pygame.key.get_pressed()
        dx, dy, rot = 0, 0, 0
        self.last_move -= 1
        self.last_drop -= 1
        self.last_fall -= 1

        # Move
        if (keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_KP4]) and self.last_dx != 1:
            dx = -1
        elif (keys[pygame.K_RIGHT] or keys[pygame.K_d] or keys[pygame.K_KP6]) and self.last_dx != -1:
            dx = 1
        else:
            self.last_dx = 0
            self.tap_check = False

        # Soft Drop
        if keys[pygame.K_DOWN] or keys[pygame.K_s] or keys[pygame.K_KP5] or self.last_fall <= 0:
            dy = 1

        # Rotate
        if keys[pygame.K_UP] or keys[pygame.K_x] or keys[pygame.K_w] or keys[pygame.K_e] or keys[pygame.K_KP8]:
            rot = 1
        elif keys[pygame.K_RCTRL] or keys[pygame.K_LCTRL] or keys[pygame.K_z] or keys[pygame.K_q]:
            rot = -1
        else:
            self.rot_check = True

        # Hard Drop
        if keys[pygame.K_SPACE]:
            if not self.hard_drop_check:
                self.hard_drop_check = True
                while self.drop_check:
                    self.update_move(dy=1)
        else:
            self.hard_drop_check = False

        # Update Move
        if rot:
            self.update_move(rot=rot)
            self.ghost_check = True
        if dx:
            self.update_move(dx=dx)
            self.ghost_check = True
        if dy and not self.hard_drop_check:
            self.update_move(dy=dy)
        if self.ghost_check:
            self.ghost_pos = self.block_pos
            while self.ghost_check:
                self.update_move(dy=1, ghost=True)

    def update_move(self, dx=0, dy=0, rot=0, ghost=False):
        # Initialization
        pos = self.block_pos if not ghost else self.ghost_pos
        block_pos = []
        block_rot = (self.block_rot + rot) % len(self.shapes)
        block_center = 0
        block_shape = self.shapes[block_rot]
        for y, line in enumerate(block_shape):
            for x, column in enumerate(line):
                if column == "0" or column == "X":
                    pos_x = pos[self.block_center][0] + self.offset[0] + x + dx
                    pos_y = pos[self.block_center][1] + self.offset[1] + y + dy
                    block_pos.append([pos_x, pos_y])
                if column == "X":
                    block_center = len(block_pos) - 1

        # Check
        move_check, drop_check, rot_check = True, True, True
        for block in block_pos:
            if not (0 <= block[0] <= 9 and block[1] <= 19) or 0 <= block[1] and self.game.grid[block[1]][block[0]] != (0, 0, 0):
                move_check, drop_check, rot_check = not (dx != 0), not (dy != 0), not (rot != 0)

        # Piece
        if not ghost:
            # Lock
            self.drop_check = drop_check
            if not self.drop_check:
                pygame.mixer.Sound.play(self.main.sound_effects["lock"])
                self.game.clear_line(self)

            # Move
            elif move_check and rot_check:
                if dx != 0:
                    if not self.tap_check or self.last_dx != dx:
                        pygame.mixer.Sound.play(self.main.sound_effects["tap"])
                        self.tap_check = True
                        self.last_move = self.tap_delay
                        self.last_dx = dx
                        self.block_pos = block_pos
                    elif self.last_move <= 0:
                        pygame.mixer.Sound.play(self.main.sound_effects["das"])
                        self.last_move = self.das_delay
                        self.block_pos = block_pos
                elif dy != 0 and (self.last_drop <= 0 or self.last_fall <= 0 or self.hard_drop_check):
                    self.last_drop = self.drop_delay
                    self.last_fall = self.fall_delay
                    self.block_pos = block_pos
                elif rot != 0 and self.rot_check or self.init_shape:
                    pygame.mixer.Sound.play(self.main.sound_effects["rotate"])
                    self.rot_check = False
                    self.block_rot = block_rot
                    self.block_center = block_center
                    self.block_pos = block_pos

        # Ghost
        else:
            if drop_check:
                self.ghost_pos = block_pos
            else:
                self.ghost_check = False

    def draw(self):
        for block in self.block_pos:
            rect = self.rect.copy()
            rect.x = self.game.grid_pos[0] + block[0] * self.game.block_size[0]
            rect.y = self.game.grid_pos[1] + block[1] * self.game.block_size[1]
            self.main.gameDisplay.blit(self.block_surface, rect)

        for block in self.ghost_pos:
            rect = self.rect.copy()
            rect.x = self.game.grid_pos[0] + block[0] * self.game.block_size[0]
            rect.y = self.game.grid_pos[1] + block[1] * self.game.block_size[1]
            self.main.gameDisplay.blit(self.ghost_surface, rect)

    def update(self):
        self.get_keys()

class Next_Piece(pygame.sprite.Sprite):
    def __init__(self, main, group, dict, data, item, parent=None, variable=None, action=None):
        # Initialization -------------- #
        init_sprite(self, main, group, dict, data, item, parent, variable, action)

    def init(self):
        init_sprite_surface(self)
        init_sprite_text(self)

    def load(self):
        # Settings
        self.shape = self.game.shape_dict[self.item][0]
        self.box_color = self.settings["box_color"]
        self.box_border_color = self.settings["box_border_color"]

    def new(self):
        # Initialization
        self.block_surface = init_surface(self.surface, self.surface_rect, self.color, self.border_color)
        len_x, len_y = len(self.shape[0]), len(self.shape)
        x_min, x_max = len_x, 0
        y_min, y_max = len_y, 0
        offset_x, offset_y = 0, self.size[1]/2

        # Box Surface & Rect
        self.box_size = len_x * self.size[0], len_y * self.size[1]
        self.box_surface = pygame.Surface(self.box_size)
        self.box_rect = self.main.align_rect(self.box_surface, int(self.pos[0]), int(self.pos[1]), self.align)
        self.box_surface_rect = (self.border_size[0], self.border_size[1], self.box_size[0] - 2*self.border_size[0], self.box_size[1] - 2*self.border_size[1])
        self.box_surface = init_surface(self.box_surface, self.box_surface_rect, self.box_color, self.box_border_color)

        # Tetromino Shape
        self.block_pos = []
        for y, line in enumerate(self.shape):
            for x, column in enumerate(line):
                if column == "0" or column == "X":
                    self.block_pos.append([x, y])
                    x_min, x_max = min(x_min, x), max(x_max, x)
                    y_min, y_max = min(y_min, y), max(y_max, y)

        # Tetromino Surface & Rect
        tetromino_width = (x_max - x_min + 1) * self.size[0]
        tetromino_height = (y_max - y_min + 1) * self.size[1]
        self.tetromino_surface = pygame.Surface((tetromino_width, tetromino_height))
        self.tetromino_rect = self.main.align_rect(self.tetromino_surface, int(self.pos[0] + offset_x), int(self.pos[1] + offset_y), self.align)
        for block in self.block_pos:
            rect = self.rect.copy()
            rect.x = (block[0]-x_min) * self.size[0]
            rect.y = (block[1]-y_min) * self.size[1]
            self.tetromino_surface.blit(self.block_surface, rect)

    def draw(self):
        # Surface
        self.main.gameDisplay.blit(self.box_surface, self.box_rect)
        self.main.gameDisplay.blit(self.tetromino_surface, self.tetromino_rect)

        # Text
        if self.text is not None and self.font is not None:
            self.main.draw_text(self.text, self.font, self.font_color, (self.pos[0], self.pos[1] - self.size[1]), self.text_align)
        else:
            print("Text or font not initialized")

    def update(self):
        pass


def init_menu(main, menu, clear=True):
    menu_dict = main.main_dict["menu"][menu]
    if clear:
        clear_menu(main)

    main.update_music(main.music_dict[menu_dict["music"]])
    main.update_background(main.background_dict[menu_dict["background"]])

    for button in main.button_dict[menu]:
        Button(main, main.buttons, main.button_dict, data=menu, item=button)

def clear_menu(main):
    for sprite in main.all_sprites:
        sprite.kill()

def main_menu(main, menu):
    init_menu(main, menu)
    main.game.new_game()

def pause_menu(main):
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
        "lock": "se_maoudamashii_system_14.ogg",  # Change se_maoudamashii_fight_07
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
        "settings": {
            "default": {
                "align": "nw", "size": (280, 50),
                "border": True, "border_size": (5, 5), "border_color": BLACK,
                "text_align": "center", "font": "LiberationSerif", "font_color": WHITE,
                "inactive_color": LIGHT_SKY_BLUE, "active_color": DARK_SKY_BLUE,
                "sound_action": None, "sound_active": None, "sound_inactive": None},
            "icon": {
                "align": "nw", "size": (50, 50),
                "border": True, "border_size": (5, 5), "border_color": BLACK,
                "text_align": "center", "font": "LiberationSerif", "font_color": WHITE,
                "inactive_color": LIGHT_SKY_BLUE, "active_color": DARK_SKY_BLUE,
                "sound_action": None, "sound_active": None, "sound_inactive": None},
        },
        "main_menu": {
            "new_game": {"type": "default", "pos": (20, 20), "text": "New Game", "action": "self.game.new_game"},
            "options": {"type": "default", "pos": (20, 90), "text": "Select Level", "action": "self.game.init_select_level"},
            "exit": {"type": "default", "pos": (20, 160), "text": "Exit", "action": "self.main.quit_game"},
        },
        "select_level": {
            "default": {"type": "icon", "pos": (0, 0), "text": None}
        }
    },
    "game": {
        "settings": {
            "play_width": 300, "play_height": 600, "block_size": (30, 30), "block_border_size": (2, 2),
            "tetromino": {
                "pos": (5, 0), "align": "nw", "size": (30, 30), "border_size": (6, 6),
                "tap_delay": 16, "das_delay": 6, "drop_delay": 2
            },
            "next_piece": {
                "pos": (885, 400), "align": "center", "size": (30, 30), "border_size": (6, 6),
                "text": "NEXT", "text_align": "s", "font": "LiberationSerif", "font_color": WHITE,
                "box_color": BLACK, "box_border_color": (150, 150, 150)
            },
        },
        "tetromino": {
            "I": {"color": (1, 240, 241), "border_color": (0, 222, 221)},
            "J": {"color": (1, 1, 238), "border_color": (6, 8, 165)},
            "L": {"color": (240, 160, 0), "border_color": (220, 145, 0)},
            "O": {"color": (240, 241, 0), "border_color": (213, 213, 0)},
            "S": {"color": (0, 241, 0), "border_color": (0, 218, 0)},
            "T": {"color": (160, 0, 243), "border_color": (147, 0, 219)},
            "Z": {"color": (238, 2, 0), "border_color": (215, 0, 0)},
        },
        "next_piece": {
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
                   '.....',
                   '.0X..',
                   '.00..',
                   '.....']],
            "J": [['.....',
                   '.....',
                   '.0X0.',
                   '...0.',
                   '.....'],
                  ['.....',
                   '..0..',
                   '..X..',
                   '.00..',
                   '.....'],
                  ['.....',
                   '.0...',
                   '.0X0.',
                   '.....',
                   '.....'],
                  ['.....',
                   '..00.',
                   '..X..',
                   '..0..',
                   '.....']],
            "L": [['.....',
                   '.....',
                   '.0X0.',
                   '.0...',
                   '.....'],
                  ['.....',
                   '.00..',
                   '..X..',
                   '..0..',
                   '.....'],
                  ['.....',
                   '...0.',
                   '.0X0.',
                   '.....',
                   '.....'],
                  ['.....',
                   '..0..',
                   '..X..',
                   '..00.',
                   '.....']],
            "T": [['.....',
                   '.....',
                   '.0X0.',
                   '..0..',
                   '.....'],
                  ['.....',
                   '..0..',
                   '.0X..',
                   '..0..',
                   '.....'],
                  ['.....',
                   '..0..',
                   '.0X0.',
                   '.....',
                   '.....'],
                  ['.....',
                   '..0..',
                   '..X0.',
                   '..0..',
                   '.....']]
        },
        "level": [48, 43, 38, 33, 28, 23, 18, 13, 8, 6, 5, 5, 5, 4, 4, 4, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    },
}
