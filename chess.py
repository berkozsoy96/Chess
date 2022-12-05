import numpy as np
from enum import Enum


class PT(int, Enum):  # piecetype = pt
    king = 6
    queen = 5
    rook = 4
    knight = 3
    bishop = 2
    pawn = 1


class PC(int, Enum):  # piececolor = pc
    black = 8
    white = 0


class Board:
    def __init__(self) -> None:
        self.board = np.zeros((8, 8), dtype=np.uint8)
        self.files = "abcdefgh"
        self.ranks = "87654321"

    def fill_board(self, fen_string=None):
        b = PC.black
        w = PC.white
        if not fen_string:
            self.board[0, :] = [
                b+PT.rook, b+PT.knight, b+PT.bishop, b+PT.queen, b+PT.king, b+PT.bishop, b+PT.knight, b+PT.rook,
            ]
            self.board[1, :] = [b+PT.pawn] * 8
            self.board[6, :] = [w+PT.pawn] * 8
            self.board[7, :] = [
                w+PT.rook, w+PT.knight, w+PT.bishop, w+PT.queen, w+PT.king, w+PT.bishop, w+PT.knight, w+PT.rook,
            ]
        else:
            print("fen_parser is not implemented.")

    def move(self, from_sq:str = None, to_sq: str = None):
        if not from_sq:
            from_sq = input("from: ")
        if not to_sq:
            to_sq = input("to: ")

        fy, fx = self.ranks.index(from_sq[1]), self.files.index(from_sq[0])
        ty, tx = self.ranks.index(to_sq[1]), self.files.index(to_sq[0])
        self.board[ty, tx] = self.board[fy, fx]
        self.board[fy, fx] = 0


board = Board()
board.fill_board()
print(board.board)
