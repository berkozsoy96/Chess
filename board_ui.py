from pyglet.shapes import Rectangle
from pyglet.text import Label

class BoardUI:
    def __init__(self, window_size, board_size=8):
        self.window_size = window_size
        self.board_size = board_size
        self.sq_size = window_size//board_size
        self.files = "abcdefgh"
        self.ranks = "12345678"

        self.piece_from: str = None

        self.tile_colors = [(184, 134, 97), (238, 214, 176)]
        self.text_color = (50, 50, 50)
        self.tiles: list[Rectangle] = [
            Rectangle(
                (i % self.board_size) * self.sq_size,
                (i // self.board_size) * self.sq_size,
                self.sq_size, 
                self.sq_size, 
                self.tile_colors[(i+(i//self.board_size))%2]
            ) for i in range(self.board_size**2)
        ]
        self.labels: list[tuple[Label, Label]] = [
            (Label(self.files[i], x=((i+1)*self.sq_size)-20, y=5, color=self.text_color),
            Label(self.ranks[i], x=5, y=(i+1)*self.sq_size-20, color=self.text_color))
            for i in range(self.board_size)
        ]
    
    def draw(self):
        for r in self.tiles:
            r.draw()
        for lf, lr in self.labels:
            lf.draw()
            lr.draw()
