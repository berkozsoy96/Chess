import numpy as np
import cv2


def create_board(size=800, light=(87, 136, 158), dark=(0, 46, 66)):
    board = np.zeros(shape=(size, size, 3), dtype="uint8")
    height, width = board.shape[:2]
    sq_h, sq_w = height // 8, width // 8
    dark_square = [[dark] * sq_w] * sq_h
    light_square = [[light] * sq_w] * sq_h
    colors = [light_square, dark_square]
    counter = 0
    for h in range(8):
        for w in range(8):
            color = colors[counter]
            board[h * sq_h: (h + 1) * sq_h, w * sq_w: (w + 1) * sq_w] = color
            counter = (counter + 1) % 2
        counter = (counter + 1) % 2
    return board


board = create_board()
cv2.imshow("board", board)
cv2.waitKey()
