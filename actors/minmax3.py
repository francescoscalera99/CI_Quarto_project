from quarto import Quarto, Player
import numpy as np
from itertools import product
from utils import *

class MinMaxPlayer3(Player):
    def __init__(self, quarto: Quarto):
        super().__init__(quarto)
        self.max_depth = 2
    
    def choose_piece(self):
        
        board = self.get_game().get_board_status()
        possible_plies = possible_ply(board)

        evaluations = list()
        for ply in possible_plies:
            b = board.copy()
            b[ply[0]] = ply[1]
            eval = self.minmax(board = b, depth = self.max_depth, isMax = True, alpha = -float("inf"), beta = float("inf"))
            evaluations.append((ply[1], eval))

        all = dict()
        for k, v in evaluations:
            if k in all:
                if all[k] < v:
                    all[k] = v
                # all[k] = all[k] + v
            else:
                all.update({k: v})

        min_ply = min(all, key=all.get)

        print(f"min_ply piece: {min_ply}")
        
        return min_ply

    def place_piece(self):

        piece_to_place = self.get_game().get_selected_piece()
        board = self.get_game().get_board_status()

        possible_ply = list()
        boardSquares = list(product([*range(0,4)],repeat=2))
        for (x, y) in boardSquares:
            if board[x, y] == -1:
                possible_ply.append(((x, y), piece_to_place))

        evaluations = list()
        for ply in possible_ply:
            b = board.copy()
            b[ply[0]] = ply[1]
            eval = self.minmax(board = b, depth = self.max_depth, isMax = True, alpha = -float("inf"), beta = float("inf"))
            evaluations.append((ply, eval))

        max_ply = max(evaluations,key=lambda k: k[1])

        print(f"max_ply move: {max_ply}")
        
        return max_ply[0][0][1], max_ply[0][0][0]

    def minmax(self, board, isMax, depth, alpha, beta):

        # does this player win?
        if check_current_player_winner(board):
            if isMax:
                return 10000
            else:
                return -10000
        else:
            if check_if_board_full(board):
                return 0

        if depth == 0:
            return self.utility(board, isMax)

        if isMax:
            best_value = -float("inf")
            possible_plies = possible_ply(board)
            for ply in possible_plies:
                new_board = board.copy()
                new_board[ply[0]] = ply[1]
                value = self.minmax(board = new_board, isMax = False, depth = depth - 1, alpha = alpha, beta = beta)
                best_value = max(best_value, value)
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break
            return best_value
        else:
            best_value = float("inf")
            possible_plies = possible_ply(board)
            for ply in possible_plies:
                new_board = board.copy()
                new_board[ply[0]] = ply[1]
                value = self.minmax(board = new_board, isMax = True, depth = depth - 1, alpha = alpha, beta = beta)
                best_value = min(best_value, value)
                beta = min(beta, best_value)
                if beta <= alpha:
                    break
            return best_value

    def utility(self, int_board, isMax):
        score = 0

        binary_board = number_to_binary(int_board)

        # Number of completed rows/columns
        row = np.all(int_board != -1, axis = 0)
        col = np.all(int_board != -1, axis = 1)
        score += row.sum() * 10
        score += col.sum() * 10

        # Number of pieces with matching attributes
        magic = np.where(int_board != -1)
        for i, j in zip(magic[0], magic[1]):
            piece = binary_board[i][j]

            # check row
            for k in range(4):
                if k != j:
                    c = (piece == binary_board[i][k])
                    score += c.sum() * 3

            # check col
            for k in range(4):
                if k != i:
                    c = (piece == binary_board[k][j])
                    score += c.sum() * 3

            # check if piece is on diagonal
            if (i == j):
                for k in range(4):
                    if k != j:
                        c = (piece == binary_board[k][k])
                        score += c.sum() * 3
                        
            if ((i + j) == 3):
                for k in range(4):
                    if k != i and (3 - k) != j:
                        c = (piece == binary_board[k][3 - k])
                        score += c.sum() * 3

        if isMax:
            return score
        else:
            return -score
