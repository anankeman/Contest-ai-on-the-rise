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
               first = 'DefendAgent', second = 'DefendAgent'):
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


#-------------------------------------------------------------------------------------
class DefendAgent(CaptureAgent):

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.boundary = self.getBoundaries(gameState)
        self.halfgrid = self.halfGrid(gameState)
        self.opponents = self.getOpponents(gameState)
        self.start = gameState.getAgentPosition(self.index)
        #implement rolling list for prediction of direction later

    def chooseAction(self, gameState):
        self.testdist(gameState)
        currentPos = gameState.getAgentPosition(self.index)
        inRange = False
        scared = False
        if gameState.getAgentState(self.index).scaredTimer > 0:
            scared = True
        for i in self.opponents:
            if gameState.getAgentState(i).isPacman:
                if gameState.getAgentPosition(i) != None:
                    inRange = True
        if scared:
            return self.UCSDefend(gameState, "scared")
        else:
            if inRange == True:
                return self.UCSDefend(gameState, "chase")
            else:
                return self.patrol(gameState)

    def getSuccessors(self, gameState):
        successors = []
        actions = gameState.getLegalActions(self.index)
        for action in actions:
            successor = gameState.generateSuccessor(self.index, action)
            pos = successor.getAgentState(self.index).getPosition()
            if pos != nearestPoint(pos):
                # Only half a grid position was covered
                successor = successor.generateSuccessor(self.index, action)
                if successor.getAgentState(self.index).getPosition() in halfgrid:
                    successors.append([successor, action, 1])
            else:
                if pos in self.halfgrid:
                    successors.append([successor, action, 1])
        return successors


    def halfGrid(self, gameState):
        grid = gameState.data.layout
        halfway = grid.width // 2
        halfgrid = []
        if self.red:    xrange = range(halfway)
        else:           xrange = range(halfway, grid.width)

        for y in range(grid.height):
            for x in xrange:
                if not gameState.hasWall(x,y):
                    halfgrid.append((x,y))
        return halfgrid

    #List with the boundary dividing red and blue area
    def getBoundaries(self, gameState):
        height_y = gameState.data.layout.height
        width_x = gameState.data.layout.width
        halfway = width_x//2
        if self.red:
          our_side_limit_x = halfway
        else:
          our_side_limit_x = halfway + 1

        boundaries = [(int(our_side_limit_x), int(i)) for i in range(1, height_y - 2)]
        final = []
        for boundary in boundaries:
          if not gameState.hasWall(boundary[0],boundary[1]):
            final.append(boundary)
        return final

    def opponentDist(self, gameState): #possibly implement conditionals for selecting which opponent to follow e.g. isPacman
        currentPos = gameState.getAgentPosition(self.index)
        opponents = {}
        for i in self.getOpponents(gameState):
            opponents[i] = [gameState.getAgentPosition(i) , gameState.getAgentDistances()[i]]
        opponentPos = None
        minimumDist = 9999
        for i in opponents.keys():
            nextOpponentPos = opponents[i][0]
            noisyDist = opponents[i][1]
            if nextOpponentPos != None:
                dist = self.getMazeDistance(currentPos, nextOpponentPos)
                if dist < minimumDist:
                    minimumDist = dist
                    opponentPos = nextOpponentPos
            else:
                if opponentPos == None:
                    if noisyDist < minimumDist:
                        minimumDist = noisyDist
        return minimumDist

    def pacmanPosition(self, gameState):
        d = 9999
        agentPos = None
        currentPos = gameState.getAgentPosition(self.index)
        opps = [gameState.getAgentPosition(i) for i in self.opponents if gameState.getAgentState(i).isPacman]
        for i in opps:
            if i != None:
                dist = self.getMazeDistance(currentPos, i)
                if dist < d:
                    d = dist
                    agentPos = i
        return agentPos

    def distanceToBorder(self, gameState):
        myPos = gameState.getAgentPosition(self.index)
        distanceToFront = {i: self.getMazeDistance(myPos, i) for i in self.boundary}
        nextGoal = min(distanceToFront, key= lambda k: distanceToFront[k])
        return self.getMazeDistance(myPos, nextGoal)

    def testdist(self, gameState):
        print("")
        count = 0
        currentState = gameState
        while count < 5:
            print("current state", currentState.getAgentPosition(self.index))
            print("next successor")
            nextState = self.getSuccessors(currentState)[0][0]
            for i in self.opponents:
                print(nextState.getAgentDistances()[i])
            currentState = nextState
            count += 1

    def patrol(self, gameState):
        priorityQ = util.PriorityQueue()
        currentPos = gameState.getAgentPosition(self.index)
        for successor in self.getSuccessors(gameState):
            borderDistance = self.distanceToBorder(successor[0])
            opponentDistance = self.opponentDist(successor[0])
            h = opponentDistance + borderDistance
            priorityQ.push(successor, h)
        nextAction = priorityQ.pop()
        return nextAction[1]

    #not working yet
    def defend(self, gameState):
        Q = util.Queue()
        Q.push(gameState)
        visited = []
        bestPos = None
        bestDist = 9999
        while not Q.isEmpty():
            currentNode = Q.pop()
            currentState = currentNode.getAgentPosition(self.index)
            if currentState in visited:
                continue
            visited.append(currentState)
            dist = self.opponentDist(currentNode)
            if dist < bestDist:
                bestDist = dist
                bestPos = currentState
            for action in currentNode.getLegalActions(self.index):
                print(action)
                if action == Directions.NORTH or Directions.SOUTH:
                    successor = gameState.generateSuccessor(self.index, action)
                    Q.push(successor)
        return self.Astar(gameState, bestPos)

    def UCSDefend(self, gameState, goal):
        from util import PriorityQueue
        opponentPos = self.pacmanPosition(gameState)
        if opponentPos != None:
            openlist = PriorityQueue()
            closedlist = []
            startNode = ([gameState, [], 0])
            openlist.push(startNode, startNode[2])
            while not openlist.isEmpty():
                currentNode = openlist.pop()
                currentPos = currentNode[0].getAgentPosition(self.index)
                if not currentPos in closedlist:
                    if self.isGoalState(goal, currentPos, opponentPos):
                        if len(currentNode[1]) > 0:
                            return currentNode[1][0]
                        else:
                            return Directions.STOP
                    closedlist.append(currentPos)
                    for successor in self.getSuccessors(currentNode[0]):
                        nextPos = successor[0].getAgentPosition(self.index)
                        nextNode = [successor[0], [], currentNode[2] + successor[2]]
                        for i in currentNode[1]:
                            nextNode[1].append(i)
                        nextNode[1].append(successor[1])
                        openlist.push(nextNode, (nextNode[2]))

    def isGoalState(self, goal, currentPos, opponentPos):
        if goal == "scared":
            return self.getMazeDistance(currentPos, opponentPos) == 3
        elif goal == "chase":
            return currentPos == opponentPos

    def AStarFood(self, gameState, goal):
        from util import PriorityQueue
        openlist = PriorityQueue()
        closedlist = {}
        startNode = ([gameState, 0, 0, []])
        openlist.push(startNode, 0)
        while not openlist.isEmpty():
            currentNode = openlist.pop()
            currentState = currentNode[0]
            currentPos = currentState.getAgentPosition(self.index)
            if not currentPos in closedlist or currentNode[2] + 1 < closedlist.get(currentPos):
                if currentPos == goal:
                    if len(currentNode[3]) > 0:
                        return currentNode[3][0]
                    else:
                        return Directions.STOP
                closedlist[currentPos] = currentNode[2]
                for successor in self.getSuccessors(currentState):
                    successorPos = successor[0].getAgentPosition(self.index)
                    nextNode = [successor[0], self.getMazeDistance(successorPos, goal), currentNode[2] + successor[2], []]
                    for i in currentNode[3]:
                        nextNode[3].append(i)
                    nextNode[3].append(successor[1])
                    openlist.push(nextNode, (nextNode[1] + nextNode[2]))


    #List distance to the nearest food
    def getDistanceNearestFood(self, gameState):
        current_state = gameState.getAgentState(self.index)
        current_position = current_state.getPosition()

        food_list = self.getFood(gameState).asList()
        if len(food_list) > 0:
          minimum_distance = min([self.getMazeDistance(current_position, food) for food in food_list])
        else:
          minimum_distance = 999
        return minimum_distance
