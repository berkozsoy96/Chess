import pyglet
from pyglet.text import Label
from pyglet.image import AbstractImage, load
from pyglet.sprite import Sprite
from pyglet.window import Window, mouse
from pyglet.shapes import Rectangle, Circle, Arc
from pyglet.graphics import Batch

from chess_cli import Chess, Piece, position_to_notation, notation_to_position, FILES, RANKS

class ChessUI:
    def __init__(self, chess_game):
        self.game: Chess = chess_game

        self.window = Window(width=1000, height=800, caption="Berk's Chess Game")
        self.square_size = self.window.height // 8
        
        # Initialize squares once
        self.squares: list[Rectangle] = []  # List to store Rectangle objects for each square
        self.file_labels: list[Label] = []
        self.rank_labels: list[Label] = []
        self.create_squares()
        
        self.textures: dict[str, AbstractImage] = {}  # Piece textures for enhanced visuals
        self.load_piece_textures()
        
        self.sprites: dict[tuple[int, int], Sprite] = {}  # Store sprites for each piece
        self.background = Batch()
        self.foreground = Batch()
        self.create_sprites()
        
        self.highlighted_squares = []  # To show possible moves
        self.selected_sprite = None  # Store the sprite for the selected piece
        self.source_sq = None  # Store the currently selected piece
        
        # Set event handlers
        self.window.on_draw = self.on_draw
        self.window.on_mouse_press = self.on_mouse_press
        self.window.on_mouse_release = self.on_mouse_release
        self.window.on_mouse_drag = self.on_mouse_drag

    def create_squares(self):
        """
        Create Rectangle objects for each square on the chessboard.
        """
        colors = [(184, 134, 97), (238, 214, 176)]  # Dark and light square colors
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
        self.file_labels = [
            Label(
                text=f,
                font_name="Arial",
                font_size=15,
                x=(i+1) * self.square_size - 15,
                y=10,
                color=(50, 50, 50)
            ) for i, f in enumerate(FILES)
        ]
        self.rank_labels = [
            Label(
                text=r,
                font_name="Arial",
                font_size=15,
                x=5,
                y=(i+1) * self.square_size - 20,
                color=(50, 50, 50)
            ) for i, r in enumerate(RANKS[::-1])
        ]

    def load_piece_textures(self):
        """
        Preload textures for chess pieces and labels as a fallback.
        """
        self.textures = {
            "r": load(f"images/br.png"),
            "n": load(f"images/bn.png"),
            "b": load(f"images/bb.png"),
            "q": load(f"images/bq.png"),
            "k": load(f"images/bk.png"),
            "p": load(f"images/bp.png"),
            "R": load(f"images/wr.png"),
            "N": load(f"images/wn.png"),
            "B": load(f"images/wb.png"),
            "Q": load(f"images/wq.png"),
            "K": load(f"images/wk.png"),
            "P": load(f"images/wp.png")
        }

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
        sprite = Sprite(texture, x=x, y=y, batch=self.background)
        sprite.scale = self.square_size / texture.width
        self.sprites[(row, col)] = sprite

    def draw_board(self):
        """
        Draw the chessboard squares (using pre-created rectangles).
        """
        for square in self.squares:
            square.draw()
        for label in self.file_labels:
            label.draw()
        for label in self.rank_labels:
            label.draw()

    def draw_pieces(self):
        """
        Draw the pieces on the board based on the game's current state.
        """
        self.background.draw()
        self.foreground.draw()

    def highlight_squares(self):
        """
        Highlight selected and possible move squares.
        """
        highlight_color = (50, 50, 50)  # Green highlight
        for move in self.highlighted_squares:
            row, col = move
            if self.game.board[row][col]:
                circle = Arc(
                    x=(col + .5) * self.square_size,
                    y=(7 - row + .5) * self.square_size,  # Reverse row for graphical representation
                    radius=self.square_size*.5 - 5,
                    color=highlight_color,
                    thickness=5
                )
            else:
                circle = Circle(
                    x=(col + .5) * self.square_size,
                    y=(7 - row + .5) * self.square_size,  # Reverse row for graphical representation
                    radius=self.square_size*.15,
                    color=highlight_color
                )
            circle.opacity = 100
            circle.draw()

    def highlight_attaced_squares(self):
        """
        Highlight selected and possible move squares.
        """
        ms = []
        highlight_color = (150, 20, 30)  # Red highlight
        for sourse, moves in self.game.attacked_squares.items():
            ms += moves
        for move in list(set(ms)):
            row, col = move
            rect = Circle(
                x=(col + .5) * self.square_size,
                y=(7 - row + .5) * self.square_size,  # Reverse row for graphical representation
                radius=self.square_size*.4,
                color=highlight_color
            )
            rect.opacity = 100  # 0 - 255
            rect.draw()

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
        # self.highlight_attaced_squares()
        self.draw_pieces()
        self.display_game_status()

    def on_mouse_press(self, x, y, button, modifiers):
        self.highlighted_squares = []
        if button == mouse.LEFT:
            col: int = x // self.square_size
            row: int = 7 - (y // self.square_size)
            piece = self.game.board[row][col]
            if piece:
                self.source_sq = position_to_notation((row, col))
                self.selected_sprite = self.sprites[(row, col)]
                self.selected_sprite.update(x-self.selected_sprite.width/2, y-self.selected_sprite.width/2)
                if piece.color == self.game.colors[self.game.turn]:
                    self.highlighted_squares = piece.possible_moves
    
    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            col: int = x // self.square_size
            row: int = 7 - (y // self.square_size)
            if self.source_sq:
                target_pos = (row, col)
                move = f"{self.source_sq}{position_to_notation(target_pos)}"
                if move[:2] != move[2:]:
                    if self.game.make_move(move):
                        self.create_sprites()
                        self.highlighted_squares = []
                
                orjrow, orjcol = notation_to_position(self.source_sq)
                self.selected_sprite.batch = self.background
                self.selected_sprite.update((orjcol) * self.square_size, (7 - orjrow) * self.square_size)
                self.source_sq = None
                self.selected_sprite = None
    
    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if button == mouse.LEFT:
            if self.selected_sprite:
                self.selected_sprite.batch = self.foreground
                self.selected_sprite.update(x-self.selected_sprite.width/2, y-self.selected_sprite.width/2)

    def run(self):
        pyglet.app.run()


if __name__ == "__main__":
    # chess_game = Chess(fen="rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8")
    # chess_game = Chess(fen="8/8/3p4/KPp4r/1R3p1k/4P3/6P1/8 w - c6 0 1")
    chess_game = Chess()
    ui = ChessUI(chess_game)
    ui.run()
