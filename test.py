from chess_cli import Chess
import time


def move_gen_test(depth, chess: Chess):
    if depth == 0:
        return 1
    moves = chess.legal_moves
    positions = 0
    for move in moves:
        chess.make_move(move)
        positions += move_gen_test(depth-1, chess)
        chess.undo_move()
    return positions

    

for d in range(1, 6):
    chess = Chess()
    start = time.time()
    result = move_gen_test(d, chess)
    print(f"Depth: {d}, Positions: {result}, Time: {time.time() - start}")
