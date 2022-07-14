import sys
import numpy as np
import pygame as pg
from tile import Tile
from fen_parser import FenParser


class Game:
    def __init__(self, fen_string: str | None = "default"):
        self.ranks = [1, 2, 3, 4, 5, 6, 7, 8][::-1]  # rows  # TODO: HARD CODED
        self.files = ["a", "b", "c", "d", "e", "f", "g", "h"]  # cols  # TODO: HARD CODED
        self.tile_sprites = pg.sprite.RenderUpdates()
        self.piece_sprites = pg.sprite.RenderUpdates()
        self.game_board = self.prepare_game_board(fen_string)

    def prepare_game_board(self, fen_string: str | None = "default"):
        colors = [pg.Color(248, 224, 176), pg.Color(163, 112, 67)]  # light, dark
        board = []
        for row_id, r in enumerate(self.ranks):
            color_idx = 0 if row_id % 2 == 0 else 1
            row = []
            for col_id, f in enumerate(self.files):
                color = colors[(color_idx + col_id) % 2]
                # position is x,y not y,x. That's why we give col_id first
                tile = Tile(name=f"{f}{r}", position=(col_id, row_id), color=color)
                row.append(tile)
                self.tile_sprites.add(tile)
            board.append(row)

        if fen_string:
            if fen_string == "default":
                fen_string = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
            FenParser.parse(fen_string, board, self.piece_sprites)

        return np.array(board, dtype=Tile).reshape((8, 8))

    def start(self):
        pg.init()
        pg.display.set_caption('Chess')
        self.screen = pg.display.set_mode([600, 600])
        pg.display.update()

        while True:
            for event in pg.event.get():
                match event.type:
                    case pg.QUIT:
                        sys.exit()
                    case pg.MOUSEBUTTONDOWN:
                        self.piece_sprites.update()

            self.tile_sprites.draw(self.screen)
            self.piece_sprites.draw(self.screen)
            pg.display.update()


if __name__ == "__main__":
    game = Game("default")
    game.start()
