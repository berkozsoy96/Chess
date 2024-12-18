from pyglet.image import load
from pyglet.sprite import Sprite


SCREEN_SIZE = 800

piece_types = {
    "p": load("images/black-pawn.png"),
    "r": load("images/black-rook.png"),
    "n": load("images/black-knight.png"),
    "b": load("images/black-bishop.png"),
    "q": load("images/black-queen.png"),
    "k": load("images/black-king.png"),

    "P": load("images/white-pawn.png"),
    "R": load("images/white-rook.png"),
    "N": load("images/white-knight.png"),
    "B": load("images/white-bishop.png"),
    "Q": load("images/white-queen.png"),
    "K": load("images/white-king.png")
}

class PieceUI(Sprite):
    def __init__(self, piece_type: str, position: tuple[int, int], batch):
        self.files = "abcdefgh"
        self.ranks = "87654321"
        super().__init__(
            img=piece_types[piece_type], 
            x=position[1] * (SCREEN_SIZE // 8),
            y=(8-position[0]-1) * (SCREEN_SIZE // 8),
            batch=batch
        )
        self.scale = (SCREEN_SIZE // 8) / self.width
        self.pos_notation = f"{self.files[position[1]]}{self.ranks[position[0]]}"
        self.piece_type = piece_type
        self.board_position = position
        self.picked = False

    def check_picked(self, x, y):
        if (self.x <= x < (self.x + self.width)) and (self.y <= y < (self.y + self.height)):
            self.picked = True
            return self.pos_notation
        return None

    def move(self, pos: str):
        self.pos_notation = pos
        self.board_position = (self.ranks.index(pos[1]), self.files.index(pos[0]))
    
    def draw(self, mouse_pos: tuple[int, int]):
        if self.picked:
            self.update(
                x=mouse_pos[0]-((SCREEN_SIZE // 8) // 2),
                y=mouse_pos[1]-((SCREEN_SIZE // 8) // 2),
                z=1
            )
        else:
            self.update(
                x=self.board_position[1] * (SCREEN_SIZE // 8),
                y=(8-self.board_position[0]-1) * (SCREEN_SIZE // 8),
                z=0
            )
        return super().draw()
    
    # def pick_piece(self, x, y):
    #     ci = x//self.sq_size
    #     ri = 8-(y//self.sq_size)-1
    #     if self.game.board[ri][ci]:
    #         print(self.game.board[ri][ci].possible_moves)
    #         self.piece_from = f"{self.game.files[ci]}{self.game.ranks[ri]}"

    # def drop_piece(self, x, y):
    #     c = self.game.files[x//self.sq_size]
    #     r = self.game.ranks[8-(y//self.sq_size)-1]
    #     if self.piece_from:
    #         self.game.make_move(f"{self.piece_from}{c}{r}")
    #         self.piece_sprites = self.update_sprites()

    # def update_sprites(self):
    #     sprites = [
    #         Sprite(piece_types[piece.symbol()], x*self.sq_size, (8-y-1)*self.sq_size) 
    #         for y, row in enumerate(self.game.board) for x, piece in enumerate(row) if piece
    #     ]
    #     for s in sprites:
    #         s.scale = self.sq_size / s.width 
    #     return sprites

    pass
