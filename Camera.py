import pygame

"""
-Initialization
self.camera = Camera(self.map.width, self.map.height, WIDTH, HEIGHT)

-Update
self.camera.update(self.cursor)

-Draw
self.camera.apply_rect(self.map_rect)
"""

class Camera:
    def __init__(self, width, height, WIDTH, HEIGHT):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(self.WIDTH / 2)
        y = -target.rect.centery + int(self.HEIGHT / 2)

        # Limit to map size (Left / Right / Top / Bottom)
        x = min(0, x)
        x = max(-(self.width - self.WIDTH), x)
        y = min(0, y)
        y = max(-(self.height - self.HEIGHT), y)
        self.camera = pygame.Rect(x, y, self.width, self.height)