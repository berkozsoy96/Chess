FILES = "abcdefgh"
RANKS = "87654321"


def notation_to_position(notation: str) -> tuple[int, int]:
    """
    Convert a chess notation like 'e4' to (4, 4) (row, col).
    """
    col = FILES.index(notation[0])
    row = RANKS.index(notation[1])
    return (row, col)

def position_to_notation(position: tuple[int, int]) -> str:
    """
    Convert a chess position like (4, 4) (row, col) to 'e4'.
    """
    # position is (row, col) -> (ranks, files)
    return f"{FILES[position[1]]}{RANKS[position[0]]}"


class Piece:
    def __init__(self, color: str, position: tuple[int, int]):
        self.color: str = color
        self.is_moved: bool = False  # store if the piece is ever moved. This stays true even if piece returns to its original place.

        self.position: tuple[int, int] = position  # (r, c) - (rank, file)
        self.position_as_notation: str = position_to_notation(self.position)
        
        self.possible_moves: list[tuple[int, int]] = []
        self.attacked_squares: list[tuple[int, int]] = []
    
    def move(self, pos: tuple[int, int]) -> None:
        self.position = pos
        self.position_as_notation = f"{FILES[pos[1]]}{RANKS[pos[0]]}"
        self.is_moved = True

    def symbol(self) -> str:
        raise NotImplementedError("This method should be implemented by subclasses.")

    def calculate_possible_moves(self, board: list[list["Piece"]], attacked_squares: dict[str, list[tuple[int, int]]], castling: str = "-", enpassant: str = "-") -> None:
        raise NotImplementedError("This method should be implemented by subclasses.")

    def calculate_attacked_squares(self, board: list[list["Piece"]]) -> None:
        raise NotImplementedError("This method should be implemented by subclasses.")

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
        self.get_attacked_squares()
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

    def get_possible_moves(self) -> None:
        [c.calculate_possible_moves(self.board, self.attacked_squares, self.castling, self.enpassant) for r in self.board for c in r if c and c.color == self.colors[self.turn]]

    def get_attacked_squares(self) -> None:
        self.attacked_squares = {}
        for r in self.board :
            for c in r:
                if c and c.color == self.colors[1-self.turn]:
                    c.calculate_attacked_squares(self.board)
                    if c.attacked_squares:
                        self.attacked_squares[c.position_as_notation] = c.attacked_squares


class Pawn(Piece):
    def symbol(self) -> str:
        return "P" if self.color == 'w' else "p"

    def calculate_possible_moves(self, board: list[list["Piece"]], attacked_squares: dict[str, list[tuple[int, int]]], castling: str = "-", enpassant: str = "-") -> None:
        self.possible_moves = []  # Clear previous moves
        direction = -1 if self.color == 'w' else 1  # Pawns move up (-1) for white, down (+1) for black

        row, col = self.position

        # Forward movement by 1
        if (0 <= row + direction < 8) and (board[row + direction][col] is None):
            self.possible_moves.append((row + direction, col))

            # Double forward movement if on starting rank
            if (not self.is_moved) and (board[row + 2 * direction][col] is None):
                self.possible_moves.append((row + 2 * direction, col))

        # Captures
        for dc in [-1, 1]:  # Diagonal left (-1) and right (+1)
            new_col = col + dc
            if (0 <= new_col < 8) and (0 <= row + direction < 8):
                target_piece = board[row + direction][new_col]
                if target_piece and target_piece.color != self.color:
                    self.possible_moves.append((row + direction, new_col))

        # En Passant
        if enpassant != "-":
            en_row, en_col = notation_to_position(enpassant)
            if abs(en_col - col) == 1 and en_row == row + direction:
                self.possible_moves.append((en_row, en_col))

    def calculate_attacked_squares(self, board: list[list["Piece"]]):
        self.attacked_squares = []
        direction = -1 if self.color == 'w' else 1  # Pawns move up (-1) for white, down (+1) for black
        row, col = self.position
        
        for dc in [-1, 1]:  # Diagonal left (-1) and right (+1)
            new_col = col + dc
            if (0 <= new_col < 8) and (0 <= row + direction < 8):
                target_piece = board[row + direction][new_col]
                if not target_piece or target_piece.color != self.color:
                    self.attacked_squares.append((row + direction, new_col))


class Rook(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.is_king_side = False if position[1] == 0 else True
    
    def symbol(self):
        return "R" if self.color == 'w' else "r"

    def calculate_possible_moves(self, board: list[list["Piece"]], attacked_squares: dict[str, list[tuple[int, int]]], castling: str = "-", enpassant: str = "-") -> None:
        self.possible_moves = []  # Clear previous moves

        # Define directions for rook movement (horizontal and vertical)
        directions = [
            (-1, 0), (1, 0),  # Vertical: up, down
            (0, -1), (0, 1)   # Horizontal: left, right
        ]

        row, col = self.position

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = board[new_row][new_col]

                if not target_piece:
                    # If the square is empty, add it to possible moves
                    self.possible_moves.append((new_row, new_col))
                elif target_piece.color != self.color:
                    # If the square contains an opponent's piece, add it and stop further movement
                    self.possible_moves.append((new_row, new_col))
                    break
                else:
                    # If the square contains a piece of the same color, stop further movement
                    break

                # Move further in the current direction
                new_row += dr
                new_col += dc

    def calculate_attacked_squares(self, board: list[list["Piece"]]):
        self.attacked_squares = []
        directions = [
            (-1, 0), (1, 0),  # Vertical: up, down
            (0, -1), (0, 1)   # Horizontal: left, right
        ]

        row, col = self.position

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = board[new_row][new_col]

                if not target_piece:
                    # If the square is empty, add it to possible moves
                    self.attacked_squares.append((new_row, new_col))
                elif target_piece.color != self.color:
                    # If the square contains an opponent's piece, add it and stop further movement
                    self.attacked_squares.append((new_row, new_col))
                    break
                else:
                    # If the square contains a piece of the same color, stop further movement
                    break

                # Move further in the current direction
                new_row += dr
                new_col += dc


class Knight(Piece):
    def symbol(self):
        return "N" if self.color == 'w' else "n"

    def calculate_possible_moves(self, board: list[list["Piece"]], attacked_squares: dict[str, list[tuple[int, int]]], castling: str = "-", enpassant: str = "-") -> None:
        self.possible_moves = []  # Clear previous moves

        # Define all potential moves for a knight
        knight_moves = [
            (-2, -1), (-2, 1),  # Two up, one left/right
            (-1, -2), (-1, 2),  # One up, two left/right
            (1, -2), (1, 2),    # One down, two left/right
            (2, -1), (2, 1)     # Two down, one left/right
        ]

        row, col = self.position

        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc

            # Ensure the new position is within the board bounds
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = board[new_row][new_col]

                # Add the move if the target square is empty or contains an opponent's piece
                if not target_piece or target_piece.color != self.color:
                    self.possible_moves.append((new_row, new_col))

    def calculate_attacked_squares(self, board):
        self.attacked_squares = []
        # Define all potential moves for a knight
        knight_moves = [
            (-2, -1), (-2, 1),  # Two up, one left/right
            (-1, -2), (-1, 2),  # One up, two left/right
            (1, -2), (1, 2),    # One down, two left/right
            (2, -1), (2, 1)     # Two down, one left/right
        ]

        row, col = self.position

        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc

            # Ensure the new position is within the board bounds
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = board[new_row][new_col]

                # Add the move if the target square is empty or contains an opponent's piece
                if not target_piece or target_piece.color != self.color:
                    self.attacked_squares.append((new_row, new_col))


class Bishop(Piece):
    def symbol(self):
        return "B" if self.color == 'w' else "b"

    def calculate_possible_moves(self, board: list[list["Piece"]], attacked_squares: dict[str, list[tuple[int, int]]], castling: str = "-", enpassant: str = "-") -> None:
        self.possible_moves = []  # Clear previous moves

        # Define directions for diagonal movement
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Top-left, top-right, bottom-left, bottom-right

        row, col = self.position

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = board[new_row][new_col]

                if not target_piece:
                    # If the square is empty, add it to possible moves
                    self.possible_moves.append((new_row, new_col))
                elif target_piece.color != self.color:
                    # If the square contains an opponent's piece, add it and stop further movement
                    self.possible_moves.append((new_row, new_col))
                    break
                else:
                    # If the square contains a piece of the same color, stop further movement
                    break

                # Move further in the current direction
                new_row += dr
                new_col += dc
    
    def calculate_attacked_squares(self, board):
        self.attacked_squares = []
         # Define directions for diagonal movement
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Top-left, top-right, bottom-left, bottom-right

        row, col = self.position

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = board[new_row][new_col]

                if not target_piece:
                    # If the square is empty, add it to possible moves
                    self.attacked_squares.append((new_row, new_col))
                elif target_piece.color != self.color:
                    # If the square contains an opponent's piece, add it and stop further movement
                    self.attacked_squares.append((new_row, new_col))
                    break
                else:
                    # If the square contains a piece of the same color, stop further movement
                    break

                # Move further in the current direction
                new_row += dr
                new_col += dc


class Queen(Piece):
    def symbol(self):
        return "Q" if self.color == 'w' else "q"

    def calculate_possible_moves(self, board: list[list["Piece"]], attacked_squares: dict[str, list[tuple[int, int]]], castling: str = "-", enpassant: str = "-") -> None:
        self.possible_moves = []  # Clear previous moves

        # Define directions for queen movement (horizontal, vertical, and diagonal)
        directions = [
            (-1, 0), (1, 0),  # Vertical: up, down
            (0, -1), (0, 1),  # Horizontal: left, right
            (-1, -1), (-1, 1),  # Diagonal: top-left, top-right
            (1, -1), (1, 1)    # Diagonal: bottom-left, bottom-right
        ]

        row, col = self.position

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = board[new_row][new_col]

                if not target_piece:
                    # If the square is empty, add it to possible moves
                    self.possible_moves.append((new_row, new_col))
                elif target_piece.color != self.color:
                    # If the square contains an opponent's piece, add it and stop further movement
                    self.possible_moves.append((new_row, new_col))
                    break
                else:
                    # If the square contains a piece of the same color, stop further movement
                    break

                # Move further in the current direction
                new_row += dr
                new_col += dc

    def calculate_attacked_squares(self, board):
        self.attacked_squares = []

        # Define directions for queen movement (horizontal, vertical, and diagonal)
        directions = [
            (-1, 0), (1, 0),  # Vertical: up, down
            (0, -1), (0, 1),  # Horizontal: left, right
            (-1, -1), (-1, 1),  # Diagonal: top-left, top-right
            (1, -1), (1, 1)    # Diagonal: bottom-left, bottom-right
        ]

        row, col = self.position

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = board[new_row][new_col]

                if not target_piece:
                    # If the square is empty, add it to possible moves
                    self.attacked_squares.append((new_row, new_col))
                elif target_piece.color != self.color:
                    # If the square contains an opponent's piece, add it and stop further movement
                    self.attacked_squares.append((new_row, new_col))
                    break
                else:
                    # If the square contains a piece of the same color, stop further movement
                    break

                # Move further in the current direction
                new_row += dr
                new_col += dc


class King(Piece):
    def symbol(self):
        return "K" if self.color == 'w' else "k"

    def calculate_possible_moves(self, board: list[list["Piece"]], attacked_squares: dict[str, list[tuple[int, int]]], castling: list[bool], enpassant: str = "-") -> None:
        self.possible_moves = []  # Clear previous moves

        # Define all possible movement directions for the king
        directions = [
            (-1, 0), (1, 0),  # Vertical: up, down
            (0, -1), (0, 1),  # Horizontal: left, right
            (-1, -1), (-1, 1),  # Diagonal: top-left, top-right
            (1, -1), (1, 1)    # Diagonal: bottom-left, bottom-right
        ]

        asf = list(set([m for _, squares in attacked_squares.items() for m in squares]))
        row, col = self.position

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = board[new_row][new_col]
                if (new_row, new_col) in asf:
                    continue
                if not target_piece or target_piece.color != self.color:
                    # Add square if empty or occupied by opponent
                    self.possible_moves.append((new_row, new_col))

        # Check castling possibilities
        if not self.is_moved:
            if self.color == 'w':
                # White castling
                if castling[0] and self.can_castle_kingside(board, asf, row, col):
                    self.possible_moves.append((row, col + 2))
                if castling[1] and self.can_castle_queenside(board, asf, row, col):
                    self.possible_moves.append((row, col - 2))
            else:
                # Black castling
                if castling[2] and self.can_castle_kingside(board, asf, row, col):
                    self.possible_moves.append((row, col + 2))
                if castling[3] and self.can_castle_queenside(board, asf, row, col):
                    self.possible_moves.append((row, col - 2))

    def can_castle_kingside(self, board: list[list["Piece"]], attacked_squares: list[tuple[int, int]], row: int, col: int) -> bool:
        # Check if squares between king and kingside rook are empty, not attacked and rook is unmoved
        
        return (
            (row, col) not in attacked_squares and  # cannot castle through check
            board[row][col + 1] is None and (row, col + 1) not in attacked_squares and
            board[row][col + 2] is None and (row, col + 2) not in attacked_squares and
            isinstance(board[row][7], Rook) and
            not board[row][7].is_moved and
            board[row][7].color == self.color
        )

    def can_castle_queenside(self, board: list[list["Piece"]], attacked_squares: list[tuple[int, int]], row: int, col: int) -> bool:
        # Check if squares between king and queenside rook are empty, not attacked and rook is unmoved
        
        return (
            (row, col) not in attacked_squares and  # cannot castle through check
            board[row][col - 1] is None and (row, col - 1) not in attacked_squares and
            board[row][col - 2] is None and (row, col - 2) not in attacked_squares and
            board[row][col - 3] is None and (row, col - 3) not in attacked_squares and
            isinstance(board[row][0], Rook) and
            not board[row][0].is_moved and
            board[row][0].color == self.color
        )

    def calculate_attacked_squares(self, board):
        self.attacked_squares = []
        # Define all possible movement directions for the king
        directions = [
            (-1, 0), (1, 0),  # Vertical: up, down
            (0, -1), (0, 1),  # Horizontal: left, right
            (-1, -1), (-1, 1),  # Diagonal: top-left, top-right
            (1, -1), (1, 1)    # Diagonal: bottom-left, bottom-right
        ]

        row, col = self.position

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = board[new_row][new_col]

                if not target_piece or target_piece.color != self.color:
                    # Add square if empty or occupied by opponent
                    self.attacked_squares.append((new_row, new_col))

if __name__ == "__main__":
    chess = Chess()
    chess.print_game_info()
    chess.print_board()
