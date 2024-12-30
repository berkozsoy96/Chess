from utils import notation_to_position, position_to_notation, FILES, RANKS

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

    def check_if_move_blocks_or_captures(self, move: tuple[int, int], checking_piece: "Piece", king_square: tuple[int, int], is_current_piece_king: bool = False) -> bool:
        if isinstance(checking_piece, (Knight, Pawn)):
            return move == checking_piece_square
        
        checking_piece_square = checking_piece.position
        direction = (checking_piece_square[0] - king_square[0], checking_piece_square[1] - king_square[1])
        if is_current_piece_king:
            opposite_direction = (0 if direction[0] == 0 else -(direction[0]/abs(direction[0])), 0 if direction[1] == 0 else -(direction[1]/abs(direction[1])))
            return move != (king_square[0] + opposite_direction[0], king_square[1] + opposite_direction[1])
        if direction[0] == 0:  # Horizontal check
            if abs(direction[1]) == 1:
                return move == checking_piece_square
            if move[0] == king_square[0]:
                l, r = min(king_square[1], checking_piece_square[1]), max(king_square[1], checking_piece_square[1])
                if l < move[1] < r:
                    return True
        elif direction[1] == 0: # Vertical check
            if abs(direction[0]) == 1:
                return move == checking_piece_square
            if move[1] == king_square[1]:
                t, b = min(king_square[0], checking_piece_square[0]), max(king_square[0], checking_piece_square[0])
                if t < move[0] < b:
                    return True
        else:  # diagonal check
            if abs(direction[0]) == 1:
                return move == checking_piece_square
            # vertical direction from king to checking piece
            vd = 1 if direction[0] > 0 else -1
            # horizontal direction from king to checking piece
            hd = 1 if direction[1] > 0 else -1
            for i in range(1, abs(direction[0])):
                if move == (king_square[0] + i*vd, king_square[1] + i*hd):
                    return True
        return False

    def calculate_possible_moves(self, board: list[list["Piece"]], attacked_squares: dict[str, list[tuple[int, int]]], checking_pieces: list["Piece"], king_square: tuple[int, int], castling: str = "-", enpassant: str = "-") -> None:
        raise NotImplementedError("This method should be implemented by subclasses.")

    def calculate_attacked_squares(self, board: list[list["Piece"]]) -> None:
        raise NotImplementedError("This method should be implemented by subclasses.")


class Pawn(Piece):
    def symbol(self) -> str:
        return "P" if self.color == 'w' else "p"

    def calculate_possible_moves(self, board: list[list["Piece"]], attacked_squares: dict[str, list[tuple[int, int]]], checking_pieces: list["Piece"], king_square: tuple[int, int], castling: str = "-", enpassant: str = "-") -> None:
        self.possible_moves = []  # Clear previous moves
        direction = -1 if self.color == 'w' else 1  # Pawns move up (-1) for white, down (+1) for black

        row, col = self.position
        if len(checking_pieces) == 2:
            return
        
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
        
        if len(checking_pieces) == 0:
            return

        # Filter moves that counters the check
        filtered_moves = []
        for move in self.possible_moves:
            if self.check_if_move_blocks_or_captures(move, checking_pieces[0], king_square):
                filtered_moves.append(move)
        self.possible_moves = filtered_moves

    def calculate_attacked_squares(self, board: list[list["Piece"]]):
        self.attacked_squares = []
        direction = -1 if self.color == 'w' else 1  # Pawns move up (-1) for white, down (+1) for black
        row, col = self.position
        
        for dc in [-1, 1]:  # Diagonal left (-1) and right (+1)
            new_col = col + dc
            if (0 <= new_col < 8) and (0 <= row + direction < 8):
                self.attacked_squares.append((row + direction, new_col))


class Rook(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.is_king_side = False if position[1] == 0 else True
    
    def symbol(self):
        return "R" if self.color == 'w' else "r"

    def calculate_possible_moves(self, board: list[list["Piece"]], attacked_squares: dict[str, list[tuple[int, int]]], checking_pieces: list["Piece"], king_square: tuple[int, int], castling: str = "-", enpassant: str = "-") -> None:
        self.possible_moves = []  # Clear previous moves

        # Define directions for rook movement (horizontal and vertical)
        directions = [
            (-1, 0), (1, 0),  # Vertical: up, down
            (0, -1), (0, 1)   # Horizontal: left, right
        ]

        row, col = self.position
        if len(checking_pieces) == 2:
            return
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
        
        if len(checking_pieces) == 0:
            return

        # Filter moves that counters the check
        filtered_moves = []
        for move in self.possible_moves:
            if self.check_if_move_blocks_or_captures(move, checking_pieces[0], king_square):
                filtered_moves.append(move)
        self.possible_moves = filtered_moves


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
                self.attacked_squares.append((new_row, new_col))
                if target_piece:
                    break
                # Move further in the current direction
                new_row += dr
                new_col += dc


class Knight(Piece):
    def symbol(self):
        return "N" if self.color == 'w' else "n"

    def calculate_possible_moves(self, board: list[list["Piece"]], attacked_squares: dict[str, list[tuple[int, int]]], checking_pieces: list["Piece"], king_square: tuple[int, int], castling: str = "-", enpassant: str = "-") -> None:
        self.possible_moves = []  # Clear previous moves

        # Define all potential moves for a knight
        knight_moves = [
            (-2, -1), (-2, 1),  # Two up, one left/right
            (-1, -2), (-1, 2),  # One up, two left/right
            (1, -2), (1, 2),    # One down, two left/right
            (2, -1), (2, 1)     # Two down, one left/right
        ]

        row, col = self.position
        if len(checking_pieces) == 2:
            return
        
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc

            # Ensure the new position is within the board bounds
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = board[new_row][new_col]

                # Add the move if the target square is empty or contains an opponent's piece
                if not target_piece or target_piece.color != self.color:
                    self.possible_moves.append((new_row, new_col))
        
        if len(checking_pieces) == 0:
            return

        # Filter moves that counters the check
        filtered_moves = []
        for move in self.possible_moves:
            if self.check_if_move_blocks_or_captures(move, checking_pieces[0], king_square):
                filtered_moves.append(move)
        self.possible_moves = filtered_moves

    def calculate_attacked_squares(self, board: list[list["Piece"]]):
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
                self.attacked_squares.append((new_row, new_col))


class Bishop(Piece):
    def symbol(self):
        return "B" if self.color == 'w' else "b"

    def calculate_possible_moves(self, board: list[list["Piece"]], attacked_squares: dict[str, list[tuple[int, int]]], checking_pieces: list["Piece"], king_square: tuple[int, int], castling: str = "-", enpassant: str = "-") -> None:
        self.possible_moves = []  # Clear previous moves

        # Define directions for diagonal movement
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Top-left, top-right, bottom-left, bottom-right

        row, col = self.position
        if len(checking_pieces) == 2:
            return
        
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
            
        if len(checking_pieces) == 0:
            return

        # Filter moves that counters the check
        filtered_moves = []
        for move in self.possible_moves:
            if self.check_if_move_blocks_or_captures(move, checking_pieces[0], king_square):
                filtered_moves.append(move)
        self.possible_moves = filtered_moves

    def calculate_attacked_squares(self, board: list[list["Piece"]]):
        self.attacked_squares = []
         # Define directions for diagonal movement
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Top-left, top-right, bottom-left, bottom-right

        row, col = self.position

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = board[new_row][new_col]
                self.attacked_squares.append((new_row, new_col))
                if target_piece:
                    break

                # Move further in the current direction
                new_row += dr
                new_col += dc


class Queen(Piece):
    def symbol(self):
        return "Q" if self.color == 'w' else "q"

    def calculate_possible_moves(self, board: list[list["Piece"]], attacked_squares: dict[str, list[tuple[int, int]]], checking_pieces: list["Piece"], king_square: tuple[int, int], castling: str = "-", enpassant: str = "-") -> None:
        self.possible_moves = []  # Clear previous moves

        # Define directions for queen movement (horizontal, vertical, and diagonal)
        directions = [
            (-1, 0), (1, 0),  # Vertical: up, down
            (0, -1), (0, 1),  # Horizontal: left, right
            (-1, -1), (-1, 1),  # Diagonal: top-left, top-right
            (1, -1), (1, 1)    # Diagonal: bottom-left, bottom-right
        ]

        row, col = self.position
        if len(checking_pieces) == 2:
            return
        
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
        
        if len(checking_pieces) == 0:
            return

        # Filter moves that counters the check
        filtered_moves = []
        for move in self.possible_moves:
            if self.check_if_move_blocks_or_captures(move, checking_pieces[0], king_square):
                filtered_moves.append(move)
        self.possible_moves = filtered_moves

    def calculate_attacked_squares(self, board: list[list["Piece"]]):
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
                self.attacked_squares.append((new_row, new_col))
                if target_piece:
                    break

                # Move further in the current direction
                new_row += dr
                new_col += dc


class King(Piece):
    def symbol(self):
        return "K" if self.color == 'w' else "k"

    def calculate_possible_moves(self, board: list[list["Piece"]], attacked_squares: dict[str, list[tuple[int, int]]], checking_pieces: list["Piece"], king_square: tuple[int, int], castling: str = "-", enpassant: str = "-") -> None:
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
        
        if len(checking_pieces) == 0:
            return

        # Filter moves that counters the check
        filtered_moves = []
        for checing_piece in checking_pieces:
            for move in self.possible_moves:
                if self.check_if_move_blocks_or_captures(move, checing_piece, king_square, True):
                    filtered_moves.append(move)
        self.possible_moves = filtered_moves

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

    def calculate_attacked_squares(self, board: list[list["Piece"]]):
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
                self.attacked_squares.append((new_row, new_col))
