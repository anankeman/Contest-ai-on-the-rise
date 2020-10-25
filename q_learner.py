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
               first = 'DefensiveReflexAgent', second = 'ApproximateQAgent'):
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

#python capture.py -r baselineTeam -b myTeam_Q -l RANDOM --numGames 100 --quiet --delay-step 0
