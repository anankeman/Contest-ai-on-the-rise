# baselineTeam.py
# ---------------
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


# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'AttackAgent', second = 'DefensiveReflexAgent'):
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
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """

  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

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

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}


#--------------------------------------------------------------------------------------------------------------------------------------------

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
                #print("alternative"+str(self.red))
                path = self.aStarSearch(gameState, 'alternative')
            else:
                capsule = self.getDistanceNearestCapsule(gameState, pos)
                if capsule > border:
                    #print("go border cus ghost"+str(self.red))
                    path = self.aStarSearch(gameState, 'getBorder')
                else:
                    #print("go capsule"+str(self.red))
                    path = self.aStarSearch(gameState, 'getCapsule')
        else:
            #Greedy approach
            nextFood = self.getDistanceNearestFood(gameState, pos, True)
            if nextFood > border and self.count > 0:
                #print("go border"+str(self.red))
                path = self.aStarSearch(gameState, 'getBorder')
            else:
                #print("go food"+str(self.red))
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
