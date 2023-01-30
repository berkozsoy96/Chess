import pygame


piece_images = {
    "r": pygame.image.load(f"images/black_rook.png"),
    "n": pygame.image.load(f"images/black_knight.png"),
    "b": pygame.image.load(f"images/black_bishop.png"),
    "q": pygame.image.load(f"images/black_quenn.png"),
    "k": pygame.image.load(f"images/black_king.png"),
    "p": pygame.image.load(f"images/black_pawn.png"),
    "R": pygame.image.load(f"images/white_rook.png"),
    "N": pygame.image.load(f"images/white_knight.png"),
    "B": pygame.image.load(f"images/white_bishop.png"),
    "Q": pygame.image.load(f"images/white_quenn.png"),
    "K": pygame.image.load(f"images/white_king.png"),
    "P": pygame.image.load(f"images/white_pawn.png")
}


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


class Piece(pygame.sprite.Sprite):
    def __init__(self, piece_symbol, size, position):
        pygame.sprite.Sprite.__init__(self)
        self.piece_symbol = piece_symbol
        self.size = size
        self.position = position
        self.on_mouse = False

        self.image = piece_images[piece_symbol]
        self.rect = self.image.get_rect()
        self.rect.x = position[0]*self.size
        self.rect.y = position[1]*self.size
    
    def update(self, mouse_pos, event_type):
        if event_type == pygame.MOUSEBUTTONDOWN:
            if self.rect.left <= mouse_pos[0] <= self.rect.right and \
                self.rect.top <= mouse_pos[1] <= self.rect.bottom:
                self.on_mouse = True
                # show possible moves
        
        if self.on_mouse:
            self.rect.x = mouse_pos[0] - self.size//2
            self.rect.y = mouse_pos[1] - self.size//2
        
        if event_type == pygame.MOUSEBUTTONUP:
            if self.rect.left <= mouse_pos[0] <= self.rect.right and \
                self.rect.top <= mouse_pos[1] <= self.rect.bottom:
                # check possible moves
                # check captures

                position_x = mouse_pos[0]//self.size
                position_y = mouse_pos[1]//self.size
                self.rect.x = position_x*self.size
                self.rect.y = position_y*self.size
                self.on_mouse = False


class Game:
    def __init__(self, window_size) -> None:
        self.window_size = window_size
        size=min(self.window_size)//8
        self.tiles = pygame.sprite.Group()
        self.pieces = pygame.sprite.Group()
        self.fill_board(size=size)
        pygame.init()
        self.screen = pygame.display.set_mode(self.window_size)
    
    def fill_board(self, size=75, light_color=(255, 206, 158), dark_color=(209, 139, 71)):
        default_board = [
            "rnbqkbnr",
            "pppppppp",
            " "*8,
            " "*8,
            " "*8,
            " "*8,
            "PPPPPPPP",
            "RNBQKBNR"
        ]
        for i in range(8):
            for j in range(8):
                color = light_color if (i + j) % 2 == 0 else dark_color
                self.tiles.add(Tile(color, size, (i, j)))
                piece_char = default_board[j][i]
                if piece_char != " ":
                    self.pieces.add(Piece(piece_char, size, (i, j)))

    def main_loop(self):
        running = True
        while running:
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        running = False
                    case pygame.MOUSEBUTTONDOWN | pygame.MOUSEBUTTONUP | pygame.MOUSEMOTION: 
                        x, y = pygame.mouse.get_pos()
                        self.pieces.update((x, y), event.type)

            self.screen.fill((255, 255, 255))
            
            self.tiles.draw(self.screen)
            self.pieces.draw(self.screen)
            
            pygame.display.update()
        pygame.quit()


if __name__ == "__main__":
    game = Game((600, 600))
    game.main_loop()
