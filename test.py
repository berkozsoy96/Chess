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
depth = 6

stockfish_results = {}
move_count_line_matcher = re.compile(
    r"([a-z][1-8][a-z][1-8][q|r|n|b]{0,1}): (\d+)")

bot = Stockfish(os.getenv("STOCKFISH_PATH"))
bot.set_fen_position(fen)
# bot.make_moves_from_current_position(["h1f1"])
bot._put(f"go perft {depth}")

print("Stockfish")
while True:
    line = bot._read_line()
    res = move_count_line_matcher.match(line)
    if res:
        print(line)
        move, count = res.groups()
        stockfish_results[move] = int(count)
    if "Nodes" in line:
        break
print()

chess = Chess(fen=fen)
# chess.make_move("h1f1")
my_engine_results = {}
print("My Engine")
result = move_gen_test(depth, chess, depth, my_engine_results)
print()

print(f"{fen = }")
print(f"{depth = }")
print("Results")
print(f"{len(stockfish_results)=}", end=", ")
print(f"{len(my_engine_results)=}", end=", ")
print(f"{'✅' if len(my_engine_results) == len(stockfish_results) else '❌'}")
print("Move: Sf - My")
for move in list(set(list(stockfish_results.keys()) + list(my_engine_results.keys()))):
    sfmc = stockfish_results.get(move, "-")
    mymc = my_engine_results.get(move, "-")
    print(f"{'✅' if str(sfmc) == str(mymc) else '❌'} {move: <5}: {str(sfmc): >6} - {str(mymc): >6}")
