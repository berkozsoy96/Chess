from piece import Piece, Pawn, Knight, Bishop, Rook, Queen, King, PieceColor
import numpy as np


class Board:
    def __init__(self, fen_string=None):
        self.fen_string = fen_string
        self.pieces = {
            "p": Pawn,
            "n": Knight,
            "b": Bishop,
            "r": Rook,
            "q": Queen,
            "k": King
        }
        self.board_state = self.state_from_fen()

    def state_from_fen(self):
        if self.fen_string is None:
            self.fen_string = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        positions, player_turn, available_castles, en_passant, half_moves, full_moves = self.fen_string.split()
        state = np.zeros(shape=(8, 8), dtype=Piece)
        rank = 0
        for row in positions.split("/"):
            file = 0
            for symbol in row:
                if symbol.isdigit():
                    file += int(symbol)
                    continue
                pt, pc = self.pieces[symbol]
                state[rank, file] = pt(pc)
                file += 1
            rank += 1

        return state


board = Board()
print(board.board_state)
