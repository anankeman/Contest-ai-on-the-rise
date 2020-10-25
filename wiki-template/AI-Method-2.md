# AI Method 2 - Game Theory - Minimax

Your notes about this part of the project, including acknowledgement, comments, strengths and limitations, etc.

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

Game theory try to model the outcome of a decision-making process for competitive or cooperative agents that are rational, self-interested and limited by certain rules or boundaries, in other words a game with several players. This frames perfecly the pacman task.

We introduced the minimax algorithm, which is a recursive algorithm that for each possible action tries to maximize the outcome for a given player, but also, if an enemy is present, it use the same metric o evaluation function to calculate the best minimizing action. This is achieve by recursibly exploring the outcomes of each decision until the maximum depth is reach.The algorithm alternate between the maximizing agent and the minizing agent.
Therefore, the algorithm has three parts:

- Once the maximum recursion depth is reach, it evaluate the current state using the evaluation function.
- a maximizing agent part that return the action that maximaze the score.
- a minimizing agent part that return the action that minimaze the score.

However, this algorithm has an issue of complexity because it calculates all posible combinations of actions. Therefore alpha-beta prunning was implemented to reduce such complexity and avoid timeouts.

Alpha-beta pruning introduce two variables to keep track of current maximum and minimum of a branch, if an agent is minimizing it will not pick branches that are greater than the current value, therefore there is no need to keep exploring that branch. Same may occur with the maximazing agent when encounter a branch that has less than than the current value.

[Back to top](#table-of-contents)

### Application  
The algorithm itself is simple to implement, however there are some critical decision. 

First there is need for a evaluation function that return the reward at each posible tree leaf, similar to an heuristic function. In our implementation we used the same values.
Also, there is need to add an exception when no enemy is at sight.
Finally some combination of actions could have the same value if they end in the same position, however to reach that position more steps were required for some actions than others (such as going forward and then going back), but the value evaluation value that backpropagates will be the same of all of them, then an additional cost to reach that state most be include for every recursion. 

Also, despipte alpha pruning the worst time complexity maybe reach, then by trial and error in teh competition we find that a depth value of four was necesarry to avoid timeouts.

In the image it is posible to observe all the final states the red agent is considerin to make a decision over the next step.
![Demo 1](images/pacman1.gif)
[Back to top](#table-of-contents)

### Trade-offs  
#### *Advantages*  
takes in consideration the next posible action for the adversary. IT plana a better sor-term strategy than A*.

#### *Disadvantages*
High complexity, which is exponential to the depth: O(A^d), where A stand for possible actions and d for the depth. Alpha-beta pruning can improve the average case, but the worst scenario may still occur.

Balance weights to have general solution is hard.
[Back to top](#table-of-contents)

### Future improvements  

Only the closest enemy is take in consideration but it may be implemented a soluciton to include a second minimazing agent.
no decision tree was develop to change weights in the evaluation function, due increasing complexity, as such tree must be implemented recursibly, but it is possible.

[Back to top](#table-of-contents)
