
BOARD_SIZE = 8
TILE_SIZE = 100

class Chess:
    files: str = "hgfedcba"
    ranks: str = "12345678"
    colors = ["w", "b"]

    def __init__(self, fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        pieces, turn, castling, enpassant, half_move_clock, full_move_clock = fen.split()
        self.board = self.parse_pieces(pieces)
        self.turn = Chess.colors.index(turn)
        self.castling = castling
        self.enpassant = enpassant
        self.half_move_clock = int(half_move_clock)
        self.full_move_clock = int(full_move_clock)

    def parse_pieces(self, fen_piece_part: str):
        rows = fen_piece_part.split('/')
        board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        for r, row in enumerate(rows):
            c = 0
            for char in row:
                if char.isdigit():
                    c += int(char)
                else:
                    board[r][c] = char
                    # color = 'white' if char.isupper() else 'black'
                    # piece = None
                    # if char.lower() == 'p':
                    #     piece = Pawn(color, (r, c))
                    # elif char.lower() == 'r':
                    #     piece = Rook(color, (r, c))
                    # # Add other pieces here as needed
                    # if piece:
                    #     board[r][c] = piece
                    c += 1
        return board

    def print_board(self):
        for r in self.board:
            for c in r:
                print(c if c else "-", end=" ")
            print()
        print()


class Piece:
    def __init__(self, color: str, name: str):
        self.color = color
        self.name = name


chess = Chess()
chess.print_board()
