import pygame
import random
from Settings import *
from os import path
vec = pygame.math.Vector2

"""
    Sprite initialization functions
"""
def init_sprite_WIP(self, main, group, dict, data, item, parent, variable, action):
    # Class
    self.main = main
    self.game = main.game

    # Group
    self.groups = self.main.all_sprites, group
    pygame.sprite.Sprite.__init__(self, self.groups)

    # Dict
    self.dict = dict
    self.data = data
    self.item = item
    self.object = self.dict[self.data][self.item]
    self.settings = self.dict["settings"][self.object["type"]]

    # Variable
    self.parent = parent
    self.variable = variable
    self.action = action

    # Initialization
    self.init()
    self.load()
    self.new()

def init_sprite_text(self):
    # Text
    if "text" in self.object:
        self.text = self.object["text"]
    else:
        self.text = None
    self.text_pos = self.rect[0] + self.rect[2] / 2, self.rect[1] + self.rect[3] / 2

    # Font
    self.font = self.main.font_dict[self.settings["font"]]
    self.font_color = self.settings["font_color"]

    # Check
    self.font_check = self.font is not None
    if not self.font_check:
        print("Font not initialized, text: %s" % self.text)

def init_sprite_surface(self):
    if "pos" in self.object:
        self.pos = self.object["pos"]
    if "pos" in self.settings:
        self.pos = self.settings["pos"]
    if "size" in self.object:
        self.size = self.object["size"]
    if "size" in self.settings:
        self.size = self.settings["size"]
    if "align" in self.object:
        self.align = self.object["align"]
    if "align" in self.settings:
        self.align = self.settings["align"]
    if "border_size" in self.object:
        self.border_size = self.object["border_size"]
    if "border_size" in self.settings:
        self.border_size = self.settings["border_size"]
    if "color" in self.object:
        self.color = self.object["color"]
    if "color" in self.settings:
        self.color = self.settings["color"]
    if "border_color" in self.object:
        self.border_color = self.object["border_color"]
    if "border_color" in self.settings:
        self.border_color = self.settings["border_color"]

    self.surface = pygame.Surface(self.size)
    self.surface_rect = (self.border_size[0], self.border_size[1], self.size[0] - 2*self.border_size[0], self.size[1] - 2*self.border_size[1])
    self.rect = self.main.align_rect(self.surface, self.pos[0], self.pos[1], self.align)








def init_sprite(sprite, game, dict, group=None, data=None, item=None, parent=None, variable=None, action=None, move=False):
    # Initialization -------------- #
    sprite.game = game
    sprite.groups = sprite.game.all_sprites, group
    sprite.data = data
    sprite.item = item
    sprite.parent = parent
    sprite.variable = variable
    sprite.action = action
    pygame.sprite.Sprite.__init__(sprite, sprite.groups)

    # Dict ------------------------ #
    sprite.dict = dict
    sprite.object = sprite.dict[sprite.data][sprite.item]
    sprite.settings = sprite.dict["type"][sprite.object["type"]]

    # Arguments Settings ---------- #
    if "variable" in sprite.object and sprite.variable is None:
        if isinstance(sprite.object["variable"], str):
            sprite.variable = eval(sprite.object["variable"])
        else:
            sprite.variable = sprite.object["variable"]
    if "action" in sprite.object and sprite.action is None:
        if isinstance(sprite.object["action"], str):
            sprite.action = eval(sprite.object["action"])
        else:
            sprite.action = sprite.object["action"]

    # Settings
    sprite.pos = sprite.object["pos"]
    sprite.size = sprite.settings["size"]
    sprite.center = sprite.settings["align"]
    sprite.surface = pygame.Surface(sprite.size)
    sprite.rect = sprite.game.align_rect(sprite.surface, sprite.pos[0], sprite.pos[1], sprite.center)

    # Border
    sprite.border_size = sprite.settings["border_size"]
    sprite.border_color = sprite.settings["border_color"]
    sprite.surface_rect = (sprite.border_size[0], sprite.border_size[1], sprite.size[0] - 2*sprite.border_size[0], sprite.size[1] - 2*sprite.border_size[1])

    if move:
        sprite.pos = vec(sprite.object["pos"][:])
        sprite.pos_dt = vec(0, 0)
        sprite.vel = vec(0, 0)
        sprite.move_speed = vec(sprite.settings["move_speed"])
        sprite.hit_rect = sprite.rect

def init_sprite_2(sprite, main, dict, group, data, item, parent=None, variable=None, action=None):
    # Initialization -------------- #
    sprite.main = main
    sprite.game = sprite.main.game
    sprite.groups = sprite.main.all_sprites, group
    sprite.data = data
    sprite.item = item
    sprite.parent = parent
    sprite.variable = variable
    sprite.action = action
    pygame.sprite.Sprite.__init__(sprite, sprite.groups)

    # Dict ------------------------ #
    sprite.dict = dict
    sprite.object = sprite.dict[sprite.data][sprite.item]
    sprite.settings = sprite.dict[sprite.data]["settings"]

    # Arguments Settings ---------- #
    if "variable" in sprite.object and sprite.variable is None:
        sprite.variable = sprite.object["variable"]
    if "action" in sprite.object and sprite.action is None:
        sprite.action = eval(sprite.object["action"])

    # Settings
    sprite.pos = vec(sprite.settings["pos"][:])
    sprite.size = sprite.settings["size"]
    sprite.center = sprite.settings["align"]
    sprite.surface = pygame.Surface(sprite.size)
    sprite.color = sprite.object["color"]
    sprite.rect = sprite.main.align_rect(sprite.surface, int(sprite.pos[0]), int(sprite.pos[1]), sprite.center)

    # Border
    if "border_size" in sprite.settings:
        if "border_size" in sprite.settings:
            sprite.border_size = sprite.settings["border_size"]
        elif "border_size" in sprite.object:
            sprite.border_size = sprite.object["border_size"]
        if "border_color" in sprite.settings:
            sprite.border_color = sprite.settings["border_color"]
        elif "border_color" in sprite.object:
            sprite.border_color = sprite.object["border_color"]
        sprite.surface_rect = (sprite.border_size[0], sprite.border_size[1], sprite.size[0] - 2*sprite.border_size[0], sprite.size[1] - 2*sprite.border_size[1])
    else:
        sprite.surface_rect = (0, 0, sprite.size[0], sprite.size[1])

def init_surface(surface, surface_rect, color, border_color=None):
    surface = surface.copy()
    if border_color is not None:
        surface.fill(border_color)
    pygame.draw.rect(surface, color, surface_rect)
    return surface



"""
    Gameplay functions
"""
def collide_with_walls(sprite, group):
    # WIP - Center only
    sprite.hit_rect.centerx = sprite.pos.x
    hits = pygame.sprite.spritecollide(sprite, group, False, collide_hit_rect)
    if hits:
        if hits[0].rect.centerx > sprite.hit_rect.centerx:
            sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
        if hits[0].rect.centerx < sprite.hit_rect.centerx:
            sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
        sprite.vel.x = 0
        sprite.hit_rect.centerx = sprite.pos.x

    sprite.hit_rect.centery = sprite.pos.y
    hits = pygame.sprite.spritecollide(sprite, group, False, collide_hit_rect)
    if hits:
        if hits[0].rect.centery > sprite.hit_rect.centery:
            sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
        if hits[0].rect.centery < sprite.hit_rect.centery:
            sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
        sprite.vel.y = 0
        sprite.hit_rect.centery = sprite.pos.y
    sprite.rect.center = sprite.hit_rect.center

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)



"""
    Sprite update functions
"""
def update_move(sprite, dx=None, dy=None):
    if dx is None and dy is None:
        sprite.pos += sprite.vel * sprite.game.dt
        sprite.pos_dt += sprite.vel.x * sprite.game.dt, sprite.vel.y * sprite.game.dt
    else:
        sprite.pos.x += dx
        sprite.pos.y += dy
    update_rect(sprite)

def update_rect(sprite, x=None, y=None):
    if x is not None:
        sprite.pos[0] = x
    if y is not None:
        sprite.pos[1] = y
    sprite.rect = sprite.game.align_rect(sprite.surface, int(sprite.pos[0]), int(sprite.pos[1]), sprite.center)

def update_time_dependent(sprite):
    if sprite.table:
        sprite.current_time += sprite.dt
        if sprite.current_time >= sprite.animation_time:
            if sprite.index == len(sprite.images)-1:
                sprite.loop += 1
            sprite.current_time = 0
            sprite.index = (sprite.index + 1) % len(sprite.images)
            sprite.image = sprite.images[sprite.index]
        if sprite.animation_loop and sprite.index == 0 and sprite.loop != 0:
            sprite.kill()
        sprite.image = pygame.transform.rotate(sprite.image, 0)

def update_center(sprite):
    if sprite.center:
        sprite.rect = sprite.image.get_rect()
        sprite.rect.center = sprite.pos

def update_bobbing(sprite):
    if sprite.bobbing:
        offset = BOB_RANGE * (sprite.tween(sprite.step / BOB_RANGE) - 0.5)
        sprite.rect.centery = sprite.pos.y + offset * sprite.dir
        sprite.step += BOB_SPEED
        if sprite.step > BOB_RANGE:
            sprite.step = 0
            sprite.dir *= -1



"""
    Miscellaneous
"""
def create_grid(locked_pos={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                c = locked_pos[(j, i)]
                grid[i][j] = c
    return grid

def load_file(path, image=False):
    file = []
    for file_name in os.listdir(path):
        if image:
            file.append(pygame.image.load(path + os.sep + file_name).convert_alpha())
        else:
            file.append(path + os.sep + file_name)
    return file


def load_image(image_path, image_directory):
    if isinstance(image_directory, list):
        images = []
        for image in image_directory:
            images.append(pygame.image.load(path.join(image_path, image)).convert_alpha())
        return images
    else:
        return pygame.image.load(path.join(image_path, image_directory)).convert_alpha()


def load_tile_table(filename, width, height, reverse, colorkey=(0, 0, 0)):
    image = pygame.image.load(filename).convert_alpha()
    image.set_colorkey(colorkey)
    image_width, image_height = image.get_size()
    tile_table = []
    if not reverse:
        for tile_y in range(int(image_height / height)):
            line = []
            tile_table.append(line)
            for tile_x in range(int(image_width / width)):
                rect = (tile_x * width, tile_y * height, width, height)
                line.append(image.subsurface(rect))
    else:
        for tile_x in range(int(image_width / width)):
            column = []
            tile_table.append(column)
            for tile_y in range(int(image_height / height)):
                rect = (tile_x * width, tile_y * height, width, height)
                column.append(image.subsurface(rect))
    return tile_table


def transparent_surface(width, height, color, border, colorkey=(0, 0, 0)):
    surface = pygame.Surface((width, height)).convert()
    surface.set_colorkey(colorkey)
    surface.fill(color)
    surface.fill(colorkey, surface.get_rect().inflate(-border, -border))
    return surface


def sort_list(list, var, reverse=False):
    if reverse:
        list.reverse()

    for i in range(len(list)):
        # Display list
        # print(list)

        if list[i] == var:
            cpt = 0
            while list[i + cpt] == var and i + cpt < len(list)-1:
                cpt += 1
            list[i] = list[i+cpt]
            list[i+cpt] = var

    if reverse:
        list.reverse()
