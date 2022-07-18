from pygame import Color, Surface, mouse
from pygame.sprite import Sprite


class Tile(Sprite):
    def __init__(self, name: str, position: tuple[int, int], piece, color: Color, size: int = 75):
        Sprite.__init__(self)  # Sprite init
        self.name = name
        self.position = position[0] * size, position[1] * size
        self.size = (size, size)
        self.color = color

        self.piece = piece
        if self.piece:
            self.piece.update(self)

        self.image = Surface((size, size))
        self.rect = self.image.fill(self.color)
        self.rect.update(self.position, self.size)

    def update(self, *args, **kwargs):
        x, y = mouse.get_pos()
        if self.rect.left < x < self.rect.right and self.rect.top < y < self.rect.bottom:
            mouse_tile = args[0]
            match (mouse_tile.piece, self.piece):
                case (None, None):
                    # do noting
                    pass
                case (None, p1):
                    mouse_tile.piece = p1
                    mouse_tile.image = p1.image
                    self.piece = None
                    mouse_tile.piece.update(mouse_tile)
                case (p1, None):
                    # TODO:  mousedaki piece i tile a koy ama kurallara uygunsa
                    self.piece = p1
                    mouse_tile.piece = None
                    mouse_tile.image = mouse_tile.default_image
                    self.piece.update(self)
                case (p1, p2):
                    # TODO:  mousedaki piece tile daki peice i yer ama kurallara uygunsa
                    self.piece = p1
                    mouse_tile.piece = None
                    mouse_tile.image = mouse_tile.default_image
                    self.piece.update(self)


class Mouse(Tile):
    def __init__(self, size: int = 75):
        super().__init__("mouse", (0, 0), None, Color(255, 255, 255, a=0), size)
        self.default_image = Surface((size, size))

    def update(self, *args, **kwargs):
        self.position = mouse.get_pos()
        self.rect.update(self.position, self.size)
        if self.piece:
            self.piece.update(self)
