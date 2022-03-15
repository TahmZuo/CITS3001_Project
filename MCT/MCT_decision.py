import numpy as np
from collections import defaultdict
from abc import ABC, abstractmethod
from agent import Agent
from itertools import combinations
import random


class MCT_Resistance_Node():

    def __init__(self, team, outcome, round_index, missions_failed, vote, number_of_players, player_list, parent=None):
        """
        Parameters (All from MCT_agent.round_outcome for the root node)
        ----------
        team: team attended the mission
        outcome: the mission succeed(True) or failed(False)
        round_index: the index recoding which round is this node in
        number_of_players: the number of players for this game
        parent : node for the last round of game
        children: nodes for the passible states of next round
        vote: for current state, should I vote True or False
        number_of_visits: how many times this node has been visited
        resistance_wins: how many times this node has won as resistance
        """
        self.team = team
        self.outcome = outcome
        self.round_index = round_index
        self.missions_failed = missions_failed
        self.number_of_players = number_of_players
        self.player_list = player_list
        self.parent = parent
        self.children = []
        self.vote = vote
        self._number_of_visits = 0
        self._resistance_wins = 0

    @property
    def q(self):
        wins = self._resistance_wins
        return wins

    @property
    def n(self):
        return self._number_of_visits

    @property
    def get_vote(self):
        return self.vote

    @property
    def is_terminal_node(self):
        if self.missions_failed >= 3 or self.round_index - self.missions_failed >= 2:
            return True
        return False

    # result: -True if the resistance won the game
    #         -False if the spies won the game
    def rollout(self):
        if self.is_terminal_node:
            if self.missions_failed >= 3:
                result = False
            elif self.round_index - self.missions_failed >= 2:
                result = True
        return result

    def expand(self):
        if len(self.children) == 0:
            # get the team size information from Agent
            number_of_players = self.number_of_players
            player_list = self.player_list
            mission_size_this_game = Agent.mission_sizes[number_of_players]
            mission_size = mission_size_this_game[self.round_index]
            # possible_combinations is a list of tuples containing all possible combinations of team
            possible_combinations = list(
                combinations(player_list, mission_size))
            # put the state of 2 possible outcomes, 2 possible vote: fail and success, True and False, with possible comb of team into children list
            for combination in possible_combinations:
                possible_team = list(combination)
                child_round_index = self.round_index + 1
                child_node_success_T = MCT_Resistance_Node(possible_team, True, child_round_index, self.missions_failed,
                                                           True, number_of_players, player_list, parent=self)
                child_node_success_F = MCT_Resistance_Node(possible_team, True, child_round_index, self.missions_failed,
                                                           False, number_of_players, player_list, parent=self)
                child_node_fail_T = MCT_Resistance_Node(possible_team, False, child_round_index, self.missions_failed+1,
                                                        True, number_of_players, player_list, parent=self)
                child_node_fail_F = MCT_Resistance_Node(possible_team, False, child_round_index, self.missions_failed+1,
                                                        False, number_of_players, player_list, parent=self)
                self.children.append(child_node_fail_T)
                self.children.append(child_node_fail_F)
                self.children.append(child_node_success_T)
                self.children.append(child_node_success_F)
        else:
            pass

    def backpropagate(self, result):
        self._number_of_visits += 1.
        if result == True:
            self._resistance_wins += 1
        if self.parent:
            self.parent.backpropagate(result)

    # return the child of current node with the highest weights

    def best_child(self, teams_failed):
        c_param = 2

        choices_weights = []
        for c in self.children:
            team_has_failed = False
            for team in teams_failed:
                if set(c.get_team) <= set(team):
                    team_has_failed = True
                    break

            if team_has_failed == False:
                weight = (c.q / c.n) + c_param * \
                    np.sqrt((2 * np.log(self.n) / c.n))
                choices_weights.append(weight)

        index_of_best = np.argmax(choices_weights)
        return self.children[index_of_best]

    @property
    def get_team(self):
        return self.team


class MCTSearch(object):

    def __init__(self, node):
        """
        MonteCarloTreeSearch
        Parameters
        ----------
        node : nodes.MCT_Resistance_Node
        """
        self.root = node

    def best_action(self, teams_failed):
        """
        Parameters
        ----------
        teams_failed: the combinations of team that has failed before, 
                        updated each time calling this function
        Returns
            best_child: best node to go to I for current state

        -------
        """
        for _ in range(0, 10000):
            v = self._tree_policy()
            reward = v.rollout()
            v.backpropagate(reward)
        # to select best child go for exploitation only
        best_child = self.root.best_child(teams_failed)
        return best_child

    def _tree_policy(self):
        """
        selects node to run rollout/playout for
        Returns
        -------
        """
        current_node = self.root
        while not current_node.is_terminal_node:
            current_node.expand()
            child_index = random.randrange(len(current_node.children))
            current_node = current_node.children[child_index]
        return current_node
