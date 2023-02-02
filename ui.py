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
    def __init__(self, piece_symbol: str, size: int, position: tuple[int, int]):
        pygame.sprite.Sprite.__init__(self)
        self.piece_symbol = piece_symbol
        self.position = position
        self.color = "w" if self.piece_symbol.isupper() else "b"
        self.size = size
        self.on_mouse = False
        
        self.legal_moves = []

        self.image = piece_images[piece_symbol]
        self.rect = self.image.get_rect()
        self.rect.y = position[0]*self.size
        self.rect.x = position[1]*self.size
    
    def calculate_legal_moves(self):
        print("here")
        pass

    def update(self, mouse_pos, event_type):
        if event_type == pygame.MOUSEBUTTONDOWN:
            if self.rect.left <= mouse_pos[0] <= self.rect.right and \
                self.rect.top <= mouse_pos[1] <= self.rect.bottom:
                self.on_mouse = True
                print(self.legal_moves)
        
        if self.on_mouse:
            self.rect.x = mouse_pos[0] - self.size//2
            self.rect.y = mouse_pos[1] - self.size//2
        
        if event_type == pygame.MOUSEBUTTONUP:
            if self.rect.left <= mouse_pos[0] <= self.rect.right and \
                self.rect.top <= mouse_pos[1] <= self.rect.bottom:
                # check captures
                position_y = mouse_pos[1]//self.size
                position_x = mouse_pos[0]//self.size
                if (position_y, position_x) in self.legal_moves:
                    self.position = (position_y, position_x)
                    self.rect.y = position_y*self.size
                    self.rect.x = position_x*self.size
                    self.calculate_legal_moves()
                elif (position_y, position_x) == self.position:
                    self.rect.x = self.position[1]*self.size
                    self.rect.y = self.position[0]*self.size
                    print("same place")
                else:
                    self.rect.x = self.position[1]*self.size
                    self.rect.y = self.position[0]*self.size
                    print("illegal")
                self.on_mouse = False


class Pawn(Piece):
    def __init__(self, piece_symbol, size, position):
        super().__init__(piece_symbol, size, position)
        self.calculate_legal_moves()
    
    def calculate_legal_moves(self):
        print("pawn")
        # TODO: need to know all the pieces on the 
        # board to calculate possible moves correctly
        match (self.color, self.position[0]):
            case ("w", 6):
                self.legal_moves = [
                    (5, self.position[1]),
                    (4, self.position[1])
                ]
            case ("w", rank):
                self.legal_moves = [
                    (rank-1, self.position[1])
                ]
            case ("b", 1):
                self.legal_moves = [
                    (2, self.position[1]),
                    (3, self.position[1])
                ]
            case ("b", rank):
                self.legal_moves = [
                    (rank+1, self.position[1])
                ]


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
                match default_board[i][j]:
                    case " ":
                        continue
                    case "p" | "P":
                        new_piece = Pawn(default_board[i][j], size, (i, j))
                    case char:
                        new_piece = Piece(char, size, (i, j))
                self.pieces.add(new_piece)

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
