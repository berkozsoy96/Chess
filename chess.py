from fen_parser import FenParser as fen
import pygame as pg
from pygame import mouse
from tile import Tile, Mouse
import sys


if __name__ == "__main__":
    window_size = (600, 600)
    
    # prepare mouse sprite
    mouse_sprite = pg.sprite.RenderUpdates()
    my_mouse = Mouse()
    mouse_sprite.add(my_mouse)

    # prepare piece sprites
    piece_sprites = pg.sprite.RenderUpdates()
    fen_str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    fen.parse(fen_str, piece_sprites)

    # prepare tile sprites
    tile_sprites = pg.sprite.RenderUpdates()
    colors = [pg.Color(248, 224, 176), pg.Color(163, 112, 67)]  # light, dark  # TODO: hardcoded
    for i in range(8):
        color_idx = 0 if i % 2 == 0 else 1
        for j in range(8):
            color = colors[(color_idx + j) % 2]
            # position is x,y not y,x. That's why we give col_id first
            tile_sprites.add(Tile((j, i), color))

    pg.init()
    pg.display.set_caption('Chess')
    screen = pg.display.set_mode(window_size)
    pg.display.update()

    while True:
        x, y = mouse.get_pos()
        mouse_sprite.update(coordinates=(x, y))
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    sys.exit()
                case pg.MOUSEBUTTONDOWN:
                    match event.button:
                        case pg.BUTTON_LEFT:
                            i = 8 * x // window_size[0]
                            j = 8 * y // window_size[1]
                            tile_sprites.update(position=(i, j))
                            piece_sprites.update(position=(i, j))
        tile_sprites.draw(screen)
        piece_sprites.draw(screen)
        mouse_sprite.draw(screen)
        pg.display.update()
