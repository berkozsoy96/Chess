from pygame.image import load
from pygame.sprite import Sprite
from enum import Enum


piece_images = {
    "r": load(f"images/black_rook.png"),
    "n": load(f"images/black_knight.png"),
    "b": load(f"images/black_bishop.png"),
    "q": load(f"images/black_quenn.png"),
    "k": load(f"images/black_king.png"),
    "p": load(f"images/black_pawn.png"),
    "R": load(f"images/white_rook.png"),
    "N": load(f"images/white_knight.png"),
    "B": load(f"images/white_bishop.png"),
    "Q": load(f"images/white_quenn.png"),
    "K": load(f"images/white_king.png"),
    "P": load(f"images/white_pawn.png")
}


class Piece(Sprite):
    def __init__(self, piece_symbol: str, size: int, position: tuple[int, int]):
        Sprite.__init__(self)
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
    
    def __str__(self, name, position) -> str:
        color = "White" if self.color == "w" else "Black"
        files = ["a", "b", "c", "d", "e", "f", "g", "h"]
        ranks = list(range(1, 9))[::-1]
        return f"{color} {name} in {files[position[1]]}{ranks[position[0]]}"
    
    def calculate_legal_moves(self):
        ...
    
    def mouse_down(self, mouse_pos):
        if self.rect.left <= mouse_pos[0] <= self.rect.right and \
            self.rect.top <= mouse_pos[1] <= self.rect.bottom:
            self.on_mouse = True
            return True
    
    def mouse_up(self, mouse_pos):
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
            else:
                self.rect.x = self.position[1]*self.size
                self.rect.y = self.position[0]*self.size
            self.on_mouse = False

    def update(self, mouse_pos):
        if self.on_mouse:
            self.rect.x = mouse_pos[0] - self.size//2
            self.rect.y = mouse_pos[1] - self.size//2


class Pawn(Piece):
    def __init__(self, piece_symbol, size, position):
        super().__init__(piece_symbol, size, position)
        self.calculate_legal_moves()
    
    def calculate_legal_moves(self):
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

    def __str__(self) -> str:
        return super().__str__("Pawn", self.position)


class Rook(Piece):
    def __init__(self, piece_symbol, size, position):
        super().__init__(piece_symbol, size, position)
        self.calculate_legal_moves()
    
    def calculate_legal_moves(self):
        ...

    def __str__(self) -> str:
        return super().__str__("Rook", self.position)


class Bishop(Piece):
    def __init__(self, piece_symbol, size, position):
        super().__init__(piece_symbol, size, position)
        self.calculate_legal_moves()
    
    def calculate_legal_moves(self):
        ...

    def __str__(self) -> str:
        return super().__str__("Bishop", self.position)


class Knight(Piece):
    def __init__(self, piece_symbol, size, position):
        super().__init__(piece_symbol, size, position)
        self.calculate_legal_moves()
    
    def calculate_legal_moves(self):
        ...

    def __str__(self) -> str:
        return super().__str__("Knight", self.position)


class King(Piece):
    def __init__(self, piece_symbol, size, position):
        super().__init__(piece_symbol, size, position)
        self.calculate_legal_moves()
    
    def calculate_legal_moves(self):
        ...

    def __str__(self) -> str:
        return super().__str__("King", self.position)


class Queen(Piece):
    def __init__(self, piece_symbol, size, position):
        super().__init__(piece_symbol, size, position)
        self.calculate_legal_moves()
    
    def calculate_legal_moves(self):
        ...

    def __str__(self) -> str:
        return super().__str__("Queen", self.position)


class PieceType(Enum):
    p = Pawn
    r = Rook
    n = Knight
    b = Bishop
    q = Queen
    k = King
