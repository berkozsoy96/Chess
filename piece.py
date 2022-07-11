import cv2
import numpy as np
from enum import Enum
from dataclasses import dataclass, field


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


@dataclass
class Piece:
    piece_color: PieceColor
    piece_type: PieceType
    piece_letter: str

    is_alive: bool = True
    is_moved: bool = False
    legal_moves: list = field(default_factory=[])

    piece_image: np.ndarray | None = None


class Pawn(Piece):
    def __init__(self, piece_color: PieceColor):
        fen_letter = "p"
        name = "pawn"
        piece_letter, image_name = (fen_letter, "black_" + name) if piece_color == PieceColor.BLACK else (fen_letter.upper(), "white_" + name)
        super().__init__(piece_color, PieceType.PAWN, piece_letter=piece_letter,
                         piece_image=cv2.imread(f"images/{image_name}.png", cv2.IMREAD_UNCHANGED))


if __name__ == '__main__':
    p = Pawn(PieceColor.BLACK)
    cv2.imshow("asd", p.piece_image)
    cv2.waitKey()
