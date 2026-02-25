# Chess Engine - University Final Project

Python chess engine implementation with `python-chess` library.



#### Evaluation function
Static evaluation funciton for a given chess board state. It calculates:
- material balance based on positional square tables
- pieces' mobility and attacks
- pawn structures
    * rewards passed pawns
    * punishes isolated and doubled pawns
 
It uses tapered evaluation formula to distinguish between middle and end-game

#### Search algorithm
- order moves to explore the most promising lines first
    - pawn promotions and captures come first with `MVV - LVA` (Most Valuable Victim - Least Valuable Aggressor) formula
- move ordering speeds up `minimax` algorithm with `alpha-beta pruning`, cutting off nonsensible moves
- upon reaching the depth limit, it runs `quiescence` search to avoid the horizon effect (stopping while trading chess pieces)

---
### How to run
Prerequisites: Python3; libraries: python-chess, Pygame.

To play against the engine in UI clone the repository and run `UI.py` file. The pygame window will pop up.

To play in a console mode, run `main.py`.

To run tests against stockfish, install it on your machine and edit engine's path in the test file.

---
#### Test results
Tests against stockfish have been run for various chess position scenarios to see how often my engine agrees with the stockfish.  
Test results for each version can be viewed in the `test/` folder.



## Future improvements
Improve the search efficiency to improve nodes per soconds:
1. Transposition tables (allow IDS to reuse work across depths)
2. Killer move heuristics
3. History heuristics
4. Null move pruning
5. Late move reductions
6. Evaluaations caching

Most immediate clear improvement will happen with implementing transposiiton tables


---
**version 1.0** - basic evaluator (material + PST)  
**version 1.1** - added mobility bonuses  
**version 1.2** - added pawn structure parameters  
**version 1.3** - added tempo bonus (+15 centipawns)  
**version 2.0** - added search with move ordering, quiescence based on minimax with alpha-beta pruning 