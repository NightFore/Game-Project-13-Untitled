import pygame
import random
import pytweening as tween
from Settings import *
from Function import *
vec = pygame.math.Vector2

class Button(pygame.sprite.Sprite):
    def __init__(self, main, group, dict, data, item, parent=None, variable=None, action=None):
        # Initialization -------------- #
        init_sprite(self, main, group, dict, data, item, parent, variable, action)

    def init(self):
        init_sprite_surface(self)
        init_sprite_text(self)

    def load(self):
        # Surface
        self.active_color = self.settings["active_color"]
        self.inactive_color = self.settings["inactive_color"]

        # Sound
        self.sound_action = self.settings["sound_action"]
        self.sound_active = self.settings["sound_active"]
        self.sound_inactive = self.settings["sound_inactive"]

    def new(self):
        # Surface
        self.surface_active = init_surface(self.surface, self.surface_rect, self.active_color, self.border_color)
        self.surface_inactive = init_surface(self.surface, self.surface_rect, self.inactive_color, self.border_color)

        # Sound
        self.sound_check = False

        # Action
        if "action" in self.object:
            self.action = eval(self.object["action"])

    def draw(self):
        # Surface
        self.main.gameDisplay.blit(self.surface, self.rect)

        # Text
        if self.font_check and self.text is not None:
            self.main.draw_text(self.text, self.font, self.font_color, self.text_pos, "center")

    def update(self):
        # Collision
        if self.rect.collidepoint(self.main.mouse):
            # Active
            self.surface = self.surface_active
            if self.sound_active is not None and not self.sound_check:
                pygame.mixer.Sound.play(self.sound_active)
                self.sound_check = True

            # Action
            if self.main.click[1]:
                if self.sound_action is not None:
                    pygame.mixer.Sound.play(self.sound_action)
                if self.action is not None:
                    if self.variable is not None:
                        self.action(self.variable)
                    else:
                        self.action()
        else:
            # Inactive
            self.surface = self.surface_inactive
            if self.sound_inactive is not None and self.sound_check:
                pygame.mixer.Sound.play(self.sound_inactive)
                self.sound_check = False
