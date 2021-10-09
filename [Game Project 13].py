import pygame
import random
from pygame.locals import *
from os import path

from Camera import *
from ScaledGame import *

from Main import *
from Class import *
from Function import *
from Settings import *

vec = pygame.math.Vector2

"""
    Game
"""
class Main:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        pygame.init()
        random.seed()
        pygame.key.set_repeat(100, 30)
        pygame.mixer.music.set_volume(default_volume/100)
        self.gameDisplay = ScaledGame(project_title, screen_size, FPS)
        self.dt = self.gameDisplay.clock.tick(FPS) / 1000
        self.load_data()
        self.new()

    def align_rect(self, surface, x, y, align):
        rect = surface.get_rect()
        if align == "nw":
            rect.topleft = (x, y)
        if align == "ne":
            rect.topright = (x, y)
        if align == "sw":
            rect.bottomleft = (x, y)
        if align == "se":
            rect.bottomright = (x, y)
        if align == "n":
            rect.midtop = (x, y)
        if align == "s":
            rect.midbottom = (x, y)
        if align == "e":
            rect.midright = (x, y)
        if align == "w":
            rect.midleft = (x, y)
        if align == "center":
            rect.center = (x, y)
        return rect

    def draw_text(self, text, font, color, pos, align="nw"):
        if not isinstance(text, str):
            text = str(text)
        text_surface = font.render(text, True, color)
        text_rect = self.align_rect(text_surface, int(pos[0]), int(pos[1]), align)
        if self.debug_mode:
            pygame.draw.rect(self.gameDisplay, CYAN, text_rect, 1)
        self.gameDisplay.blit(text_surface, text_rect)

    def draw_image(self, image, x, y, align="nw"):
        image_rect = self.align_rect(image, x, y, align)
        self.gameDisplay.blit(image, image_rect)

    def load_data(self):
        # Main settings
        self.project_title = project_title
        self.default_volume = default_volume
        self.volume = self.default_volume

        # Directories
        self.game_folder = path.dirname(__file__)
        self.data_folder = path.join(self.game_folder, "data")
        self.graphics_folder = path.join(self.data_folder, "graphics")
        self.se_folder = path.join(self.data_folder, "sound")
        self.music_folder = path.join(self.data_folder, "music")
        self.map_folder = path.join(self.data_folder, "map")
        self.font_folder = path.join(self.data_folder, "fonts")

        # Dict
        self.main_dict = MAIN_DICT
        self.game_dict = self.main_dict["game"]
        self.background_dict = self.main_dict["background"]
        self.music_dict = self.main_dict["music"]
        self.sound_dict = self.main_dict["sound"]
        self.font_dict = self.main_dict["font"]
        self.menu_dict = self.main_dict["menu"]
        self.button_dict = self.main_dict["button"]

        self.sound_effects = {}
        for sound in self.sound_dict:
            self.sound_effects[sound] = pygame.mixer.Sound(path.join(self.se_folder, self.sound_dict[sound]))
        for sound in self.sound_dict:
            self.sound_effects[sound].set_volume(default_sound_volume / 100)

        self.font = pygame.font.Font(None, 100)
        for font in self.font_dict:
            self.load_font(font)

        # Pause Screen
        self.dim_screen = pygame.Surface(self.gameDisplay.get_size()).convert_alpha()
        self.dim_screen.fill((100, 100, 100, 120))

    def new(self):
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.uis = pygame.sprite.Group()
        self.buttons = pygame.sprite.Group()
        self.player = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()

    def init_main(self):
        self.debug_color = CYAN
        self.debug_mode = True
        self.paused = False
        self.pause_check = True
        self.background_image = None
        self.background_color = None
        self.music = None
        self.menu = "main_menu"
        self.update_menu(self.menu)

    # Game Loop ----------------------- #
    def run(self):
        self.game = Game(self)
        self.init_main()
        self.playing = True
        while self.playing:
            self.dt = self.gameDisplay.clock.tick(FPS) / 1000
            self.events()
            if not self.paused:
                self.update()
            self.draw()
        self.quit_game()

    def quit_game(self):
        pygame.quit()
        quit()

    def events(self):
        self.event = pygame.event.get()
        self.click = [None, False, False, False, False, False]
        for event in self.event:
            self.mouse = pygame.mouse.get_pos()

            # Rescaling mouse position to screen size
            if self.gameDisplay.factor_w != 1 or self.gameDisplay.factor_h != 1:
                mouse_w = int(self.mouse[0] / self.gameDisplay.factor_w)
                mouse_h = int(self.mouse[1] / self.gameDisplay.factor_h)
                self.mouse = (mouse_w, mouse_h)

            if event.type == pygame.QUIT:
                self.quit_game()

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.click[event.button] = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit_game()
                if event.key == pygame.K_p:
                    if self.pause_check:
                        self.paused = not self.paused
                    if self.paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                    self.pause_check = False
                if event.key == pygame.K_h:
                    self.debug_mode = not self.debug_mode
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_p:
                    self.pause_check = True

    def update(self):
        self.game.update()
        self.all_sprites.update()

    def draw(self):
        # Background ------------------ #
        if self.background_image is not None:
            self.gameDisplay.blit(self.background_image, (0, 0))
        if self.background_color is not None:
            self.gameDisplay.fill(self.background_color)

        # Game ------------------------ #
        self.game.draw()

        # Sprites --------------------- #
        for sprite in self.all_sprites:
            sprite.draw()

        # Pause ----------------------- #
        if self.paused:
            self.gameDisplay.blit(self.dim_screen, (0, 0))
            self.draw_text("Paused", self.font, RED, (WIDTH / 2, HEIGHT / 2), align="center")

        # Update ---------------------- #
        self.gameDisplay.update(self.event)

    def update_background(self, background_dict):
        color = background_dict["color"]
        if color is not None and self.background_color != color:
            self.background_color = color

        image = background_dict["image"]
        if image is not None:
            image = load_image(self.graphics_folder, image)
        if self.background_image != image:
            self.background_image = image

    def update_menu(self, menu=None):
        if menu is not None:
            self.menu = menu
            self.menu_dict[menu]["call"](self, menu)
        else:
            self.menu_dict[self.menu]["call"](self, self.menu)

    def update_music(self, music):
        if music is not None:
            music = path.join(self.music_folder, music)
            if self.music != music:
                self.music = music
                pygame.mixer.music.load(self.music)
                pygame.mixer.music.play(-1)

    def update_volume(self, dv=0):
        if 0 <= self.volume + dv <= 100:
            self.volume = self.volume + dv
            pygame.mixer.music.set_volume(self.volume/100)

    def update_sprite(self, sprite, move=False, keys=False):
        if move:
            sprite.update_move()
        if keys:
            sprite.get_keys()
        update_time_dependent(sprite)
        update_center(sprite)
        update_bobbing(sprite)

    def load_font(self, font):
        font_ttf = self.font_dict[font]["ttf"]
        font_size = self.font_dict[font]["size"]
        self.font_dict[font] = pygame.font.Font(path.join(self.font_folder, font_ttf), font_size)

m = Main()
while True:
    m.run()
