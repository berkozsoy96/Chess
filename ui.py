import pyglet
from pyglet.window import mouse
from pyglet.shapes import Rectangle, Circle
from pyglet.text import Label

from chess_cli import Chess, Piece, position_to_notation, notation_to_position

class ChessUI:
    def __init__(self, chess_game):
        self.game: Chess = chess_game
        self.window = pyglet.window.Window(width=1000, height=800, caption="Berk's Chess Game")
        self.square_size = self.window.height // 8
        self.selected_piece = None  # Store the currently selected piece
        self.highlighted_squares = []  # To show possible moves
        self.textures: dict[str, pyglet.image.AbstractImage] = {}  # Piece textures for enhanced visuals
        self.sprites: dict[tuple[int, int], pyglet.sprite.Sprite] = {}  # Store sprites for each piece
        self.selected_sprite = None  # Store the sprite for the selected piece
        self.squares = []  # List to store Rectangle objects for each square
        # TODO: add file and rank labels
        # Load resources
        self.load_piece_textures()
        self.create_sprites()
        
        # Set event handlers
        self.window.on_draw = self.on_draw
        self.window.on_mouse_press = self.on_mouse_press
        self.window.on_mouse_release = self.on_mouse_release
        self.window.on_mouse_drag = self.on_mouse_drag

        # Initialize squares once
        self.create_squares()

    def load_piece_textures(self):
        """
        Preload textures for chess pieces and labels as a fallback.
        """
        pieces = "rnbqkpRNBQKP"
        for piece in pieces:
            piece_name: str
            match piece.lower():
                case "r":
                    piece_name = "rook"
                case "n":
                    piece_name = "knight"
                case "b":
                    piece_name = "bishop"
                case "q":
                    piece_name = "queen"
                case "k":
                    piece_name = "king"
                case "p":
                    piece_name = "pawn"
                case _:
                    print("wtf!")
            # Load textures for each piece from a hypothetical `resources` directory
            self.textures[piece] = pyglet.image.load(f"images/{'black' if piece.islower() else 'white'}-{piece_name}.png")

    def create_squares(self):
        """
        Create Rectangle objects for each square on the chessboard.
        """
        colors = [(184, 134, 97), (238, 214, 176)]  # Light and dark square colors
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                square = Rectangle(
                    x=col * self.square_size,
                    y=row * self.square_size,
                    width=self.square_size,
                    height=self.square_size,
                    color=color
                )
                self.squares.append(square)

    def create_sprites(self):
        """
        Create sprite objects for each piece based on the current board state.
        """
        self.sprites = {}
        for row in range(8):
            for col in range(8):
                piece = self.game.board[row][col]
                if piece:
                    self.create_piece_sprite(piece, row, col)

    def create_piece_sprite(self, piece: Piece, row, col):
        """
        Create a sprite for a specific piece at its position.
        """
        x = (col) * self.square_size
        y = (7 - row) * self.square_size  # Reverse row for graphical representation

        texture = self.textures[piece.symbol()]
        sprite = pyglet.sprite.Sprite(texture, x=x, y=y)
        sprite.scale = self.square_size / texture.width
        self.sprites[(row, col)] = sprite

    def draw_board(self):
        """
        Draw the chessboard squares (using pre-created rectangles).
        """
        for square in self.squares:
            square.draw()

    def draw_pieces(self):
        """
        Draw the pieces on the board based on the game's current state.
        """
        for (row, col), sprite_or_label in self.sprites.items():
            sprite_or_label.draw()

    def highlight_squares(self):
        """
        Highlight selected and possible move squares.
        """
        highlight_color = (50, 50, 50)  # Green highlight
        for move in self.highlighted_squares:
            row, col = move
            square = Circle(
                x=(col + .5) * self.square_size,
                y=(7 - row + .5) * self.square_size,  # Reverse row for graphical representation
                radius=15,
                color=highlight_color
            )
            square.opacity = 100
            square.draw()

    def display_game_status(self):
        """
        Display the current status of the game (turn, check, win, etc.).
        """
        turn_label = Label(
            f"Turn: {'White' if self.game.turn == 0 else 'Black'}",
            font_name="Arial",
            font_size=20,
            x=810,
            y=self.window.height - 30,
            anchor_x="left",
            anchor_y="center"
        )
        
        castling_label = Label(
            f"Castling: {'K' if self.game.castling[0] else ''}{'Q' if self.game.castling[1] else ''}{'k' if self.game.castling[2] else ''}{'q' if self.game.castling[3] else ''}",
            font_name="Arial",
            font_size=20,
            x=810,
            y=self.window.height - 60,
            anchor_x="left",
            anchor_y="center"
        )

        enpassant_label = Label(
            f"En Passant: {self.game.enpassant}",
            font_name="Arial",
            font_size=20,
            x=810,
            y=self.window.height - 90,
            anchor_x="left",
            anchor_y="center"
        )

        half_move_label = Label(
            f"Half Move: {self.game.half_move_clock}",
            font_name="Arial",
            font_size=20,
            x=810,
            y=self.window.height - 120,
            anchor_x="left",
            anchor_y="center"
        )

        full_move_label = Label(
            f"Full Move: {self.game.full_move_clock}",
            font_name="Arial",
            font_size=20,
            x=810,
            y=self.window.height - 150,
            anchor_x="left",
            anchor_y="center"
        )
        turn_label.draw()
        castling_label.draw()
        enpassant_label.draw()
        half_move_label.draw()
        full_move_label.draw()

    def on_draw(self):
        """
        Draw the entire UI (board, pieces, highlights, and status).
        """
        self.window.clear()
        self.draw_board()
        self.highlight_squares()
        self.draw_pieces()
        self.display_game_status()

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Handle mouse clicks for selecting and moving pieces.
        """
        self.highlighted_squares = []
        if button == mouse.LEFT:
            col: int = x // self.square_size
            row: int = 7 - (y // self.square_size)  # Reverse for graphical representation
            piece = self.game.board[row][col]
            if piece:
                self.selected_piece = position_to_notation((row, col))
                self.selected_sprite = self.sprites[(row, col)]
                self.selected_sprite.update(x-self.selected_sprite.width/2, y-self.selected_sprite.width/2)
                if piece.color == self.game.colors[self.game.turn]:
                    self.highlighted_squares = piece.possible_moves
    
    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            col: int = x // self.square_size
            row: int = 7 - (y // self.square_size)  # Reverse for graphical representation
            # piece = self.game.board[row][col]
            if self.selected_piece:
                # Attempt to make a move
                target_pos = (row, col)
                move = f"{self.selected_piece}{position_to_notation(target_pos)}"
                if move[:2] != move[2:]:
                    if self.game.make_move(move):
                        self.create_sprites()  # Update pieces after move
                        self.highlighted_squares = []
                # restore piece to its original place
                orjrow, orjcol = notation_to_position(self.selected_piece)
                self.selected_sprite.update((orjcol) * self.square_size, (7 - orjrow) * self.square_size)
                self.selected_piece = None
                self.selected_sprite = None
    
    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if button == mouse.LEFT:
            if self.selected_sprite:
                self.selected_sprite.update(x-self.selected_sprite.width/2, y-self.selected_sprite.width/2, 5)

    def run(self):
        """
        Start the Pyglet application.
        """
        pyglet.app.run()


# Example usage:
if __name__ == "__main__":
    chess_game = Chess()  # Use your Chess class here
    ui = ChessUI(chess_game)
    ui.run()
