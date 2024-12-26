class Chess:
    def __init__(self, fen: str = None):
        self.files = "abcdefgh"
        self.ranks = "87654321"
        self.colors = ["w", "b"]

        fen_string = fen if fen else "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        pieces, turn, castling, enpassant, half_move_clock, full_move_clock = fen_string.split()
        self.board: list[list[Piece]] = self.parse_pieces(pieces)
        self.turn = self.colors.index(turn)
        self.castling: list[bool] = self.parse_castling(castling)
        self.enpassant = enpassant
        self.half_move_clock = int(half_move_clock)
        self.full_move_clock = int(full_move_clock)
        self.call_calculate_possible_moves_for_every_piece()

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
            (move[0] not in self.files) or \
            (move[1] not in self.ranks) or \
            (move[2] not in self.files) or \
            (move[3] not in self.ranks):
            print(f"{move} is not a valid string. Valid string example: 'e2e4'.")
            return False

        # Parse the move
        (start_row, start_col) = self.notation_to_position(move[:2])
        (end_row, end_col) = self.notation_to_position(move[2:])

        # Get the piece that will be moved
        piece = self.board[start_row][start_col]
        if not piece:
            print(f"No piece at {move[:2]} to move.")
            return False
        if piece.color != self.colors[self.turn]:
            print(f"It is {self.colors[self.turn]}'s turn.")
            return False
        if (end_row, end_col) not in piece.possible_moves:
            print("Move is not valid!")
            return False

        # CHECK MOVE
        if isinstance(piece, Pawn) and abs(end_row-start_row) == 2:
            # check if pawn moved 2 sq and update enpassant
            self.enpassant = self.position_to_notation((end_row+1, end_col)) if piece.color == "w" else self.position_to_notation((end_row-1, end_col))
        elif isinstance(piece, Pawn) and move[2:] == self.enpassant:
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
            if piece.color == "w":
                self.castling[0] = False
                self.castling[1] = False
            else:
                self.castling[2] = False
                self.castling[3] = False
            self.enpassant = "-"
            pass
        elif isinstance(piece, Rook):
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
        else:
            self.enpassant = "-"
        # default move or capture
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None
        piece.move((end_row, end_col))

        # Update turn and move counters
        self.turn = 1 - self.turn
        self.full_move_clock += 1 if self.turn == 0 else 0
        self.half_move_clock = 0 if isinstance(piece, Pawn) else self.half_move_clock + 1
        self.print_board()
        self.call_calculate_possible_moves_for_every_piece()
        return True

    def notation_to_position(self, notation: str) -> tuple[int, int]:
        """
        Convert a chess position like 'e4' to (row, col).
        """
        col = self.files.index(notation[0])
        row = self.ranks.index(notation[1])
        return (row, col)

    def position_to_notation(self, position: tuple[int, int]) -> str:
        # position is (row, col) -> (ranks, files)
        return f"{self.files[position[1]]}{self.ranks[position[0]]}"

    def call_calculate_possible_moves_for_every_piece(self):
        [c.calculate_possible_moves(self.board, self.castling, self.enpassant) for r in self.board for c in r if c]

class Piece:
    def __init__(self, color: str, position: tuple[int, int]):
        self.files = "abcdefgh"
        self.ranks = "87654321"
        self.color = color
        self.is_moved = False

        self.position = position  # (r, c) - (rank, file)
        self.position_as_notation = f"{self.files[position[1]]}{self.ranks[position[0]]}"
        
        self.possible_moves = []
    
    def move(self, pos: tuple) -> None:
        self.position = pos
        self.position_as_notation = f"{self.files[pos[1]]}{self.ranks[pos[0]]}"
        self.is_moved = True

    def symbol(self) -> str:
        raise NotImplementedError("This method should be implemented by subclasses.")

    def calculate_possible_moves(self, board: list[list["Piece"]], castling: str = "-", enpassant: str = "-") -> None:
        # TODO: write this function for every piece
        raise NotImplementedError("This method should be implemented by subclasses.")


class Pawn(Piece):
    def symbol(self) -> str:
        return "P" if self.color == 'w' else "p"

    def calculate_possible_moves(self, board: list[list["Piece"]], castling: str = "-", enpassant: str = "-") -> None:
        if not self.is_moved:
            if self.color == "w":
                return [(self.position[0]-1, self.position[1]), (self.position[0]-2, self.position[1])]
            if self.color == "b":
                return [(self.position[0]+1, self.position[1]), (self.position[0]+2, self.position[1])]
        else:
            if self.color == "w":
                return [(self.position[0]-1, self.position[1])]
            if self.color == "b":
                return [(self.position[0]+1, self.position[1])]

class Rook(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.is_king_side = False if position[1] == 0 else True
    
    def symbol(self):
        return "R" if self.color == 'w' else "r"

    def calculate_possible_moves(self):
        return []

class Knight(Piece):
    def symbol(self):
        return "N" if self.color == 'w' else "n"

    def calculate_possible_moves(self):
        return []

class Bishop(Piece):
    def symbol(self):
        return "B" if self.color == 'w' else "b"

    def calculate_possible_moves(self):
        return []

class Queen(Piece):
    def symbol(self):
        return "Q" if self.color == 'w' else "q"

    def calculate_possible_moves(self):
        return []

class King(Piece):
    def symbol(self):
        return "K" if self.color == 'w' else "k"

    def calculate_possible_moves(self):
        return []


chess = Chess()
chess.print_game_info()
chess.print_board()
