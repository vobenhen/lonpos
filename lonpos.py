# d7341
# Solver for my little path puzzle. Can it find all the permutations?


import numpy as np
from blessings import Terminal  # for multiline text rewriting
from time import time


# convention
# 0 = empty space
# -1 = outside
# char = filled space of piece corresponding to the char


def create_pieces() -> list:
    """Create all of the valid pieces"""
    red = np.array([[1, 1, 1], [1, 1, 0]])
    cyan = np.array([[1, 1, 1], [1, 0, 0], [1, 0, 0]]) * 2
    orange = np.array([[1, 1, 1], [1, 0, 0]]) * 3
    lime = np.ones((2, 2), dtype=int) * 4
    white = np.array([[1, 1], [1, 0]]) * 5
    yellow = np.array([[1, 1, 1], [1, 0, 1]]) * 6
    blue = np.array([[1, 1, 1, 1], [1, 0, 0, 0]]) * 7
    purple = np.ones((4, 1), dtype=int) * 8
    pink = np.array([[1, 1, 0], [0, 1, 1], [0, 0, 1]]) * 9
    green = np.array([[1, 1, 1, 0], [0, 0, 1, 1]]) * 10
    gray = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]) * 11
    salmon = np.array([[1, 1, 1, 1], [0, 1, 0, 0]]) * 12
    tee = np.array([[1,1,1],[0,1,0],[0,1,0]]) * 14
    zed = np.array([[0,0,1],[1,1,1],[1,0,0]]) * 15
    return [red, cyan, orange, lime, white, yellow, blue, purple, pink, green, gray, salmon]


def rotate(piece: np.ndarray) -> np.ndarray:
    """Rotate a piece 90 degrees clockwise"""
    return np.rot90(piece)


def flip(piece: np.ndarray) -> np.ndarray:
    """Flip a piece 180 degrees"""
    return np.flip(piece, 1)  # flip along the vertical line of symmetry


def is_in(l:list, b:np.ndarray) -> bool:
    """Return if b is in l"""
    for p in l:
        if p.shape == b.shape and np.all(p == b):
            return True
    return False


def create_permutations(pieces: list = None) -> list:
    """Create all the possible permutations (rotations and flips) of all given pieces.
    A list of a list of different ways"""
    all_perms = []
    if pieces is None:
        pieces = create_pieces()

    for p in pieces:
        perms = []
        for f in range(2):
            for r in range(4):
                if not is_in(perms, p):
                    perms.append(p)
                p = rotate(p)
            p = flip(p)
        all_perms.append(perms)
    return all_perms


def create_board() -> np.ndarray:
    """Create a board of correct dimensions"""
    b = np.zeros((9, 9), dtype=int)
    invalid = 13
    b[3, 2] = invalid  # missing middle piece
    b[6:, 0] = invalid  # bottom right corner
    b[7:, 1] = invalid
    b[8, 2] = invalid
    b[0, 6:] = invalid  # bottom left corner
    b[1, 7:] = invalid
    b[2, 8] = invalid
    b[5, 7:] = invalid  # bottom
    b[6, 6:] = invalid
    b[7, 5:] = invalid
    b[8, 5:] = invalid
    return b


def place(board: np.ndarray, piece: np.ndarray, x: int, y: int) -> (bool, np.ndarray):
    """Place the piece in the board if possible"""
    # Offset the piece if it is L or +
    offset = np.where(piece[0] != 0)[0][0]

    # check dimensions
    if piece.shape[1] + x - offset > board.shape[1] or piece.shape[0] + y > board.shape[0] or x - offset < 0 or y < 0:
        return False, board  # Piece exceeds board space

    view = board[y:y + piece.shape[0], x - offset:x + piece.shape[1] - offset]

    if np.sum(view[piece != 0]) == 0:  # only replacing zeros with the piece
        temp = board.copy()
        temp[y:y + piece.shape[0], x - offset:x + piece.shape[1] - offset] += piece
        return True, temp
    return False, board


def compute(board: np.ndarray = None, perms: list = None, i=0, j=0, pieces: list = None, wait=False):
    if board is None:  # for if it is the initial call
        board = create_board()
    if perms is None:
        perms = create_permutations(pieces)

    global best_fit
    global dead_ends
    global best_times
    global solutions
    # Assumes that the top left piece of a piece is nonzero; so it will be filled in upon placement.
    # This is an invalid assumption eg for the + shape.

    # TODO: Make this multithreaded

    # i=x, j=y

    while j < board.shape[0]:
        while i < board.shape[1]:
            if board[j, i] == 0:  # find the piece that goes here!
                for p_inx in range(len(perms)):
                    piece_potentials = perms[p_inx]
                    for piece in piece_potentials:
                        poss, b = place(board, piece, i, j)
                        print_place(poss)
                        if poss:
                            print_board(b)
                            remaining = perms.copy()
                            remaining.pop(p_inx)
                            if len(remaining) <= best_fit:  # we're the best so far
                                if len(remaining) < best_fit:  # its a new best
                                    best_fit = len(remaining)
                                    best_times = 0
                                print(term.move(16, 0))
                                best_times += 1
                                print("Fitted", term.bold(str(12 - len(remaining)) + "/12"),
                                      "pieces into the board", term.bold(str(best_times)), "times")
                                print_board(b, good=True)
                                print_remaining(remaining)

                            if len(remaining) == 0:
                                # Done!
                                solutions.append(b)
                            else:
                                if wait:
                                    a = input("waiting")
                                compute(board=b, perms=remaining, i=i, j=j)  # next loop will increment i,j
                # Was unable to place the piece. So this sim sucks
                dead_ends += 1
                return
            i += 1
        j += 1
        i = 0
    return


def to_emoji(n: int, space=True) -> str:
    """Convert from number to emoji"""
    #             [red, cyan, orange, lime, white, yellow, blue, purple, pink, green, gray, salmon]
    emojis = ["⬛", "🟥", "🔵", "🟧", "🟩", "⬜", "🟨", "🟦", "🟣", "🟫", "🟢", "⚪", "🟠", "🚫", "🌾", "🎲"]
    # emojis = ['\U00002B1B', '\U0001F7E5', '\U0001F535', '\U0001F7E7', '\U0001F7E9', '\U00002B1C', '\U0001F7E8',
    # '\U0001F7E6', '\U0001F7E3', '\U0001F7EB', '\U0001F7E2', '\U000026AA', '\U0001F7E0']
    if space:
        emojis[0] = "  "
    return emojis[n]


def print_board(board: np.ndarray, good=False) -> None:
    """Print the board to the special screen"""
    try:
        buffs = []
        for line in board:
            buff = ""
            for ball in line:
                buff += to_emoji(int(ball))
            buffs.append(buff)
    except:
        print(board)
        a = input("ummm")

    # Flush the board
    if good:
        print(term.move(17, 0))
    else:
        print(term.move(5, 0))
    [print(i) for i in buffs]
    # print("➖" * 9)


def print_remaining(pieces: list) -> None:
    """Print the remaining pieces to play"""

    # Assume every piece is 4x4 at max
    buffs = []
    for r in range(4):
        buff = ""
        for p in pieces:
            if len(p[0]) > r:
                buff += "".join([to_emoji(int(i), space=True) for i in p[0][r]] + ["  "] * (4 - len(p[0][r])))
            else:
                buff += "".join(["  "] * 4)
            buff += " "
        buffs.append(buff)

    print(term.move(28, 0))
    print(term.move(28, 0))
    [print(term.clear_eol, i) for i in buffs]


def print_place(possible: bool) -> None:
    """Print the placement stats"""
    global total_placements
    global successful_placements
    global tic
    total_placements += 1
    successful_placements += possible
    print(term.move(2, 0))
    print(term.bold("{:,}".format(successful_placements)), "successful placements out of",
          term.bold("{:,}".format(total_placements)), "total placements with",
          term.bold("{:,}".format(dead_ends)), "dead ends")
    print("Running time of", term.bold("{:.2f} mins".format((time() - tic) / 60)))


if __name__ == "__main__":
    term = Terminal()
    print(term.clear())

    # create statistic variables
    total_placements = 0
    successful_placements = 0
    dead_ends = 0
    best_fit = 100  # best number of pieces fitted in the board
    best_times = 0  # number of times the best fit was achieved
    solutions = []
    tic = time()  # start time

    print(term.bold("Lonpos Game Solver v1.0"), term.green('"It almost works!"'))

    print(term.move(4, 0))
    print("Current board state:")

    print(term.move(15, 0))
    print("Best board so far:")

    print(term.move(27, 0))
    print("Remaining pieces:")

    try:
        with term.hidden_cursor():
            # print_board(create_board())
            if True:
                b = create_board()
                p = create_pieces()
                _, b = place(b, p[1], 0, 0)
                p.pop(1)
                pms = create_permutations(p)
                compute(b, pms, 0, 0)
            else:
                compute()
    except KeyboardInterrupt:
        pass
    finally:
        print(term.move(32, 0))
        #save_solutions(solutions)
