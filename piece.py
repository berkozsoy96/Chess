from dataclasses import dataclass
from enum import Enum


class Color(Enum):
    WHITE = 0
    BLACK = 8


@dataclass
class Piece:
    color: Color
    is_moved: bool = False


@dataclass
class King(Piece):
    can_castle: bool = True
    repr: str = "k"


@dataclass
class Quenn(Piece):
    value: int = 9


@dataclass
class Rook(Piece):
    can_castle: bool = True
    value: int = 5


@dataclass
class Knight(Piece):
    value: int = 3


@dataclass
class Bishop(Piece):
    value: int = 3


@dataclass
class Pawn(Piece):
    value: int = 1


PIECES = {
    "p": Pawn,
    "n": Knight,
    "b": Bishop,
    "r": Rook,
    "q": Quenn,
    "k": King
}
