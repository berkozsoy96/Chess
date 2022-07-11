import numpy as np


def create_board(size=800, light=(87, 136, 158), dark=(0, 46, 66)):
    board_image = np.zeros(shape=(size, size, 3), dtype="uint8")
    sq_size = size // 8
    dark_square = [[dark] * sq_size] * sq_size
    light_square = [[light] * sq_size] * sq_size
    colors = [light_square, dark_square]
    counter = 0
    for h in range(8):
        for w in range(8):
            color = colors[counter]
            board_image[h * sq_size:(h + 1) * sq_size, w * sq_size:(w + 1) * sq_size] = color
            counter = (counter + 1) % 2
        counter = (counter + 1) % 2
    return board_image, sq_size
