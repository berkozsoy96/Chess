from enum import Enum


class PieceColor(Enum):
    WHITE = 8
    BLACK = 16


class PieceType(Enum):
    EMPTY = 0
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6
