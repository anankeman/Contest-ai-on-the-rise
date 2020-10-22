# AI Method 1 - A start Approach


Your notes about this part of the project, including acknowledgement, comments, strengths and limitations, etc.

If you use Greedy Best First Search (GBFS) or Monte Carlo Tree Search (MCTS), you do not need to explain the algorithm GBFS/MCTS, tell us how you used it and how you applied it in your team.

# Table of Contents
- [Governing Strategy Tree](#governing-strategy-tree)
  * [Motivation](#motivation)
  * [Design and Workflow](#design-and-workflow)
  * [Application](#application)
  * [Trade-offs](#trade-offs)     
     - [Advantages](#advantages)
     - [Disadvantages](#disadvantages)
  * [Future improvements](#future-improvements)

## Governing Strategy Tree  

### Motivation  
Pac-Man can be formulated as a series of different classical planning problems; finding food, returning home, and capturing an opponent can all be framed as simple goals. As such, a rational first place to start was to use a basic strategy implementing a heuristic search. The motivation for this was that the strategy is easy to implement and quite versatile. Additionally, given the structure of the game, with 15 seconds to do computations such as calculate maze distances, meant that for static problems such as finding food it was possible to calculate and use the perfect heuristic h* effectively in game. The algorithm chosen for implementing heuristic search was A*, given that the search had requirements for both a heuristic and a cost function. 
[Back to top](#table-of-contents)

### Design and Workflow
Initially, several approaches were attempted in order to design the most effective agent possible. Each member of the group separately tried to design their own agent as a starting point, and used slightly different implementations of the algorithm:
The different strategies applied were as follows:

1) An abstraction of the Pac Man game state was used in order to try and limit calls to the program running the game, which had significant computational cost. For example, if the agent was finding food, the goal was framed as going to the nearest food, and the state was represented as the position and the remaining food. 
An A* search using maze distance was run on this game state each turn while assuming all entities were static except the agent making the next move. Taking a simple abstraction of the game state, and updating this abstraction was effective in reducing computational complexity and allowed a path to be found to the nearest food quickly. However it proved to be ineffective as it didn’t have enough detail in the representation of the game state and taking into account ghost movement more dynamically was necessary. Additionally, it made a bulky program where every goal had to be framed as a new problem. 

2) A* was run only for the offensive agent. In the 15 first seconds of the initial state, A* using maze distance was run to give an optimal path for the offensive agent to eat all the food. Then, in subsequent steps, this plan was followed without updating at each turn. Ghosts were dealt with by having the agent run back to the closest point in it’s own territory. After running away, the agent would go back to the last point of the plan that was successfully followed, and continue following the same plan. The Heuristic used was simple the shortest path to every food for every closest food (iterative). This was discarded because of its simplicity and inflexibility. 

3) A* was run search every turn on the full game state, but stopping after N iterations to limit computational complexity, returning only the first step in latest path considered. A more complex heuristic was implemented, using the weighted combination of the distance to the closest food, the distance to the closest capsule, and the inverse distance to the closest ghost to discourage the agent from moving close to the ghosts. The weights were change according to a goal set selected by a decision tree: If a ghost is in sight the weight to closest food is set to zero, the distance to the closest point of the border is set to 1, and distance to the closest capsule is set to 1. Else the distance to capsule is set to one. In this way it was possible to modify the agent’s behaviour simply based on the heuristic. 

4) A similar approach was tested as in 3, but instead of only varying the heuristic, goals were also changed every turn as well, according to a decision tree. The tree consisted of several decisions based on the current state. First, the tree check if any ghost is visible and not scared, in which case the goal was to run away by either getting back to it’s own territory or eating a capsule. If there were no ghosts in sight, or the ghost was scared, the goal was to eat food. And if the agent had eaten food and there was no food nearby, the goal was to get back to their side to score points. Both the heuristic and goal were updated for each different outcome of the decision tree in this strategy. 
[Back to top](#table-of-contents)

### Application
The various approaches for the offensive agent were then assessed for the best starting point: In the first approach, taking a simple abstraction of the game state, and updating this abstraction was effective in reducing computational complexity and allowed a path to be found to the nearest food quickly. However it proved to be ineffective as it didn’t have enough detail in the representation of the game state and taking into account ghost movement more dynamically was necessary. Additionally, it made a bulky program where every goal had to be framed as a new problem. 
The second approach was abandoned as although at the start the plan was optimal, the further away from the next step the agent moved or was chased, the further from optimal the plan became. There was also a large overhead in calculating the optimal plan at the start, and it was not certain that 15 seconds was sufficient with all mazes in addition to other calculations. 
The third and fourth approach worked well. The fourth lacked some flexibility in relying on decision trees, but was chosen as the basis for the defensive agent due to having the ability to implement a more complex strategy with several separate goals. The third was used for the offensive agent, as the behaviour was more clearly mapped out by a heuristic function which balanced the various goals, and this gave the agent a higher degree of flexibility. 

#### Offensive Agent
As an A* approach with a single goal was chosen, a large amount of testing was done to try and select an appropriate goal and heuristic.

##### Goals
The initial goal chosen for the offensive agent was to eliminate all the food from the map, and as such the goal state was simply met when the food on the map was 0. The issue that arose with this goal was that it didn’t actually meet the criteria for winning a game. An agent could eat all the food, and then if it didn’t make it back to the other side this would be ineffective, and potentially score no points. This was backed up by the fact that when the agent successfully ate all the food, it stopped and no further actions were taken. 
The next goal chosen was to have the score equal to the number of food items at the start of the game. In this way, the goal was not achieved until the agent was successfully across the line into it’s own territory. 

##### Heuristic
The heuristic function chosen was a composite of several sources of information. This contained most of the computation that decided what the agent should do. The heuristic function used was a combination of: 
1)	minimum distance to food
2)	inverse of minimum distance to ghost
3)	minimum distance to the border
4)	minimum distance to the capsule

These were weighted according to the goal, chosen by a decision tree. These were set up as follows:

1)	If the goal was ‘get food’, the minimum distance to the border and capsule were set to 0. 
2)	If the goal was ‘get border’, the minimum distance to food and the capsule were set to 0
3)	If the goal was ‘get capsule’ the minimum distance to food and to the border was set to 0
This approach was taken in order to let the agent decide the best path based on the overall goal, and the heuristic was used as a guide. 

##### Issues:
The use of only a heuristic made the behaviour harder to control than expected. Behaviour in the average situation was as expected, and given no defence the agent worked optimally. However, the agent’s performance was significantly impacted by the presence of a defender. When a ghost was nearby it would often get stuck in a loop, or never leave the border. Having a limit on the number of iterations of A* also meant that it wouldn’t find an alternative route around the defender, and increasing the number of iterations resulted in erratic performance as it tried to balance the less well defined goal.
[Back to top](#table-of-contents)

#### Defensive agent: 
The defensive agent relied on a more comprehensive decision tree. The first strategy implemented was to attempt to pre-empt the opponents move by going to the ‘middle’ of the food, or the median food point in the grid. This was decided to be ineffective as the defensive agent may have ended up getting stuck behind a wall, making it unable to defend even if at a close manhattan distance. A patrol function was implemented second, which seemed to work more effectively. 
The defender also employed a different strategy for when a Pac Man was seen. If the defender wasn’t scared, a simple chase was done, whereas if the defender was scared, it opted to remain within 2 squares, to try and stay close without being caught. 
##### Goal:
The goal state in the defender consisted of one of the following:
1)	If the goal state was ‘patrol’, then two points were selected upon start-up that represented the ‘top’ and the ‘bottom’. These points were alternated upon achieving either as the goal state. 
2)	If the goal state was ‘get invaders’ then the goal was chosen to be whatever the enemy’s position was. 
3)	If the goal state was ‘get invaders scared’ the goal state was a distance of 2 from the invader. 
4)	If the goal state was ‘go centre’ the defender would reset to resume patrol
The heuristic used in all these cases was the maze distance. 
##### Issues:
The strategy was quite robust, until something unexpected happened, and it turned out to be less intelligent than originally thought. The issue became that although many branches were programmed into the decision tree, the strategy was quite inflexible, and it was an all or nothing response. If there was an agent nearby on the border, the defender would get stuck, or go into a loop, which clearly is counter productive to the strategy. 
The more loops introduced to try and fix these issues, the more goal types were added, and the result was worse decision boundaries which exacerbated the problem. 
[Back to top](#table-of-contents)

### Trade-offs  
#### *Advantages*  
complete optimal as branching factor es finite and cost are fixed in a given step

#### *Disadvantages*
High complexity in most cases
[Back to top](#table-of-contents)

### Future improvements  

[Back to top](#table-of-contents)
