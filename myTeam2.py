# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 19:59:16 2020

@author: framo
"""
from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
import capture

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'AstarAgent', second = 'defenseAgent'):
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

class defenseAgent(CaptureAgent):
    
    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        
        CaptureAgent.registerInitialState(self, gameState)
        
        
        self.frontier = halfGrid(gameState.data.layout, self.red, gameState)
        #print(self.frontier)

        
        
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



class AstarAgent(CaptureAgent):
    
    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        
        CaptureAgent.registerInitialState(self, gameState)
        
        self.frontier = halfGrid(gameState.data.layout, self.red, gameState)


        
        
    def chooseAction(self, gameState):
        
        myPos = gameState.getAgentState(self.index).getPosition()
        actions = gameState.getLegalActions(self.index)
        

        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        ghost = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        amIghost = gameState.getAgentState(self.index).isPacman
        
        if len(ghost)>0 and amIghost:
            nextAction = self.runFromGhost(gameState, ghost, actions, myPos)
        else:
            nextAction = self.aStar(gameState)
        
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
    
    def aStar(self, gameState, w = 1, maxS = 5, ghost = []):
        priorityQ = util.PriorityQueue()
        mark = [] #mark visited states
        #startState = self.start
        case = []
        maxSight = maxS
        priorityQ.push((gameState, [((0),"start")], 0), 0)
       
        bestG = dict()
        while not priorityQ.isEmpty() or maxSight > 0:
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
                    """
                    if len(ghost)>0:
                        heu = self.saveYourSelf(gameState, ghost, actions, pos)
                    else:
                        heu = self.evaluate(nextState)
                    """
                    heu = self.heuristic_Astar(nextState, "getFood")
                    currentPath = list(answer)
                    currentPath.append((pos, action))
                    priorityQ.push((nextState, currentPath, currentCost), (heu*w)+nextCost)
        
        return case[1][1]
    
    
    
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
    
    def heuristic_Astar(self, successor, goal):
        food_list = self.getFood(successor).asList()
        features = util.Counter()
        if goal == "getCapsule":
            features['minDistanceFood'] = 0
            features['minDistanceOpponent'] = 1/self.getOpponentsDistances(successor)
            features['minDistanceCapsule'] = self.getDistanceNearestCapsule(successor)
            features['minDistanceOurArea'] = 0
        elif goal == "getFood_Scared":
            features['minDistanceFood'] = self.getDistanceNearestFood(successor)
            features['minDistanceOpponent'] = 1/self.getOpponentsDistances(successor)
            features['minDistanceCapsule'] = 0
            features['minDistanceOurArea'] = 0
        elif goal == "getFood":
            features['minDistanceFood'] = self.evaluate(successor)
            features['minDistanceOpponent'] = 1/self.getOpponentsDistances(successor)
            features['minDistanceCapsule'] = 0
            features['minDistanceOurArea'] = 0
            features['successorScore'] = 0
            
        weights = self.getWeights(goal)

        return features*weights
    
    def getWeights(self, goal):
        if goal == "getCapsule":
            return {'minDistanceFood': 0,
                          'minDistanceOpponent': 50,
                          'minDistanceCapsule': 1,
                          'minDistanceOurArea': 0}
        elif goal == "getFood_Scared":
            return {'minDistanceFood': 1,
                          'minDistanceOpponent': 0,
                          'minDistanceCapsule': 0,
                          'minDistanceOurArea': 0}
        elif goal == "getFood":
            return {'minDistanceFood': 1,
                          'minDistanceOpponent': 100,
                          'minDistanceCapsule': 0,
                          'minDistanceOurArea': 1,
                          'successorScore':1}
    
          
  #List distance to the nearest capsule
  #Add None when there are no capsules left
    def getDistanceNearestCapsule(self, gameState):
        current_state = gameState.getAgentState(self.index)
        current_position = current_state.getPosition()
        capsules_list = self.getCapsules(gameState)
    
        capsules_distance_list = [self.getMazeDistance(current_position, x) for x in capsules_list]
        if len(capsules_list) > 0:
            minimum_distance = min(capsules_distance_list)
        else:
            minimum_distance = 999999 #if there are not more capsules dont go
        return minimum_distance
    
      #Distance to nearest point of our area
    
    def getDistanceNearestPointArea(self, gameState):
        boundaries = self.frontier
        current_state = gameState.getAgentState(self.index)
        current_position = current_state.getPosition()
        boundary_distance_list = []
        for boundary in boundaries:
            dist = self.getMazeDistance(current_position, boundary)
            boundary_distance_list.append(dist)
        
        return min(boundary_distance_list)
    
    def getGoal(self, goal, initialState, finalState, count):
        if goal == "getCapsule":
            capsules_list_init = self.getCapsules(initialState)
            capsules_list_fin = self.getCapsules(finalState)
            if len(capsules_list_init) - len(capsules_list_fin) == 1 or count == 13:
                return True
            else:
                return False
        if goal == "getFood" or goal == "getFood_Scared":
            food_list_init = self.getFood(initialState).asList()
            food_list_fin = self.getFood(finalState).asList()
            if len(food_list_init) - len(food_list_fin) == 1  or count == 13:
                return True
            else:
                return False
        
    def getDistanceNearestFood(self, gameState):
        current_state = gameState.getAgentState(self.index)
        current_position = current_state.getPosition()
        
        food_list = self.getFood(gameState).asList()
        minimum_distance = min([self.getMazeDistance(current_position, food) for food in food_list])
        return minimum_distance
    
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
                opponents_distance_list.append(dist)
        if len(opponents_distance_list) == 0:
            approx_distances = self.getCurrentObservation().getAgentDistances()
            opponents_index_list = self.getOpponents(gameState)
            opponents_distance_list = [approx_distances[x] for x in opponents_index_list]
        if min(opponents_distance_list) == 0:
            return 0.01
        
        return min(opponents_distance_list)

