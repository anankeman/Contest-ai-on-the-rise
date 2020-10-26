# AI Method 1 - A start Approach


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
#### Offensive Agent
Initially, several approaches were attempted in order to design the most effective offensive agent possible. Each member of the group separately tried to design their own agent as a starting point, and used slightly different implementations of the algorithm:
The different strategies applied were as follows:

1) Abstracting the problem and solving with A*

An abstraction of the Pac Man game state was used in order to try and limit calls to the program running the game, which had significant computational cost. For example, if the agent was finding food, the goal was framed as going to the nearest food, and the state was represented as the position and the remaining food. 

An A* search using maze distance was run on this game state each turn while assuming all entities were static except the agent making the next move. Taking a simple abstraction of the game state, and updating this abstraction was effective in reducing computational complexity and allowed a path to be found to the nearest food quickly. 

2) Following an optimal path from initialization

In the 15 first seconds of the initial state, A* using maze distance was run to give an optimal path for the offensive agent to eat all the food. Then, in subsequent steps, this plan was followed without updating at each turn. Ghosts were dealt with by having the agent run back to the closest point in it’s own territory. After running away, the agent would go back to the last point of the plan that was successfully followed, and continue following the same plan. The Heuristic used was simple the shortest path to every food for every closest food (iterative). This was discarded because of its simplicity and inflexibility. 

3) Finding an optimal path each turn with a single goal

A* was run search every turn on the full game state, but stopping after N iterations to limit computational complexity, returning only the first step in latest path considered. A more complex heuristic was implemented, using the weighted combination of the distance to the closest food, the distance to the closest capsule, and the inverse distance to the closest ghost to discourage the agent from moving close to the ghosts. The weights were change according to a goal set selected by a decision tree: If a ghost is in sight the weight to closest food is set to zero, the distance to the closest point of the border is set to 1, and distance to the closest capsule is set to 1. Else the distance to capsule is set to 1. In this way it was possible to modify the agent’s behaviour simply based on the heuristic. 

4) Finding an optimal path each turn with multiple goals

A similar approach was tested as in 3, but instead of only varying the heuristic, goals were also changed every turn as well, according to a decision tree. The tree consisted of several decisions based on the current state. First, the tree check if any ghost is visible and not scared, in which case the goal was to run away by either getting back to it’s own territory or eating a capsule. If there were no ghosts in sight, or the ghost was scared, the goal was to eat food. And if the agent had eaten food and there was no food nearby, the goal was to get back to their side to score points. Both the heuristic and goal were updated for each different outcome of the decision tree in this strategy. 

#### Defensive Agent

The defensive agent was implemented using multiple goals with a different heuristic for each different goal. This followed a basic tree structure, where the goals with higher priority were further up the tree, and the goal was selected according to the tree logic. The primary goal of the defender was to try to chase any enemies that were attacking. If no enemies were in sight, the agent would patrol the border, and if there was a food eaten on the defender's side, the defender would go towards the food to try and cut the enemy off. The basis for the defensive agent strategy was the ability to implement a more complex strategy encoded in the decision tree. 

The first strategy implemented was to attempt to pre-empt the opponents move by going to the ‘middle’ of the food, or the median food point in the grid. This was decided to be ineffective as the defensive agent may have ended up getting stuck behind a wall, making it unable to defend even if at a close manhattan distance. A patrol function was implemented second, which seemed to work more effectively as it could pick up enemies more easily by covering more ground. 

The defender also had to try and avoid being eaten when scared, and the strategy chosen was to try and remain within a small radius of the enemy at all times without going too close. 


#### Optimization and Troubleshooting

The various approaches for the offensive agent were then assessed for the best starting point: 
1) In the first approach, taking a simple abstraction of the game state, and updating this abstraction was effective in reducing computational complexity and allowed a path to be found to the nearest food quickly. However it proved to be ineffective as it didn’t have enough detail in the representation of the game state and taking into account ghost movement more dynamically was necessary. Additionally, it made a bulky program where every goal had to be framed as a new problem. 
2) The second approach was abandoned as although at the start the plan was optimal, the further away from the next step the agent moved or was chased, the further from optimal the plan became. There was also a large overhead in calculating the optimal plan at the start, and it was not certain that 15 seconds was sufficient with all mazes in addition to other calculations. 
3) The third approach worked well, but had erratic behaviour in some situations because it relied only on the heuristic, But more importantly, as in most scenarios the algorithm was truncated when reaching the maximum number of recursions, returning a suboptimal decision, taking erratical behavior which was critical in cirtuntances such as running away.  
4) The fourth strategy was ultimately chosen optimization for the offensive agent, as the behaviour was more clearly mapped out by a heuristic function which balanced the various goals, and this gave the agent a higher degree of flexibility, rather than purely relying on the heuristic, which gave a fuzzy decision boundary and sometimes resulted in erratic behaviour.
[Back to top](#table-of-contents)

### Application

#### Offensive Agent
As an A* approach with a several goals was chosen, a large amount of testing was done to try and select an appropriate goal and heuristic.

##### Goals
The goals used for the offensive agent were as follows:
1) Finding food: if no enemies were within range, the agent would attempt to eat as much food as possible until an enemy came into range. 
2) Finding capsule: if an enemy is in range and the capsule is closer than the border, the agent would try and eat the capsule. 
3) Finding border: if an enemy is in range and the border was closer than a capsule, or there were no capsules, the agent would try and return to its side.
4) Patrol: if the agent was stuck on the border with an enemy on the other side, it would try and find a new point to attack from.

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
The distance from ghosts was taken into account in all heuristics to ensure the agent didn't run into an enemy.
This approach allowed the agent to set up the overall problem as several sub problems based on the goal. 

##### Issues:
The main issues facing the approach chosen were that the more complex decision tree used to try and capture optimal behaviour, the more it misbehaved in unexpected situations. It was difficult to encode every decision in the tree, and this caused problems. 
[Back to top](#table-of-contents)

##### Trade-offs  
*Advantages*  
1) The decision tree was quite easy to program and adjust to design choices. 
2) The strategy was fast computationally and so this gave the freedom to change it however was necessary without having to worry about time outs.
3) The strategy was easy to troubleshoot as it was interpretable
4) No training was required

*Disadvantages*
1) It wasn't that intelligent. Given it's a fairly simple strategy, there was always a trade off between the goals, unless an extremely comprehensive decision tree was implemented that accounted for every situation possible. It was found that the more complexity the decision tree had, the worse the agent performed, and so this would have required a huge amount of optimization and fine tuning in all the parameters, goals, heuristics, and weights for every aspect of the strategy, which may have been suitable for some maps over others, and may not have even resulted in an increase in performance. Therefore, the most general approach possible was taken. 

2) As it was simple, any issues in the logic caused a huge performance defecit. 
[Back to top](#table-of-contents)

#### Defensive agent: 
The defensive agent wasn't varied as much, as it seemed to have a fairly robust strategy, and the A* strategy implemented early on was adopted for competition. 

##### Goal:
The goal state in the defender consisted of one of the following:
1)	If the goal state was ‘patrol’, then two points were selected upon start-up that represented the ‘top’ and the ‘bottom’. These points were alternated upon achieving either as the goal state. 
2)	If the goal state was ‘get invaders’ then the goal was chosen to be whatever the enemy’s position was. 
3)	If the goal state was ‘get invaders scared’ the goal state was a distance of 2 from the invader. 
4)	If the goal state was ‘go centre’ the defender would reset to resume patrol
The heuristic used in all these cases was the maze distance to the enemy. 

##### Issues:
The issue became that although many branches were programmed into the decision tree, the strategy was quite inflexible, and it was an all or nothing response. If there was an agent nearby on the border, the defender would get stuck, or go into a loop, which clearly is counter productive to the strategy. 

This resulted in a lot of troubleshooting to improve the decision boundaries in the tree. 

Ultimately the problem was the agent being out of position, and this was difficult to overcome, as it could only act on enemies that were seen. 

##### Trade-offs
*Advantages*
1) The strategy was fast computationally.
2) The strategy was robust and easy to understand.
3) The strategy worked for most cases where there was one offensive agent, and when the map allowed the agent to be in position most of the time. 

*Disadvantages*
1) Inflexible
2) In multi attacker situation, was unable to handle both and so became very ineffective
3) Often out of position on large maps
[Back to top](#table-of-contents)

### Future improvements
The obvious improvements would be to implement a more flexible and dynamic strategy using another technique that wasn't so simple. 

However, using A* as a basis, one possible improvement is to mix the offensive and defensive strategy to give a more flexible overall approach, where both agents either go on the offensive or defend based on their positioning in relation to the enemies, which would overcome problems with two attacking agents. Another strategy that would be a variation of this is to try and switch the strategy over periodically to give both agents a chance to attack and defend. 

[Back to top](#table-of-contents)
