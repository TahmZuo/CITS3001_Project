from random import random
from random_agent import RandomAgent
from Against import Game
# from game import Game
from MCT_agent import MCTAgent
from improved_Bounder import Bounder
from Grader import Grader

'''4 Bounder spies with 6 random resistance'''


i = 0
spy_wins = 0
res_wins = 0
beginer_win_as_spy = 0
beginer_win_as_res = 0
beginer_index = 0
while i < 1000:

    agents = [
        # GreedyAgent(name='g1'),
        # GreedyAgent(name='g2'),
        RandomAgent(name='r1'),
        RandomAgent(name='r2'),
        # RandomAgent(name='r2'),
        # RandomAgent(name='r2'),
        Bounder(name='B1'),
        Bounder(name='B1'),
        Bounder(name='B1'),
        # Bounder(name='B1'),
        # Bounder(name='B2'),
        # Bounder(name='B3'),
        # Grader(name='G1'),
        # Grader(name='G2'),
        # Grader(name='G3'),
        # MCTAgent(name='m1'),
        # MCTAgent(name='m2'),
        # MCTAgent(name='m3'),
        # MCTAgent(name='m1'),
        # MCTAgent(name='m2'),
        # MCTAgent(name='m3'),

    ]
    beginer = agents[4]

    game = Game(agents)
    game.play()
    beginer_index = beginer.player_number
    if game.missions_lost >= 3:
        spy_wins += 1
        if beginer_index in game.spies:
            beginer_win_as_spy += 1
    else:
        res_wins += 1
        if beginer_index not in game.spies:
            beginer_win_as_res += 1
    i += 1
beginer_wins = beginer_win_as_spy + beginer_win_as_res


# print(game)
print('spy  wins: ', spy_wins)
print('res wins: ', res_wins)
print('When as res: ', beginer_win_as_res)
print('When as spy: ', beginer_win_as_spy)
print('total win times: ', beginer_wins)
