import quarto
from quarto import Quarto, Player
import random
import sqlite3
import sys
import gc
import numpy as np
from utils import *

class ReinforcementV1(Player):
    """ReinforcementV1 player"""

    def __init__(self, quarto: Quarto, alpha=0.15, random_factor=0.8) -> None:
        super().__init__(quarto)
        self.cells_row = [*range(0,4)]
        self.all = [*range(0, 16, 1)]
        self.q_moves = dict()
        self.q_pieces = dict()
        self.alpha = alpha
        self.random_factor = random_factor
        self.history_state_moves = list()
        self.history_state_pieces = list()
        self.opp_history_state_moves = list()
        self.opp_history_state_pieces = list()
        self.hitratio = 0
        self.preGame = np.array([])
        
        self.read_from_db(5)

    def seek_symm_pieces(self, board):
        hash_board = 0
        found_symmetry = False
        sym_type = ''
        sym_count = 0
        if not found_symmetry:
            for r in range(1,4):
                copyBoard = symmRotation(board, r)
                hash_board_Symm = boardHash(copyBoard)
                if hash_board_Symm in self.q_pieces:
                    hash_board = hash_board_Symm
                    found_symmetry = True
                    sym_type = 'rot'
                    sym_count = r
                    break

        if not found_symmetry:
            copyBoard = symmFlipOrizontal(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_pieces:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_h'
        
        if not found_symmetry:
            copyBoard = symmFlipVertical(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_pieces:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_v'
        
        if not found_symmetry:
            copyBoard = symmFlipMid(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_pieces:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_m'
        
        if not found_symmetry:
            copyBoard = symmFlipInside(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_pieces:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_i'

        return hash_board, sym_type, sym_count

    def seek_symm_moves(self, board):
        hash_board = 0
        found_symmetry = False
        sym_type = ''
        sym_count = 0
        if not found_symmetry:
            for r in range(1,4):
                copyBoard = symmRotation(board, r)
                hash_board_Symm = boardHash(copyBoard)
                if hash_board_Symm in self.q_moves:
                    hash_board = hash_board_Symm
                    found_symmetry = True
                    sym_type = 'rot'
                    sym_count = r
                    break

        if not found_symmetry:
            copyBoard = symmFlipOrizontal(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_moves:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_h'
        
        if not found_symmetry:
            copyBoard = symmFlipVertical(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_moves:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_v'
        
        if not found_symmetry:
            copyBoard = symmFlipMid(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_moves:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_m'
        
        if not found_symmetry:
            copyBoard = symmFlipInside(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_moves:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_i'

        return hash_board, sym_type, sym_count


    def choose_piece(self) -> int:
        board = self.get_game().get_board_status()

        piece_choosen = None
        randomN = random.random()
        hash_board = boardHash(board)

        if hash_board not in self.q_pieces:
            #look for symmetries
            hash_board_temp, _, _ = self.seek_symm_pieces(board) 
            if hash_board_temp != 0:
                hash_board=hash_board_temp
               
        poss_pieces = possible_pieces(board)

        if not hash_board in self.q_pieces:
            self.q_pieces.update({hash_board : {one_piece : 0 for one_piece in poss_pieces}})
        else:
            self.hitratio += 1        

        if randomN < self.random_factor:
            piece_choosen = random.choice(poss_pieces)
        else:
            potential_pieces = self.q_pieces[hash_board]
            piece_choosen = max(potential_pieces, key= potential_pieces.get)

        self.update_history_state_pieces(hash_board, piece_choosen)
        return piece_choosen

    def update_history_state_moves(self, hash_board, ply):
        self.history_state_moves.append((hash_board, ply))

    def update_history_state_pieces(self, hash_board, ply):
        self.history_state_pieces.append((hash_board, ply))

    def update_opp_history_state_moves(self, hash_board, ply):
        self.opp_history_state_moves.append((hash_board, ply))

    def update_opp_history_state_pieces(self, hash_board, ply):
        self.opp_history_state_pieces.append((hash_board, ply))

    def saveOpponentMoveAndPiece(self, piece_to_place):
        if len(self.preGame) == 0:
            return

        board=self.get_game().get_board_status()
        opponentMoveDirt = np.where(( board - self.preGame) != 0)
        opponentMove = (opponentMoveDirt[0][0], opponentMoveDirt[1][0])
        hash_board = boardHash(board)
    
        if hash_board not in self.q_pieces:
            hash_board_temp, _, _ = self.seek_symm_pieces(board) 
            if hash_board_temp != 0:
                hash_board=hash_board_temp
        
        if not hash_board in self.q_pieces:
            poss_pieces = possible_pieces(board)
            self.q_pieces.update({hash_board : {one_piece : 0 for one_piece in poss_pieces}})

        self.update_opp_history_state_pieces(hash_board, piece_to_place)
        
        prePiece= board[opponentMove[0]][opponentMove[1]]

        xored_board = xorer(self.preGame, prePiece)
        found_symm = False
        hash_board = boardHash(xored_board)
        if hash_board not in self.q_moves:
            #look for symmetries
            hash_board_temp, sym_type, sym_count = self.seek_symm_moves(xored_board) 
            if hash_board_temp != 0:
                found_symm = True
                hash_board = hash_board_temp

        if hash_board not in self.q_moves:
            poss_actions = possible_moves(self.preGame)
            self.q_moves.update({hash_board : {one_action : 0 for one_action in poss_actions}})
        
        if found_symm:
            opponentMoveSymm = de_symm_move(opponentMove, sym_type, -sym_count-4)
            self.update_opp_history_state_moves(hash_board, opponentMoveSymm)                 
        else:
            self.update_opp_history_state_moves(hash_board, opponentMove)
       
           


    def place_piece(self) -> tuple[int, int]:
        board = self.get_game().get_board_status()
        piece_to_place = self.get_game().get_selected_piece()

        action_chosen = None
        randomN = random.random()

        self.saveOpponentMoveAndPiece(piece_to_place)

        # board xor with the piece
        # seek sym on board xored
        xored_board = xorer(board, piece_to_place)
        found_symm = False
        hash_board = boardHash(xored_board)
        if hash_board not in self.q_moves:
            #look for symmetries
            hash_board_temp, sym_type, sym_count = self.seek_symm_moves(xored_board) 
            if hash_board_temp != 0:
                found_symm = True
                hash_board = hash_board_temp
                # print("sym")

        if found_symm:
            # print(f'found symm: {found_symm}')
            if randomN < self.random_factor:
                # print(f'random: {randomN}')
                potential_actions_sym = list(self.q_moves[hash_board].keys())
                action_chosen_sym = random.choice(potential_actions_sym)
            else:
                # print(f'not random: {randomN}')
                potential_actions_sym = self.q_moves[hash_board]
                action_chosen_sym = max(potential_actions_sym, key= potential_actions_sym.get)
            
            self.update_history_state_moves(hash_board, action_chosen_sym)
            action_chosen = de_symm_move(action_chosen_sym, sym_type, sym_count)
        else:
            initial_poss_actions = possible_moves(board)
            if not hash_board in self.q_moves:
                self.q_moves.update({hash_board : {one_action : 0 for one_action in initial_poss_actions}})

            # print(f'not found symm: {found_symm}')
            if randomN < self.random_factor:
                # print(f'random: {randomN}')
                action_chosen = random.choice(initial_poss_actions)
            else:
                # print(f'not random: {randomN}')
                potential_actions = self.q_moves[hash_board]
                action_chosen = max(potential_actions, key= potential_actions.get)
            
            self.update_history_state_moves(hash_board, action_chosen)

        
        copy_board = board
        copy_board[action_chosen[0], action_chosen[1]] = piece_to_place
        self.preGame = copy_board
        
        return action_chosen[1], action_chosen[0]
    
    def learn_all(self, reward):
        
        for h in self.history_state_moves:
            self.__learn_moves(h[0], h[1], reward = reward)

        for h in self.history_state_pieces:
            self.__learn_pieces(h[0], h[1], reward = reward)

        for h in self.opp_history_state_moves:
            self.__learn_moves(h[0], h[1], reward = -reward)

        for h in self.opp_history_state_pieces:
            self.__learn_pieces(h[0], h[1], reward = -reward)

        self.history_state_moves = list()
        self.history_state_pieces = list()
        self.opp_history_state_moves = list()
        self.opp_history_state_pieces = list()
        self.preGame = np.array([])

    def nowExploit(self,random_factor):
        # print("hi there")
        self.random_factor = random_factor
    
    def __learn_moves(self, state, ply, reward):
        self.q_moves[state][ply] = self.q_moves[state][ply] + self.alpha * (reward - self.q_moves[state][ply])
    
    def __learn_pieces(self, state, ply, reward):
        self.q_pieces[state][ply] = self.q_pieces[state][ply] + self.alpha * (reward - self.q_pieces[state][ply])

    def __row_to_q_moves(self, row):
        temp_dict = dict()
        check_list = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3), (3, 0), (3, 1), (3, 2), (3, 3)]
        for a, b in zip(check_list, row[3:19]):
            if b != 91:
                temp_dict.update({a : b})
        self.q_moves.update({row[1]: temp_dict})
        
    def __row_to_q_pieces(self, row):
        temp_dict = dict()
        check_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        for a, b in zip(check_list, row[3:19]):
            if b != 91:
                temp_dict.update({a : b})
        self.q_pieces.update({row[1]: temp_dict})

    def save_to_db(self, version):
        conn = sqlite3.connect('actors/final_database/reinforcement.db')
        cursor = conn.cursor()

        print("Saving data to DB")

        for key, value in self.q_moves.items():
            insertion = q_moves_to_insertion(hash_value = key, in_dict = value, version = version)
            cursor.execute(insertion)

        for key, value in self.q_pieces.items():
            insertion = q_pieces_to_insertion(hash_value = key, in_dict = value, version = version)
            cursor.execute(insertion)

        print("Finished Saving data to DB")

        conn.commit()
        conn.close()

    def read_from_db(self, version):
        conn = sqlite3.connect('actors/final_database/reinforcement.db')
        cursor = conn.cursor()

        print("Reading data from DB")

        statement = f"SELECT * FROM moves WHERE version = {version}"
        cursor.execute(statement)
        while True:
            rows = cursor.fetchmany(10000)
            if len(rows) == 0:
                break
            for row in rows:
                self.__row_to_q_moves(row)

        print("first part")
        cursor.close()
        conn.close()
        gc.collect()


        conn = sqlite3.connect('actors/final_database/reinforcement.db')
        cursor = conn.cursor()

        statement = f"SELECT * FROM pieces WHERE version = {version}"
        cursor.execute(statement)
        while True:
            rows = cursor.fetchmany(10000)
            if len(rows) == 0:
                break
            for row in rows:
                self.__row_to_q_pieces(row)

        print("Finished Reading data from DB")

        conn.close()

class ReinforcementPlay(Player):
    """ReinforcementPlay player"""

    def __init__(self, quarto: Quarto) -> None:
        super().__init__(quarto)
        self.cells_row = [*range(0,4)]
        self.all = [*range(0, 16, 1)]

        self.q_moves = dict()
        self.q_pieces = dict()
        self.hit_move = 0
        self.no_hit_move = 0
        self.hit_piece = 0
        self.no_hit_piece = 0
        self.place_call = 0
        self.choose_call = 0
        self.place_special = 0
        self.choose_special = 0
        
        self.read_from_db(11)


    def seek_symm_pieces(self, board):
        hash_board = 0
        found_symmetry = False
        sym_type = ''
        sym_count = 0
        if not found_symmetry:
            for r in range(1,4):
                copyBoard = symmRotation(board, r)
                hash_board_Symm = boardHash(copyBoard)
                if hash_board_Symm in self.q_pieces:
                    hash_board = hash_board_Symm
                    found_symmetry = True
                    sym_type = 'rot'
                    sym_count = r
                    break

        if not found_symmetry:
            copyBoard = symmFlipOrizontal(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_pieces:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_h'
        
        if not found_symmetry:
            copyBoard = symmFlipVertical(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_pieces:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_v'
        
        if not found_symmetry:
            copyBoard = symmFlipMid(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_pieces:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_m'
        
        if not found_symmetry:
            copyBoard = symmFlipInside(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_pieces:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_i'

        return hash_board, sym_type, sym_count

    def seek_symm_moves(self, board):
        hash_board = 0
        found_symmetry = False
        sym_type = ''
        sym_count = 0
        if not found_symmetry:
            for r in range(1,4):
                copyBoard = symmRotation(board, r)
                hash_board_Symm = boardHash(copyBoard)
                if hash_board_Symm in self.q_moves:
                    hash_board = hash_board_Symm
                    found_symmetry = True
                    sym_type = 'rot'
                    sym_count = r
                    break

        if not found_symmetry:
            copyBoard = symmFlipOrizontal(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_moves:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_h'
        
        if not found_symmetry:
            copyBoard = symmFlipVertical(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_moves:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_v'
        
        if not found_symmetry:
            copyBoard = symmFlipMid(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_moves:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_m'
        
        if not found_symmetry:
            copyBoard = symmFlipInside(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_moves:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_i'

        return hash_board, sym_type, sym_count


    def choose_piece(self) -> int:
        self.choose_call += 1
        board = self.get_game().get_board_status()

        piece_choosen = None
        hash_board = boardHash(board)

        if hash_board not in self.q_pieces:
            #look for symmetries
            hash_board_temp, _, _ = self.seek_symm_pieces(board) 
            if hash_board_temp != 0:
                hash_board=hash_board_temp

        poss_pieces = possible_pieces(board)
        if len(poss_pieces) < 6:
            self.choose_special += 1
            # last 6 pieces
            # this uses defensive logic
            poss_moves = possible_moves(board)
            for piece in poss_pieces:
                for move in poss_moves:
                    new_board = deepcopy(board)
                    new_board[move] = piece
                    if check_current_player_winner(new_board):
                        poss_pieces.remove(piece)
                        break
            # check if list is empty, otherwise reset the list 
            if len(poss_pieces) == 0:
                poss_pieces = possible_pieces(board)
            return random.choice(poss_pieces)
        else:
            # first 10 pieces
            # this uses the q_pieces hashmap
            if hash_board not in self.q_pieces:
                piece_choosen = random.choice(poss_pieces)
                self.no_hit_piece += 1
            else:
                potential_pieces = self.q_pieces[hash_board]
                piece_choosen = max(potential_pieces, key= potential_pieces.get)
                self.hit_piece += 1

        return piece_choosen

    def place_piece(self) -> tuple[int, int]:
        self.place_call += 1
        board = self.get_game().get_board_status()
        piece_to_place = self.get_game().get_selected_piece()

        _possible_moves = possible_moves(board)
        for move in _possible_moves:
            new_board = deepcopy(board)
            new_board[move] = piece_to_place
            if check_current_player_winner(new_board):
                return move[1], move[0]

        check = possible_pieces(board)
        if len(check) < 6:
            self.place_special += 1
            # last 6 moves
            x, y = check_tris(board)
            if x != -1:
                return y, x
            else:
                return random.randint(0, 3), random.randint(0, 3)
        else:
            # first 10 moves
            action_chosen = None

            xored_board = xorer(board, piece_to_place)
            found_symm = False
            hash_board = boardHash(xored_board)
            if hash_board not in self.q_moves:
                #look for symmetries
                hash_board_temp, sym_type, sym_count = self.seek_symm_moves(xored_board) 
                if hash_board_temp != 0:
                    found_symm = True
                    hash_board = hash_board_temp
                    # print("sym")

            if found_symm:
                potential_actions_sym = self.q_moves[hash_board]
                action_chosen_sym = max(potential_actions_sym, key= potential_actions_sym.get)
                action_chosen = de_symm_move(action_chosen_sym, sym_type, sym_count)
                self.hit_move += 1
                return action_chosen[1], action_chosen[0]
            else:
                # no sym
                if not hash_board in self.q_moves:
                    # no hit
                    # use defensive logic
                    self.no_hit_move += 1
                    x, y = check_tris(board)
                    if x != -1:
                        return y, x
                    else:
                        return random.randint(0, 3), random.randint(0, 3)
                else:
                    # hit on hash not sym
                    self.hit_move += 1
                    potential_actions = self.q_moves[hash_board]
                    action_chosen = max(potential_actions, key= potential_actions.get)
                    return action_chosen[1], action_chosen[0]       
    
    def printHits(self):
        print("we have these nuts for moves:")
        print(f"hits: {self.hit_move}")
        print(f"NOhits: {self.no_hit_move}")
        print(f"calls: {self.place_call}")
        print(f"special: {self.place_special}")
        print(f"q_moves length {len(self.q_moves)}")
        print("we have these nuts for pieces:")
        print(f"hits: {self.hit_piece}")
        print(f"NOhits: {self.no_hit_piece}")
        print(f"calls: {self.choose_call}")
        print(f"special: {self.choose_special}")
        print(f"q_moves length {len(self.q_pieces)}")

    def __row_to_q_moves(self, row):
        temp_dict = dict()
        check_list = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3), (3, 0), (3, 1), (3, 2), (3, 3)]
        for a, b in zip(check_list, row[3:19]):
            if b != 91:
                temp_dict.update({a : b})
        self.q_moves.update({row[1]: temp_dict})
        
    def __row_to_q_pieces(self, row):
        temp_dict = dict()
        check_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        for a, b in zip(check_list, row[3:19]):
            if b != 91:
                temp_dict.update({a : b})
        self.q_pieces.update({row[1]: temp_dict})

    def read_from_db(self, version):
        conn = sqlite3.connect('actors/final_database/reinforcement.db')
        cursor = conn.cursor()

        print("Reading data from DB")

        statement = f"SELECT * FROM moves WHERE version = {version}"
        cursor.execute(statement)
        while True:
            rows = cursor.fetchmany(10000)
            if len(rows) == 0:
                break
            for row in rows:
                self.__row_to_q_moves(row)

        print("first part")
        cursor.close()
        conn.close()
        gc.collect()

        conn = sqlite3.connect('actors/final_database/reinforcement.db')
        cursor = conn.cursor()

        statement = f"SELECT * FROM pieces WHERE version = {version}"
        cursor.execute(statement)
        while True:
            rows = cursor.fetchmany(10000)
            if len(rows) == 0:
                break
            for row in rows:
                self.__row_to_q_pieces(row)

        print("Finished Reading data from DB")

        conn.close()

class ReinforcementV2(Player):
    """ReinforcementV2 player"""

    def __init__(self, quarto: Quarto, alpha=0.15, random_factor=0.8) -> None:
        super().__init__(quarto)
        self.cells_row = [*range(0,4)]
        self.all = [*range(0, 16, 1)]
        self.q_moves = dict()
        self.q_pieces = dict()
        self.alpha = alpha
        self.random_factor = random_factor
        self.history_state_moves = list()
        self.history_state_pieces = list()
        self.opp_history_state_moves = list()
        self.opp_history_state_pieces = list()
        self.hitratio = 0
        self.preGame = np.array([])
        
        # self.read_from_db(5)

    def seek_symm_pieces(self, board):
        hash_board = 0
        found_symmetry = False
        sym_type = ''
        sym_count = 0
        if not found_symmetry:
            for r in range(1,4):
                copyBoard = symmRotation(board, r)
                hash_board_Symm = boardHash(copyBoard)
                if hash_board_Symm in self.q_pieces:
                    hash_board = hash_board_Symm
                    found_symmetry = True
                    sym_type = 'rot'
                    sym_count = r
                    break

        if not found_symmetry:
            copyBoard = symmFlipOrizontal(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_pieces:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_h'
        
        if not found_symmetry:
            copyBoard = symmFlipVertical(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_pieces:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_v'
        
        if not found_symmetry:
            copyBoard = symmFlipMid(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_pieces:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_m'
        
        if not found_symmetry:
            copyBoard = symmFlipInside(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_pieces:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_i'

        return hash_board, sym_type, sym_count

    def seek_symm_moves(self, board):
        hash_board = 0
        found_symmetry = False
        sym_type = ''
        sym_count = 0
        if not found_symmetry:
            for r in range(1,4):
                copyBoard = symmRotation(board, r)
                hash_board_Symm = boardHash(copyBoard)
                if hash_board_Symm in self.q_moves:
                    hash_board = hash_board_Symm
                    found_symmetry = True
                    sym_type = 'rot'
                    sym_count = r
                    break

        if not found_symmetry:
            copyBoard = symmFlipOrizontal(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_moves:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_h'
        
        if not found_symmetry:
            copyBoard = symmFlipVertical(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_moves:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_v'
        
        if not found_symmetry:
            copyBoard = symmFlipMid(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_moves:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_m'
        
        if not found_symmetry:
            copyBoard = symmFlipInside(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_moves:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_i'

        return hash_board, sym_type, sym_count

    def choose_piece(self) -> int:        
        board = self.get_game().get_board_status()

        piece_choosen = None
        randomN = random.random()
        hash_board = boardHash(board)

        if hash_board not in self.q_pieces:
            #look for symmetries
            hash_board_temp, _, _ = self.seek_symm_pieces(board) 
            if hash_board_temp != 0:
                hash_board=hash_board_temp
               
        poss_pieces = possible_pieces(board)

        if not hash_board in self.q_pieces:
            self.q_pieces.update({hash_board : {one_piece : 0 for one_piece in poss_pieces}})

        if len(poss_pieces) < 6:
            # last 6 pieces
            poss_moves = possible_moves(board)
            for piece in poss_pieces:
                for move in poss_moves:
                    new_board = deepcopy(board)
                    new_board[move] = piece
                    if check_current_player_winner(new_board):
                        poss_pieces.remove(piece)
                        break
            # check if list is empty, otherwise reset the list 
            if len(poss_pieces) == 0:
                poss_pieces = possible_pieces(board)
            return random.choice(poss_pieces)
        else:
            # first 10 pieces
            if randomN < self.random_factor:
                piece_choosen = random.choice(poss_pieces)
            else:
                potential_pieces = self.q_pieces[hash_board]
                piece_choosen = max(potential_pieces, key= potential_pieces.get)

        self.update_history_state_pieces(hash_board, piece_choosen)
        return piece_choosen

    def update_history_state_moves(self, hash_board, ply):
        self.history_state_moves.append((hash_board, ply))

    def update_history_state_pieces(self, hash_board, ply):
        self.history_state_pieces.append((hash_board, ply))

    def update_opp_history_state_moves(self, hash_board, ply):
        self.opp_history_state_moves.append((hash_board, ply))

    def update_opp_history_state_pieces(self, hash_board, ply):
        self.opp_history_state_pieces.append((hash_board, ply))

    def saveOpponentMoveAndPiece(self, piece_to_place):
        if len(self.preGame) == 0:
            return

        board=self.get_game().get_board_status()
        opponentMoveDirt = np.where(( board - self.preGame) != 0)
        opponentMove = (opponentMoveDirt[0][0], opponentMoveDirt[1][0])
        hash_board = boardHash(board)
    
        if hash_board not in self.q_pieces:
            hash_board_temp, _, _ = self.seek_symm_pieces(board) 
            if hash_board_temp != 0:
                hash_board=hash_board_temp
        
        if not hash_board in self.q_pieces:
            poss_pieces = possible_pieces(board)
            self.q_pieces.update({hash_board : {one_piece : 0 for one_piece in poss_pieces}})

        self.update_opp_history_state_pieces(hash_board, piece_to_place)
        
        prePiece= board[opponentMove[0]][opponentMove[1]]

        xored_board = xorer(self.preGame, prePiece)
        found_symm = False
        hash_board = boardHash(xored_board)
        if hash_board not in self.q_moves:
            #look for symmetries
            hash_board_temp, sym_type, sym_count = self.seek_symm_moves(xored_board) 
            if hash_board_temp != 0:
                found_symm = True
                hash_board = hash_board_temp

        if hash_board not in self.q_moves:
            poss_actions = possible_moves(self.preGame)
            self.q_moves.update({hash_board : {one_action : 0 for one_action in poss_actions}})
        
        if found_symm:
            opponentMoveSymm = de_symm_move(opponentMove, sym_type, -sym_count-4)
            self.update_opp_history_state_moves(hash_board, opponentMoveSymm)                 
        else:
            self.update_opp_history_state_moves(hash_board, opponentMove)

    def place_piece(self) -> tuple[int, int]:
        board = self.get_game().get_board_status()
        piece_to_place = self.get_game().get_selected_piece()

        check = possible_pieces(board)
        if len(check) < 6:
            # last 6 moves
            _possible_moves = possible_moves(board)
            for move in _possible_moves:
                new_board = deepcopy(board)
                new_board[move] = piece_to_place
                if check_current_player_winner(new_board):
                    return move[1], move[0]
            # print("here")
            x, y = check_tris(board)
            if x != -1:
                return y, x
            else:
                return random.randint(0, 3), random.randint(0, 3)

        action_chosen = None
        randomN = random.random()

        self.saveOpponentMoveAndPiece(piece_to_place)

        # board xor with the piece
        # seek sym on board xored
        xored_board = xorer(board, piece_to_place)
        found_symm = False
        hash_board = boardHash(xored_board)
        if hash_board not in self.q_moves:
            #look for symmetries
            hash_board_temp, sym_type, sym_count = self.seek_symm_moves(xored_board) 
            if hash_board_temp != 0:
                found_symm = True
                hash_board = hash_board_temp
                # print("sym")

        if found_symm:
            # print(f'found symm: {found_symm}')
            if randomN < self.random_factor:
                # print(f'random: {randomN}')
                potential_actions_sym = list(self.q_moves[hash_board].keys())
                action_chosen_sym = random.choice(potential_actions_sym)
            else:
                # print(f'not random: {randomN}')
                potential_actions_sym = self.q_moves[hash_board]
                action_chosen_sym = max(potential_actions_sym, key= potential_actions_sym.get)
            
            self.update_history_state_moves(hash_board, action_chosen_sym)
            action_chosen = de_symm_move(action_chosen_sym, sym_type, sym_count)
        else:
            initial_poss_actions = possible_moves(board)
            if not hash_board in self.q_moves:
                self.q_moves.update({hash_board : {one_action : 0 for one_action in initial_poss_actions}})

            # print(f'not found symm: {found_symm}')
            if randomN < self.random_factor:
                # print(f'random: {randomN}')
                action_chosen = random.choice(initial_poss_actions)
            else:
                # print(f'not random: {randomN}')
                potential_actions = self.q_moves[hash_board]
                action_chosen = max(potential_actions, key= potential_actions.get)
            
            self.update_history_state_moves(hash_board, action_chosen)

        
        copy_board = board
        copy_board[action_chosen[0], action_chosen[1]] = piece_to_place
        self.preGame = copy_board
        
        return action_chosen[1], action_chosen[0]
    
    def learn_all(self, reward):
        
        for h in self.history_state_moves:
            self.__learn_moves(h[0], h[1], reward = reward)

        for h in self.history_state_pieces:
            self.__learn_pieces(h[0], h[1], reward = reward)

        for h in self.opp_history_state_moves:
            self.__learn_moves(h[0], h[1], reward = -reward)

        for h in self.opp_history_state_pieces:
            self.__learn_pieces(h[0], h[1], reward = -reward)

        self.history_state_moves = list()
        self.history_state_pieces = list()
        self.opp_history_state_moves = list()
        self.opp_history_state_pieces = list()
        self.preGame = np.array([])

    def nowExploit(self,random_factor):
        # print("hi there")
        self.random_factor = random_factor
    
    def __learn_moves(self, state, ply, reward):
        self.q_moves[state][ply] = self.q_moves[state][ply] + self.alpha * (reward - self.q_moves[state][ply])
    
    def __learn_pieces(self, state, ply, reward):
        self.q_pieces[state][ply] = self.q_pieces[state][ply] + self.alpha * (reward - self.q_pieces[state][ply])

    def __row_to_q_moves(self, row):
        temp_dict = dict()
        check_list = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3), (3, 0), (3, 1), (3, 2), (3, 3)]
        for a, b in zip(check_list, row[3:19]):
            if b != 91:
                temp_dict.update({a : b})
        self.q_moves.update({row[1]: temp_dict})
        
    def __row_to_q_pieces(self, row):
        temp_dict = dict()
        check_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        for a, b in zip(check_list, row[3:19]):
            if b != 91:
                temp_dict.update({a : b})
        self.q_pieces.update({row[1]: temp_dict})

    def save_to_db(self, version):
        conn = sqlite3.connect('actors/final_database/reinforcement.db')
        cursor = conn.cursor()

        print("Saving data to DB")

        for key, value in self.q_moves.items():
            insertion = q_moves_to_insertion(hash_value = key, in_dict = value, version = version)
            cursor.execute(insertion)

        for key, value in self.q_pieces.items():
            insertion = q_pieces_to_insertion(hash_value = key, in_dict = value, version = version)
            cursor.execute(insertion)

        print("Finished Saving data to DB")

        conn.commit()
        conn.close()

    def read_from_db(self, version):
        conn = sqlite3.connect('actors/final_database/reinforcement.db')
        cursor = conn.cursor()

        print("Reading data from DB")

        statement = f"SELECT * FROM moves WHERE version = {version}"
        cursor.execute(statement)
        while True:
            rows = cursor.fetchmany(10000)
            if len(rows) == 0:
                break
            for row in rows:
                self.__row_to_q_moves(row)

        print("first part")
        cursor.close()
        conn.close()
        gc.collect()


        conn = sqlite3.connect('actors/final_database/reinforcement.db')
        cursor = conn.cursor()

        statement = f"SELECT * FROM pieces WHERE version = {version}"
        cursor.execute(statement)
        while True:
            rows = cursor.fetchmany(10000)
            if len(rows) == 0:
                break
            for row in rows:
                self.__row_to_q_pieces(row)

        print("Finished Reading data from DB")

        conn.close()

        
class ReinforcementPlay2(Player):
    """ReinforcementPlay player"""

    def __init__(self, quarto: Quarto) -> None:
        super().__init__(quarto)
        self.cells_row = [*range(0,4)]
        self.all = [*range(0, 16, 1)]

        self.q_moves = dict()
        self.q_pieces = dict()
        self.hit_move = 0
        self.no_hit_move = 0
        self.hit_piece = 0
        self.no_hit_piece = 0
        self.place_call = 0
        self.choose_call = 0
        self.place_special = 0
        self.choose_special = 0
        
        self.read_from_db(1)


    def seek_symm_pieces(self, board):
        hash_board = 0
        found_symmetry = False
        sym_type = ''
        sym_count = 0
        if not found_symmetry:
            for r in range(1,4):
                copyBoard = symmRotation(board, r)
                hash_board_Symm = boardHash(copyBoard)
                if hash_board_Symm in self.q_pieces:
                    hash_board = hash_board_Symm
                    found_symmetry = True
                    sym_type = 'rot'
                    sym_count = r
                    break

        if not found_symmetry:
            copyBoard = symmFlipOrizontal(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_pieces:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_h'
        
        if not found_symmetry:
            copyBoard = symmFlipVertical(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_pieces:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_v'
        
        if not found_symmetry:
            copyBoard = symmFlipMid(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_pieces:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_m'
        
        if not found_symmetry:
            copyBoard = symmFlipInside(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_pieces:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_i'

        return hash_board, sym_type, sym_count

    def seek_symm_moves(self, board):
        hash_board = 0
        found_symmetry = False
        sym_type = ''
        sym_count = 0
        if not found_symmetry:
            for r in range(1,4):
                copyBoard = symmRotation(board, r)
                hash_board_Symm = boardHash(copyBoard)
                if hash_board_Symm in self.q_moves:
                    hash_board = hash_board_Symm
                    found_symmetry = True
                    sym_type = 'rot'
                    sym_count = r
                    break

        if not found_symmetry:
            copyBoard = symmFlipOrizontal(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_moves:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_h'
        
        if not found_symmetry:
            copyBoard = symmFlipVertical(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_moves:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_v'
        
        if not found_symmetry:
            copyBoard = symmFlipMid(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_moves:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_m'
        
        if not found_symmetry:
            copyBoard = symmFlipInside(board)
            hash_board_Symm = boardHash(copyBoard)
            if hash_board_Symm in self.q_moves:
                hash_board = hash_board_Symm
                found_symmetry = True
                sym_type='flip_i'

        return hash_board, sym_type, sym_count


    def choose_piece(self) -> int:
        self.choose_call += 1
        board = self.get_game().get_board_status()

        piece_choosen = None
        hash_board = boardHash(board)

        if hash_board not in self.q_pieces:
            #look for symmetries
            hash_board_temp, _, _ = self.seek_symm_pieces(board) 
            if hash_board_temp != 0:
                hash_board=hash_board_temp

        if hash_board not in self.q_pieces:
            poss_pieces = possible_pieces(board)
            piece_choosen = random.choice(poss_pieces)
            self.no_hit_piece += 1
        else:
            potential_pieces = self.q_pieces[hash_board]
            piece_choosen = max(potential_pieces, key= potential_pieces.get)
            self.hit_piece += 1

        return piece_choosen

    def place_piece(self) -> tuple[int, int]:
        self.place_call += 1
        board = self.get_game().get_board_status()
        piece_to_place = self.get_game().get_selected_piece()

        _possible_moves = possible_moves(board)
        for move in _possible_moves:
            new_board = deepcopy(board)
            new_board[move] = piece_to_place
            if check_current_player_winner(new_board):
                return move[1], move[0]

        action_chosen = None

        xored_board = xorer(board, piece_to_place)
        found_symm = False
        hash_board = boardHash(xored_board)
        if hash_board not in self.q_moves:
            #look for symmetries
            hash_board_temp, sym_type, sym_count = self.seek_symm_moves(xored_board) 
            if hash_board_temp != 0:
                found_symm = True
                hash_board = hash_board_temp
                # print("sym")

        if found_symm:
            potential_actions_sym = self.q_moves[hash_board]
            action_chosen_sym = max(potential_actions_sym, key= potential_actions_sym.get)
            action_chosen = de_symm_move(action_chosen_sym, sym_type, sym_count)
            self.hit_move += 1
            return action_chosen[1], action_chosen[0]
        else:
            # no sym
            if not hash_board in self.q_moves:
                # no hit
                # use defensive logic
                self.no_hit_move += 1
                x, y = check_tris(board)
                if x != -1:
                    return y, x
                else:
                    return random.randint(0, 3), random.randint(0, 3)
            else:
                # hit on hash not sym
                self.hit_move += 1
                potential_actions = self.q_moves[hash_board]
                action_chosen = max(potential_actions, key= potential_actions.get)
                return action_chosen[1], action_chosen[0]       
    
    def printHits(self):
        print("we have these nuts for moves:")
        print(f"hits: {self.hit_move}")
        print(f"NOhits: {self.no_hit_move}")
        print(f"calls: {self.place_call}")
        print(f"special: {self.place_special}")
        print(f"q_moves length {len(self.q_moves)}")
        print("we have these nuts for pieces:")
        print(f"hits: {self.hit_piece}")
        print(f"NOhits: {self.no_hit_piece}")
        print(f"calls: {self.choose_call}")
        print(f"special: {self.choose_special}")
        print(f"q_moves length {len(self.q_pieces)}")

    def __row_to_q_moves(self, row):
        temp_dict = dict()
        check_list = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3), (3, 0), (3, 1), (3, 2), (3, 3)]
        for a, b in zip(check_list, row[3:19]):
            if b != 91:
                temp_dict.update({a : b})
        self.q_moves.update({row[1]: temp_dict})
        
    def __row_to_q_pieces(self, row):
        temp_dict = dict()
        check_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        for a, b in zip(check_list, row[3:19]):
            if b != 91:
                temp_dict.update({a : b})
        self.q_pieces.update({row[1]: temp_dict})

    def read_from_db(self, version):
        conn = sqlite3.connect('actors/final_database/reinforcement.db')
        cursor = conn.cursor()

        print("Reading data from DB")

        statement = f"SELECT * FROM moves WHERE version = {version}"
        cursor.execute(statement)
        while True:
            rows = cursor.fetchmany(10000)
            if len(rows) == 0:
                break
            for row in rows:
                self.__row_to_q_moves(row)

        print("first part")
        cursor.close()
        conn.close()
        gc.collect()

        conn = sqlite3.connect('actors/final_database/reinforcement.db')
        cursor = conn.cursor()

        statement = f"SELECT * FROM pieces WHERE version = {version}"
        cursor.execute(statement)
        while True:
            rows = cursor.fetchmany(10000)
            if len(rows) == 0:
                break
            for row in rows:
                self.__row_to_q_pieces(row)

        print("Finished Reading data from DB")

        conn.close()