from agent import Agent
import random
from MCT_decision import MCT_Resistance_Node
from MCT_decision import MCTSearch


class MCTAgent(Agent):
    '''An agent based on MCT decision'''

    def __init__(self, name='Rando'):
        '''
        Initialises the agent.
        Parameters:
        ------------------------
        name: the name of this agent
        round_index: Int number to record which round is going now
        best_choice: a list storing the best team decide by MCT search
        curr_node: storing current node for the game state, including team attended the mission and out come
                   of that mission
        best_team: is the team we would love to see for next round
        vote_times: how many times voted this round. if this is 5th vote in a round, yes anyway

        '''
        self.name = name
        self.round_index = 0
        self.best_team = []
        self.best_child = None
        self.best_vote = True
        self.curr_node = None
        self.vote_times = 0
        self.clearly_know = []
        self.teams_failed = []

    def new_game(self, number_of_players, player_number, spy_list):
        '''
        initialises the game, informing the agent of the 
        number_of_players, the player_number (an id number for the agent in the game),
        and a list of agent indexes which are the spies, if the agent is a spy, or empty otherwise
        '''
        self.number_of_players = number_of_players
        self.player_number = player_number
        self.spy_list = spy_list
        self.fails_required = 1

        self.player_list = []
        num = 0
        while len(self.player_list) in range(self.number_of_players):
            self.player_list.append(num)
            num += 1

    def is_spy(self):
        '''
        returns True iff the agent is a spy
        '''
        return self.player_number in self.spy_list

    def propose_mission(self, team_size, betrayals_required):
        '''
        expects a team_size list of distinct agents with id between 0 (inclusive) and number_of_players (exclusive)
        to be returned. 
        betrayals_required are the number of betrayals required for the mission to fail.
        '''
        if self.round_index == 0:
            team = []
            while len(team) < team_size:
                agent = random.randrange(team_size)
                if agent not in team:
                    team.append(agent)
            return team

        if not self.is_spy():
            team = self.best_child.get_team
        return team

    def vote(self, mission, proposer):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''
        self.vote_times += 1
        # do not give spies a free fail
        if self.vote_times == 5:
            return True
        # always vote True at first round
        if self.round_index == 0:
            return True

        if proposer == self.player_number:
            return True

        self.best_vote = self.best_child.get_vote

    def vote_outcome(self, mission, proposer, votes):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        votes is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.
        '''
        pass

    def betray(self, mission, proposer):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players, and include this agent.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The method should return True if this agent chooses to betray the mission, and False otherwise. 
        By default, spies will betray 30% of the time. 
        '''
        if self.is_spy():
            return random.random() < 0.3

    def mission_outcome(self, mission, proposer, betrayals, mission_success):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        betrayals is the number of people on the mission who betrayed the mission, 
        and mission_success is True if there were not enough betrayals to cause the mission to fail, False otherwise.
        It iss not expected or required for this function to return anything.
        '''
        # Having the outcome of first mission, now we can initialize a  MCT search
        self.mission = mission
        self.teams_failed.append(mission)
        self.mission_success = mission_success

    def round_outcome(self, rounds_complete, missions_failed):
        '''
        basic informative function, where the parameters indicate:
        rounds_complete, the number of rounds (0-5) that have been completed
        missions_failed, the numbe of missions (0-3) that have failed.
        '''
        if self.round_index == 0:
            self.curr_node = MCT_Resistance_Node(self.mission, self.mission_success, self.round_index,
                                                 missions_failed, True, self.number_of_players, self.player_list, parent=None)
            self.Tree = MCTSearch(self.curr_node)

        # if the game haven't finished yet, assign current state to self.curr_node
        elif rounds_complete - missions_failed < 3 and missions_failed < 3:
            for node in self.curr_node.children:
                if set(node.team) == set(self.mission) and node.missions_failed == missions_failed and self.round_index == node.round_index and self.best_vote == node.get_vote:
                    self.curr_node = node
                    self.Tree = MCTSearch(self.curr_node)
        if not self.curr_node.is_terminal_node:
            self.best_child = self.Tree.best_action(self.teams_failed)
        else:
            self.best_child = self.curr_node
        self.round_index += 1
        self.vote_times = 0

    def game_outcome(self, spies_win, spies):
        '''
        basic informative function, where the parameters indicate:
        spies_win, True iff the spies caused 3+ missions to fail
        spies, a list of the player indexes for the spies.
        '''
        self.round_index = 0
        self.best_team = []
        self.best_child = None
        self.best_vote = True
        self.curr_node = None
        self.vote_times = 0
