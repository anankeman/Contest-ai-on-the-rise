# AI Method 2 - Game Theory - Minimax



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

GGame theory try to model the outcome of a decision-making process for competitive or cooperative agents that are rational, self-interested and limited by certain rules or boundaries, in other words a game with several players. This frames perfectly the pacman task.

We introduced the minimax algorithm, which is a recursive algorithm that for each possible action tries to maximize the outcome for a given player, but also, if an enemy is present, it use the same metric o evaluation function to calculate the best minimizing action. This is achieved by recursively exploring the outcomes of each decision until the maximum depth is reach. The algorithm alternates between the maximizing agent and the minimizing agent.
Therefore, the algorithm has three parts:

- Once the maximum recursion depth is reach, it evaluates the current state using the evaluation function.
- a maximizing agent part that return the action that maximizes the score.
- a minimizing agent part that return the action that minimizes the score.

However, this algorithm has an issue of complexity because it calculates all possible combinations of actions. Therefore alpha-beta pruning was implemented to reduce such complexity and avoid timeouts.

Alpha-beta pruning introduce two variables to keep track of current maximum and minimum of a branch, if an agent is minimizing it will not pick branches that are greater than the current value, therefore there is no need to keep exploring that branch. Same may occur with the maximizing agent when encounter a branch that has less than the current value.

[Back to top](#table-of-contents)

### Application  
The algorithm itself is simple to implement, however there are some critical decision. 

First there is need for an evaluation function that return the reward at each possible tree leaf, similar to a heuristic function. In our implementation we used the same values.
Also, there is need to add an exception when no enemy is at sight.
Finally, some combination of actions could have the same value if they end in the same position. However, to reach that position more steps were required for some actions than others (such as going forward and then going back), but the value evaluation value that backpropagates will be the same of all of them, then an additional cost to reach that state must be include for every recursion. 

Also, despite alpha-beta pruning technique, the worst time complexity could be reach, then by trial and error in the competition we found that a depth value of four was necessary to avoid timeouts.

In the image it is possible to observe all the final states the red agent is considering making a decision over the next step.
![Demo 1](images/pacman1.gif)
[Back to top](#table-of-contents)

### Trade-offs  
#### *Advantages*  
Takes in consideration the next possible action for the adversary. It plans a better short-term strategy than A*.

#### *Disadvantages*
High complexity, which is exponential to the depth: O(A^d), where A stand for possible actions and d for the depth. Alpha-beta pruning can improve the average case, but the worst scenario may still occur.

Balance weights to have general solution is hard.
[Back to top](#table-of-contents)

### Future improvements  

Only the closest enemy is taken in consideration, but it may be implemented a solution to include a second minimizing agent.
No decision tree was developed to change weights in the evaluation function, due increasing complexity, as such tree must be implemented recursively, but it is possible.


Roger B. Myerson, Game Theory: Analysis of Conflict


[Back to top](#table-of-contents)
