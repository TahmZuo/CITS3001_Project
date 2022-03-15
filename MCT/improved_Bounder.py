from queue import PriorityQueue
import random
from agent import Agent

class Bounder:
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
       
        self.fails_required = 1
        # recording the times that mission failed when a player is in that mission.
        # Player number is the indices of this list
        self.lost_in_mission = []
        
        self.player_list = []
        num = 0
        while len(self.player_list) in range(self.number_of_players):
            self.player_list.append(num)
            self.lost_in_mission.append(0)
            num += 1
        self.trust_set = set(self.player_list)
        
        self.spy_list = spies
        # Initialize a trust list, trust everyone at the start,containing 4 trust sets
        self.trust_list = []
        for i in range(4):
            trust_set = set(self.player_list)
            self.trust_list.append(trust_set)
        # If the agent clearly know who is a spy, put its number in this list
        self.clearly_know = []
    

    def propose_mission(self, team_size, fails_required):
        '''
        expects a team_size list of distinct agents with id between 0 (inclusive) and number_of_players (exclusive)
        to be returned. 
        fails_required are the number of fails required for the mission to fail.
        '''
        # if the leader agent is spy, then he wants to have a team list that at least containing 1 spy
        # if the leader agent is resistance, then he wants to figure out the most possible spies and do not choose them
        team = []
        # no matter when, put myself in the team
        # candidate is a set containing the agents from the player list
        candidate_list = []
        # if the agent is not a spy, the intersection is calculated 
        # based on the trust set obtained by the results of all previous turns
        # and propose the mission with the final candidate set
        if not self.is_spy():
            team.append(self.player_number)
            for i in self.trust_list:
                self.trust_set = self.trust_set & i
            for i in self.trust_set :
                if i not in self.clearly_know:
                    candidate_list.append(i)
            for i in candidate_list:
                if len(team) < team_size and i != self.player_number:
                    team.append(i)
            # If the agents in trust set is not enough
            while len(team) < team_size:
                agent = random.randrange(team_size)
                if agent not in team:
                    team.append(agent)
                              
        else:
            while len(team) < fails_required:
                agent = random.choice(self.spy_list)
                if agent not in team:
                    team.append(agent)
            while len(team) < team_size:
                agent = random.choice(self.player_list)
                if agent not in team and self.spy_list:
                    team.append(agent)
        
        return team
            
            

            
            


    def vote(self, mission, proposer):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''
        
        # if I am not a spy, I have to vote yes in the 5th propose, or spies will have a free win
        self.vote_times += 1
        
        # First round, vote yes because everyone is in trust_set
        # From second round, check if agents of the proposed team in trust set/clearly_know list or not
        if self.is_spy():
            spy_set = set(self.spy_list)
            team_set = set(mission)
            return not team_set.isdisjoint(spy_set)
        else:
            # this is the 5th propose, have to vote yes as a resistance
            if self.vote_times == 5:
                self.vote_times = 0
                return True
        # if I am proposer, or i am chosed to do the mission, vote yes
        # if proposer == self.player_number or self.player_number in mission:
        #     return True
        # else:
        #     return False
        
                

    def vote_outcome(self, mission, proposer, votes):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        votes is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.
        '''
        # when fight with random agent, only spies can fail the mission 
        # all other players propose the team randomly
        # Only raise the Degree of suspicion when a mission failed
        pass

        
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
        if self.is_spy():
            # First round, too risky
            if self.round_index == 0:
                return False
            # If other situations are not suit, just betray because I am a spy
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
        # when fight with random agent, only spies can fail the mission 
        # all other players propose the team randomly
        # if num_fails == spy_num, they are all clearly spies
        if mission_success != True and self.spy_num == num_fails:
            self.clearly_know = mission
        elif mission_success != True and self.spy_num != num_fails:
            for agents in mission:
                if self.player_number != agents and self.round_index < 4:
                    self.trust_list[self.round_index].discard(agents)
                self.lost_in_mission[agents] += 1
            
                
        # The agent was in the mission and it fails
        if self.player_number in mission and self.spy_num - 1 == num_fails:
            for agents in mission:
                self.clearly_know.append(agents)
                
            

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
