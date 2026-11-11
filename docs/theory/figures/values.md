# Measured values

Written by `make theory-figs` (scripts/theory_figs.py) from the domain itself. Do not edit by hand.
The last column is the relative error; where the theory column is 0 it is the absolute value.

| id | what is measured | measured | theory | error |
|---|---|---|---|---|
| `turn-cycle` | a tile after four quarter-turns equals the tile it started as (1 = equal) | 1 | 1 | 0.00e+00 |
| `turn-ports` | ports of a north-east corner after one turn are east and south (1 = yes) | 1 | 1 | 0.00e+00 |
| `turn-distinct-corner` | different port sets among the four orientations of a corner (theory 4) | 4 | 4 | 0.00e+00 |
| `turn-distinct-bar` | the same for a straight bar (theory 2: it repeats after two turns) | 2 | 2 | 0.00e+00 |
| `turn-distinct-cross` | the same for a cross (theory 1: every turn looks the same and still costs a move) | 1 | 1 | 0.00e+00 |
| `orientation-rejected` | of four values outside 0..3 or not whole numbers, how many are refused (theory 4) | 4 | 4 | 0.00e+00 |
| `connect-example-dark` | lamp powered in the documented one-row example before the turn (theory 0) | 0 | 0 | 0.00e+00 |
| `connect-example-lit` | lamp powered after one turn of the bar (theory 1) | 1 | 1 | 0.00e+00 |
| `connect-one-sided` | lamp powered when the middle wire has no port towards the source (theory 0) | 0 | 0 | 0.00e+00 |
| `connect-no-wrap` | lamp powered when source and lamp point off opposite ends of the row (theory 0) | 0 | 0 | 0.00e+00 |
| `connect-cycle` | tiles powered in the 2 x 3 board with a cycle (theory 4: the loop, not the lamp) | 4 | 4 | 0.00e+00 |
| `connect-island` | tiles powered when a connected wire-lamp pair is not joined to the source (theory 1: the source only) | 1 | 1 | 0.00e+00 |
| `starter-wires` | wire tiles on the starter board (the rest: one source, two lamps) | 6 | 6 | 0.00e+00 |
| `starter-powered-start` | tiles powered at the start (theory 1: the source alone) | 1 | 1 | 0.00e+00 |
| `starter-solved` | state after the four rotations (1 = solved) | 1 | 1 | 0.00e+00 |
| `starter-events` | events those four rotations returned (theory 5: four TileRotated and one BoardSolved) | 5 | 5 | 0.00e+00 |
| `starter-solved-events` | of them, BoardSolved events (theory 1: only on the first transition) | 1 | 1 | 0.00e+00 |
| `starter-moves` | move numbers carried by the TileRotated events run 1..4 (1 = yes) | 1 | 1 | 0.00e+00 |
| `starter-combos` | combinations of orientations of the six wires, enumerated (theory 4^6) | 4096 | 4096 | 0.00e+00 |
| `starter-solutions` | of them, combinations that power both lamps | 32 | 0 | 3.20e+01 |
| `starter-minimum` | fewest rotations among them (the budget is 6) | 4 | 0 | 4.00e+00 |
| `starter-within-budget` | combinations reachable within the budget of six rotations | 7 | 0 | 7.00e+00 |
| `starter-shortest-play` | shortest sequence of legal rotations that solves the board, by breadth-first search through the aggregate (the same as the minimum above) | 4 | 4 | 0.00e+00 |
| `last-move-wins` | state when the only move of a budget of one solves the board (1 = solved, not exhausted) | 1 | 1 | 0.00e+00 |
| `budget-exhausts` | state after two unsolving moves of a budget of two (1 = exhausted) | 1 | 1 | 0.00e+00 |
| `terminal-refuses` | a rotation on an exhausted board raises BoardFinished (theory 1) | 1 | 1 | 0.00e+00 |
| `terminal-moves` | moves used after that refusal (theory 2: nothing was added) | 2 | 2 | 0.00e+00 |
| `invalid-refused` | rotations of the source, the two lamps and a cell off the board that are refused (theory 4) | 4 | 4 | 0.00e+00 |
| `invalid-free` | moves used after those four refusals (theory 0) | 0 | 0 | 0.00e+00 |
| `board-rejected` | malformed boards refused: no source, two sources, no lamp, zero budget, a tile off the board (theory 5) | 5 | 5 | 0.00e+00 |
