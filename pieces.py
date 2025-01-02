from utils import notation_to_position, position_to_notation, FILES, RANKS

class Piece:
    def __init__(self, color: str, position: tuple[int, int]):
        self.color: str = color
        self.position: tuple[int, int] = position  # (r, c) - (rank, file)
        self.position_as_notation: str = position_to_notation(self.position)
        self.previous_positions: list[tuple[int, int]] = []
        
        self.possible_moves: list[tuple[int, int]] = []
        self.attacked_squares: list[tuple[int, int]] = []
    
    def move(self, pos: tuple[int, int]) -> None:
        self.previous_positions.append(self.position)
        self.position = pos
        self.position_as_notation = f"{FILES[pos[1]]}{RANKS[pos[0]]}"

    def undo_move(self) -> None:
        if len(self.previous_positions) == 0:
            return
        last_pos = self.previous_positions.pop()
        self.position = last_pos
        self.position_as_notation = f"{FILES[self.position[1]]}{RANKS[self.position[0]]}"

    def symbol(self) -> str:
        raise NotImplementedError("This method should be implemented by subclasses.")

    def move_blocks_or_captures_the_checking_piece(self, move: tuple[int, int], checking_piece: "Piece", king_square: tuple[int, int]) -> bool:
        checking_piece_square = checking_piece.position
        if isinstance(checking_piece, (Knight, Pawn)):
            return move == checking_piece_square
        
        direction = (checking_piece_square[0] - king_square[0], checking_piece_square[1] - king_square[1])
        if direction[0] == 0:  # Horizontal check
            if abs(direction[1]) == 1:
                return move == checking_piece_square
            if move[0] == king_square[0]:
                l, r = min(king_square[1], checking_piece_square[1]), max(king_square[1], checking_piece_square[1])
                if l < move[1] < r or move[1] == checking_piece_square[1]:
                    return True
        elif direction[1] == 0: # Vertical check
            if abs(direction[0]) == 1:
                return move == checking_piece_square
            if move[1] == king_square[1]:
                t, b = min(king_square[0], checking_piece_square[0]), max(king_square[0], checking_piece_square[0])
                if t < move[0] < b or move[0] == checking_piece_square[0]:
                    return True
        else:  # diagonal check
            if abs(direction[0]) == 1:
                return move == checking_piece_square
            # vertical direction from king to checking piece
            vd = 1 if direction[0] > 0 else -1
            # horizontal direction from king to checking piece
            hd = 1 if direction[1] > 0 else -1
            for i in range(1, abs(direction[0])+1):
                if move == (king_square[0] + i*vd, king_square[1] + i*hd):
                    return True
        return False

    def move_brokes_pin(self, move: tuple[int, int], board: list[list["Piece"]], attacked_squares: dict[str, list[tuple[int, int]]], king_square: tuple[int, int]) -> bool:
        attacking_pieces: list[Piece] = []
        for source, squares in attacked_squares.items():
            if self.position in squares:
                row, col = notation_to_position(source)
                attacking_pieces.append(board[row][col])
        

        for piece in attacking_pieces:
            if isinstance(piece, (Knight, Pawn, King)):
                continue
            if (self.position[0] == piece.position[0]) and (self.position[0] == king_square[0]):
                l, r = min(king_square[1], piece.position[1]), max(king_square[1], piece.position[1])
                empty_squares = [sq is None for sq in [board[self.position[0]][c] for c in range(l+1, r)] if sq is not self]
                if not empty_squares:
                    empty_squares = [False]
                if l < self.position[1] < r and all(empty_squares):
                    if (move[0] != self.position[0]) or not (l < move[1] < r):
                        return True
            if (self.position[1] == piece.position[1]) and (self.position[1] == king_square[1]):
                t, b = min(king_square[0], piece.position[0]), max(king_square[0], piece.position[0])
                empty_squares = [sq is None for sq in [board[r][self.position[1]] for r in range(t+1, b)] if sq is not self]
                if not empty_squares:
                    empty_squares = [False]
                if t < self.position[0] < b and all(empty_squares):
                    if (move[1] != self.position[1]) or not (t < move[0] < b):
                        return True
            if abs(king_square[0] - piece.position[0]) == abs(king_square[1] - piece.position[1]):
                vd = 1 if piece.position[0] - king_square[0] > 0 else -1
                hd = 1 if piece.position[1] - king_square[1] > 0 else -1
                possible_moves = [(king_square[0] + i*vd, king_square[1] + i*hd) for i in range(1, abs(piece.position[0] - king_square[0])+1)]
                empty_squares = [sq is None for sq in [board[move[0]][move[1]] for move in possible_moves[:-1]] if sq is not self]
                if not empty_squares:
                    empty_squares = [False]
                if self.position in possible_moves and move not in possible_moves and all(empty_squares):
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
            if ((self.position[0] == 1 and self.color == "b") or (self.position[0] == 6 and self.color == "w")) and (board[row + 2 * direction][col] is None):
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
        
        filtered_moves = []
        for move in self.possible_moves:
            if not self.move_brokes_pin(move, board, attacked_squares, king_square):
                filtered_moves.append(move)
        self.possible_moves = filtered_moves

        if len(checking_pieces) == 0:
            return

        # Filter moves that counters the check
        filtered_moves = []
        for move in self.possible_moves:
            if self.move_blocks_or_captures_the_checking_piece(move, checking_pieces[0], king_square):
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
        
        filtered_moves = []
        for move in self.possible_moves:
            if not self.move_brokes_pin(move, board, attacked_squares, king_square):
                filtered_moves.append(move)
        self.possible_moves = filtered_moves
        
        if len(checking_pieces) == 0:
            return

        # Filter moves that counters the check
        filtered_moves = []
        for move in self.possible_moves:
            if self.move_blocks_or_captures_the_checking_piece(move, checking_pieces[0], king_square):
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
        
        filtered_moves = []
        for move in self.possible_moves:
            if not self.move_brokes_pin(move, board, attacked_squares, king_square):
                filtered_moves.append(move)
        self.possible_moves = filtered_moves
        
        if len(checking_pieces) == 0:
            return

        # Filter moves that counters the check
        filtered_moves = []
        for move in self.possible_moves:
            if self.move_blocks_or_captures_the_checking_piece(move, checking_pieces[0], king_square):
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
        
        filtered_moves = []
        for move in self.possible_moves:
            if not self.move_brokes_pin(move, board, attacked_squares, king_square):
                filtered_moves.append(move)
        self.possible_moves = filtered_moves
        
        if len(checking_pieces) == 0:
            return

        # Filter moves that counters the check
        filtered_moves = []
        for move in self.possible_moves:
            if self.move_blocks_or_captures_the_checking_piece(move, checking_pieces[0], king_square):
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
        
        filtered_moves = []
        for move in self.possible_moves:
            if not self.move_brokes_pin(move, board, attacked_squares, king_square):
                filtered_moves.append(move)
        self.possible_moves = filtered_moves
        
        if len(checking_pieces) == 0:
            return

        # Filter moves that counters the check
        filtered_moves = []
        for move in self.possible_moves:
            if self.move_blocks_or_captures_the_checking_piece(move, checking_pieces[0], king_square):
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
        if self.color == 'w':
            if self.position_as_notation == "e1":
                # White castling
                if castling[0] and self.can_castle_kingside(board, asf, row, col):
                    self.possible_moves.append((row, col + 2))
                if castling[1] and self.can_castle_queenside(board, asf, row, col):
                    self.possible_moves.append((row, col - 2))
        else:
            if self.position_as_notation == "e8":
                # Black castling
                if castling[2] and self.can_castle_kingside(board, asf, row, col):
                    self.possible_moves.append((row, col + 2))
                if castling[3] and self.can_castle_queenside(board, asf, row, col):
                    self.possible_moves.append((row, col - 2))
        
        if len(checking_pieces) == 0:
            return

        # Filter moves that counters the check
        filtered_moves = []
        for checking_piece in checking_pieces:
            checking_piece_square = checking_piece.position
            direction = (checking_piece_square[0] - king_square[0], checking_piece_square[1] - king_square[1])
            for move in self.possible_moves:
                if not isinstance(checking_piece, (Knight, Pawn)):
                    opposite_direction = (0 if direction[0] == 0 else -(direction[0]/abs(direction[0])), 0 if direction[1] == 0 else -(direction[1]/abs(direction[1])))
                    if (move == (king_square[0] + opposite_direction[0], king_square[1] + opposite_direction[1])):
                        continue
                filtered_moves.append(move)
        self.possible_moves = filtered_moves

    def can_castle_kingside(self, board: list[list["Piece"]], attacked_squares: list[tuple[int, int]], row: int, col: int) -> bool:
        # Check if squares between king and kingside rook are empty, not attacked and rook is unmoved
        
        return (
            (row, col) not in attacked_squares and  # cannot castle through check
            board[row][col + 1] is None and (row, col + 1) not in attacked_squares and
            board[row][col + 2] is None and (row, col + 2) not in attacked_squares and
            isinstance(board[row][7], Rook) and
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
