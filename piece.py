from pygame.sprite import Sprite
from pygame.image import load

from enum import Enum, auto


class PieceColor(Enum):
    WHITE = auto()
    BLACK = auto()


class PieceType(Enum):
    PAWN = auto()
    KNIGHT = auto()
    BISHOP = auto()
    KING = auto()
    QUEEN = auto()
    ROOK = auto()


class Piece(Sprite):
    def __init__(self, piece_type: PieceType, color: PieceColor, position: tuple[int, int], size: int = 75):
        Sprite.__init__(self)
        self.piece_type = piece_type
        self.position = position
        self.color = color
        self.size = (size, size)
        
        color_name = "white" if self.color == PieceColor.WHITE else "black"
        self.image = load(f"images/{color_name}_{piece_type.name.lower()}.png")
        self.coordinates = (self.position[0]*self.size[0], self.position[1]*self.size[1])
        self.rect = self.image.get_rect()
        self.rect.update(self.coordinates, self.size)

    def __str__(self) -> str:
        return f"{self.piece_type.name.lower()}({self.color.name.lower()[0]})"

    def __repr__(self) -> str:
        return f"{self.piece_type.name.lower()}({self.color.name.lower()[0]})"

    def update(self, *args, **kwargs):
        pos = kwargs.get("position", None)
        if pos == self.position:
            print("Piece", self.position)
        # self.position = (x, y)
        # self.coordinates = (self.position[0]*self.size[0], self.position[1]*self.size[1])
        # self.rect.update(self.coordinates, self.size)
        pass
