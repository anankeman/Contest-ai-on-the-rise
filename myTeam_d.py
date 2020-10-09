# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).
from game import Grid

from captureAgents import CaptureAgent
import random, time, util
from game import Directions
from util import nearestPoint
import game
import math


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='DeffendAgent', second='DeffendAgent'):
    """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
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
        # self.priorBelief = initializePriorBelief(gameState)
        # self.posteriorBelief = initializeposteriorBelief(gameState)

    def chooseAction(self, gameState):
        """
    Picks among actions randomly.
    """
        actions = gameState.getLegalActions(self.index)

        '''
    You should change this in your own agent.
    '''

        return random.choice(actions)


# -------------------------------------------------------------------------------------
class DeffendAgent(CaptureAgent):
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
        self.count = 0
        self.target = None
        self.boundaries = self.getBoundaries(gameState)
        food_list = self.getFoodYouAreDefending(gameState).asList()
        self.initial_food = len(food_list)
        self.centerOurFood = self.getCenterOurFood(gameState)
        self.scared = gameState.getAgentState(self.index).scaredTimer
        width_x = gameState.data.layout.height
        if self.red:
          self.halfway = width_x // 2
        else:
          self.halfway = width_x // 2 + 1
        '''
    Your initialization code goes here, if you need any.
    '''

    def chooseAction(self, gameState):
        """
    Picks among actions randomly.
    """
        self.scared = gameState.getAgentState(self.index).scaredTimer
        pos = gameState.getAgentPosition(self.index)
        self.centerOurFood = self.getCenterOurFood(gameState)
        width_x = gameState.data.layout.height
        halfway = width_x // 2
        previous = self.getPreviousObservation()
        food_list_previous = []
        if previous is not None:
            food_list_previous = self.getFoodYouAreDefending(previous).asList()
            if previous.hasFood(pos[0], pos[1]):
                self.count += 1
            elif (self.red & pos[1] < halfway) or (not self.red & pos[1] > halfway):
                self.count += 0
        start = time.time()
        capsules_list = self.getCapsules(gameState)
        opponents_index_list = self.getOpponents(gameState)
        opponents_agent_list = [gameState.getAgentState(x).scaredTimer for x in opponents_index_list]
        food_list_current = self.getFoodYouAreDefending(gameState).asList()
        if self.target is not None:
            if pos == self.target:
                self.target = None
        # print(food_list)
        if self.getExactInvaders(gameState) is not None and self.scared == 0:
            self.target = self.getExactInvaders(gameState)
            path = self.aStarSearch(gameState, 'getInvaders', start)
        elif self.getExactInvaders(gameState) is not None and self.scared > 0:
            self.target = self.getExactInvaders(gameState)
            path = self.aStarSearch(gameState, 'getInvaders_scared', start)
        elif len(food_list_previous) - len(food_list_current) > 0:
            food_pos = list(set(food_list_previous) - set(food_list_current))[0]
            self.target = self.getNearestFood(gameState, food_pos)
            path = self.aStarSearch(gameState, 'getFood', start)
        elif self.getOpponentNear(gameState) is not None and self.scared == 0:
            self.target = self.getOpponentNear(gameState)
            path = self.aStarSearch(gameState, 'getOpponent', start)
        elif self.target is not None:
            path = self.aStarSearch(gameState, 'getInvaders', start)
        elif util.manhattanDistance(pos, self.centerOurFood) > 5:
            self.target = self.centerOurFood
            path = self.aStarSearch(gameState, 'goCenter', start)
        else:
            return Directions.STOP
        print('eval time for agent %d: %.4f' % (self.index, time.time() - start))
        '''
    You should change this in your own agent.
    '''

        return path

    def getSuccessor(self, gameState, action):
        """
    Finds the next successor which is a grid position (location tuple).
    """
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    # -------------------------------------------------------------------------------------
    def halfGrid(grid, red):
        halfway = grid.width // 2
        halfgrid = Grid(grid.width, grid.height, False)
        if red:
            xrange = range(halfway)
        else:
            xrange = range(halfway, grid.width)

        for y in range(grid.height):
            for x in xrange:
                if grid[x][y]: halfgrid[x][y] = True

        return halfgrid
    def getNearestFood(self, gameState, food_pos):
        food_list_current = self.getFoodYouAreDefending(gameState).asList()
        food_pos_list = util.Counter()
        for food in food_list_current:
            dist = self.getMazeDistance(food, food_pos)
            food_pos_list[food] = -dist
        return food_pos_list.argMax()
    # List with the boundary dividing red and blue area
    def getBoundaries(self, gameState):
        height_y = gameState.data.layout.height
        width_x = gameState.data.layout.width
        halfway = width_x // 2

        if self.red:
            our_side_limit_x = halfway - 1
        else:
            our_side_limit_x = halfway + 1

        boundaries = [(int(our_side_limit_x), int(i)) for i in range(1, height_y - 2)]
        final = []
        for boundary in boundaries:
            if not gameState.hasWall(boundary[0], boundary[1]):
                final.append(boundary)
        # print(boundaries)
        return final

    def getExactInvaders(self, gameState):
        opponents_pos_list = util.Counter()
        current_state = gameState.getAgentState(self.index)
        current_position = current_state.getPosition()

        opponents_index_list = self.getOpponents(gameState)
        opponents_agent_list = [gameState.getAgentState(x) for x in opponents_index_list]

        for opponent_agent in opponents_agent_list:
            if opponent_agent.isPacman:
                opponent_pos = opponent_agent.getPosition()
                if opponent_pos is not None:
                    dist = self.getMazeDistance(current_position, opponent_pos)
                    opponents_pos_list[opponent_pos] = -dist
        if opponents_pos_list:
            key = opponents_pos_list.argMax()
            return key
        else:
            return None

    def getOpponentNear(self, gameState):
        opponents_pos_list = util.Counter()
        boundary_pos_list = util.Counter()
        current_state = gameState.getAgentState(self.index)
        current_position = current_state.getPosition()

        opponents_index_list = self.getOpponents(gameState)
        opponents_agent_list = [gameState.getAgentState(x) for x in opponents_index_list]

        for opponent_agent in opponents_agent_list:
            if not opponent_agent.isPacman:
                opponent_pos = opponent_agent.getPosition()
                if opponent_pos is not None:
                    dist = self.getMazeDistance(current_position, opponent_pos)
                    opponents_pos_list[opponent_pos] = -dist

        if opponents_pos_list:
            key = opponents_pos_list.argMax()
            for boundary in self.boundaries:
              dist = self.getMazeDistance(boundary, key)
              boundary_pos_list[key] = -dist

            return boundary_pos_list.argMax()
        else:
            return None

    # List with opponents classified in PacMan or Ghost, and the Maze Distance to it
    def getOpponentsDistances(self, gameState):

        opponents_distance_list = util.Counter()
        opponents_noisyDistance_list = util.Counter()
        final = {}
        current_state = gameState.getAgentState(self.index)
        current_position = current_state.getPosition()

        opponents_index_list = self.getOpponents(gameState)
        opponents_agent_list = [gameState.getAgentState(x) for x in opponents_index_list]

        for oponent_agent in opponents_agent_list:
            if oponent_agent.isPacman:
                index = opponents_agent_list.index(oponent_agent)
                opponent_pos = oponent_agent.getPosition()
                if opponent_pos is not None:
                    dist = self.getMazeDistance(current_position, opponent_pos)
                    opponents_distance_list[opponent_pos] = -dist
                else:
                    approx_distances = self.getCurrentObservation().getAgentDistances()[index]
                    opponents_noisyDistance_list[oponent_agent] = -abs(approx_distances)
        if len(opponents_distance_list):
            key = opponents_distance_list.argMax()
            final['exact'] = [key, opponents_distance_list[key]]
        elif len(opponents_noisyDistance_list):
            key = opponents_noisyDistance_list.argMax()
            final['noisy'] = [key, opponents_noisyDistance_list[key]]
        else:
            final = []

        return final

    # List distance to the nearest food
    def getDistanceNearestFood(self, gameState):
        current_state = gameState.getAgentState(self.index)
        current_position = current_state.getPosition()

        food_list = self.getFoodYouAreDefending(gameState).asList()
        if len(food_list) > 0:
            minimum_distance = min([self.getMazeDistance(current_position, food) for food in food_list])
        else:
            minimum_distance = 999
        return minimum_distance

    # List distance to the nearest capsule
    # Add None when there are no capsules left
    def getDistanceNearestCapsule(self, gameState):
        current_state = gameState.getAgentState(self.index)
        current_position = current_state.getPosition()

        capsules_list = self.getCapsules(gameState)

        capsules_distance_list = [self.getMazeDistance(current_position, x) for x in capsules_list]
        if len(capsules_list) > 0:
            minimum_distance = min(capsules_distance_list)
        else:
            minimum_distance = 0
        return minimum_distance

    # Distance to nearest point of our area

    def getDistanceNearestPointArea(self, gameState):
        boundaries = self.boundaries
        current_state = gameState.getAgentState(self.index)
        current_position = current_state.getPosition()
        boundary_distance_list = []
        for boundary in boundaries:
            dist = self.getMazeDistance(current_position, boundary)
            boundary_distance_list.append(dist)

        return min(boundary_distance_list)

    def getCenterOurFood(self, gameState):
        food_list = self.getFoodYouAreDefending(gameState).asList()
        x_sum = 0
        y_sum = 0
        len_list = len(food_list)
        for x, y in food_list:
            x_sum += x
            y_sum += y

        near_pos = nearestPoint((x_sum / len_list, y_sum / len_list))
        near = 999
        final_pos = ()
        for pos_food in food_list:
            dist = util.manhattanDistance(pos_food, near_pos)
            if dist < near:
                near = dist
                final_pos = pos_food
        return final_pos

    def getGoal(self, goal, initialState, finalState):
        current_pos = finalState.getAgentState(self.index).getPosition()
        if goal == "getInvaders" or goal == "getFood":
            if current_pos == self.target:
                return True
            else:
                return False
        elif goal == "goCenter":
            if current_pos == self.target:
                return True
            else:
                return False
        elif goal == "getInvaders_scared":
            if self.getMazeDistance(current_pos, self.target) == 3:
                return True
            else:
                return False
        elif goal == "getOpponent":
            if self.getMazeDistance(current_pos, self.target) > 1:
                return True
            else:
                return False

            self.boundaries

    def aStarSearch(self, gameState, goal, start):
        """Search the node that has the lowest combined cost and heuristic first."""
        # dic[pos]: [parent,action,cost_to_point]
        open = util.PriorityQueue()
        pos = gameState.getAgentState(self.index).getPosition()
        visited = set([pos])
        dict = {}
        dict[pos] = (None, None, 0, self.heuristic_Astar(gameState, goal))
        open.push(gameState, self.heuristic_Astar(gameState, goal))
        while not open.isEmpty():
            current_state = open.pop()
            pos_cur = current_state.getAgentState(self.index).getPosition()
            if self.getGoal(goal, gameState, current_state):
                parent, action, cost, heuristic = dict[pos_cur]
                heuristic = 0
                dict.update({pos_cur: (parent, action, cost, heuristic)})
            else:
                actions = current_state.getLegalActions(self.index)
                for action in actions:
                    successor = self.getSuccessor(current_state, action)
                    pos_suc = successor.getAgentState(self.index).getPosition()
                    dict.setdefault(pos_suc, (None, None, 999, 0))
                    if (pos_suc not in visited) or (dict[pos_cur][2] + 1) < dict[pos_suc][2]:
                        dict[pos_suc] = (pos_cur, action, (dict[pos_cur][2] + 1), self.heuristic_Astar(successor, goal))
                        visited.add(pos_suc)
                        open.update(successor, dict[pos_suc][2] + self.heuristic_Astar(successor, goal))
        path = self.keyName(gameState, dict)
        return path

    def keyName(self, startPoint, dict):
        pos = startPoint.getAgentState(self.index).getPosition()
        val = 9999
        final_action = None
        for key in dict.keys():
            parent, action, cost, heuristic = dict[key]
            if parent != None and parent == pos and heuristic < val:
                print(parent, action, cost, heuristic)
                val = heuristic
                final_action = action
        if final_action is None:
            final_action = Directions.STOP
        return final_action

    def getExactInvader(self, gameState):
        current_state = gameState.getAgentState(self.index)
        current_position = current_state.getPosition()
        return self.getMazeDistance(current_position, self.target)

    def heuristic_Astar(self, successor, goal):
        features = util.Counter()
        pos = successor.getAgentPosition(self.index)
        if goal == "getInvaders" or goal == "getInvaders_scared":
            features['minDistanceFood'] = 99
            features['minDistanceOpponent'] = self.getExactInvader(successor)
            features['minDistanceCapsule'] = 99
            features['minDistanceOurArea'] = 0
            if successor.getAgentState(self.index).isPacman: features['minDistanceOurArea'] = 1
        elif goal == "getFood":
            features['minDistanceFood'] = self.getExactInvader(successor)
            features['minDistanceOpponent'] = 99
            features['minDistanceCapsule'] = 99
            features['minDistanceOurArea'] = 99
        elif goal == "goCenter":
            features['minDistanceFood'] = self.getMazeDistance(pos, self.centerOurFood)
            features['minDistanceOpponent'] = 99
            features['minDistanceCapsule'] = 99
            features['minDistanceOurArea'] = 99
        elif goal == "getOpponent":
            features['minDistanceFood'] = self.getExactInvader(successor)
            features['minDistanceOpponent'] = 99
            features['minDistanceCapsule'] = 99
            features['minDistanceOurArea'] = 0
            if successor.getAgentState(self.index).isPacman: features['minDistanceOurArea'] = 1
        weights = self.getWeights(goal)
        return features * weights

    def getWeights(self, goal):
        if goal == "getInvaders" or goal == "getInvaders_scared":
            return {'minDistanceFood': 1,
                    'minDistanceOpponent': 1,
                    'minDistanceCapsule': 1,
                    'minDistanceOurArea': 99}
        elif goal == "getFood":
            return {'minDistanceFood': 1,
                    'minDistanceOpponent': 1,
                    'minDistanceCapsule': 1,
                    'minDistanceOurArea': 1}
        elif goal == "goCenter":
            return {'minDistanceFood': 1,
                    'minDistanceOpponent': 1,
                    'minDistanceCapsule': 1,
                    'minDistanceOurArea': 1}
        elif goal == "getOpponent":
            return {'minDistanceFood': 1,
                    'minDistanceOpponent': 1,
                    'minDistanceCapsule': 1,
                    'minDistanceOurArea': 999}
