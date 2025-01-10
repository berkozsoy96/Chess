from utils import notation_to_position, position_to_notation, FILES, RANKS


class Piece:
    def __init__(self, color: str, position: tuple[int, int]):
        self.color: str = color
        self.position: tuple[int, int] = position  # (r, c) - (rank, file)
        self.position_as_notation: str = position_to_notation(self.position)
        self.previous_positions: list[tuple[int, int]] = []

        self.possible_moves: list[tuple[int, int]] = []
        self.attacked_squares: list[tuple[int, int]] = []
        self.is_enemy_king_in_vision: bool = False

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
        raise NotImplementedError(
            "This method should be implemented by subclasses.")

    def move_removes_check(self, move: tuple[int, int], checking_piece: "Piece", king_square: tuple[int, int], enpassant: str) -> bool:
        move = (move[0], move[1])
        checking_piece_square = checking_piece.position
        if isinstance(checking_piece, Knight):
            return move == checking_piece_square
        if isinstance(checking_piece, Pawn):
            if enpassant != "-":
                en_row, en_col = notation_to_position(enpassant)
                if move == (en_row, en_col) and isinstance(self, Pawn):
                    return True
            return move == checking_piece_square
        distance = (checking_piece.position[0] - king_square[0],
                    checking_piece.position[1] - king_square[1])
        direction = (distance[0]//abs(distance[0]) if distance[0] != 0 else 0,
                     distance[1]//abs(distance[1]) if distance[1] != 0 else 0)
        in_between_squares = []
        for i in range(1, max(abs(distance[0]), abs(distance[1]))):
            in_between_squares.append(
                (king_square[0] + i * direction[0], king_square[1] + i * direction[1]))

        if move in in_between_squares or move == checking_piece_square:
            return True
        return False

    def move_brokes_pin(self, move: tuple[int, int], board: list[list["Piece"]], king_square: tuple[int, int], enpassant: str) -> bool:
        move = (move[0], move[1])
        pinning_pieces: list[Piece] = []
        for r in board:
            for piece in r:
                if piece and piece.color != self.color and piece.is_enemy_king_in_vision:
                    pinning_pieces.append(piece)
        for piece in pinning_pieces:
            distance = (piece.position[0] - king_square[0],
                        piece.position[1] - king_square[1])
            direction = (distance[0]//abs(distance[0]) if distance[0] != 0 else 0,
                         distance[1]//abs(distance[1]) if distance[1] != 0 else 0)
            in_between_squares = []
            for i in range(1, max(abs(distance[0]), abs(distance[1]))):
                in_between_squares.append(
                    (king_square[0] + i * direction[0], king_square[1] + i * direction[1]))
            if self.position not in in_between_squares:
                continue

            in_between_pieces = [board[sq[0]][sq[1]]
                                 for sq in in_between_squares]
            # in_between_pieces_count is minimum 1 which is self
            in_between_pieces_count = len(
                in_between_pieces) - in_between_pieces.count(None)
            if in_between_pieces_count == 1:
                if move not in in_between_squares and move != piece.position:
                    return True
            elif in_between_pieces_count == 2:
                # if move is enpassant
                if enpassant != "-":
                    en_row, en_col = notation_to_position(enpassant)
                    if move == (en_row, en_col) and isinstance(self, Pawn):
                        return True
        return False

    def calculate_possible_moves(self, board: list[list["Piece"]], attacked_squares: dict[str, list[tuple[int, int]]], checking_pieces: list["Piece"], king_square: tuple[int, int], castling: str = "-", enpassant: str = "-") -> None:
        raise NotImplementedError(
            "This method should be implemented by subclasses.")

    def calculate_attacked_squares(self, board: list[list["Piece"]]) -> None:
        raise NotImplementedError(
            "This method should be implemented by subclasses.")


class Pawn(Piece):
    def symbol(self) -> str:
        return "P" if self.color == 'w' else "p"

    def calculate_possible_moves(self, board: list[list["Piece"]], attacked_squares: dict[str, list[tuple[int, int]]], checking_pieces: list["Piece"], king_square: tuple[int, int], castling: str = "-", enpassant: str = "-") -> None:
        self.possible_moves = []  # Clear previous moves
        # Pawns move up (-1) for white, down (+1) for black
        direction = -1 if self.color == 'w' else 1

        row, col = self.position
        if len(checking_pieces) == 2:
            return

        # Forward movement by 1
        if (0 <= row + direction < 8) and (board[row + direction][col] is None):
            if row + direction == 0 or row + direction == 7:
                self.possible_moves.append((row + direction, col, "n"))
                self.possible_moves.append((row + direction, col, "r"))
                self.possible_moves.append((row + direction, col, "b"))
                self.possible_moves.append((row + direction, col, "q"))
            else:
                self.possible_moves.append((row + direction, col, "-"))

            # Double forward movement if on starting rank
            if ((self.position[0] == 1 and self.color == "b") or (self.position[0] == 6 and self.color == "w")) and (board[row + 2 * direction][col] is None):
                self.possible_moves.append((row + 2 * direction, col, "-"))

        # Captures
        for dc in [-1, 1]:  # Diagonal left (-1) and right (+1)
            new_col = col + dc
            if (0 <= new_col < 8) and (0 <= row + direction < 8):
                target_piece = board[row + direction][new_col]
                if target_piece and target_piece.color != self.color:
                    if row + direction == 0 or row + direction == 7:
                        self.possible_moves.append(
                            (row + direction, new_col, "n"))
                        self.possible_moves.append(
                            (row + direction, new_col, "r"))
                        self.possible_moves.append(
                            (row + direction, new_col, "b"))
                        self.possible_moves.append(
                            (row + direction, new_col, "q"))
                    else:
                        self.possible_moves.append(
                            (row + direction, new_col, "-"))

        # En Passant
        if enpassant != "-":
            en_row, en_col = notation_to_position(enpassant)
            if abs(en_col - col) == 1 and en_row == row + direction:
                self.possible_moves.append((en_row, en_col, "-"))

        filtered_moves = []
        for move in self.possible_moves:
            if not self.move_brokes_pin(move, board, king_square, enpassant):
                filtered_moves.append(move)
        self.possible_moves = filtered_moves

        if len(checking_pieces) == 0:
            return

        # Filter moves that counters the check
        filtered_moves = []
        for move in self.possible_moves:
            if self.move_removes_check(move, checking_pieces[0], king_square, enpassant):
                filtered_moves.append(move)
        self.possible_moves = filtered_moves

    def calculate_attacked_squares(self, board: list[list["Piece"]]):
        self.attacked_squares = []
        # Pawns move up (-1) for white, down (+1) for black
        direction = -1 if self.color == 'w' else 1
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
                    self.possible_moves.append((new_row, new_col, "-"))
                elif target_piece.color != self.color:
                    # If the square contains an opponent's piece, add it and stop further movement
                    self.possible_moves.append((new_row, new_col, "-"))
                    break
                else:
                    # If the square contains a piece of the same color, stop further movement
                    break

                # Move further in the current direction
                new_row += dr
                new_col += dc

        filtered_moves = []
        for move in self.possible_moves:
            if not self.move_brokes_pin(move, board, king_square, enpassant):
                filtered_moves.append(move)
        self.possible_moves = filtered_moves

        if len(checking_pieces) == 0:
            return

        # Filter moves that counters the check
        filtered_moves = []
        for move in self.possible_moves:
            if self.move_removes_check(move, checking_pieces[0], king_square, enpassant):
                filtered_moves.append(move)
        self.possible_moves = filtered_moves

    def calculate_attacked_squares(self, board: list[list["Piece"]]):
        self.attacked_squares = []
        self.is_enemy_king_in_vision = False

        directions = [
            (-1, 0), (1, 0),  # Vertical: up, down
            (0, -1), (0, 1)   # Horizontal: left, right
        ]

        row, col = self.position

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            blocking_piece = False
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = board[new_row][new_col]
                if not blocking_piece:
                    self.attacked_squares.append((new_row, new_col))
                if target_piece:
                    blocking_piece = True
                if target_piece and isinstance(target_piece, King) and target_piece.color != self.color:
                    self.is_enemy_king_in_vision = True
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
                    self.possible_moves.append((new_row, new_col, "-"))

        filtered_moves = []
        for move in self.possible_moves:
            if not self.move_brokes_pin(move, board, king_square, enpassant):
                filtered_moves.append(move)
        self.possible_moves = filtered_moves

        if len(checking_pieces) == 0:
            return

        # Filter moves that counters the check
        filtered_moves = []
        for move in self.possible_moves:
            if self.move_removes_check(move, checking_pieces[0], king_square, enpassant):
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
        # Top-left, top-right, bottom-left, bottom-right
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        row, col = self.position
        if len(checking_pieces) == 2:
            return

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = board[new_row][new_col]

                if not target_piece:
                    # If the square is empty, add it to possible moves
                    self.possible_moves.append((new_row, new_col, "-"))
                elif target_piece.color != self.color:
                    # If the square contains an opponent's piece, add it and stop further movement
                    self.possible_moves.append((new_row, new_col, "-"))
                    break
                else:
                    # If the square contains a piece of the same color, stop further movement
                    break

                # Move further in the current direction
                new_row += dr
                new_col += dc

        filtered_moves = []
        for move in self.possible_moves:
            if not self.move_brokes_pin(move, board, king_square, enpassant):
                filtered_moves.append(move)
        self.possible_moves = filtered_moves

        if len(checking_pieces) == 0:
            return

        # Filter moves that counters the check
        filtered_moves = []
        for move in self.possible_moves:
            if self.move_removes_check(move, checking_pieces[0], king_square, enpassant):
                filtered_moves.append(move)
        self.possible_moves = filtered_moves

    def calculate_attacked_squares(self, board: list[list["Piece"]]):
        self.attacked_squares = []
        self.is_enemy_king_in_vision = False
        # Define directions for diagonal movement
        # Top-left, top-right, bottom-left, bottom-right
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        row, col = self.position

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            blocking_piece = False
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = board[new_row][new_col]
                if not blocking_piece:
                    self.attacked_squares.append((new_row, new_col))
                if target_piece:
                    blocking_piece = True
                if target_piece and isinstance(target_piece, King) and target_piece.color != self.color:
                    self.is_enemy_king_in_vision = True
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
                    self.possible_moves.append((new_row, new_col, "-"))
                elif target_piece.color != self.color:
                    # If the square contains an opponent's piece, add it and stop further movement
                    self.possible_moves.append((new_row, new_col, "-"))
                    break
                else:
                    # If the square contains a piece of the same color, stop further movement
                    break

                # Move further in the current direction
                new_row += dr
                new_col += dc

        filtered_moves = []
        for move in self.possible_moves:
            if not self.move_brokes_pin(move, board, king_square, enpassant):
                filtered_moves.append(move)
        self.possible_moves = filtered_moves

        if len(checking_pieces) == 0:
            return

        # Filter moves that counters the check
        filtered_moves = []
        for move in self.possible_moves:
            if self.move_removes_check(move, checking_pieces[0], king_square, enpassant):
                filtered_moves.append(move)
        self.possible_moves = filtered_moves

    def calculate_attacked_squares(self, board: list[list["Piece"]]):
        self.attacked_squares = []
        self.is_enemy_king_in_vision = False

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
            blocking_piece = False
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = board[new_row][new_col]
                if not blocking_piece:
                    self.attacked_squares.append((new_row, new_col))
                if target_piece:
                    blocking_piece = True
                if target_piece and isinstance(target_piece, King) and target_piece.color != self.color:
                    self.is_enemy_king_in_vision = True
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

        asf = list(set([m for _, squares in attacked_squares.items()
                   for m in squares]))
        row, col = self.position

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = board[new_row][new_col]
                if (new_row, new_col) in asf:
                    continue
                if not target_piece or target_piece.color != self.color:
                    # Add square if empty or occupied by opponent
                    self.possible_moves.append((new_row, new_col, "-"))

        # Check castling possibilities
        if self.color == 'w':
            if self.position_as_notation == "e1":
                # White castling
                if castling[0] and self.can_castle_kingside(board, asf, row, col):
                    self.possible_moves.append((row, col + 2, "-"))
                if castling[1] and self.can_castle_queenside(board, asf, row, col):
                    self.possible_moves.append((row, col - 2, "-"))
        else:
            if self.position_as_notation == "e8":
                # Black castling
                if castling[2] and self.can_castle_kingside(board, asf, row, col):
                    self.possible_moves.append((row, col + 2, "-"))
                if castling[3] and self.can_castle_queenside(board, asf, row, col):
                    self.possible_moves.append((row, col - 2, "-"))

        if len(checking_pieces) == 0:
            return

        filtered_moves = []
        for move in self.possible_moves:
            legal = True
            for checking_piece in checking_pieces:
                if not isinstance(checking_piece, (Knight, Pawn)):
                    checking_piece_square = checking_piece.position
                    direction = (
                        checking_piece_square[0] - king_square[0], checking_piece_square[1] - king_square[1])
                    opposite_direction = (0 if direction[0] == 0 else -(direction[0]/abs(
                        direction[0])), 0 if direction[1] == 0 else -(direction[1]/abs(direction[1])))
                    if move == (king_square[0] + opposite_direction[0], king_square[1] + opposite_direction[1], "-"):
                        legal = False
                        break
            if legal:
                filtered_moves.append(move)

        self.possible_moves = filtered_moves

    def can_castle_kingside(self, board: list[list["Piece"]], attacked_squares: list[tuple[int, int]], row: int, col: int) -> bool:
        # Check if squares between king and kingside rook are empty, not attacked and rook is unmoved

        return (
            # cannot castle through check
            (row, col) not in attacked_squares and
            board[row][col + 1] is None and (row, col + 1) not in attacked_squares and
            board[row][col + 2] is None and (row, col + 2) not in attacked_squares and
            isinstance(board[row][7], Rook) and
            board[row][7].color == self.color
        )

    def can_castle_queenside(self, board: list[list["Piece"]], attacked_squares: list[tuple[int, int]], row: int, col: int) -> bool:
        # Check if squares between king and queenside rook are empty, not attacked and rook is unmoved

        return (
            # cannot castle through check
            (row, col) not in attacked_squares and
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
