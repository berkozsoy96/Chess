from chess_cli import Chess, notation_to_position
import time


def move_gen_test(depth, chess: Chess, max_depth):
    if depth == 0:
        return 1
    moves = chess.legal_moves
    positions = 0
    for move in moves:
        chess.make_move(move)
        res = move_gen_test(depth - 1, chess, max_depth)
        if depth == max_depth:
            print(f"{move}: {res}")
        positions += res
        chess.undo_move()
    return positions

d = 1
chess = Chess(fen="rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8")
# d=5 default_fen 4865609
# chess.make_move("f2f4")
# chess.make_move("e7e5")
# chess.make_move("e1f2")
# chess.make_move("d8f6")
start = time.time()
result = move_gen_test(d, chess, d)
print(f"Depth: {d}, Positions: {result}, Time: {time.time() - start}")
