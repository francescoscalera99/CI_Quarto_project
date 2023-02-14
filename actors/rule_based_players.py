from quarto import Quarto, Player
import random
from copy import deepcopy
from itertools import product
from utils import check_tris
from utils import *


class RandomPlayer(Player):
    """Random player"""

    def __init__(self, quarto: Quarto) -> None:
        super().__init__(quarto)

    def choose_piece(self) -> int:
        return random.randint(0, 15)

    def place_piece(self) -> tuple[int, int]:
        return random.randint(0, 3), random.randint(0, 3)

class FirstCenter(Player):
    """FirstCenter player"""

    def __init__(self, quarto: Quarto) -> None:
        super().__init__(quarto)

    def choose_piece(self) -> int:
        return random.randint(0, 15)

    def place_piece(self) -> tuple[int, int]:
        if all(cell == -1 for lst in self.get_game().get_board_status() for cell in lst):
            return 1,1
        else:
            return random.randint(0, 3), random.randint(0, 3)

class FirstCorner(Player):
    """FirstCorner player"""

    def __init__(self, quarto: Quarto) -> None:
        super().__init__(quarto)

    def choose_piece(self) -> int:
        return random.randint(0, 15)

    def place_piece(self) -> tuple[int, int]:
        if all(i == -1 for lst in self.get_game().get_board_status() for i in lst):
            return 0,0
        else:
            return random.randint(0, 3), random.randint(0, 3)

class AggressivePlayer(Player):
    """AggressivePlayer player"""

    def __init__(self, quarto: Quarto) -> None:
        super().__init__(quarto)
        self.cells_row = [*range(0,4)]

    def choose_piece(self) -> int:
        board = self.get_game().get_board_status()
        _possible_pieces = possible_pieces(board)
        _possible_moves = possible_moves(board)
        for piece in _possible_pieces:
            for move in _possible_moves:
                new_board = deepcopy(board)
                new_board[move] = piece
                if check_current_player_winner(new_board):
                    # we know this piece is bad
                    _possible_pieces.remove(piece)
                    break

        if len(_possible_pieces) > 0:
            return _possible_pieces[0]
        else:
            return random.choice(possible_pieces(board))

    def place_piece(self) -> tuple[int, int]:
        piece_to_place = self.get_game().get_selected_piece()
        board = self.get_game().get_board_status()

        list_of_best = []

        poss_moves = possible_moves(board)

        for ply in poss_moves:
            if board[ply] == -1:
                # here we can test for the piece to place
                b = board.copy()
                b[ply] = piece_to_place          
                for j in range(4, 1, -1):
                    res = check_horizontal(b, j)
                    if res:
                        list_of_best.append((j, ply))
                    res = check_vertical(b, j)
                    if res:
                        list_of_best.append((j, ply))
                    res = check_diagonal(b, j)
                    if res:
                        list_of_best.append((j, ply))    

        if len(list_of_best) > 0:
            max_ply = max(list_of_best, key=lambda k: k[0])
            return max_ply[1][1], max_ply[1][0]
        else:
            return random.randint(0, 3), random.randint(0, 3)


class DefensivePlayer(Player):
    """DefensivePlayer player"""

    def __init__(self, quarto: Quarto) -> None:
        super().__init__(quarto)
        self.all = [*range(0, 16, 1)]
        self.cells_row = [*range(0,4)]

    def choose_piece(self) -> int:
        board = self.get_game().get_board_status()
        _possible_pieces = possible_pieces(board)
        _possible_moves = possible_moves(board)
        for piece in _possible_pieces:
            for move in _possible_moves:
                new_board = deepcopy(board)
                new_board[move] = piece
                if check_current_player_winner(new_board):
                    # we know this piece is bad
                    _possible_pieces.remove(piece)
                    break

        if len(_possible_pieces) > 0:
            return _possible_pieces[0]
        else:
            return random.choice(possible_pieces(board))

    def place_piece(self) -> tuple[int, int]:
        board = self.get_game().get_board_status()
        piece_to_place = self.get_game().get_selected_piece()
        _possible_moves = possible_moves(board)
        for move in _possible_moves:
            # here we can test for the piece to place
            new_board = deepcopy(board)
            new_board[move] = piece_to_place
            if check_current_player_winner(new_board):
                return move[1], move[0]

        # 2 check if there is a 3 piece row or column or diagnonal
        x, y = check_tris(board)
        if x != -1:
            return y, x
        else:
            return random.randint(0, 3), random.randint(0, 3)

class FirstCornerDefensivePlayer(Player):

    def __init__(self, quarto:Quarto) -> None:
        super().__init__(quarto)
        self.all_cells=[*range(16)]
        self.cells_row = [*range(0,4)]
    
    def choose_piece(self) -> int:
        flattened_board = sum(self.get_game().get_board_status().tolist(), [])
        available = list(set(self.all_cells) - set(flattened_board))
        random.shuffle(available)

        selected = -1

        boardSquares= list(product(self.cells_row, repeat=2))
    
        for piece_to_place in available:
            res = False
            for (x,y) in boardSquares:
                if self.get_game().get_board_status()[x][y] == -1:
                    # here we can test for the piece to place
                    copy_game = deepcopy(self.get_game())
                    copy_game.test_place(piece_to_place, x, y)
                    res= copy_game.check_winner() != -1
                    if res:
                        break
            if not res:
                selected=piece_to_place
                break

        if selected == -1:
            return random.choice(available)
        else:
            return selected

    
    def place_piece(self) -> tuple[int, int]:
        if all(cell == -1 for lst in self.get_game().get_board_status() for cell in lst):
            return 0,0
        else:
            piece_to_place = self.get_game().get_selected_piece()

            boardSquares= list(product(self.cells_row, repeat=2))
            random.shuffle(boardSquares)

            for (x,y) in boardSquares:       
            # 1 check if we can win
                if self.get_game().get_board_status()[x][y] == -1:
                    # here we can test for the piece to place
                    copy_game = deepcopy(self.get_game())
                    copy_game.test_place(piece_to_place, x, y)
                    res=copy_game.check_winner() != -1
                    if res:
                        return y, x

            # 2 check if there is a 3 piece row or column or diagnonal
            x, y = check_tris(self.get_game().get_board_status())
            if x != -1:
                return y, x
            else:
                return random.randint(0, 3), random.randint(0, 3)



class FirstCenterAggressivePlayer(Player):
    """AggressivePlayer player"""

    def __init__(self, quarto: Quarto) -> None:
        super().__init__(quarto)
        self.all = [*range(0, 16, 1)]
        self.cells_row = [*range(0,4)]

    def choose_piece(self) -> int:
        possible_ply = possible_ply(self.get_game().get_board_status())

        for ply in possible_ply:
            if self.get_game().get_board_status()[x][y] == -1:
                # here we can test for the piece to place
                copy_game = deepcopy(self.get_game())
                copy_game.test_place(piece_to_place, x, y)
                res= copy_game.check_winner() != -1
                if res:
                    break
            if not res:
                selected=piece_to_place
                break

        if selected == -1:
            return random.choice(available)
        else:
            return selected

    def place_piece(self) -> tuple[int, int]:
        if all(cell == -1 for lst in self.get_game().get_board_status() for cell in lst):
            return 1,1
        else:
            piece_to_place = self.get_game().get_selected_piece()

            list_of_best = []

            boardSquares= list(product(self.cells_row,repeat=2))
            random.shuffle(boardSquares)

            for (x,y) in boardSquares:
                if self.get_game().get_board_status()[x][y] == -1:
                    # here we can test for the piece to place
                    copy_game = deepcopy(self.get_game())
                    copy_game.test_place(piece_to_place, x, y)           
                    for j in range(4, 1, -1):
                        res = copy_game.check_horizontal(j)
                        if res:
                            list_of_best.append((j, x, y))
                        res = copy_game.check_vertical(j)
                        if res:
                            list_of_best.append((j, x, y))
                        res = copy_game.check_diagonal(j)
                        if res:
                            list_of_best.append((j, x, y))    

            list_of_best.sort(key=lambda x: x[0], reverse=True)
            if len(list_of_best) > 0:
                return list_of_best[0][2], list_of_best[0][1]
            else:
                return random.randint(0, 3), random.randint(0, 3)
