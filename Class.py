import pygame
import random
import pytweening as tween
from Settings import *
from Function import *
vec = pygame.math.Vector2

class Button(pygame.sprite.Sprite):
    def __init__(self, game, dict, group=None, data=None, item=None, parent=None, variable=None, action=None):
        # Initialization -------------- #
        init_sprite(self, game, dict, group, data, item, parent, variable, action)

        # Surface --------------------- #
        self.inactive_surface = init_surface(self.surface, self.surface_rect, self.settings["inactive_color"], border_color=self.border_color)
        self.active_surface = init_surface(self.surface, self.surface_rect, self.settings["active_color"], border_color=self.border_color)

        # Font Settings --------------- #
        self.text = self.object["text"]
        self.text_pos = self.rect[0] + self.rect[2] / 2, self.rect[1] + self.rect[3] / 2
        self.font = self.game.font_dict[self.settings["font"]]
        self.font_color = self.settings["font_color"]

        # Sound Settings -------------- #
        self.sound_active = self.settings["sound_active"]
        self.sound_action = self.settings["sound_action"]

        # Check ----------------------- #
        self.font_check = False
        self.sound_check = False

    def draw(self):
        self.game.gameDisplay.blit(self.surface, self.rect)
        if self.text is not None:
            if self.font is not None:
                self.game.draw_text(self.text, self.font, self.font_color, self.text_pos, "center")
            elif not self.font_check:
                self.font_check = True
                print("Font not initialized, text: %s" % self.text)

    def update(self):
        if self.rect.collidepoint(self.game.mouse):
            self.surface = self.active_surface
            if self.sound_active is not None and not self.sound:
                pygame.mixer.Sound.play(self.sound_active)
                self.sound_check = True
            if self.game.click[1] and self.action is not None:
                if self.sound_action is not None:
                    pygame.mixer.Sound.play(self.sound_action)
                if self.variable is not None:
                    self.action(self.variable)
                else:
                    self.action()
        else:
            self.surface = self.inactive_surface
            self.sound_check = False

class UI(pygame.sprite.Sprite):
    def __init__(self, game, dict, group=None, data=None, item=None, parent=None, variable=None, action=None):
        # Initialization -------------- #
        init_sprite(self, game, dict, group, data, item, parent, variable, action)

        # Surface --------------------- #
        self.surface = init_surface(self.surface, self.surface_rect, self.settings["color"], border_color=self.border_color)

        # Font Settings --------------- #
        self.text = self.object["text"]
        self.text_pos = self.rect[0] + self.rect[2] / 2, self.rect[1] + self.rect[3] / 2
        self.font = self.game.font_dict[self.settings["font"]]
        self.font_color = self.settings["font_color"]

        # Check ----------------------- #
        self.font_check = False

    def draw(self):
        self.game.gameDisplay.blit(self.surface, self.rect)
        if self.text is not None:
            if self.font is not None:
                self.game.draw_text(self.text, self.font, self.font_color, self.text_pos, "center")
            elif not self.font_check:
                self.font_check = True
                print("Font not initialized, text: %s" % self.text)

    def update(self):
        pass



class Player(pygame.sprite.Sprite):
    def __init__(self, game, dict, group=None, data=None, item=None, parent=None, variable=None, action=None):
        # Initialization -------------- #
        init_sprite(self, game, dict, group, data, item, parent, variable, action, move=True)

        # Surface --------------------- #
        self.surface = init_surface(self.surface, self.surface_rect, self.settings["color"])

    def init_move(self):
        self.pos = vec(self.object["pos"][:])
        self.pos_dt = vec(0, 0)
        self.vel = vec(0, 0)
        self.move_speed = vec(self.settings["move_speed"])
        self.hit_rect = self.rect

    def update_move(self):
        self.pos += self.vel * self.dt
        self.pos_dt += self.vel.x * self.dt, self.vel.y * self.dt
        self.rect = self.game.align_rect(self.surface, int(self.pos[0]), int(self.pos[1]), self.center)

    def get_keys(self):
        keys = pygame.key.get_pressed()
        move = [0, 0]
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move[1] = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move[1] = 1
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move[0] = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move[0] = 1
        self.vel = vec(self.move_speed.elementwise() * move)

    def draw(self):
        self.game.gameDisplay.blit(self.surface, self.rect)

    def update(self):
        self.get_keys()
        update_move(self)

        collide_with_walls(self, self.game.walls)
        hits = pygame.sprite.spritecollide(self, self.game.entities, False, collide_hit_rect)
        if hits:
            pass

class Entity(pygame.sprite.Sprite):
    def __init__(self, game, dict, group=None, data=None, item=None, parent=None, variable=None, action=None):
        # Initialization -------------- #
        init_sprite(self, game, dict, group, data, item, parent, variable, action, move=True)

        # Surface --------------------- #
        self.surface = init_surface(self.surface, self.surface_rect, self.settings["color"])

    def draw(self):
        self.game.gameDisplay.blit(self.surface, self.rect)

    def update(self):
        if self.vel == (0, 0):
            self.vel = self.move_speed
        update_move(self)

        if abs(self.pos_dt[0]) > WIDTH + self.size[0] or abs(self.pos_dt[1]) > HEIGHT + self.size[1]:
            self.kill()

class Wall(pygame.sprite.Sprite):
    def __init__(self, game, dict, group=None, data=None, item=None, parent=None, variable=None, action=None):
        # Initialization -------------- #
        init_sprite(self, game, dict, group, data, item, parent, variable, action)

        # Surface --------------------- #
        self.surface = init_surface(self.surface, self.surface_rect, self.settings["color"])

    def draw(self):
        self.game.gameDisplay.blit(self.surface, self.rect)

    def update(self):
        pass


LEVEL_DICT = {
    "easy": {
        "offset": [340, 60],
    },
    "normal": {
        "offset": [415, 135],
    },
    "hard": {
        "offset": [465, 185],
    },
}

class Level:
    def __init__(self, game):
        # Initialization -------------- #
        self.game = game
        self.difficulty = 1
        self.level = 1
        self.entity_count = 0
        self.entity_max = 1
        self.last_entity = pygame.time.get_ticks()

    def init(self, menu):
        self.game.level_mode = True
        Player(self.game, self.game.entity_dict, self.game.player, data=menu, item="player")

    def update(self):
        if self.game.level_mode:
            if self.entity_count < self.entity_max:
                if self.level == 1:
                    if pygame.time.get_ticks() - self.last_entity >= 1500:
                        for i in range(self.level):
                            entity = Entity(self.game, self.game.entity_dict, self.game.entities, data="level_menu", item="entity_1")
                            update_rect(entity, 340 + random.randrange(25, 575))
                        self.entity_count += 1
                        self.last_entity = pygame.time.get_ticks()

                if self.level == 2:
                    if pygame.time.get_ticks() - self.last_entity >= 1000:
                        for i in range(self.level):
                            entity = Entity(self.game, self.game.entity_dict, self.game.entities, data="level_menu", item="entity_2")
                            update_rect(entity, 415 + random.randrange(25, 425))
                        self.entity_count += 1
                        self.last_entity = pygame.time.get_ticks()

                if self.level >= 3:
                    if pygame.time.get_ticks() - self.last_entity >= 750:
                        for i in range(self.level):
                            entity = Entity(self.game, self.game.entity_dict, self.game.entities, data="level_menu", item="entity_2")
                            update_rect(entity, 465 + random.randrange(25, 325))
                        self.entity_count += 1
                        self.last_entity = pygame.time.get_ticks()
            elif len(self.game.entities.sprites()) == 0:
                self.level += 1
                self.entity_count = 0
                self.entity_max += 1
