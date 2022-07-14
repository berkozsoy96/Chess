from pygame.transform import scale
from pygame.sprite import Sprite
from pygame.image import load
from pygame import mouse

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
    def __init__(self, piece_type: PieceType, color: PieceColor, tile):
        Sprite.__init__(self)  # Sprite init
        self.piece_type = piece_type
        self.color = color
        self.tile = tile
        
        color_name = "white" if self.color == PieceColor.WHITE else "black"
        self.image = load(f"images/{color_name}_{piece_type.name.lower()}.png")
        self.image = scale(self.image, self.tile.size)
        
        self.rect = self.image.get_rect()
        self.rect.update(self.tile.position, self.tile.size)
    
    def __str__(self) -> str:
        return f"{self.color.name.lower()} {self.piece_type.name.lower()}"

    def update(self):
        x, y = mouse.get_pos()
        if self.rect.left < x < self.rect.right and self.rect.top < y < self.rect.bottom:
            print(self.tile.name, self.piece_type, self.color)
