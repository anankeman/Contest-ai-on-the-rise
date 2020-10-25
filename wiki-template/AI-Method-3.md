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

![f4]

![f5]

It can be noticed that the weights for the features converges in a kind of gradient descent method, as the following image for 4 of the features used in the approximate Q-learning. A set of initial values which are believed to be the appropriate ones is selected to reduce the number of iterations to converge. 


[f1]: http://chart.apis.google.com/chart?cht=tx&chl=f(s,a) 
[f2]: http://chart.apis.google.com/chart?cht=tx&chl=f_1(s,a),f_2(s,a)\ldots,f_n(s,a)
[f3]: http://chart.apis.google.com/chart?cht=tx&chl=Q(s,a)=\sum_{n=1}^{\infty}f_i(s,a)w_i
[f4]: http://chart.apis.google.com/chart?cht=tx&chl=V(s)=w_1f_1(s)%2Bw_2f_2(s)%2B...%2Bw_nf_n(s)
[f5]: http://chart.apis.google.com/chart?cht=tx&chl=G(s,a)=w_1f_1(s,a)%2Bw_2f_2(s,a)%2B...%2Bw_nf_n(s,a)


![](https://i.imgur.com/Zhj0iHG.png)

[Back to top](#table-of-contents)

### Trade-offs  

#### *Advantages*  

1. Simplifies the analysis in just a set of few features
2. Reduces the computational time to select best action to be taken in each state
. Allows generalisation for similar and/or univisited states


#### *Disadvantages*

1. A set of features is required, with specific domain-knowledge that represent clearly the different states
2. A clear reward has to be set properly, if not the agent might prefer accumulating the small rewards
3. Reward might not be linear

[Back to top](#table-of-contents)

### Future improvements  

1. Improve the score function 
2. Given that the reward function might not have a linear behavior, a different approach has to be taken. One of the option is Deep Q-Learning which will help add non linearity to the function

[Back to top](#table-of-contents)
