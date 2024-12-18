class Chess:
    def __init__(self, fen: str = None):
        self.files = "abcdefgh"
        self.ranks = "87654321"
        self.colors = ["w", "b"]

        fen_string = fen if fen else "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        pieces, turn, castling, enpassant, half_move_clock, full_move_clock = fen_string.split()
        self.board: list[list[Piece]] = self.parse_pieces(pieces)
        self.turn = self.colors.index(turn)
        self.castling = castling
        self.enpassant = enpassant
        self.half_move_clock = int(half_move_clock)
        self.full_move_clock = int(full_move_clock)

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

    def print_board(self):
        for r in self.board:
            for c in r:
                c: Piece
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
        # Parse the move
        (start_row, start_col) = self.parse_position(move[:2])
        (end_row, end_col) = self.parse_position(move[2:])

        # Get the piece to move
        piece = self.board[start_row][start_col]
        if not piece:
            print(f"No piece at {move[1]}{move[0]} to move.")
            return False
        if piece.color != self.colors[self.turn]:
            print(f"It is {self.colors[self.turn]}'s turn.")
            return False
        if (end_row, end_col) not in piece.possible_moves:
            print("Move is not valid!")
            return False

        # Move the piece
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None

        # Update piece position
        piece.move((end_row, end_col))

        # Handle special rules
        # self.handle_special_rules(piece, start_row, start_col, end_row, end_col)

        # Update turn and move counters
        self.turn = 1 - self.turn
        self.full_move_clock += 1 if self.turn == 0 else 0
        self.half_move_clock = 0 if isinstance(piece, Pawn) else self.half_move_clock + 1
        self.print_board()
        return True

    def handle_special_rules(self, piece, start_row, start_col, end_row, end_col):
        """
        Handle special chess rules like capturing, en passant, castling, and pawn promotion.
        """
        # Capture
        if self.board[end_row][end_col] and self.board[end_row][end_col].color != piece.color:
            self.board[end_row][end_col] = None
            self.half_move_clock = 0

        # En passant
        if isinstance(piece, Pawn) and self.enpassant != "-" and (end_row, end_col) == self.parse_position(self.enpassant):
            capture_row = start_row + (1 if piece.color == 'black' else -1)
            self.board[capture_row][end_col] = None

        # Pawn promotion
        if isinstance(piece, Pawn) and (end_row == 0 or end_row == 7):
            self.board[end_row][end_col] = Queen(piece.color, (end_row, end_col))

        # Castling
        if isinstance(piece, King) and abs(end_col - start_col) == 2:
            rook_start_col = 0 if end_col < start_col else 7
            rook_end_col = 3 if end_col < start_col else 5
            rook = self.board[start_row][rook_start_col]
            self.board[start_row][rook_end_col] = rook
            self.board[start_row][rook_start_col] = None
            rook.position = (start_row, rook_end_col)

    def parse_position(self, pos: str):
        """
        Convert a chess position like 'e4' to (row, col).
        """
        col = self.files.index(pos[0])
        row = self.ranks.index(pos[1])
        return (row, col)


class Piece:
    def __init__(self, color: str, position: tuple):
        self.color = color
        self.position = position
        self.possible_moves = []
    
    def move(self, pos: tuple):
        self.position = pos

    def symbol(self):
        raise NotImplementedError("This method should be implemented by subclasses.")

    def calculate_possible_moves(self):
        raise NotImplementedError("This method should be implemented by subclasses.")


class Pawn(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.is_first_move = True
        self.possible_moves = self.calculate_possible_moves()

    def move(self, pos: tuple):
        self.position = pos
        self.is_first_move = False
        self.possible_moves = self.calculate_possible_moves()
    
    def symbol(self):
        return "P" if self.color == 'w' else "p"

    def calculate_possible_moves(self):
        if self.is_first_move:
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
