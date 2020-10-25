# AI Method 3 - Computational Approach

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

Capture the Flag (Pac-Man) state space
* Location for our agents (# possibilities^2)
* State of our agents (Pac-Man, not scared ghost, scared ghost)
* Location for enemy agents (# possibilities^2)
* State of our agents (Pac-Man, not scared ghost, scared ghost)
* If it is possible to know the location of the ghost or not 
* Location for food
* Location for pills

Given the above, it can be concluded that the number of possible states in the game is very large, leading to several problems that can increase or decrease depending on the chosen approach. 

Approximate Q-Learning
Among the different approaches to solve Capture the Flag is approximate Q-learning. This method uses the same approach as Q-learning, which uses rewards to guide the agent in the right direction and, the exploration and exploitation approach to encourage the agent to search for novel states and rewards. With the difference that approximate Q-learning assumes the existence of a feature function ![f1] over state and action pairs, where the feature function is represented by a vector of feature values ![f2], reducing the description of a state to a number of features determined with domain knowledge. 


[Back to top](#table-of-contents)

### Application  

For the specific case of Capture the Flag, the main features selected to represent a state are:
* distanceToFood: maze distance to the nearest pellet of food
* distanceToEnemy
* distanceToCapsule: maze distance to the nearest capsule. If not capsules, the state doesn't show any, and weight doesn't affect the linear combination
* scored: represent the score of the game 
* enemyRadar: boolean variable that activates if enemy is equal to or less than 2 steps
* stop: boolean variable that activates if action is 'stop' punishing it to avoid being considered in the available options
* foodLeft: # of food left in the game

The approximate Q-function takes the following form

![f3]

Additionally, the game score between the current state and the next was used as a reward.

Then with the steps taken and multiple simulations, using the following steps

![f1]

![f2]
It can be noticed that the weights for the features converges in a kind of gradient descent method, as the following image for 4 of the features used in the approximate Q-learning. A set of initial values which are believed to be the appropriate ones is selected to reduce the number of iterations to converge. 

![](https://i.imgur.com/Zhj0iHG.png)

[Back to top](#table-of-contents)

### Trade-offs  
#### *Advantages*  

* Si


#### *Disadvantages*

[Back to top](#table-of-contents)

### Future improvements  

[Back to top](#table-of-contents)
