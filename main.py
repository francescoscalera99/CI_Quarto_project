# Free for personal or classroom use; see 'LICENSE.md' for details.
# https://github.com/squillero/computational-intelligence

import logging
import argparse
import random
from quarto import Quarto
from actors.rule_based_players import *
from actors.minmax3 import MinMaxPlayer3
from actors.reinforcement_bases_players  import *
# from actors.final_agent import ReinforcementPlay, ReinforcementV2
import time
from actors import *

def evaluate(player0, player1):
    win = 0
    games_won = 0
    games_ties = 0
    game = Quarto()

    for _ in range(0, 5):
        if _ % 1000 == 0:
            print(_)

        game.reset()
        game.set_players((player0(game), player1(game)))
        winner = game.run()

        if winner == 0:
            win += 1
            games_won += 1
        if winner == 1:
            games_won += 1
        if winner == -1:
            games_ties += 1

        game.reset()
        game.set_players((player1(game), player0(game)))
        winner = game.run()

        if winner == 1:
            win += 1
            games_won += 1
        if winner == 0:
            games_won += 1
        if winner == -1:
            games_ties += 1

        print(_)

    print(f"{player0.__name__} won: {win} / {games_won} ({win/games_won}); ties {games_ties}")

def trainReinforcement(player0):
    
    version = 0
    game = Quarto()

    player0_withgame = player0(game)
    player1_withgame = RandomPlayer(game)

    for _ in range(0, 10_000_000):

        if _ % 50_000 == 0 and _ != 0:
            player0_withgame.save_to_db(version)
            version += 1

        if _ % 1000 == 0:
            print(_)

        game.reset()
        
        game.set_players((player0_withgame, player1_withgame))
        winner = game.run()

        if winner == 0:
            player0_withgame.learn_all(1)
        if winner == 1:
            player0_withgame.learn_all(-1)
        if winner == -1:
            player0_withgame.learn_all(1)

        game.reset()

        game.set_players((player1_withgame, player0_withgame))
        winner = game.run()

        if winner == 1:
            player0_withgame.learn_all(1)
        if winner == 0:
            player0_withgame.learn_all(-1)
        if winner == -1:
            player0_withgame.learn_all(1)

        # print(_)

def evaluateReinforcementPlay(player0, player1):
    win = 0
    games_won = 0
    games_ties = 0
    version = 0

    game = Quarto()

    player0_withgame = player0(game)
    player1_withgame = player1(game)

    for _ in range(0, 5000):

        if _ % 1000 == 0:
            print(_)

        game.reset()
        
        game.set_players((player0_withgame, player1_withgame))
        winner = game.run()

        if winner == 0:
            win += 1
            games_won += 1
        if winner == 1:
            games_won += 1
        if winner == -1:
            games_ties += 1

        game.reset()

        game.set_players((player1_withgame, player0_withgame))
        winner = game.run()

        if winner == 1:
            win += 1
            games_won += 1
        if winner == 0:
            games_won += 1
        if winner == -1:
            games_ties += 1
            
    print(f"{player0.__name__} won: {win} / {games_won} ({win/games_won}); ties {games_ties}")
    player0_withgame.printHits()

def main():
    random.seed(42)
    start = time.time()
    # e = evaluate(MinMaxPlayer3, DefensivePlayer)
    # e = trainReinforcement(ReinforcementV1)
    evaluateReinforcementPlay(ReinforcementPlay, DefensivePlayer)
    end = time.time()

    print(end - start)

    # print(e)
    # game = Quarto()
    # game.set_players((MinMaxPlayer3(game), DefensivePlayer(game)))
    # winner = game.run()
    # logging.warning(f"main: Winner: player {winner}")
    # print(game.get_board_status())
    # game.print_play_list()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', default=0, help='increase log verbosity')
    parser.add_argument('-d',
                        '--debug',
                        action='store_const',
                        dest='verbose',
                        const=2,
                        help='log debug messages (same as -vv)')
    args = parser.parse_args()

    if args.verbose == 0:
        logging.getLogger().setLevel(level=logging.WARNING)
    elif args.verbose == 1:
        logging.getLogger().setLevel(level=logging.INFO)
    elif args.verbose == 2:
        logging.getLogger().setLevel(level=logging.DEBUG)

    main()
