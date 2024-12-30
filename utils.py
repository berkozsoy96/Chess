FILES = "abcdefgh"
RANKS = "87654321"


def notation_to_position(notation: str) -> tuple[int, int]:
    """
    Convert a chess notation like 'e4' to (4, 4) (row, col).
    """
    col = FILES.index(notation[0])
    row = RANKS.index(notation[1])
    return (row, col)

def position_to_notation(position: tuple[int, int]) -> str:
    """
    Convert a chess position like (4, 4) (row, col) to 'e4'.
    """
    # position is (row, col) -> (ranks, files)
    return f"{FILES[position[1]]}{RANKS[position[0]]}"

