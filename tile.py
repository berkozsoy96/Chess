from pygame import Color, Surface, mouse
from pygame.sprite import Sprite


class Tile(Sprite):
    def __init__(self, name: str, position: tuple[int, int], color: Color, size:int = 75, piece=None):
        Sprite.__init__(self)  # Sprite init
        self.name = name
        self.position = position[0] * size, position[1] * size
        self.size = (size, size)

        self.image = Surface((size, size))
        self.rect = self.image.get_rect()
        self.image.fill(color)
        self.rect.update(self.position, self.size)

        self.piece = piece
    
    def update(self):
        x, y = mouse.get_pos()
        if self.rect.left < x < self.rect.right and self.rect.top < y < self.rect.bottom:
            print(self.name, end="")
            if self.piece is not None:
                print(" -", self.piece)
            else:
                print()
            
