from chess_cli import Chess
import time


def move_gen_test(depth, chess: Chess):
    if depth == 0:
        return 1
    moves = chess.legal_moves
    positions = 0
    for move in moves:
        chess.make_move(move)
        result = move_gen_test(depth - 1, chess)
        if depth == 5:
            print(move, result)
        positions += result
        chess.undo_move()
    return positions


chess = Chess(fen="8/8/7p/3KNN1k/2p4p/8/3P2p1/8 w - - 0 1")
start = time.time()
result = move_gen_test(5, chess)
print(f"Depth: {5}, Positions: {result}, Time: {time.time() - start}")
