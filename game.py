from dataclasses import dataclass
from enum import Enum, auto

import numpy as np


class Color(Enum):
    WHITE = auto()
    BLACK = auto()


@dataclass
class Piece:
    name: str

    def __str__(self):
        return self.name


class Player:
    def __init__(self, player_name: str, color: Color):
        self.player_name = player_name
        self.color = color


class Tile:
    def __init__(self, tile_id: int, piece: Piece | None):
        self.tile_id = tile_id
        self.piece = piece

    def __str__(self):
        return f"{self.tile_id}, {self.piece}"


class Game:
    def __init__(self, fen_string: str | None = None):
        self.ranks = [8, 7, 6, 5, 4, 3, 2, 1]  # rows  # TODO: HARD CODED
        self.files = ["a", "b", "c", "d", "e", "f", "g", "h"]  # cols  # TODO: HARD CODED
        self.game_board = self.prepare_game_board(fen_string)

        self.turn_count = 0
        self.player_count = 2
        self.board_perspective = "white"
        self.move_history = []

    @staticmethod
    def prepare_game_board(fen_string: str | None = "default"):
        board = []
        if fen_string is None:
            for i in range(64):  # TODO: HARD CODED
                board.append(Tile(i, None))
            return np.array(board).reshape((8, 8))

        if fen_string == "default":
            fen_string = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        for i in range(64):  # TODO: HARD CODED
            board.append(Tile(i, Piece(str(i))))
        return np.array(board).reshape((8, 8))


@dataclass
class History:
    moved_from: Tile
    moved_to: Tile


if __name__ == '__main__':
    game = Game()
    for i in range(8):
        for j in range(8):
            print(game.game_board[i, j])
