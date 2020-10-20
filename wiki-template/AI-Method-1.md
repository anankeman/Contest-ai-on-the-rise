# AI Method 1 - A start Approach


Your notes about this part of the project, including acknowledgement, comments, strengths and limitations, etc.

If you use Greedy Best First Search (GBFS) or Monte Carlo Tree Search (MCTS), you do not need to explain the algorithm GBFS/MCTS, tell us how you used it and how you applied it in your team.

# Table of Contents
- [Governing Strategy Tree](#governing-strategy-tree)
  * [Motivation](#motivation)
  * [Application](#application)
  * [Trade-offs](#trade-offs)     
     - [Advantages](#advantages)
     - [Disadvantages](#disadvantages)
  * [Future improvements](#future-improvements)

## Governing Strategy Tree  

### Motivation  
Our team choose A star because its simple implementation and the idea that is possible to have control over the state expansion to keep the complexity and time execution on check.

[Back to top](#table-of-contents)

### Application
To do so, the team each member tried different implementations of the algorithm:

1) It runs the A* in the 15 first seconds of the initial state to give to an Offensive pacman a route to eat all food.
Then, in the chooseAction, the pacman will try to follow the path until it finds a ghost, which in that case wil run back to the closest point
to its own territory. The Heuristic used was simple the shortest path to every food for every closest food (iterative).

2) The team tested to run the algorithm every turn, but it stopping after  N number of iterations, returning the first step in latest path considered.
using as a Heristic the weighted combination of distantance to the closest food, the inverse distance to the closest ghost and to the closest capsule. The weights change according to a goal set selected by a decision tree: If a ghost is at sight the weight to closest food is set to zero, the distance to the closest point of the border is set to 1, and distance to the closest capsulet is set to 1. Else the distance to capsule is set to one.

3) The team also  tested to run the algorithm every turn but hanging goals and weighted heuristic. The goal is a short-term goal and change according a decision tree. The tree check if any ghost is visible and no scared, then it calcualte the distance back to its own territory or to the closest capsule. Else, if no ghost was visible, then it calculate the distance to the closest food.

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
