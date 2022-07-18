import sys
import numpy as np
import pygame as pg
from tile import Tile, Mouse
from piece import Piece
from fen_parser import FenParser


class Game:
    def __init__(self, fen_string: str | None = "default"):
        self.ranks = [1, 2, 3, 4, 5, 6, 7, 8][::-1]  # rows  # TODO: HARD CODED
        self.files = ["a", "b", "c", "d", "e", "f", "g", "h"]  # cols  # TODO: HARD CODED

        self.mouse_tile = Mouse()  # TODO: hardcoded
        self.tile_sprites = pg.sprite.RenderUpdates()
        self.piece_sprites = pg.sprite.RenderUpdates()

        self.mouse_sprite = pg.sprite.RenderUpdates()
        self.game_board = self.prepare_game_board(fen_string)

    def prepare_game_board(self, fen_string: str | None = "default"):
        piece_board = np.ndarray(shape=(8, 8), dtype=Piece)
        if fen_string:
            if fen_string == "default":
                fen_string = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
            FenParser.parse(fen_string, piece_board, self.piece_sprites)

        self.mouse_sprite.add(self.mouse_tile)

        colors = [pg.Color(248, 224, 176), pg.Color(163, 112, 67)]  # light, dark  # TODO: hardcoded
        tile_board = []
        for row_id, r in enumerate(self.ranks):
            color_idx = 0 if row_id % 2 == 0 else 1
            row = []
            for col_id, f in enumerate(self.files):
                color = colors[(color_idx + col_id) % 2]
                # position is x,y not y,x. That's why we give col_id first
                tile = Tile(f"{f}{r}", (col_id, row_id), piece_board[row_id, col_id], color)
                row.append(tile)
                self.tile_sprites.add(tile)
            tile_board.append(row)

        return np.array(tile_board, dtype=Tile).reshape((8, 8))

    def start(self):
        pg.init()
        pg.display.set_caption('Chess')
        self.screen = pg.display.set_mode([600, 600])  # TODO: hardcoded
        pg.display.update()

        while True:
            self.mouse_sprite.update()
            for event in pg.event.get():
                match event.type:
                    case pg.QUIT:
                        sys.exit()
                    case pg.MOUSEBUTTONDOWN:
                        match event.button:
                            case pg.BUTTON_LEFT:
                                self.tile_sprites.update(self.mouse_tile)

            self.tile_sprites.draw(self.screen)
            self.piece_sprites.draw(self.screen)
            self.mouse_sprite.draw(self.screen)
            pg.display.update()


if __name__ == "__main__":
    game = Game("default")
    game.start()
