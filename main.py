from piece import PIECES, Color
import numpy as np


class Game:
    def __init__(self):
        pass


class Board:
    def __init__(self, fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        pieces, _, _, _, _, _ = fen.split()
        board = []
        for rank in pieces.split("/"):
            row = []
            for char in rank:
                if char.isdigit():
                    for _ in range(int(char)):
                        row.append(".")
                else:
                    color = Color.BLACK if char.islower() else Color.WHITE
                    row.append(PIECES[char.lower()](color))
            board.append(row)
        self.board = np.array(board)


b = Board()
print(b.board)
