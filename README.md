# SudokuSolver
A backtracking algorithm to solve a Sudoku puzzle modeled as a Constraint Satisfaction Problem (CSP).

Inspired by Stanford CS221's Course Scheduling Assignment, this is a backtracking algorithm for solving a Sudoku puzzle.
Although Sudoku is an unweighted factor graph, this algorithm is generalized for solving a weighted CSP.
Also implemented Most Constraint Variable heuristic as well as AC-3 algorithm (Arc-Consistency) for performance speed-up. These two significantly reduce the number of recursive calls to the backtracking procedure.

An initial Sudoku grid is given by a text file containing a signle integer representing the grid size (needs to be a square of an integer) followed by several lines each containing three space-separated integers, with the first two representing the 2D location of the cell and the third representing the cell's value. Each of the three integers needs to be in the inclusive range of 1 and grid_size.

command line arguments:
-m / --mcv False: for disabling mcv heuristic
-a / --ac3 False: for disabeling arc-consistency check

Usage:
python main.py sudoku3.txt
python main.py sudoku3.txt -m False -a False
