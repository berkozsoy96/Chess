from piece import PieceType, PieceColor, Piece


class FenParser:
    @staticmethod
    def parse(fen_string, board, sprite_list):
        piece_type_from_symbol = {
            "p": PieceType.PAWN,
            "n": PieceType.KNIGHT,
            "b": PieceType.BISHOP,
            "r": PieceType.ROOK,
            "q": PieceType.QUEEN,
            "k": PieceType.KING
        }

        pieces, _, _, _, _, _ = fen_string.split()
        for rank, row in enumerate(pieces.split("/")):
            file = 0
            for symbol in row:
                if symbol.isdigit():
                    file += int(symbol)
                    continue
                color = PieceColor.BLACK if symbol.islower() else PieceColor.WHITE
                piece_type = piece_type_from_symbol[symbol.lower()]
                piece = Piece(piece_type, color)
                board[rank, file] = piece
                sprite_list.add(piece)
                file += 1
