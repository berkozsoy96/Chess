from pygame import Color, Surface
from pygame.sprite import Sprite


class Tile(Sprite):
    def __init__(self, name: str, position: tuple[int, int], color: Color, size: int = 75):
        Sprite.__init__(self)  # Sprite init
        self.name = name
        self.position = position[0] * size, position[1] * size
        self.size = (size, size)

        self.image = Surface((size, size))
        self.rect = self.image.get_rect()
        self.image.fill(color)
        self.rect.update(self.position, self.size)
