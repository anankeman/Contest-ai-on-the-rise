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
                             first = 'AttackAgent', second = 'defenseAgent'):
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

class defenseAgent(CaptureAgent):
    
    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        
        CaptureAgent.registerInitialState(self, gameState)
        self.frontier = halfGrid(gameState.data.layout, self.red, gameState)
        print(self.frontier)
        
        
    def chooseAction(self, gameState):
        start = time.time()
        myPos = gameState.getAgentState(self.index).getPosition()
        actions = gameState.getLegalActions(self.index)
        
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        pac = [a for a in enemies if a.isPacman and a.getPosition() != None]
        #amIpacman = gameState.getAgentState(self.index).isPacman
        
        if len(pac)>0:
            nextAction = self.goForPacman(gameState, pac, actions, myPos)
        else:
            nextAction = self.patrol(gameState, myPos, actions)
            
        print('eval time for agent %d: %.4f' % (self.index, time.time() - start))
        
        return nextAction
    
    def goForPacman(self, gameState, pacman, actions, myPos):
        pacmanPos = pacman[0].getPosition()
        #distanceToFront = {i: self.getMazeDistance(myPos, i) for i in self.frontier}
        #nextGoal = min(distanceToFront, key= lambda k: distanceToFront[k])
        
        bestDist = 999999
        for action in actions:
            successor = self.getSuccessor(gameState, action)
            pos2 = successor.getAgentPosition(self.index)
            dist = self.getMazeDistance(pos2, pacmanPos)
            if dist < bestDist:# and ghostDistance > ghostFear:
              bestAction = action
              bestDist = dist
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
    
    def patrol(self, gameState, myPos, actions):
        
        distanceToFront = {i: self.getMazeDistance(myPos, i) for i in self.frontier}
        nextGoal = min(distanceToFront, key= lambda k: distanceToFront[k])
        bestDist = 999999
        for action in actions:
            successor = self.getSuccessor(gameState, action)
            pos2 = successor.getAgentPosition(self.index)
            dist = self.getMazeDistance(pos2, nextGoal)
            if dist < bestDist:# and ghostDistance > ghostFear:
              bestAction = action
              bestDist = dist
        nextAction = bestAction
        
        return nextAction
        

def halfGrid(grid, red, gameState):
    border = [0]*grid.height
    if red:
        x = (grid.width//2)-1
    else:
        x= (grid.width//2)
    for y in range(grid.height):
        if not gameState.hasWall(x, y):
            border[y] = (x, y)
    border= [i for i in border if i!=0]
    return border

#-------------------------------------------------------------------------------------
class AttackAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """

    def registerInitialState(self, gameState):
        
        CaptureAgent.registerInitialState(self, gameState)
        self.count = 0
        self.boundaries = self.getBoundaries(gameState, gameState.data.layout, self.red)
        self.halfway = gameState.data.layout.width//2
        food_list = self.getFood(gameState).asList()
        self.initial_food = len(food_list)
        
        

    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """
        start = time.time()

        pos = gameState.getAgentPosition(self.index)
        
        previous = self.getPreviousObservation()
        if previous is not None:
            if previous.hasFood(pos[0], pos[1]):
                self.count += 1
            else:
                if (self.red and pos[0] < self.halfway) or (not self.red and pos[0] > self.halfway):
                    self.count = 0
                    
        #issues: ghost information is shared between teammates

        
        ghost = self.getOpponentsDistances(gameState, pos)
        border = self.getDistanceNearestPointArea(gameState, pos) 
        
        if ghost < 10:
            capsule = self.getDistanceNearestCapsule(gameState, pos)
            
            if capsule > border:
                print("go border cus ghost")
                path = self.aStarSearch(gameState, 'getBorder')
            else:
                print("go capsule")
                path = self.aStarSearch(gameState, 'getCapsule')
        else:
            nextFood = self.getDistanceNearestFood(gameState, pos, True)
            if nextFood > border and self.count > 0:
                print("go border")
                path = self.aStarSearch(gameState, 'getBorder')
            else:
                print("go food")
                path = self.aStarSearch(gameState, 'getFood')

        print('eval time for agent %d: %.4f' % (self.index, time.time() - start))

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
            #return distance to the closes ghost
            return min([self.getMazeDistance(pos, i) for i in ghost])
        else:
            return 999 #smooth value?

    #Maze distance to the nearest food
    def getDistanceNearestFood(self, gameState, pos, one = False):
        food = self.getFood(gameState).asList()
        if len(food) == 0:
            return 0
        if one:
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


    def getGoal(self, goal, initialState, finalState, count):
        if goal == "getCapsule":
            capsules_list_init = self.getCapsules(initialState)
            capsules_list_fin = self.getCapsules(finalState)
            if len(capsules_list_init) - len(capsules_list_fin) == 1:
                return True
            else:
                return False
        if goal == "getFood" or goal == "getFood_Scared":
            food_list_init = self.getFood(initialState).asList()
            food_list_fin = self.getFood(finalState).asList()
            if len(food_list_init) - len(food_list_fin) == 1:
                return True
            else:
                return False

    def aStarSearch(self, gameState, goal, maxSight = 7):
        """Search the node that has the lowest combined cost and heuristic first."""
        priorityQ = util.PriorityQueue()
        mark = [] #mark visited states  
        case = []
        priorityQ.push((gameState, [((0),"start")], 0), 0)
       
        bestG = dict()
        while not priorityQ.isEmpty() and (maxSight > 0):
            currentState, answer, currentCost = priorityQ.pop()
            case = answer
            
            if currentState not in mark or currentCost < bestG.get(currentState):
                mark.append(currentState)
                bestG[currentState] = currentCost
                
                if len(self.getFood(currentState).asList())== 0:                    
                    return answer[1][1]
                maxSight -= 1
                
                actions = currentState.getLegalActions(self.index)
                pos = currentState.getAgentState(self.index).getPosition()
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
            features['minDistanceOurArea'] = 0#(self.getDistanceNearestPointArea(successor, pos)# + min_dist_food + self.initial_food - current_food)*(2-per)
        
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

#-----------------------------------------------------------------------------------

