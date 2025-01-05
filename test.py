import os
import re
from chess_cli import Chess
from stockfish import Stockfish
from dotenv import load_dotenv

load_dotenv()


def move_gen_test(depth, chess: Chess, max_depth, results):
    if depth == 0:
        return 1
    moves = chess.legal_moves
    positions = 0
    for move in moves:
        res = 0
        if chess.make_move(move):
            res = move_gen_test(depth - 1, chess, max_depth, results)
            if depth == max_depth:
                results[move] = res
                print(f"{move}: {res}")
        positions += res
        chess.undo_move()
    return positions


fen = "8/8/3p4/KPp4r/1R3p1k/4P3/6P1/8 w - c6 0 1"
depth = 2

stockfish_results = {}
move_count_line_matcher = re.compile(
    r"([a-z][1-8][a-z][1-8][q|r|n|b]{0,1}): (\d+)")

bot = Stockfish(os.getenv("STOCKFISH_PATH"))
bot.set_fen_position(fen)
# bot.make_moves_from_current_position(["a2a3"])
bot._put(f"go perft {depth}")

while True:
    line = bot._read_line()
    res = move_count_line_matcher.match(line)
    if res:
        move, count = res.groups()
        stockfish_results[move] = int(count)
    if "Nodes" in line:
        break

chess = Chess(fen=fen)
# chess.make_move("a2a3")
my_engine_results = {}
result = move_gen_test(depth, chess, depth, my_engine_results)

print("Results")
print(f"{len(stockfish_results) = }")
print(f"{len(my_engine_results) = }")
for move in stockfish_results:
    print(
        f"{'✅' if stockfish_results[move] == my_engine_results[move] else '❌'} {move}: {stockfish_results[move]} {my_engine_results[move]}")
