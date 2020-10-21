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
               first = 'MinimaxAgent', second = 'MinimaxAgent'):
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

class MinimaxAgent(CaptureAgent):
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
    #Depth of the MiniMax model
    self.depth = 5
    #Index of enemies in the Map
    self.indexEnemies = self.getOpponents(gameState)

  # For PacMan the system maximized the Utility. Choose action based on legal actions
  def chooseAction(self, gameState):
    maxDepth = self.depth

    actionValues = util.Counter()
    for action in gameState.getLegalActions(self.index):
        successorGameState = getSuccessor(self.index, gameState, action)
        actionValues[action] = self.getEnemies(successorGameState, self.index, maxDepth - 1)
    print(actionValues)
    action = actionValues.argMax()
    print(action)
    return action

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
  def evaluationFunction(self, currentGameState):
        """
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState
        newPos = successorGameState.getAgentPosition(self.index)
        features = util.Counter()

        # Nearest food distance
        newFood_list = self.getFood(successorGameState).asList()
        if newFood_list:
            posFood_list = [self.getMazeDistance(newPos, newFood) for newFood in newFood_list]
            features['distanceToFood'] = min(posFood_list)
            averageFood = sum(posFood_list)/len(posFood_list)

        # Nearest capsule distance and score capsule
        newCapsules_list = self.getCapsules(successorGameState)
        if len(newCapsules_list) > 0:
            posCapsule_list = [self.getMazeDistance(newPos, newCapsule) for newCapsule in newCapsules_list]
            minPosCapsule = min(posCapsule_list)
            features['successorCapsule'] = len(posCapsule_list)
        else:
            minPosCapsule = 0
            features['successorCapsule'] = 0

        features['distanceToCapsule'] = minPosCapsule

        # Nearest enemy distance
        newOpponentPosition = [successorGameState.getAgentState(x).getPosition() for x in self.indexEnemies]
        posEnemy_list = []
        for newOpponent in newOpponentPosition:
            if newOpponent is not None:
                posOpponent= self.getMazeDistance(newPos, newOpponent)
                posEnemy_list.append(posOpponent)
        if posEnemy_list:
            minPosEnemy =  min(posEnemy_list)
            print(min(posEnemy_list))
        else:
            minPosEnemy = 0
        features['distanceToEnemy'] = minPosEnemy
        newOpponentstates = [successorGameState.getAgentState(x) for x in self.indexEnemies]
        newScaredTimes = [ghostState.scaredTimer for ghostState in newOpponentstates]
        minScaredTime = min(newScaredTimes)

        # Reflects if the new state has less food in the map
        features['eatenFood'] = len(newFood_list)

        # Reflects if the new state scores
        features['successorScore']: successorGameState.getScore()
        weights = self.getWeights()

        return features * weights

  #Maximize utility of Pacman based on the evaluation and the available action in the current state
  def getPacman(self, gameState, depth):
      if depth == 0:
        return self.evaluationFunction(gameState)
      nextAgentIndex = self.index
      score_list = [self.getEnemies(getSuccessor(nextAgentIndex, gameState, action), nextAgentIndex, depth - 1) for action in gameState.getLegalActions(nextAgentIndex)]
      return max(score_list)

  #Minimize utility of Ghosts based on the evaluation and the available action in the current state
  def getEnemies(self, gameState, indexGhost, depth):
    if depth == 0:
        return self.evaluationFunction(gameState)
    if indexGhost == self.index:
        nextAgentIndex = self.indexEnemies[0]
        enemyState = gameState.getAgentState(nextAgentIndex).getPosition()
        if enemyState is not None:
            score_list = [self.getEnemies(getSuccessor(nextAgentIndex, gameState, action), nextAgentIndex, depth - 1) for action in gameState.getLegalActions(nextAgentIndex)]
            return min(score_list)
        else:
            return self.getPacman(gameState, depth)
    elif indexGhost == self.indexEnemies[0]:
        nextAgentIndex = self.indexEnemies[1]
        enemyState = gameState.getAgentState(nextAgentIndex).getPosition()
        if enemyState is not None:
            score_list = [self.getPacman(getSuccessor(nextAgentIndex, gameState, action), depth - 1) for action in gameState.getLegalActions(nextAgentIndex)]
            return min(score_list)
        else:
            return self.getPacman(gameState, depth)
    else:
        return self.getPacman(gameState, depth)

  # Weights for the features, the idea is to tune in this weights for the features defined above
  def getWeights(self):
      return {'successorScore': -1000,
              'distanceToFood': -1,
              'distanceToEnemy': 100,
              'distanceToCapsule': -1,
              'successorCapsule': -10,
              'eatenFood': -100}

# Gets succesor state based on agent and the chosen action
def getSuccessor(index, gameState, action):
  """
  Finds the next successor which is a grid position (location tuple).
  """
  successorGameState = gameState.generateSuccessor(index, action)
  pos = successorGameState.getAgentState(index).getPosition()
  if pos is None:
      return gameState
  elif pos != nearestPoint(pos):
    # Only half a grid position was covered
    return successorGameState.generateSuccessor(index, action)
  else:
    return successorGameState
