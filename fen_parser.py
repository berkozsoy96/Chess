from piece import PieceType, PieceColor
import numpy as np


class FenParser:
    @staticmethod
    def parse(fen_string):
        piece_type_from_symbol = {
            "p": PieceType.PAWN,
            "n": PieceType.KNIGHT,
            "b": PieceType.BISHOP,
            "r": PieceType.ROOK,
            "q": PieceType.QUEEN,
            "k": PieceType.KING
        }

        pieces, _, _, _, _, _ = fen_string.split()
        board = np.zeros(shape=(8, 8), dtype="uint8")
        for rank, row in enumerate(pieces.split("/")):
            for file, symbol in enumerate(row):
                if not symbol.isdigit():
                    color = PieceColor.BLACK if symbol.islower() else PieceColor.WHITE
                    board[rank, file] = piece_type_from_symbol[symbol.lower()].value | color.value
        return board


if __name__ == '__main__':
    # starter fen: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    board = FenParser.parse("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    print(board)
