## Analysis

A set of approaches were developed tackling the Defence and Attack. Taking as a basis the following approaches:

Defence
* Baseline
* Defence method

Attack
* Baseline
* A star + heuristic
* Minimax
* Approximate Q Learning

The idea is to determine which is the best combination between Defence approach and Attack approach among the different combinations, running 100 simulations with random mazes. 

First, an Attack approach is set as base (A star) and the two different Defence approaches are tested to select the one with the best performance. 
* Team 1 – Defence:  Baseline + A star
* Team 2 – Defence:  Defence method + A star

![](https://i.imgur.com/7aEGE6R.png)

The best Defence strategy is Defence method, beating 73 times the baseline, with only 6 defeats and remaining 21 ties.

Then, the best Defence approach selected from the above is set as base (Defence method), and the 4 different Attack approaches are tested.
* Team 1 – Attack:  Defence method + Baseline
* Team 2 – Attack:  Defence method + A star
* Team 3 – Attack:  Defence method + Minimax
* Team 4 – Attack:  Defence method + Approximate Q Learning

![](https://i.imgur.com/9hTjIQu.png)

As it can be seen, the best Attack approach is A star (heuristic), with a big winning ratio against the other three methodologies, as well as a higher average score. Additionally, the three implemented approaches beat the Baseline Attack, and the MiniMax and Approximate Q-Learning with similar performance, only with a slightly difference in favour of the MiniMax approach.


## Challenges  

## Conclusions and Learnings
