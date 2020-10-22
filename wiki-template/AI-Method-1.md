# AI Method 1 - A start Approach


Your notes about this part of the project, including acknowledgement, comments, strengths and limitations, etc.

If you use Greedy Best First Search (GBFS) or Monte Carlo Tree Search (MCTS), you do not need to explain the algorithm GBFS/MCTS, tell us how you used it and how you applied it in your team.

# Table of Contents
- [Governing Strategy Tree](#governing-strategy-tree)
  * [Motivation](#motivation)
  * [Design and Workflow](#design-and-workflow)
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

In first case: complexity was low but exceution cannot adapt to changing context.
In the second case complexity was constrain to the N steps, however it does not always optimal and for large N, cost of calculating to the final path was high.
In the thrird case was high in some cases, particular in the begining of the match were food was at maximum distance, but then optimal path for short-term goal were quite fast.


Finally we applied the algorithm the defendant, using again changing goal and heuristic. The decision tree followed: If there is enemy pacman at sight then patrol the border....

The team tried to introduce more branchs to the decision tree, such as more goal types to force the pacman to patrol the border if encounter an enemy ghost defending, however the result was worse as decision boundaries were hard, creating behavior loops.
[Back to top](#table-of-contents)

### Trade-offs  
#### *Advantages*  
complete optimal as branching factor es finite and cost are fixed in a given step

#### *Disadvantages*
High complexity in most cases
[Back to top](#table-of-contents)

### Future improvements  

[Back to top](#table-of-contents)
