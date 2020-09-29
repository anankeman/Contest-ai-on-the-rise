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
import random, time, util
from game import Directions
import game
import capture

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'AstartAgent', second = 'DefensiveReflexAgent'):
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

class AstartAgent(CaptureAgent):
    
    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        
        CaptureAgent.registerInitialState(self, gameState)
        
        self.plan = self.aStar(gameState)
        
        self.frontier = halfGrid(gameState.data.layout, self.red, gameState)
        print(self.frontier)

        
        
    def chooseAction(self, gameState):
        

        myPos = gameState.getAgentState(self.index).getPosition()
        actions = gameState.getLegalActions(self.index)
        

        nextGoal = self.plan[0]
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        ghost = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        amIghost = gameState.getAgentState(self.index).isPacman
        
        if len(ghost)>0 and amIghost:
            nextAction = self.runFromGhost(gameState, ghost, actions, myPos)
        else:
            # if state in policy execute policy
            if myPos == nextGoal[0]:
                nextAction = self.plan.pop(0)[1]
                
            else:
                #go to the closest state in remaining plan
                bestDist = 999999
                for action in actions:
                    successor = self.getSuccessor(gameState, action)
                    pos2 = successor.getAgentPosition(self.index)
                    dist = self.getMazeDistance(pos2, nextGoal[0])
                    if dist < bestDist:
                      bestAction = action
                      bestDist = dist
                nextAction = bestAction
        
        return nextAction
    
    def runFromGhost(self, gameState, ghost, actions, myPos):
        ghostPos = ghost[0].getPosition()
        distanceToFront = {i: self.getMazeDistance(myPos, i) for i in self.frontier}
        nextGoal = min(distanceToFront, key= lambda k: distanceToFront[k])
        
        bestDist = 999999
        ghostFear = 0
        for action in actions:
            successor = self.getSuccessor(gameState, action)
            pos2 = successor.getAgentPosition(self.index)
            dist = self.getMazeDistance(pos2, nextGoal)
            ghostDistance = self.getMazeDistance(pos2, ghostPos)
            dist = dist - ghostDistance
            if dist < bestDist:# and ghostDistance > ghostFear:
              bestAction = action
              bestDist = dist
              ghostFear = ghostDistance
        nextAction = bestAction
        
        return nextAction
    
    def getSuccessor(self, gameState, action):
        
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != util.nearestPoint(pos):
          # Only half a grid position was covered
          return successor.generateSuccessor(self.index, action)
        else:
          return successor
        
        
        return successor
    
    def aStar(self, gameState, w = 1):
        priorityQ = util.PriorityQueue()
        mark = [] #mark visited states
        #startState = self.start
        
        priorityQ.push((gameState, [((0),"start")], 0), 0)
       
        bestG = dict()
        while not priorityQ.isEmpty():
            currentState, answer, currentCost = priorityQ.pop()
            
            if currentState not in mark or currentCost < bestG.get(currentState):
                mark.append(currentState)
                bestG[currentState] = currentCost
                
                if len(self.getFood(currentState).asList())== 0:                    
                    return answer[1:]
                actions = currentState.getLegalActions(self.index)
                pos = currentState.getAgentState(self.index).getPosition()
                
                for action in actions:
                    nextState = self.getSuccessor(currentState, action)
                    nextCost = currentCost + 1
                    heu = self.evaluate(nextState)
                    currentPath = list(answer)
                    currentPath.append((pos, action))
                    priorityQ.push((nextState, currentPath, currentCost), (heu*w)+nextCost)
        
        return []
    
    
    
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
        
    def evaluate(self, gameState):
        
        myState = gameState.getAgentState(self.index)
        position = myState.getPosition()
        food = self.getFood(gameState);
        
        food = food.asList()
        heuristic = 0
    
        if len(food) == 0:
            return heuristic
        heuristic = self.closestPoint(position, food, 0)
        return heuristic





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
    if pos != util.nearestPoint(pos):
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

def halfGrid(grid, red, gameState):
    halfway = grid.width // 2
    halfgrid = [[0]*halfway for i in range(grid.height)]
    
    if red:    xrange = range(halfway)
    else:       xrange = range(halfway, grid.width)
    
    for y in range(grid.height):
        for x in xrange:
            if not gameState.hasWall(x,y):
                halfgrid[x][y] = (x,y)         

    if red:
        front = [i for i in halfgrid[-1] if i!=0]
    else:
        front = [i for i in halfgrid[0] if i!=0]
            
    return front