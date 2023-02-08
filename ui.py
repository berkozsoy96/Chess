import pygame
from pieces import PieceType, Piece


class Tile(pygame.sprite.Sprite):
    def __init__(self, color, size, position):
        pygame.sprite.Sprite.__init__(self)
        
        self.color = color
        self.size = size
        self.position = position  # returns (y, x)

        self.image = pygame.Surface([self.size, self.size])
        self.rect = self.image.fill(self.color)
        self.rect.x = self.position[0]*self.size
        self.rect.y = self.position[1]*self.size


class Game:
    def __init__(self, window_size) -> None:
        self.window_size = window_size
        size=min(self.window_size)//8
        self.tiles = pygame.sprite.Group()
        self.pieces = pygame.sprite.Group()
        self.current_piece = None
        self.fill_board(
            size=size
        )
        self.turn_for_white = True
        pygame.init()
        self.screen = pygame.display.set_mode(self.window_size)
    
    def fill_board(self, fen=None, size=75, light_color=(255, 206, 158), dark_color=(209, 139, 71)):
        for i in range(8):
            for j in range(8):
                color = light_color if (i + j) % 2 == 0 else dark_color
                self.tiles.add(Tile(color, size, (i, j)))
        
        default_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        piece_dict = {i.name: i.value for i in PieceType}
        fen_string = fen if fen else default_fen
        piece_placement, turn, can_castle, en_passant, hm_clock, fm_clock = fen_string.split(" ")
        for rank_id, rank in zip(list(range(8)), piece_placement.split("/")):
            file_id = 0
            for file in rank:
                if file.isdigit():
                    file_id += int(file)
                else:
                    new_piece = piece_dict[file.lower()](file, size, (rank_id, file_id))
                    self.pieces.add(new_piece)
                    file_id += 1
    
    def main_loop(self):
        running = True
        while running:
            for event in pygame.event.get():
                x, y = pygame.mouse.get_pos()
                match event.type:
                    case pygame.QUIT:
                        running = False
                    case pygame.MOUSEBUTTONDOWN:
                        for piece in self.pieces.sprites():
                            piece: Piece
                            if piece.mouse_down((x, y)):
                                self.current_piece = piece
                                print(self.current_piece.legal_moves)
                                break
                    case pygame.MOUSEBUTTONUP:
                        if self.current_piece:
                            self.current_piece.mouse_up((x, y))
                    case pygame.MOUSEMOTION:
                        if self.current_piece:
                            self.current_piece.update((x, y))

            self.screen.fill((255, 255, 255))
            
            self.tiles.draw(self.screen)
            self.pieces.draw(self.screen)
            
            pygame.display.update()
        pygame.quit()


if __name__ == "__main__":
    game = Game((600, 600))
    game.main_loop()
