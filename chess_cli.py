from utils import notation_to_position, position_to_notation, FILES, RANKS
from pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King

class Chess:
    def __init__(self, fen: str = None):
        self.colors = ["w", "b"]

        fen_string = fen if fen else "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        pieces, turn, castling, enpassant, half_move_clock, full_move_clock = fen_string.split()
        self.board: list[list[Piece]] = self.parse_pieces(pieces)
        self.turn = self.colors.index(turn)
        self.castling: list[bool] = self.parse_castling(castling)
        self.enpassant = enpassant
        self.half_move_clock = int(half_move_clock)
        self.full_move_clock = int(full_move_clock)
        self.attacked_squares: dict[str, list[tuple[int, int]]]
        
        self.kings: tuple[Piece, Piece] = (None, None)
        self.checking_pieces_squares: list[Piece] = []  # bu listenin uzunluğu 0, 1 veya 2 olabilir daha fazlası olursa hata var demektir.
        self.get_kings()
        
        self.get_attacked_squares()
        self.check_check()
        self.get_possible_moves()

    def parse_pieces(self, fen_piece_part: str):
        rows = fen_piece_part.split('/')
        board = [[None for _ in range(8)] for _ in range(8)]

        for r, row in enumerate(rows):
            c = 0
            for char in row:
                if char.isdigit():
                    c += int(char)
                else:
                    color = 'w' if char.isupper() else 'b'
                    piece_type = char.lower()
                    piece = self.create_piece(piece_type, color, (r, c))
                    board[r][c] = piece
                    c += 1
        return board
    
    def create_piece(self, piece_type: str, color: str, position: tuple):
        piece_classes = {
            'p': Pawn,
            'r': Rook,
            'n': Knight,
            'b': Bishop,
            'q': Queen,
            'k': King,
        }
        return piece_classes[piece_type](color, position)

    def get_kings(self):
        wk, bk = None, None
        for row in self.board:
            for piece in row:
                if wk != None and bk != None:
                    self.kings = (wk, bk)
                    return
                if piece:
                    if piece.symbol() == "K":
                        wk = piece
                    elif piece.symbol() == "k":
                        bk = piece

    def parse_castling(self, castling: str) -> list[bool]:
        return [
            "K" in castling,
            "Q" in castling,
            "k" in castling,
            "q" in castling
        ]
        
    def print_board(self):
        for r in self.board:
            for c in r:
                print(c.symbol() if c else "-", end=" ")
            print()
        print()

    def print_game_info(self):
        print("Turn:", self.turn, self.colors[self.turn])
        print("Castling:", self.castling)
        print("En Passant:", self.enpassant)
        print("Half Move:", self.half_move_clock)
        print("Full Move:", self.full_move_clock)

    def make_move(self, move: str):
        """
        Make a move on the board using algebraic notation, e.g., 'e2e4'.
        """
        # check if move is valid
        if (len(move) != 4) or \
            (move[0] not in FILES) or \
            (move[1] not in RANKS) or \
            (move[2] not in FILES) or \
            (move[3] not in RANKS):
            print(f"{move} is not a valid string. Valid string example: 'e2e4'.")
            return False

        # Parse the move
        (start_row, start_col) = notation_to_position(move[:2])
        (end_row, end_col) = notation_to_position(move[2:])

        # Get the piece that will be moved
        piece = self.board[start_row][start_col]
        target_piece = self.board[end_row][end_col]
        if not piece:
            # print(f"No piece at {move[:2]} to move.")
            return False
        if piece.color != self.colors[self.turn]:
            # print(f"It is {self.colors[self.turn]}'s turn.")
            return False
        if (end_row, end_col) not in piece.possible_moves:
            # print("Move is not valid!")
            return False

        self.check_special_cases(piece, target_piece, start_row, start_col, end_row, end_col)
        
        # update the board
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None
        
        # move the piece
        piece.move((end_row, end_col))

        # Update turn and move counters
        self.turn = 1 - self.turn
        self.full_move_clock += 1 if self.turn == 0 else 0
        self.half_move_clock = 0 if isinstance(piece, Pawn) else self.half_move_clock + 1
        self.print_board()
        self.get_attacked_squares()
        self.check_check()
        self.get_possible_moves()
        return True

    def check_special_cases(self, piece: Piece, target_piece: Piece, start_row: int, start_col: int, end_row: int, end_col: int):
        if isinstance(piece, Pawn) and abs(end_row-start_row) == 2:
            # check if pawn moved 2 sq and update enpassant
            self.enpassant = position_to_notation((end_row+1, end_col)) if piece.color == "w" else position_to_notation((end_row-1, end_col))
        elif isinstance(piece, Pawn) and position_to_notation((end_row, end_col)) == self.enpassant:
            # check for enpassant capturing
            if piece.color == "w":
                self.board[end_row+1][end_col] = None
            else:
                self.board[end_row-1][end_col] = None
            self.enpassant = "-"
        elif isinstance(piece, King) and abs(end_col-start_col) == 2:
            # check for castling
            if end_col-start_col == 2:
                rook = self.board[end_row][-1]
                self.board[end_row][end_col-1] = rook
                self.board[end_row][-1] = None
                rook.move((end_row, end_col-1))
            else:
                rook = self.board[end_row][0]
                self.board[end_row][end_col+1] = rook
                self.board[end_row][0] = None
                rook.move((end_row, end_col+1))
            if piece.color == "w":
                self.castling[0] = False
                self.castling[1] = False
            else:
                self.castling[2] = False
                self.castling[3] = False
            self.enpassant = "-"
        elif isinstance(piece, King):
            if not piece.is_moved:
                if piece.color == "w":
                    self.castling[0] = False
                    self.castling[1] = False
                else:
                    self.castling[2] = False
                    self.castling[3] = False
            self.enpassant = "-"
        elif isinstance(piece, Rook):
            if not piece.is_moved:
                match (piece.color, piece.is_king_side):
                    case ("w", True):
                        self.castling[0] = False
                    case ("w", False):
                        self.castling[1] = False
                    case ("b", True):
                        self.castling[2] = False
                    case ("b", False):
                        self.castling[3] = False
                    case _:
                        print("HUH!!!", piece.color, piece.is_king_side)
            self.enpassant = "-"
        elif isinstance(target_piece, Rook):
            match (target_piece.color, target_piece.is_king_side):
                case ("w", True):
                    self.castling[0] = False
                case ("w", False):
                    self.castling[1] = False
                case ("b", True):
                    self.castling[2] = False
                case ("b", False):
                    self.castling[3] = False
                case _:
                    print("HUH!!!", target_piece.color, target_piece.is_king_side)
            self.enpassant = "-"
        else:
            self.enpassant = "-"

    def check_check(self):
        self.checking_pieces = []
        for source, squares in self.attacked_squares.items():
            if self.kings[self.turn].position in squares:
                row, col = notation_to_position(source)
                self.checking_pieces.append(self.board[row][col])

    def get_possible_moves(self) -> None:
        [c.calculate_possible_moves(self.board, self.attacked_squares, self.checking_pieces, self.kings[self.turn].position, self.castling, self.enpassant) for r in self.board for c in r if c and c.color == self.colors[self.turn]]

    def get_attacked_squares(self) -> None:
        self.attacked_squares = {}
        for r in self.board :
            for c in r:
                if c and c.color == self.colors[1-self.turn]:
                    c.calculate_attacked_squares(self.board)
                    if c.attacked_squares:
                        self.attacked_squares[c.position_as_notation] = c.attacked_squares


if __name__ == "__main__":
    chess = Chess()
    chess.print_game_info()
    chess.print_board()
