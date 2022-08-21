from pygame import Color, Surface
from pygame.sprite import Sprite


class Tile(Sprite):
    def __init__(self, position: tuple[int, int], color: Color, size: int = 75):
        Sprite.__init__(self)  # Sprite init
        self.files = ["a", "b", "c", "d", "e", "f", "g", "h"]
        self.ranks = ["1", "2", "3", "4", "5", "6", "7", "8"][::-1]
        self.position = position
        self.color = color

        self.size = (size, size)
        self.coordinates = (self.position[0]*self.size[0], self.position[1]*self.size[1])
        self.image = Surface((size, size))
        self.rect = self.image.fill(self.color)
        self.rect.update(self.coordinates, self.size)

    def update(self, *args, **kwargs):
        pos = kwargs.get("position", None)
        if pos == self.position:
            file, rank = self.position
            print("Tile", self.files[file]+self.ranks[rank])


class Mouse(Sprite):
    def __init__(self, size: int = 75, coordinates: tuple[int, int] = (0, 0)) -> None:
        Sprite.__init__(self)
        self.size = (size, size)
        self.coordinates = coordinates

        self.image = Surface((size, size))
        self.rect = self.image.fill(Color(255, 255, 255, 0))
        self.rect.update(self.coordinates, self.size)
    
    def update(self, *args, **kwargs):
        coor = kwargs.get("coordinates", None)
        if coor:
            self.coordinates = coor
            self.rect.update(self.coordinates, self.size)
