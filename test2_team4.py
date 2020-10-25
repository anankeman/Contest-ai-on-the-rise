# myTeam.py
# ---------
# Licensing Information:    You are free to use or extend these projects for
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
                             first = 'ApproximateQAgent', second = 'DefendAgent'):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.    isRed is True if the red team is being created, and
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


#-------------------------------------------------------------------------------------
class AttackAgent(CaptureAgent):

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.count = 0
        self.boundaries = self.getBoundaries(gameState, gameState.data.layout, self.red)
        self.halfway = gameState.data.layout.width//2
        food_list = self.getFood(gameState).asList()
        self.initial_food = len(food_list)
        self.patrol = 'up'



    def chooseAction(self, gameState):
        start = time.time()

        pos = gameState.getAgentPosition(self.index)

        #count eaten food
        previous = self.getPreviousObservation()
        if previous is not None:
            if previous.hasFood(pos[0], pos[1]):
                self.count += 1
            else:
                # rest to zero when crossing the border
                if (self.red and pos[0] < self.halfway) or (not self.red and pos[0] >= self.halfway):
                    self.count = 0

        #issues: ghost information is shared between teammates

        ghost = self.getOpponentsDistances(gameState, pos)
        border = self.getDistanceNearestPointArea(gameState, pos)

        if ghost < 7:
            if (self.red and pos[0] < self.halfway) or (not self.red and pos[0] >= self.halfway):
                print("alternative"+str(self.red))
                path = self.aStarSearch(gameState, 'alternative')
            else:
                capsule = self.getDistanceNearestCapsule(gameState, pos)
                if capsule > border:
                    print("go border cus ghost"+str(self.red))
                    path = self.aStarSearch(gameState, 'getBorder')
                else:
                    print("go capsule"+str(self.red))
                    path = self.aStarSearch(gameState, 'getCapsule')
        else:
            #Greedy approach
            nextFood = self.getDistanceNearestFood(gameState, pos, True)
            if nextFood > border and self.count > 0:
                print("go border"+str(self.red))
                path = self.aStarSearch(gameState, 'getBorder')
            else:
                print("go food"+str(self.red))
                path = self.aStarSearch(gameState, 'getFood')

        #print('eval time for agent %d: %.4f' % (self.index, time.time() - start))

        return path

    def getSuccessor(self, gameState, action):
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor
#-------------------------------------------------------------------------------------

    #List with the boundary dividing red and blue area
    def getBoundaries(self, gameState, grid, red):
        border = [0]*grid.height
        if red:
            x = (grid.width//2)-1
        else:
            x = (grid.width//2)
        for y in range(grid.height):
            if not gameState.hasWall(x, y):
                border[y] = (x, y)
        border= [i for i in border if i!=0]
        return border


    # Maze Distance to nearest enemy ghost
    def getOpponentsDistances(self, gameState, pos):
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        ghost = [a.getPosition() for a in enemies if (not a.isPacman and a.scaredTimer < 2) and a.getPosition() is not None]

        if len(ghost) > 0:
            #return distance to the closest ghost
            return min([self.getMazeDistance(pos, i) for i in ghost])
        else:
            return 999 #smooth value?

    #Maze distance to the nearest food
    def getDistanceNearestFood(self, gameState, pos, onlyOne = False):
        food = self.getFood(gameState).asList()
        if onlyOne:
            if len(food) == 0:
                return 9999

            return min([self.getMazeDistance(pos, i) for i in food])

        return self.closestPoint(pos, food, 0)
        #return min([self.getMazeDistance(pos, i) for i in food])

    def closestPoint(self, position, food, path):
        if len(food)==0:
            return 0
        else:
            distances = {f: self.getMazeDistance(position, f) for f in food}
            closePoint = min(distances, key= lambda k: distances[k])
            newFood = [e for e in food if e!=closePoint]
            path += self.closestPoint(closePoint, newFood, path)
            path += distances[closePoint]
            return path

    #List distance to the nearest capsule
    #Add None when there are no capsules left
    def getDistanceNearestCapsule(self, gameState, pos):
        capsules_list = self.getCapsules(gameState)
        if len(capsules_list) > 0:
            return min([self.getMazeDistance(pos, x) for x in capsules_list])
        else:
            return 0

    #Distance to nearest point of our area

    def getDistanceNearestPointArea(self, gameState, pos):
        return min([self.getMazeDistance(pos, i) for i in self.boundaries])


    def getGoal(self, goal, initialState, currentState, pos):
        if goal == "getCapsule":
            if len(self.getCapsules(initialState))-len(self.getCapsules(currentState)) == 1:
                return True
        elif goal == "getFood":
            if len(self.getFood(initialState).asList())-len(self.getFood(currentState).asList()) == 1:
                return True
        elif goal == 'getBorder':
            if pos in self.boundaries:
                return True
        else:
            return False

    def getPatrol(self, pos):
        if self.patrol == 'up':
            if pos in self.boundaries[-3]:
                self.patrol == 'down'
                return self.getMazeDistance(pos, self.boundaries[0])
            else:
                return self.getMazeDistance(pos, self.boundaries[-1])
        else:
            if pos in self.boundaries[2]:
                self.patrol == 'up'
                return self.getMazeDistance(pos, self.boundaries[-1])
            else:
                return self.getMazeDistance(pos, self.boundaries[0])

    def monteCarlo(self, gameState):
        path = True
        path = gameState.getAgentPosition(self.index)
        return path

    def aStarSearch(self, gameState, goal, maxSight = 60):
        """Search the node that has the lowest combined cost and heuristic first."""
        priorityQ = util.PriorityQueue()
        mark = [] #mark visited states
        case = []
        initialState = gameState
        priorityQ.push((gameState, [((0),"start")], 0), 0)

        bestG = dict()
        while not priorityQ.isEmpty() and (maxSight > 0):
            currentState, answer, currentCost = priorityQ.pop()
            case = answer

            if currentState not in mark or currentCost < bestG.get(currentState):
                mark.append(currentState)
                bestG[currentState] = currentCost
                pos = currentState.getAgentState(self.index).getPosition()
                if self.getGoal(goal,initialState, currentState, pos):
                    if len(answer) > 1:
                        return answer[1][1]
                    else:
                        return Directions.STOP

                maxSight -= 1
                actions = currentState.getLegalActions(self.index)

                for action in actions:
                    nextState = self.getSuccessor(currentState, action)
                    nextCost = currentCost + 1
                    heu = self.heuristic_Astar(nextState, goal)
                    #print('heu: '+str(heu))
                    currentPath = list(answer)
                    currentPath.append((pos, action))
                    priorityQ.push((nextState, currentPath, currentCost), heu+nextCost)

        return case[1][1]


    def heuristic_Astar(self, successor, goal):
        #food_list = self.getFood(successor).asList()
        features = util.Counter()
        pos = successor.getAgentState(self.index).getPosition()


        if goal == "getCapsule":
            features['minDistanceFood'] = 0
            features['minDistanceOpponent'] = 1/self.getOpponentsDistances(successor, pos)
            features['minDistanceCapsule'] = self.getDistanceNearestCapsule(successor, pos)
            features['minDistanceOurArea'] = 0
        elif goal == "getBorder":
            features['minDistanceFood'] = 0#self.getDistanceNearestFood(successor, pos)
            features['minDistanceOpponent'] = 1/self.getOpponentsDistances(successor, pos)
            features['minDistanceCapsule'] = 0
            features['minDistanceOurArea'] = self.getDistanceNearestPointArea(successor, pos)
        elif goal == "getFood":
            features['minDistanceFood'] = self.getDistanceNearestFood(successor, pos)
            features['minDistanceOpponent'] = (1/ self.getOpponentsDistances(successor, pos))
            features['minDistanceCapsule'] = 0
            features['minDistanceOurArea'] = 0 #(self.getDistanceNearestPointArea(successor, pos)# + min_dist_food + self.initial_food - current_food)*(2-per)
        else:
            features['minDistanceFood'] = self.getPatrol(pos)
            features['minDistanceOpponent'] = 0#(1/ self.getOpponentsDistances(successor, pos))
            features['minDistanceCapsule'] = 0
            features['minDistanceOurArea'] = 0

        weights = self.getWeights(goal)
        return features*weights

    def getWeights(self, goal):
        if goal == "getCapsule":
            return {'minDistanceFood': 0,
                                            'minDistanceOpponent': 30,
                                            'minDistanceCapsule': 1,
                                            'minDistanceOurArea': 0}
        elif goal == "getBorder":
            return {'minDistanceFood': 1,
                                            'minDistanceOpponent': 0,
                                            'minDistanceCapsule': 0,
                                            'minDistanceOurArea': 1}
        elif goal == "getFood":
            return {'minDistanceFood': 1,
                                            'minDistanceOpponent': 30,
                                            'minDistanceCapsule': 0,
                                            'minDistanceOurArea': 0}
        else:
            return {'minDistanceFood': 1,
                                            'minDistanceOpponent': 30,
                                            'minDistanceCapsule': 0,
                                            'minDistanceOurArea': 0}
#---------------------------------------------------------------------------------------------------------


class MinimaxAgent(AttackAgent):


    def registerInitialState(self, gameState):

        CaptureAgent.registerInitialState(self, gameState)
        '''
        Your initialization code goes here, if you need any.
        '''
        #Depth of the MiniMax model
        self.depth = 5
        #Index of enemies in the Map
        self.indexEnemies = self.getOpponents(gameState)
        self.latestEnemyState = None
        self.boundaries = self.getBoundaries(gameState, gameState.data.layout, self.red)
        #print(self.boundaries)


    #return the index of the closest opponent at sight and not scared
    def getClosestOpponent(self, gameState):
        pos = gameState.getAgentPosition(self.index)
        enemies = [(i, gameState.getAgentPosition(i)) for i in self.getOpponents(gameState) if gameState.getAgentState(i).scaredTimer < 3 and (not gameState.getAgentState(i).isPacman)]
        distance = {i: self.getMazeDistance(pos, p) for i, p in enemies if p is not None}
        if len(distance):
            minD = min(distance, key = lambda k: distance[k])
            if distance[minD] < 7: #check it is to our sight
                return minD
        else:
            return None

# For PacMan the system maximized the Utility. Choose action based on legal actions
    def chooseAction(self, gameState):
        start = time.time()
        self.indexEnemies = self.getClosestOpponent(gameState)
        self.latestEnemyState = None
        #self.debugDraw(self.boundaries, [1,1,1])
        '''
        actionValues = util.Counter()
        for action in gameState.getLegalActions(self.index):
            successorGameState = self.getSuccessor(gameState, action, self.index)
            actionValues[action] = self.minimaxFunc(successorGameState, maxDepth -1,-float('Inf'),float('Inf'),True)
        print(actionValues)
        action = actionValues.argMax()
        print(action)
        
        return action
        '''
        step, value = self.minimaxFunc(gameState, self.depth -1,-float('Inf'),float('Inf'),True)
        print("------\nfinal value:            "+str(value))
        print('eval time for minimax %d: %.4f' % (self.index, time.time() - start))
        self.debugClear()
        return step

    '''
    Get the utility of a game state based on certain features 
    Currenty using:
    - distanceToFood: Nearest Food distance (Maze Distance)
    - successorCapsule: Reflects if Pacman ate a Capsule
    - distanceToCapsule: Nearest Capsule distance (Maze Distance)
    - distanceToEnemy: Nearest Enemy Distance (Maze Distance)
    - eatenFood: Reflects if Pacman ate a Food 
    - successorScore: Make Pacman go to our area to score 
    Ideas
    - Maybe include scared time
    '''
    def evaluationFunction(self, gameState, alpha, beta):
        # Useful information you can extract from a GameState (pacman.py)
        succesor = gameState
        pos = succesor.getAgentPosition(self.index)
        features = util.Counter()

        # Nearest enemy distance

        if self.latestEnemyState is not None:
            opponentLateState = self.latestEnemyState.getAgentPosition(self.indexEnemies)
            self.debugDraw(opponentLateState, [1,1,1])
            minPosEnemy = self.getMazeDistance(pos, opponentLateState)
        else:
            minPosEnemy = 0


        disFood = self.getDistanceNearestFood(succesor, pos)
        #if disFood == 0:
        #   disFood = -999

        # Reflects if the new state has less food in the map
        features['distanceToFood'] = disFood#self.getDistanceNearestFood(succesor, pos)
        features['eatenFood'] = 0#len(newFood_list)
        features['distanceToEnemy'] = minPosEnemy
        features['distanceToCapsule'] = self.getDistanceNearestCapsule(succesor, pos)
        features['successorCapsule'] = 0#abs(succesor.getScore())
        # Reflects if the new state scores
        #if succesor.isOver():
        #    border = -9999
        #else:
        border = self.getDistanceNearestPointArea(succesor, pos)#abs(successorGameState.getScore())

        if (border + disFood)== 0:
            border = -3

        features['successorScore'] = border
        print('food: ' +str(disFood*-10))
        print('border: '+ str( border *-1))

        weights = self.getWeights()

        value = features * weights
        print('final score: ', str(value))
        #if alpha >= value:
            #self.debugDraw(pos, [1,0,0])
        return value

    # Weights for the features, the idea is to tune in this weights for the features defined above
    def getWeights(self):
        return {'successorScore': -1,
                    'distanceToFood': -10,
                    'distanceToEnemy': 100,
                    'distanceToCapsule': -0.1,
                    'successorCapsule': 10,
                    'eatenFood': -100}


    # Minimax with alpha-beta pruning. If no enemy present, skip rival moves
    def minimaxFunc(self, gameState, depth, alpha, beta, player):
        if depth == 0 or gameState.isOver():
            return None, self.evaluationFunction(gameState, alpha, beta)
        if player:
            maxEval = -float('Inf')
            finalStep = None
            for action in gameState.getLegalActions(self.index):
                succ = self.getSuccessor(gameState, action, self.index)
                enemies = self.indexEnemies
                if enemies is not None:
                    step, currentEval = self.minimaxFunc(succ, depth-1, alpha, beta, False)
                else:
                    step, currentEval = self.minimaxFunc(succ, depth-1, alpha, beta, True)
                currentEval -= 1 #additional cost for not
                if currentEval > maxEval:
                    finalStep = action
                    maxEval = currentEval
                alpha = max(alpha, currentEval)
                if beta <= alpha:
                    break
            return finalStep, maxEval
        else: #rival moves
            minEval = float('Inf')
            finalStep = None
            for action in gameState.getLegalActions(self.indexEnemies):
                succ = self.getSuccessor(gameState, action, self.indexEnemies)
                self.latestEnemyState = succ
                step, currentEval = self.minimaxFunc(succ, depth-1, alpha, beta, True)
                if currentEval < minEval:
                    finalStep = action
                    minEval = currentEval
                beta = min(beta, currentEval)
                if beta <= alpha:
                    break
            return finalStep, minEval


#-----------------------------------------------------------------------------------

class DefendAgent(AttackAgent):

    def registerInitialState(self, gameState):

        CaptureAgent.registerInitialState(self, gameState)
        self.count = 0
        self.target = None
        self.boundaries = self.getBoundaries(gameState, gameState.data.layout, self.red)
        food_list = self.getFoodYouAreDefending(gameState).asList()
        self.initial_food = len(food_list)
        self.scared = gameState.getAgentState(self.index).scaredTimer
        self.halfway = gameState.data.layout.width//2
        self.top = self.getTop(gameState)
        self.bottom = self.getBottom(gameState)
        self.goingUp = False

    def chooseAction(self, gameState):
        start = time.time()
        self.scared = gameState.getAgentState(self.index).scaredTimer
        pos = gameState.getAgentPosition(self.index)
        previous = self.getPreviousObservation()
        food_list_previous = []
        if previous is not None:

            food_list_previous = self.getFoodYouAreDefending(previous).asList()
            if previous.hasFood(pos[0], pos[1]):
                self.count += 1
            if (self.red and pos[0] < self.halfway) or (not self.red and pos[0] >= self.halfway):
                self.count = 0

        food_list_current = self.getFoodYouAreDefending(gameState).asList()

        if self.target is not None:
            if pos == self.target:
                if self.target == self.top:
                    self.goingUp = False
                elif self.target == self.bottom:
                    self.goingUp = True
                self.target = None

        invaders = self.getExactInvaders(gameState, pos)
        if invaders is not None:
            self.target = invaders
            if self.scared == 0:
                path = self.aStarSearch(gameState, 'getInvaders')
            else:
                path = self.aStarSearch(gameState, 'getInvaders_scared')

        elif len(food_list_previous) - len(food_list_current) > 0:
            self.target = list(set(food_list_previous) - set(food_list_current))[0]
            path = self.aStarSearch(gameState, 'getFood')

        elif self.target is not None:
            path = self.aStarSearch(gameState, 'getInvaders')

        elif self.target is None:
            border_dist = util.manhattanDistance(self.getNearestBorder(gameState), pos)
            if border_dist > 5:
                self.target = self.getNearestBorder(gameState)
                path = self.aStarSearch(gameState, 'goCenter')
            else:
                if self.goingUp == False:
                    self.target = self.bottom
                else:
                    self.target = self.top
                path = self.aStarSearch(gameState, 'goCenter')

        else:
            return Directions.STOP

        #print('eval time for agent %d: %.4f' % (self.index, time.time() - start))
        return path

    #gets top coordinate for patrol. checks 8 further coordinates if wall found.
    def getTop(self, gameState):
        height = gameState.data.layout.height
        if self.red:
            top = (self.boundaries[0][0] - 2, height - 4)
        else:
            top = (self.boundaries[0][0] + 2, height - 4)
        x, y = top
        if gameState.hasWall(x, y):
            for i in range(2):
                for j in range(2):
                    next_x = x - 1 + i
                    next_y = y - 1 + j
                    if not gameState.hasWall(next_x, next_y):
                        top = (next_x, next_y)
        return top

    #gets the bottom coordinate for the patrol. checks 8 further coordinates if wall found.
    def getBottom(self, gameState):
        if self.red:
            bottom = (self.boundaries[0][0] - 2, 4)
        else:
            bottom = (self.boundaries[0][0] + 2, 4)
        x, y = bottom
        if gameState.hasWall(x, y):
            for i in range(2):
                for j in range(2):
                    next_x = x - 1 + i
                    next_y = y - 1 + j
                    if not gameState.hasWall(next_x, next_y):
                        bottom = (next_x, next_y)
        return bottom

    def getExactInvaders(self, gameState, pos):
        opponents_pos_list = util.Counter()
        current_position = pos
        opponents_index_list = self.getOpponents(gameState)
        opponents_agent_list = [gameState.getAgentState(x) for x in opponents_index_list]

        for oponent_agent in opponents_agent_list:
            if oponent_agent.isPacman:
                opponent_pos = oponent_agent.getPosition()
                if opponent_pos is not None:
                    dist = self.getMazeDistance(current_position, opponent_pos)
                    opponents_pos_list[opponent_pos] = -dist
        if opponents_pos_list:
            key = opponents_pos_list.argMax()
            return key
        else:
            return None


    #List with opponents classified in PacMan or Ghost, and the Maze Distance to it
    def getOpponentsDistances(self, gameState, pos):

        opponents_distance_list = util.Counter()
        opponents_noisyDistance_list = util.Counter()
        final = {}
        current_position = pos

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

    def getCenterOurFood(self, gameState):
        food_list = self.getFoodYouAreDefending(gameState).asList()
        x_sum = 0
        y_sum = 0
        len_list = len(food_list)
        for x, y in food_list:
            x_sum += x
            y_sum += y

        near_pos = nearestPoint((x_sum/len_list, y_sum/len_list))
        near = 999
        final_pos = ()
        for pos_food in food_list:
            dist = util.manhattanDistance(pos_food, near_pos)
            if dist < near:
                near = dist
                final_pos = pos_food
        return final_pos

    def getExactInvader(self, gameState, pos):
        return self.getMazeDistance(pos, self.target)

    def heuristic_Astar(self, successor, goal):
        features = util.Counter()
        pos = successor.getAgentPosition(self.index)
        if goal == "getInvaders" or goal == "getInvaders_scared":
            features['minDistanceFood'] = 99
            features['minDistanceOpponent'] = self.getExactInvader(successor, pos)
            features['minDistanceCapsule'] = 99
            features['minDistanceOurArea'] = 99
        elif goal == "getFood":
            features['minDistanceFood'] = self.getExactInvader(successor, pos)
            features['minDistanceOpponent'] = 99
            features['minDistanceCapsule'] = 99
            features['minDistanceOurArea'] = 99
        else: #goal == "goCenter"
            features['minDistanceFood'] = self.getMazeDistance(pos, self.target)
            features['minDistanceOpponent'] = 99
            features['minDistanceCapsule'] = 99
            features['minDistanceOurArea'] = 99
        weights = self.getWeights(goal)
        return features*weights

    def getWeights(self, goal):
        if goal in ["getInvaders", "getInvaders_scared"]:
            return {'minDistanceFood': 1,
                                            'minDistanceOpponent': 1,
                                            'minDistanceCapsule': 1,
                                            'minDistanceOurArea': 1}
        elif goal == "getFood":
            return {'minDistanceFood': 1,
                                            'minDistanceOpponent': 1,
                                            'minDistanceCapsule': 1,
                                            'minDistanceOurArea': 1}
        else: #"goCenter"
            return {'minDistanceFood': 1,
                                            'minDistanceOpponent': 1,
                                            'minDistanceCapsule': 1,
                                            'minDistanceOurArea': 1}

    def getNearestBorder(self, gameState):
        current_position = gameState.getAgentPosition(self.index)
        boundary_distance = 9999
        boundary_position = None
        for i in self.boundaries:
                dist = self.getMazeDistance(i, current_position)
                if dist < boundary_distance:
                        boundary_distance = dist
                        boundary_position = i
        return boundary_position

    #defensive Astar added with goal state as target
    def aStarSearch(self, gameState, goal):

        from util import PriorityQueue

        open_list = PriorityQueue()
        closed_list = {}
        start_node = [gameState, 0, []]
        open_list.push(start_node, 0)
        while not open_list.isEmpty():
            current_node = open_list.pop()
            current_pos = current_node[0].getAgentPosition(self.index)
            current_state, cost, path = current_node
            if not current_pos in closed_list or cost < closed_list.get(current_pos):
                if self.getGoal(goal, current_pos):
                    if len(path) > 0:
                        return path[0]
                    else:
                        return Directions.STOP
                closed_list[current_pos] = cost
                actions = current_state.getLegalActions(self.index)
                for action in actions:
                    successor = self.getSuccessor(current_state, action)
                    new_path = []
                    for i in path:
                        new_path.append(i)
                    new_path.append(action)
                    next_node = [successor, cost + 1, new_path]
                    open_list.push(next_node, (next_node[1] + self.heuristic_Astar(successor, goal)))
        return Directions.STOP

    #same implementation as carlos' initial code, works with Astar to check if goal = target
    def getGoal(self, goal, current_pos):
      if goal == "getInvaders" or goal == "getFood" or goal == "goCenter":
        if current_pos == self.target:
          return True
        else:
          return False
      elif goal == "getInvaders_scared":
        if self.getMazeDistance(current_pos, self.target) == 2:
          return True
        else:
          return False

#----------------------------------------------------------------------------------------------------------------

class ApproximateQAgent(CaptureAgent):
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
    #Learning rate
    self.alpha = 0.2
    #Discount rate
    self.gamma = 0.8
    #Threshold
    self.epsilon = 0
    # weights of features
    try:
      with open('featureWeights.txt', "r") as file:
        self.weights = eval(file.read())
        file.close()
    except:
      self.weights = self.getWeights()

  # For PacMan the system maximized the Utility. Choose action based on legal actions
  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index)
    probability = util.flipCoin(self.epsilon)
    if probability:
      action = random.choice(actions)

    else:
      action = self.getPolicy(gameState)
    #self.update(gameState, action)
    return action

  def getWeights(self):
    return {'distanceToFood': -1.1480349373521266, 'distanceToEnemy': -1.8946601365929547, 'distanceToCapsule': -0.7064242777388614, 'scored': 19.40290051060966, 'enemyRadar': -99.71284329473492, 'stop': -66.43243035410164, 'foodLeft': -2.8920070226206036}
    #return {'distanceToFood':  -8, 'distanceToEnemy': 10, 'distanceToCapsule': -10, 'scored': 100, 'enemyRadar': -100, 'stop': -100, 'foodLeft': -5}
    #{'distanceToFood': -1.79860243631401, 'distanceToEnemy': 3.079869160216298, 'distanceToCapsule': -0.29299771938486846, 'scored': 42.736656524685465, 'enemyRadar': -99.92962494140701, 'stop': -81.56425788286805, 'foodLeft': -4.816807737706834}
    #{'distanceToFood': -1.1480349373521266, 'distanceToEnemy': -1.8946601365929547, 'distanceToCapsule': -0.7064242777388614, 'scored': 19.40290051060966, 'enemyRadar': -99.71284329473492, 'stop': -66.43243035410164, 'foodLeft': -2.8920070226206036}
    #{'distanceToFood': -1.1480349373521266, 'distanceToEnemy': -1.8946601365929547, 'distanceToCapsule': -0.7064242777388614, 'scored': 19.40290051060966, 'enemyRadar': -99.71284329473492, 'stop': -66.43243035410164, 'foodLeft': -2.8920070226206036}

  def getQValue(self, gameState, action):
    features = self.getFeatures(gameState, action)
    weights = self.weights

    return features*weights

  def getFeatures(self, gameState, action):

    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    foodListLast = self.getFood(gameState).asList()
    foodList = self.getFood(successor).asList()
    myPos = successor.getAgentState(self.index).getPosition()
    if len(foodList) > 0:
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
    if len(foodListLast) - len(foodList) == 1:
      features['distanceToFood'] = 0

    features['foodLeft'] = len(foodList)

    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    ghosts = [a for a in enemies if (not a.isPacman) and a.getPosition() != None]
    if len(ghosts) > 0:
      dists = [self.getMazeDistance(myPos, ghost.getPosition()) for ghost in ghosts]
      features['distanceToEnemy'] = min(dists)
      features['enemyRadar'] = 1 if min(dists) <= 2 else 0


    capsules = self.getCapsules(successor)
    if len(capsules) > 0:
      dists = [self.getMazeDistance(myPos, capsule) for capsule in capsules]
      features['distanceToCapsule'] = min(dists)
      currentCapsule = self.getCapsules(gameState)
      if len(currentCapsule) - len(capsules) == 1:
        features['distanceToCapsule'] = 0


    features['distanceToFood'] = features['distanceToFood']*(1-features['enemyRadar'])
    features['distanceToCapsule'] = features['distanceToCapsule']*(1-features['enemyRadar'])
    features['scored'] = self.getScore(successor)
    features['stop'] = 1 if action == Directions.STOP else 0

    #features.normalize()
    #print(action, features)
    return features

  # Compute Action from Qvalues
  def getPolicy(self, gameState):
    values = util.Counter()
    actions = gameState.getLegalActions(self.index)
    for action in actions:
      values[action] = self.getQValue(gameState, action)

    #print(values)
    return values.argMax()

  # Compute Value and Action from Qvalues
  def getValue(self, gameState):
    values = util.Counter()
    actions = gameState.getLegalActions(self.index)
    for action in actions:
      values[action] = self.getQValue(gameState, action)

    return values[max(values)]

  def update(self, gameState, action):

    features = self.getFeatures(gameState, action)
    successor = self.getSuccessor(gameState, action)

    reward = (self.getScore(successor) - self.getScore(gameState))
    difference = (reward + self.gamma*self.getValue(gameState)) - self.getQValue(gameState, action)
    for feature in features:
      self.weights[feature] += self.alpha*difference*features[feature]
    with open('featureWeights.txt', "w") as file:
      file.write(str(self.weights))
      file.close()
    with open("featureWeightsH.txt", "a") as file:
      file.write(str(self.weights))
      file.close()

  def getSuccessor(self, gameState, action):
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def getScore(self, gameState):
    """
    Returns how much you are beating the other team by in the form of a number
    that is the difference between your score and the opponents score.  This number
    is negative if you're losing.
    """
    if self.red:
      return gameState.getScore()
    else:
      return gameState.getScore() * -1
