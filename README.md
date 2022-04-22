# Sudoku Solver
Sudoku Solver built in Python - uses pygame for GUI

- Allows you to play sudoku normally if you want to
- Mistake Checker - Checks every move for safety
- Auto Solver - Press Spacebar to solve automatically using a [backtracking approach](https://www.geeksforgeeks.org/sudoku-backtracking-7/) 
- Timer functionality
- Can read input from an input file  
*Change the `__INPUT_FILE__` variable in solver.py to change the input file path and name*
- Defaults to a predefined sudoku board if the input file is missing or is in invalid state

## How to build
1. Install pygame package if you do not already have it  
`pip install pygame`
2. Clone this repository or download as zip file
3. Run *solver.py* in your python IDE or in a command line terminal 
`python3 solver.py`
