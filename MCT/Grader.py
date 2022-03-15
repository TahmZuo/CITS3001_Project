from queue import PriorityQueue
import random
from agent import Agent

class Grader:
    '''An abstract super class for an agent in the game The Resistance.
    new_game and *_outcome methods simply inform agents of events that have occured,
    while propose_mission, vote, and betray require the agent to commit some action.'''

    # game parameters for agents to access
    # python is such that these variables could be mutated, so tournament play
    # will be conducted via web sockets.
    # e.g. self.mission_size[8][3] is the number to be sent on the 3rd mission in a game of 8
    mission_sizes = {
        5: [2, 3, 2, 3, 3],
        6: [3, 3, 3, 3, 3],
        7: [2, 3, 3, 4, 5],
        8: [3, 4, 4, 5, 5],
        9: [3, 4, 4, 5, 5], 
        10: [3, 4, 4, 5, 5]
    }
    # number of spies for different game sizes
    spy_count = {5: 2, 6: 2, 7: 3, 8: 3, 9: 3, 10: 4}
    # e.g. self.betrayals_required[8][3] is the number of betrayals required for the 3rd mission in a game of 8 to fail
    fails_required = {
        5: [1, 1, 1, 1, 1],
        6: [1, 1, 1, 1, 1],
        7: [1, 1, 1, 2, 1],
        8: [1, 1, 1, 2, 1],
        9: [1, 1, 1, 2, 1],
        10: [1, 1, 1, 2, 1]
    }

    def __init__(self, name):
        '''
        Initialises the agent, and gives it a name
        You can add configuration parameters etc here,
        but the default code will always assume a 1-parameter constructor, which is the agent's name.
        The agent will persist between games to allow for long-term learning etc.
        '''
        self.name = name
        self.vote_times = 0
        self.round_index = 0
        
    def __str__(self):
        '''
        Returns a string represnetation of the agent
        '''
        return 'Agent '+self.name

    def __repr__(self):
        '''
        returns a representation fthe state of the agent.
        default implementation is just the name, but this may be overridden for debugging
        '''
        return self.__str__()

    def new_game(self, number_of_players, player_number, spies):
        '''
        initialises the game, informing the agent of the number_of_players, 
        the player_number (an id number for the agent in the game),
        and a list of agent indexes, which is the set of spies if this agent is a spy,
        or an empty list if this agent is not a spy.
        '''
        self.player_number = player_number
        self.number_of_players = number_of_players
        self.spy_num = len(spies)
        self.round_index = 0
        self.fails_required = 1
        self.player_list = []
        self.spy_list = spies
        self.votes_thisRound = []
        num = 0
        while len(self.player_list) in range(self.number_of_players):
            self.player_list.append(num)
            num += 1
        self.suspicion = dict.fromkeys(self.player_list, 0)
        
        

    def propose_mission(self, team_size, fails_required=1):
        '''
        expects a team_size list of distinct agents with id between 0 (inclusive) and number_of_players (exclusive)
        to be returned. 
        fails_required are the number of fails required for the mission to fail.
        current_suspicion is the value to determine if a player is spy or not
        as a resistance, always choose those who has lower suspicion value
        as a spy, always choose spies with lower value
        '''
        # if the leader agent is spy, then he wants to have a team list that at least containing 1 spy
        # if the leader agent is resistance, then he wants to figure out the most possible spies and do not choose them
        team = []
        current_suspicion = sorted(self.suspicion)
        if not self.is_spy():
            if self.round_index == 0:
                while len(team) < team_size:
                    agent = random.choice(self.player_list)
                    if agent not in team :
                        team.append(agent)
            if self.suspicion[0] != 0:
            # sort the dictionary of suspicion, from small to great
                team = team + current_suspicion[:team_size]
            else:
                while len(team) < team_size:
                    agent = random.choice(self.player_list)
                    if agent not in team :
                        team.append(agent)
            
        else:
            # as a spy, maximum the uncertainty of resistances. 
            # Choose the spies with lower suspicion value
            for spy in current_suspicion:
                if len(team) < fails_required and spy in self.spy_list:
                    team.append(spy)
            # Choose the resistance with high suspicion value
            while len(team) < team_size:
                agent = current_suspicion.pop()
                if agent not in self.spy_list and team:
                    team.append(agent)
                                      
        return team

    def vote(self, mission, proposer):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        Args:
            self.round_index shows which round is the game now
            _in_mission is the number of spies in this mission (guess it if I am not a spy )
        '''
        # always agree with at the first round and the 5th vote
        self.vote_times += 1
        if self.round_index == 0 or self.vote_times == 5:
            return True
        elif self.is_spy():
            # vote yes if there are enough spies in the mission
            # '''可以添加一步判断，是否为第三次使任务失败，支持提出者是否有暴露的风险'''
            _in_mission = 0
            for agent in mission:
                if agent in self.spy_list:
                    _in_mission += 1
            if _in_mission >= self.fails_required:
                return True
            else:
                return False
        else:
            # if i am resistance and there are members with high suspicion value, vote false
            current_suspicion = sorted(self.suspicion)
            likely_spy = current_suspicion[:self.spy_num]
            # if proposer is likely a spy, start with 1 
            # cause he may put another spy in the team instead himself
            if proposer in likely_spy:
                _in_mission = 1
            else:
                _in_mission = 0
            # check each agent in the mission
            for agent in mission:
                if agent in likely_spy:
                    _in_mission += 1
            # justify if there are enough spies in the team
            if _in_mission >= self.fails_required:
                return False
            else:
                return True
            

    def vote_outcome(self, mission, proposer, votes):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        votes is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.
        '''
        self.votes_thisRound = votes

    def is_spy(self):
        '''
        returns True iff the agent is a spy
        '''
        return self.player_number in self.spy_list



    def betray(self, mission, proposer):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players, and include this agent.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The method should return True if this agent chooses to betray the mission, and False otherwise. 
        Only spies are permitted to betray the mission. 
        '''
        return True

    def mission_outcome(self, mission, proposer, num_fails, mission_success):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        num_fails is the number of people on the mission who betrayed the mission, 
        and mission_success is True if there were not enough betrayals to cause the mission to fail, False otherwise.
        It iss not expected or required for this function to return anything.
        '''
        current_suspicion = sorted(self.suspicion)
        likely_spy = current_suspicion[:self.spy_num+1]
        if self.player_number in mission and num_fails == self.fails_required-1:
            for agent in mission:
                if agent != self.player_number:
                    self.suspicion[agent] += 100
        if mission_success == False:
            if proposer in likely_spy and self.suspicion[proposer] != 0 and proposer != self.player_number:
                self.suspicion[proposer] += 10
            else:
                self.suspicion[proposer] += 5
            for agent in mission:
                if agent in likely_spy:
                    self.suspicion[agent] += 15
                else:
                    self.suspicion[agent] += 10
            # calculate a total value that related to proposer and engagers
            total_value = self.suspicion[proposer]
            for agent in mission:
                total_value += self.suspicion[agent]
            for support in self.votes_thisRound:
                if self.vote_times != 5:
                    if support in likely_spy:
                        self.suspicion[support] += (1/5)*(total_value)
                    else:
                        self.suspicion[support] += (1/3)*(total_value)
                    
        elif mission_success and self.round_index != 0:
            self.suspicion[proposer] -= 10
            for agent in mission:
                self.suspicion[agent] -= 10
            if self.vote_times != 5:
                for support in self.votes_thisRound:
                    self.suspicion[support] -= 5
                

                
    def round_outcome(self, rounds_complete, missions_failed):
        '''
        basic informative function, where the parameters indicate:
        rounds_complete, the number of rounds (0-5) that have been completed
        missions_failed, the numbe of missions (0-3) that have failed.
        '''
        # round_index increased by 1
        self.round_index = rounds_complete - 1
        # reset vote_times for proposed missions
        self.vote_times = 0
        # For the 4th round, if players more than (including) 7, then need 2 spies to betray
        if rounds_complete == 3 and self.number_of_players >= 7:
            self.fails_required = 2
        else:
            self.fails_required = 1


    def game_outcome(self, spies_win, spies):
        '''
        basic informative function, where the parameters indicate:
        spies_win, True iff the spies caused 3+ missions to fail
        spies, a list of the player indexes for the spies.
        '''
        pass
