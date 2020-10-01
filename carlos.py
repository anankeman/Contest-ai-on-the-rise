# myTeam.py
# ---------
# Licensing Information:	You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
import math

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
							 first = 'DummyAgent', second = 'DummyAgent'):
	"""
	This function should return a list of two agents that will form the
	team, initialized using firstIndex and secondIndex as their agent
	index numbers.	isRed is True if the red team is being created, and
	will be False if the blue team is being created.

	As a potentially helpful development aid, this function can take
	additional string-valued keyword arguments ("first" and "second" are
	such arguments in the case of this function), which will come from
	the --redOpts and --blueOpts command-line arguments to capture.py.
	For the nightly contest, however, your team will be created without
	any extra arguments, so you should make sure that the default
	behavior is what you want for the nightly contest.
	"""

	# The following line is an example only; feel free to change it.
	return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
	"""
	A Dummy agent to serve as an example of the necessary agent structure.
	You should look at baselineTeam.py for more details about how to
	create an agent as this is the bare minimum.
	"""

	def registerInitialState(self, gameState):
		"""
		This method handles the initial setup of the
		agent to populate useful fields (such as what team
		we're on).

		A distanceCalculator instance caches the maze distances
		between each pair of positions, so your agents can use:
		self.distancer.getDistance(p1, p2)

		IMPORTANT: This method may run for at most 15 seconds.
		"""

		'''
		Make sure you do not delete the following line. If you would like to
		use Manhattan distances instead of maze distances in order to save
		on initialization time, please take a look at
		CaptureAgent.registerInitialState in captureAgents.py.
		'''
		CaptureAgent.registerInitialState(self, gameState)

		'''
		Your initialization code goes here, if you need any.
		'''
		self.priorBelief = initializePriorBelief(gamestate)
		self.posteriorBelief = initializeposteriorBelief(gamestate)

	def chooseAction(self, gameState):
		"""
		Picks among actions randomly.
		"""
		actions = gameState.getLegalActions(self.index)

		'''
		You should change this in your own agent.
		'''

		return random.choice(actions)

#-------------------------------------------------------------------------------------
class AttackAgent(CaptureAgent):
	"""
	A Dummy agent to serve as an example of the necessary agent structure.
	You should look at baselineTeam.py for more details about how to
	create an agent as this is the bare minimum.
	"""

	def registerInitialState(self, gameState):
		"""
		This method handles the initial setup of the
		agent to populate useful fields (such as what team
		we're on).

		A distanceCalculator instance caches the maze distances
		between each pair of positions, so your agents can use:
		self.distancer.getDistance(p1, p2)

		IMPORTANT: This method may run for at most 15 seconds.
		"""

		'''
		Make sure you do not delete the following line. If you would like to
		use Manhattan distances instead of maze distances in order to save
		on initialization time, please take a look at
		CaptureAgent.registerInitialState in captureAgents.py.
		'''
		CaptureAgent.registerInitialState(self, gameState)

		'''
		Your initialization code goes here, if you need any.
		'''

	def chooseAction(self, gameState):
		"""
		Picks among actions randomly.
		"""
		capsules_list = self.getCapsules().asList()
		if len(capsules_list) > 0 and gameState.getAgentState(self.index).scaredTimer == 0:
			path = aStarSearch(self, gameState, 'getCapsule')


		'''
		You should change this in your own agent.
		'''

		return random.choice(actions)
#-------------------------------------------------------------------------------------

	#List with the boundary dividing red and blue area
	def getBoundaries(self, gameState):
		width_x = gameState.data.layout.width
		height_y = gameState.data.layout.height
		middle_x = width_x/2

		if self.red:
			our_side_limit_x = middle_x - 1
		else:
			our_side_limit_x = middle_x + 1

		boundaries = [(i, our_side_limit_x) for i in range(1, height_y - 2)]

		return boundaries

	#List with opponents classified in PacMan or Ghost, and the Maze Distance to it
	def getOpponentsDistances(self, gameState):

		opponents_distance_list = []
		current_state = gameState.getAgentState(self.index)
		current_position = current_state.getPosition()

		opponents_index_list = self.getOpponents(gameState)
		opponents_agent_list = [gameState.getAgentState(x) for x in opponents_index_list]

		for oponent_agent in opponents_agent_list:
			if oponent_agent.isPacman:
				type = 'pacman'
			else:
				type = 'ghost'
			opponent_distance = oponent_agent.getPosition()
			if opponent_distance is not None:
				dist = self.getMazeDistance(current_position, opponent_distance)
				opponents_distance_list.append((type, dist))

		return opponents_distance_list

	#List distance to the nearest food
	def getDistanceNearestFood(self, gameState):
		current_state = gameState.getAgentState(self.index)
		current_position = current_state.getPosition()

		food_list = self.getFood(gameState).asList()
		minimum_distance = min([util.manhattanDistance(current_position, x) for x in food_list])
		return minimum_distance

	#List distance to the nearest capsule
	#Add None when there are no capsules left
	def getDistanceNearestCapsule(self, gameState):
		current_state = gameState.getAgentState(self.index)
		current_position = current_state.getPosition()

		capsules_list = self.getCapsules().asList()
		minimum_distance = min([util.manhattanDistance(current_position, x) for x in capsules_list])
		return minimum_distance

	#Distance to nearest point of our area
	def getDistanceNearestPointArea(self, gameState):
		boundaries = getBoundaries(self, gameState)
		current_state = gameState.getAgentState(self.index)
		current_position = current_state.getPosition()
		boundary_distance_list = []
		for boundary in boundaries:
			boundary_distance = oponent_agent.getPosition()
			dist = self.getMazeDistance(current_position, boundary)
			boundary_distance_list.append(dist)

		return math.min(boundary_distance_list)

	def aStarSearch(self, gameState, goal):
		"""Search the node that has the lowest combined cost and heuristic first."""
		#dic[pos]: [parent,action,cost_to_point]
		open = util.PriorityQueue()
		visited = set([gameState])
		dict = {}
		dict[gameState] = (None,None,0)
		open.push(gameState, heuristic_sStar(gameState))
		while not open.isEmpty():
			current_state = open.pop()
			food_list = self.getFood(current_state).asList()
			if len(food_list) > 0:
				break
			else:
				actions = current_state.getLegalActions(self.index)
				for action in actions:
					successor = self.getSuccessor(gameState, action)
					if (successor not in visited):
						visited.add(successor)
						dict[successor] = (current_state,action,map[current_state][2] + 1)
						open.update(successor,dict[successor][2] + heuristic_Astar(successor, goal))
					elif (dict[current_state][2] + 1) <= dict[successor][2]:
						dict[successor] = None
			dict[successor] = (point,action,(map[point][2] + 1))
			open.update(successor,dict[successor][2] + heuristic_Astar(successor, goal))
		pass

	def heuristic_Astar(self, successor, goal):
		features = util.Counter()
		if goal == "getCapsule":
			features['minDistanceFood'] = 1
			features['minDistanceOpponent'] = getOpponentsDistances(successor)
			features['minDistanceOurArea'] = 1
			features['minDistanceCapsule'] = getDistanceNearestCapsule(successor)




		features['minDistanceFood'] = getDistanceNearestFood(successor)
		features['minDistanceOpponent'] = getOpponentsDistances(successor)
		features['minDistanceOurArea'] = getDistanceNearestPointArea(successor)
		features['minDistanceCapsule'] = getDistanceNearestCapsule(successor)

		weights = self.getWeightsCapsule(goal)
		print(features*weights)

		return features*weights

	def getWeights(goal):
		if goal == "getCapsule":
			return {'minDistanceFood': 999,
											'minDistanceOpponent': 99,
											'minDistanceCapsule': 10,
											'minDistanceOurArea': 999}
		elif goal == "getFood":
			return {'minDistanceFood': 0,
											'minDistanceOpponent': 30,
											'minDistanceCapsule': 10,
											'minDistanceOurArea': 0}

#-----------------------------------------------------------------------------------
	#Initialize prior belief P(X_0)
	def initializePriorBelief(self, gameState):
		priorBelief = util.Counter()
		opponents_index_list = self.getOpponents(gameState)
		legal_positions = self.legalPositions
		for opponent in opponents_index_list:
			for position in legal_positions:
				priorBelief[opponent][position] = 1
			priorBelief[opponent].normalize()
		return priorBelief

	#Initialize posterior P(X_0|Y_0) = P(Y_0|X_0)*P(X_0)
	def initializeposteriorBelief(self, gameState):
		posteriorBelief = util.Counter()
		approx_distances = self.getCurrentObservation().getAgentDistances()
		opponents_index_list = self.getOpponents(gameState)
		legal_positions = self.legalPositions
		for opponent in opponents_index_list:
			for position in legal_positions:
				PX_0Y_0 = gameState.getDistanceProb(approx_distances[opponent], knownDistance)
				PX_0 = self.priorBelief[opponent][position]


	#Calculate distance based on Probability
	def getProbabilityDistance(self, gameState):
		#List of distances to each agent based on i
		approx_distances = self.getCurrentObservation().getAgentDistances()
		opponents_index_list = self.getOpponents(gameState)
		legal_positions = self.legalPositions
		dist_prob = util.Counter()

		for opponent in opponents_index_list:
			for position in legal_positions:
				dist_prob[opponent] = self.getMazeDistance(current_position, opponent_distance)
