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


from captureAgents import CaptureAgent
from game import Directions
import game
import distanceCalculator
import random, time, util, sys
from util import nearestPoint
from game import Actions


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveAgent', second = 'DefensiveReflexAgent'):
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


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''

    return random.choice(actions)

'''
notes: still very early testing phase of all classes, so all have duplicate methods which can be cleaned up a lot.
Strategy is to have 3 problems, each with different goals, which is chosen by the ChooseAction method.
Weighting is to have a positive or negative, positive being go find food, negative being go home. Weights need to be dialed in.
I have not implemented distance from ghost on the heuristic yet.
'''

class OffensiveAgent(CaptureAgent):
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.start = gameState.getAgentPosition(self.index)
        self.walls = gameState.getWalls()
        self.food = len(self.getFood(gameState).asList())
        self.top, self.right = self.walls.height-2, self.walls.width-2
        halfPoint = self.right/2
        x,y = self.start
        if x < halfPoint:
            self.border = int(halfPoint)
        else:
            self.border = int(halfPoint) + 1
        self.hasFood = 0

    def chooseAction(self, gameState):
        run = False
        startTime = time.time()
        x,y = gameState.getAgentPosition(self.index)
        x1,y1 = self.start
        if x1 < self.border:
            if x <= self.border:
                self.hasFood = 0
        else:
            if x >= self.border:
                self.hasFood = 0
        self.hasFood = self.hasFood + (self.food - len(self.getFood(gameState).asList()))
        self.food = len(self.getFood(gameState).asList())
        foodDist = 9999
        foodLocation = None
        for i in self.getFood(gameState).asList():
            dist = self.distancer.getDistance((x,y), i)
            #dist = manhattanDistance(self.start, i)
            if dist < foodDist:
                foodDist = dist
                foodLocation = i
        ghostDist = 999
        for i in self.getOpponents(gameState):
            ghost = gameState.getAgentDistances()[i]
            if ghost < ghostDist:
                ghostDist = ghost
            if gameState.getAgentPosition(i) != None:
                run = True

        ghostWeight = -ghostDist/5
        carryWeight = -self.hasFood*2
        foodWeight = 100 * 1/foodDist
        totalWeight = ghostWeight + carryWeight + foodWeight
        print(totalWeight)
        if run == True:
            print("run")
            problem = RunAwayProblem(gameState, self)
        else:
            if totalWeight > 0:
                print("food")
                problem = SearchProblem(gameState, self, foodLocation)
            else:
                print("home")
                problem = GoHomeProblem(gameState, self)
        plan = aStarSearch(problem)
        #print('search - total of %d nodes expanded in %.1f seconds' % (problem._expanded, time.time() - startTime))
        return plan[0]

    def isGoalState(self, gameState):
        return len(foodList) == 0

    def getSuccessors(self, gameState):
        successors = []
        actions = gameState.getLegalActions(self.index)
        for action in actions:
            successor = gameState.generateSuccessor(self.index, action)
            pos = successor.getAgentState(self.index).getPosition()
            if pos != nearestPoint(pos):
                # Only half a grid position was covered
                successor = successor.generateSuccessor(self.index, action)
                successors.append([successor, action, 1])
            else:
                successors.append([successor, action, 1])
        return successors

class DefensiveAgent(CaptureAgent):
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.start = gameState.getAgentPosition(self.index)
        self.walls = gameState.getWalls()

    def chooseAction(self, gameState):
        return Directions.STOP

class Problem:

    def getStartState(self):

        util.raiseNotDefined()

    def isGoalState(self, state):

        util.raiseNotDefined()

    def getSuccessors(self, state):

        util.raiseNotDefined()

    def getCostOfActions(self, actions):

        util.raiseNotDefined()

class SearchProblem(Problem):
    def __init__(self, gameState, CaptureAgent, goal):
        self.opponentPos = []
        for i in CaptureAgent.getOpponents(gameState):
            self.opponentPos.append(gameState.getAgentPosition(i))
        self.food = CaptureAgent.getFood(gameState)
        self.walls = gameState.getWalls()
        self.start = gameState.getAgentPosition(CaptureAgent.index)
        self.costFn = lambda x: 1
        self.startState = (self.start, self.food)
        self.index = CaptureAgent.index
        self.distancer = CaptureAgent.distancer
        self._expanded = 0
        #shortestFood = 9999
        #foodLocation = None
        #for i in self.food.asList():
        #    dist = self.distancer.getDistance(self.start, i)
        #    #dist = manhattanDistance(self.start, i)
        #    if dist < shortestFood:
        #        shortestFood = dist
        #        foodLocation = i
        #self.goal = foodLocation
        self.goal = goal

    def teamInfo(self):
        print(self.index)
        print(self.food)
        print(self.start)

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):
        #return len(state[1].asList()) == (len(self.food.asList()) - 2)
        return state[0] == self.goal

    def getSuccessors(self, state):
        successors = []
        self._expanded += 1 # DO NOT CHANGE
        for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state[0]
            dx, dy = Actions.directionToVector(direction)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                if not (nextx, nexty) in  self.opponentPos:
                    nextFood = state[1].copy()
                    nextFood[nextx][nexty] = False
                    successors.append( ( ((nextx, nexty), nextFood), direction, 1) )
        return successors


class GoHomeProblem(Problem):
    def  __init__(self, gameState, CaptureAgent):
        self.opponentPos = []
        for i in CaptureAgent.getOpponents(gameState):
            self.opponentPos.append(gameState.getAgentPosition(i))
        self.walls = gameState.getWalls()
        self.start = gameState.getAgentPosition(CaptureAgent.index)
        self.capsules = CaptureAgent.getCapsules(gameState)
        self.food = CaptureAgent.getFood(gameState)
        self.distancer = CaptureAgent.distancer
        self.startState = (self.start, self.food)
        closestDist = 999
        closestPos = None
        for y in range(1, CaptureAgent.top + 1):
            if not self.walls[CaptureAgent.border][y]:
                dist = CaptureAgent.distancer.getDistance(self.start, (CaptureAgent.border, y))
                if dist < closestDist:
                    closestPos = (CaptureAgent.border, y)
                    closestDist = dist
        self.goal = closestPos
        self._expanded = 0

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):
        return state[0] == self.goal

    def getSuccessors(self, state):
        successors = []
        self._expanded += 1
        for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state[0]
            dx, dy = Actions.directionToVector(direction)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                if not (nextx, nexty) in self.opponentPos:
                    nextFood = state[1].copy()
                    nextFood[nextx][nexty] = False
                    successors.append( ( ((nextx, nexty), nextFood), direction, 1) )
        return successors

class RunAwayProblem(Problem):
        def  __init__(self, gameState, CaptureAgent):
            self.opponentPos = []
            for i in CaptureAgent.getOpponents(gameState):
                self.opponentPos.append(gameState.getAgentPosition(i))
            self.walls = gameState.getWalls()
            self.start = gameState.getAgentPosition(CaptureAgent.index)
            self.capsules = CaptureAgent.getCapsules(gameState)
            self.food = CaptureAgent.getFood(gameState)
            self.distancer = CaptureAgent.distancer
            self.startState = (self.start, self.food)
            closestDist = 999
            closestPos = None
            for y in range(1, CaptureAgent.top + 1):
                if not self.walls[CaptureAgent.border][y]:
                    dist = CaptureAgent.distancer.getDistance(self.start, (CaptureAgent.border, y))
                    if dist < closestDist:
                        closestPos = (CaptureAgent.border, y)
                        closestDist = dist
            for i in self.capsules:
                dist = CaptureAgent.distancer.getDistance(self.start, i)
                if dist < closestDist:
                    closestPos = (i)
                    closestDist = dist
            self.goal = closestPos
            self._expanded = 0

        def getStartState(self):
            return self.startState

        def isGoalState(self, state):
            return state[0] == self.goal

        def getSuccessors(self, state):
            successors = []
            self._expanded += 1
            for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
                x,y = state[0]
                dx, dy = Actions.directionToVector(direction)
                nextx, nexty = int(x + dx), int(y + dy)
                if not self.walls[nextx][nexty]:
                    if not (nextx, nexty) in  self.opponentPos:
                        nextFood = state[1].copy()
                        nextFood[nextx][nexty] = False
                        successors.append( ( ((nextx, nexty), nextFood), direction, 1) )
            return successors

def aStarSearch(problem):
    from util import PriorityQueue

    openlist = PriorityQueue()
    closedlist = {}
    startNode = ([problem.getStartState(), heuristic(problem.getStartState(), problem), 0, []])
    openlist.push(startNode, startNode[1])
    while not openlist.isEmpty():
        currentNode = openlist.pop()
        if not currentNode[0] in closedlist or currentNode[2] + 1 < closedlist.get(currentNode[0]):
            if problem.isGoalState(currentNode[0]):
                return currentNode[3]
            closedlist[currentNode[0]] = currentNode[2]
            for successor in problem.getSuccessors(currentNode[0]):
                nextNode = [successor[0], heuristic(successor[0], problem), currentNode[2] + successor[2], []]
                for i in currentNode[3]:
                    nextNode[3].append(i)
                nextNode[3].append(successor[1])
                openlist.push(nextNode, (nextNode[1] + nextNode[2]))
    return "failure"

    util.raiseNotDefined()

def aStarSearch2(captureAgent, gameState):

    from util import PriorityQueue

    openlist = PriorityQueue()
    closedlist = {}
    startNode = ([gameState, heuristic(gameState.getAgentState(captureAgent.index).getPosition()), 0, []])
    openlist.push(startNode, startNode[1])
    while not openlist.isEmpty():
        currentNode = openlist.pop()
        print("")
        print("index is", captureAgent.index)
        print("currentNode", currentNode[0].getAgentState(captureAgent.index))
        if not currentNode[0] in closedlist or currentNode[2] + 1 < closedlist.get(currentNode[0]):
            if captureAgent.isGoalState(currentNode[0]):
                return currentNode[3]
            closedlist[currentNode[0]] = currentNode[2]
            for successor in captureAgent.getSuccessors(currentNode[0]):
                nextNode = [successor[0], heuristic(successor[0].getAgentState(captureAgent.index).getPosition()), currentNode[2] + successor[2], []]
                for i in currentNode[3]:
                    nextNode[3].append(i)
                nextNode[3].append(successor[1])
                openlist.push(nextNode, (nextNode[1] + nextNode[2]))
        else:
            print("state found already")
    return []

    util.raiseNotDefined()

def nullheuristic(state, problem):
    return 0

def heuristic(state, problem):
    return problem.distancer.getDistance(state[0], problem.goal)

def searchHeuristic(state, problem):
    currentPos = state[0]
    shortestFood = 9999
    foodLocation = None
    for i in problem.food.asList():
        dist = problem.distancer.getDistance(currentPos, i)
        if dist < shortestFood:
            shortestFood = dist
            foodLocation = i
    return shortestFood

def heuristic2(state, problem):
    currentPos = state[0]
    totalDist = 0
    visited = []
    while len(visited) <= 5:
        shortestFood = 999
        foodLocation = None
        for i in problem.food.asList():
            if i not in visited:
                dist = problem.distancer.getDistance(currentPos, i)
                #dist = manhattanDistance(currentPos, i)
                if dist < shortestFood:
                    shortestFood = dist
                    foodLocation = i
        totalDist += dist
        visited.append(foodLocation)
        currentPos = foodLocation
    return totalDist

def manhattanDistance(x, y ):
  return abs( x[0] - y[0] ) + abs( x[1] - y[1] )


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
