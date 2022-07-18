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
    def __init__(self, piece_type: PieceType, color: PieceColor):
        Sprite.__init__(self)
        self.piece_type = piece_type
        self.color = color
        
        color_name = "white" if self.color == PieceColor.WHITE else "black"
        self.image = load(f"images/{color_name}_{piece_type.name.lower()}.png")
        self.rect = self.image.get_rect()

    def __str__(self) -> str:
        return f"{self.piece_type.name.lower()}({self.color.name.lower()[0]})"

    def update(self, tile):
        self.image = tile.piece.image
        self.rect.update(tile.position, tile.size)


if __name__ == '__main__':
    import numpy as np

    board = np.ndarray(shape=(8, 8), dtype=Piece)
    print(board)
