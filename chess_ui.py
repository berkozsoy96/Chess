from pyglet.window import Window, mouse
from pyglet.graphics import Batch
from pyglet.app import run

from board_ui import BoardUI
from piece_ui import PieceUI

from chess_cli import Chess


SCREEN_SIZE = 800


class MouseEventHandler:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.piece_from: str = None

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self.x = x
            self.y = y
            for p in pieces:
                self.piece_from = p.check_picked(self.x, self.y)
                if self.piece_from:
                    break
        return True

    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT and self.piece_from:
            c = game.files[x//(SCREEN_SIZE//8)]
            r = game.ranks[8-(y//(SCREEN_SIZE//8))-1]
            is_success = game.make_move(f"{self.piece_from}{c}{r}")
            
            piece_index_to_be_removed = -1
            for i, p in enumerate(pieces):
                piece = p.get_sprite(x, y)
                if piece and not piece.picked and is_success:
                    piece_index_to_be_removed = i
                    break
            
            if piece_index_to_be_removed != -1:
                pieces.pop(piece_index_to_be_removed)

            for p in pieces:
                if p.picked:
                    p.picked = False
                    if is_success:
                        p.move(f"{c}{r}")
                    break
        self.piece_from = None
        return True
    
    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if button == mouse.LEFT:
            self.x = x
            self.y = y
        return True


game = Chess()
window = Window(width=SCREEN_SIZE + 200, height=SCREEN_SIZE)
board = BoardUI(window_size=SCREEN_SIZE)
pieces = [
    PieceUI(piece.symbol(), piece.position) 
    for row in game.board for piece in row if piece
]

mouse_event_handlers = MouseEventHandler()
window.push_handlers(mouse_event_handlers)

@window.event
def on_draw():
    window.clear()
    board.draw()
    for p in pieces:
        p.draw((mouse_event_handlers.x, mouse_event_handlers.y))

run()
