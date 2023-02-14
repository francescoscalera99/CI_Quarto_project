from collections import Counter
from copy import deepcopy
from itertools import combinations
import random
from itertools import product
import numpy as np
import hashlib

BOARD_SIDE = 4

all = [*range(0, 16, 1)]

piece_dict = {
    -1: np.nan,
    0: [0, 0, 0, 0],
    1: [0, 0, 0, 1],
    2: [0, 0, 1, 0],
    3: [0, 0, 1, 1],
    4: [0, 1, 0, 0],
    5: [0, 1, 0, 1],
    6: [0, 1, 1, 0],
    7: [0, 1, 1, 1],
    8: [1, 0, 0, 0],
    9: [1, 0, 0, 1],
    10: [1, 0, 1, 0],
    11: [1, 0, 1, 1],
    12: [1, 1, 0, 0],
    13: [1, 1, 0, 1],
    14: [1, 1, 1, 0],
    15: [1, 1, 1, 1]
}

def three_in_a_row(in_list) -> bool:
    test_list = deepcopy(in_list)
    count_empty = Counter(test_list)

    if count_empty[-1] != 1:
        return False

    test_list.remove(-1)

    possible_combinations = combinations(test_list, 2)

    xor_combinations = [(a^b) for a,b in possible_combinations]

    or_result = xor_combinations[0] | xor_combinations[1] | xor_combinations[2]

    if or_result == 15:
        return False
    else:
        return True
    
def check_tris(in_board) -> tuple[int, int]:
    board_test = in_board.tolist()
    three_pieces=[]
    # horizontal
    for x in range(4):
        if three_in_a_row(board_test[x]):
            three_pieces.append((x, board_test[x].index(-1)))

    right_diag = []
    left_diag = []

    # vertical and generate the 2 diagnonals
    for y in range(4):
        right_diag.append(board_test[y][y])
        left_diag.append(board_test[y][3-y])
        temp = board_test[:][y]
        if three_in_a_row(temp):
            three_pieces.append((temp.index(-1), y))

    # right diag
    if three_in_a_row(right_diag):
        three_pieces.append((right_diag.index(-1), right_diag.index(-1)))

    # left diag
    if three_in_a_row(left_diag):
        three_pieces.append((left_diag.index(-1), 3-left_diag.index(-1)))

    if len(three_pieces) > 0:
        return random.choice(three_pieces)
    else:
        return -1, -1
    
def possible_ply(board) -> list():
    _possible_moves = possible_moves(board)
    _possible_pieces = possible_pieces(board)
    possible_plies = list(product(_possible_moves, _possible_pieces))
    random.shuffle(possible_plies)
    return possible_plies

def possible_moves(board) -> list():
    magic = np.where(board == -1)
    return [mov for mov in zip(magic[0], magic[1])]

def possible_pieces(board) -> list():
    flattened_board = sum(board.tolist(), [])
    return list(set(all) - set(flattened_board))

def check_current_player_winner(in_board) -> bool:
    board = number_to_binary(in_board)

    # horizontal
    hsum = np.sum(board, axis=1)
    if BOARD_SIDE in hsum or 0 in hsum:
        return True
    
    # vertical
    vsum = np.sum(board, axis=0)
    if BOARD_SIDE in vsum or 0 in vsum:
        return True
    
    # diagonal
    dsum1 = np.trace(board, axis1=0, axis2=1)
    dsum2 = np.trace(np.fliplr(board), axis1=0, axis2=1)
    if BOARD_SIDE in dsum1 or BOARD_SIDE in dsum2 or 0 in dsum1 or 0 in dsum2:
        return True
    
    return False

def number_to_binary(board) -> np.ndarray:
    binary_board = np.full(shape=(BOARD_SIDE, BOARD_SIDE, 4), fill_value=np.nan)
    for j in range(0, 4):
        for i in range(0, 4):
            binary_board[i, j][:] = piece_dict[board[i, j]]
    return binary_board

def check_if_board_full(board) -> bool:
    for row in board:
        for elem in row:
            if elem == -1:
                return False
    #print("tie")
    return True

def piece_xorer(piece, xorer):
    if piece != -1:
        return piece^xorer
    else:
        return piece

def boardHash(board):
    m1 = hashlib.sha256()
    m1.update(board.tobytes())
    return m1.hexdigest() 

def xorer_hash(board, piece):
    after_xor = xorer(board, piece)
    return boardHash(after_xor)

def xorer(board, piece_xor):
    new_board = deepcopy(board)
    vfunc = np.vectorize(piece_xorer)
    xored = vfunc(new_board, piece_xor)
    return xored

def symmRotation(board, numRot) -> np.ndarray:
    board_copy = deepcopy(board)
    board_copy = np.rot90(board_copy, numRot)
    return board_copy

def symmFlipOrizontal(board) -> np.ndarray:
    board_copy = deepcopy(board)
    board_copy = np.fliplr(board_copy)
    return board_copy

def symmFlipVertical(board) -> np.ndarray:
    board_copy = deepcopy(board)
    board_copy = np.flipud(board_copy)
    return board_copy

def symmFlipMid(board) -> np.ndarray:
    board_copy = deepcopy(board)
    board_copy[0][1] = board[0][2]
    board_copy[0][2] = board[0][1]
    board_copy[3][2] = board[3][1]
    board_copy[3][1] = board[3][2]

    board_copy[1][0] = board[2][0]
    board_copy[2][0] = board[1][0]
    board_copy[1][3] = board[2][3]
    board_copy[2][3] = board[1][3]

    board_copy[1][1] = board[2][2]
    board_copy[2][2] = board[1][1]
    board_copy[1][2] = board[2][1]
    board_copy[2][1] = board[1][2]
    return board_copy

def symmFlipInside(board) -> np.ndarray:
    board_copy = deepcopy(board)
    board_copy[0][0] = board[1][1]
    board_copy[1][1] = board[0][0]
    board_copy[0][1] = board[1][0]
    board_copy[1][0] = board[0][1]

    board_copy[0][2] = board[1][3]
    board_copy[1][3] = board[0][2]
    board_copy[0][3] = board[1][2]
    board_copy[1][2] = board[0][3]

    board_copy[2][0] = board[3][1]
    board_copy[3][1] = board[2][0]
    board_copy[2][1] = board[3][0]
    board_copy[3][0] = board[2][1]

    board_copy[2][2] = board[3][3]
    board_copy[3][3] = board[2][2]
    board_copy[2][3] = board[3][2]
    board_copy[3][2] = board[2][3]
    return board_copy

def de_symm_move(move, sym_typ, sym_count):
    
    board = np.ones(shape=(BOARD_SIDE, BOARD_SIDE), dtype=bool) * False
    board[move] = True
    
    if sym_typ == 'rot':
        board = symmRotation(board, 4 - sym_count)

    if sym_typ == 'flip_h':
        board = symmFlipOrizontal(board)

    if sym_typ == 'flip_v':
        board = symmFlipVertical(board)

    if sym_typ == 'flip_i':
        board = symmFlipInside(board)

    if sym_typ == 'flip_m':
        board = symmFlipMid(board)

    coordinate = np.where(board==True)

    return coordinate[0][0], coordinate[1][0]

def q_moves_to_list(in_dict):
    retval = list()
    check_list = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3), (3, 0), (3, 1), (3, 2), (3, 3)]
    for j in check_list:
        if j in in_dict:
            retval.append(in_dict[j])
        else:
            retval.append(91)
    return retval

def q_pieces_to_list(in_dict):
    retval = list()
    check_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    for j in check_list:
        if j in in_dict:
            retval.append(in_dict[j])
        else:
            retval.append(91)
    return retval

def q_moves_to_insertion(hash_value, in_dict, version) -> str:
    q = q_moves_to_list(in_dict)
    retval = "INSERT INTO moves (hash_value, version, '00', '01', '02', '03', '10', '11', '12', '13', '20', '21', '22', '23', '30', '31', '32', '33') VALUES " \
            f"('{hash_value}', {version}, {q[0]}, {q[1]}, {q[2]}, {q[3]}, {q[4]}, {q[5]}, {q[6]}, {q[7]}, {q[8]}, {q[9]}, {q[10]}, {q[11]}, {q[12]}, {q[13]}, {q[14]}, {q[15]})"
    return retval

def q_pieces_to_insertion(hash_value, in_dict, version) -> str:
    q = q_pieces_to_list(in_dict)
    retval = "INSERT INTO pieces (hash_value, version, '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15') VALUES " \
            f"('{hash_value}', {version}, {q[0]}, {q[1]}, {q[2]}, {q[3]}, {q[4]}, {q[5]}, {q[6]}, {q[7]}, {q[8]}, {q[9]}, {q[10]}, {q[11]}, {q[12]}, {q[13]}, {q[14]}, {q[15]})"
    return retval


    
def check_horizontal(board, board_len_test) -> bool:
    for i in range(board_len_test):
        high_values = [
            elem for elem in board[i] if elem >= 0 and (elem>>3)&1
        ]
        coloured_values = [
            elem for elem in board[i] if elem >= 0 and (elem>>2)&1
        ]
        solid_values = [
            elem for elem in board[i] if elem >= 0 and (elem>>1)&1
        ]
        square_values = [
            elem for elem in board[i] if elem >= 0 and (elem>>0)&1
        ]
        low_values = [
            elem for elem in board[i] if elem >= 0 and not (elem>>3)&1
        ]
        noncolor_values = [
            elem for elem in board[i] if elem >= 0 and not (elem>>2)&1
        ]
        hollow_values = [
            elem for elem in board[i] if elem >= 0 and not (elem>>1)&1
        ]
        circle_values = [
            elem for elem in board[i] if elem >= 0 and not (elem>>0)&1
        ]
        if len(high_values) == board_len_test or len(
                coloured_values
        ) == board_len_test or len(solid_values) == board_len_test or len(
                square_values) == board_len_test or len(low_values) == board_len_test or len(
                    noncolor_values) == board_len_test or len(
                        hollow_values) == board_len_test or len(
                            circle_values) == board_len_test:
            return True
    return False

def check_vertical(board, board_len_test)-> bool:
    for i in range(board_len_test):
        high_values = [
            elem for elem in board[:, i] if elem >= 0 and (elem>>3)&1
        ]
        coloured_values = [
            elem for elem in board[:, i] if elem >= 0 and (elem>>2)&1
        ]
        solid_values = [
            elem for elem in board[:, i] if elem >= 0 and (elem>>1)&1
        ]
        square_values = [
            elem for elem in board[:, i] if elem >= 0 and (elem>>0)&1
        ]
        low_values = [
            elem for elem in board[:, i] if elem >= 0 and not (elem>>3)&1
        ]
        noncolor_values = [
            elem for elem in board[:, i] if elem >= 0 and not (elem>>2)&1
        ]
        hollow_values = [
            elem for elem in board[:, i] if elem >= 0 and not (elem>>1)&1
        ]
        circle_values = [
            elem for elem in board[:, i] if elem >= 0 and not (elem>>0)&1
        ]
        if len(high_values) == board_len_test or len(
                coloured_values
        ) == board_len_test or len(solid_values) == board_len_test or len(
                square_values) == board_len_test or len(low_values) == board_len_test or len(
                    noncolor_values) == board_len_test or len(
                        hollow_values) == board_len_test or len(
                            circle_values) == board_len_test:
            return True
    return False

def check_diagonal(board, board_len_test)-> bool:
    high_values = []
    coloured_values = []
    solid_values = []
    square_values = []
    low_values = []
    noncolor_values = []
    hollow_values = []
    circle_values = []
    for i in range(board_len_test):
        if board[i, i] < 0:
            break
        if (board[i, i]>>3)&1:
            high_values.append(board[i, i])
        else:
            low_values.append(board[i, i])
        if (board[i, i]>>2)&1:
            coloured_values.append(board[i, i])
        else:
            noncolor_values.append(board[i, i])
        if (board[i, i]>>1)&1:
            solid_values.append(board[i, i])
        else:
            hollow_values.append(board[i, i])
        if (board[i, i]>>0)&1:
            square_values.append(board[i, i])
        else:
            circle_values.append(board[i, i])
    if len(high_values) == board_len_test or len(coloured_values) == board_len_test or len(
            solid_values) == board_len_test or len(square_values) == board_len_test or len(
                low_values
            ) == board_len_test or len(noncolor_values) == board_len_test or len(
                hollow_values) == board_len_test or len(circle_values) == board_len_test:
        return True
    high_values = []
    coloured_values = []
    solid_values = []
    square_values = []
    low_values = []
    noncolor_values = []
    hollow_values = []
    circle_values = []
    for i in range(board_len_test):
        if board[i, board_len_test - 1 - i] < 0:
            break
        if (board[i, board_len_test - 1 - i]>>3)&1:
            high_values.append(board[i, board_len_test - 1 - i])
        else:
            low_values.append(board[i, board_len_test - 1 - i])
        if (board[i, board_len_test - 1 - i]>>2)&1:
            coloured_values.append(
                board[i, board_len_test - 1 - i])
        else:
            noncolor_values.append(
                board[i, board_len_test - 1 - i])
        if (board[i, board_len_test - 1 - i]>>1)&1:
            solid_values.append(board[i, board_len_test - 1 - i])
        else:
            hollow_values.append(board[i, board_len_test - 1 - i])
        if (board[i, board_len_test - 1 - i]>>0)&1:
            square_values.append(board[i, board_len_test - 1 - i])
        else:
            circle_values.append(board[i, board_len_test - 1 - i])
    if len(high_values) == board_len_test or len(coloured_values) == board_len_test or len(
            solid_values) == board_len_test or len(square_values) == board_len_test or len(
                low_values
            ) == board_len_test or len(noncolor_values) == board_len_test or len(
                hollow_values) == board_len_test or len(circle_values) == board_len_test:
        return True
    return False