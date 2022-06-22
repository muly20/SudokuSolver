import util, sudoku_init
import sys
from optparse import OptionParser


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-m', '--mcv', dest='mcv', default='True',
                      help='Set Most Constraint Variable heuristic')
    parser.add_option('-a', '--ac3', dest='ac3', default='True',
                      help='Use Arc-Consistency-3 algorithm in backtracking')
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <e.g. sudoku_init_file.txt>")
        sys.exit(1)
    options, _ = parser.parse_args(sys.argv[2:])
    mcv = options.mcv=='True'
    ac3 = options.ac3=='True'

    initFilePath = sys.argv[1]
    sudoku = sudoku_init.SudokuInit(initFilePath)
    sudoku.print_initial_grid()

    cspConstructor = sudoku_init.SudokuCSPConstructor(sudoku)
    csp = cspConstructor.get_csp()

    alg = util.Backtracking()
    alg.solve(csp, mcv=mcv, ac3=ac3)
    alg.print_stats()

    if alg.optimalAssignment:
        print(f'Algorithm Congifuration:\n\tMCV: {mcv}\n\tAC3: {ac3}')
        print('Found Optimal Assignment:')
        grid = []
        for i in range(1, sudoku.get_size()+1):
            grid.append([])
            for j in range(1, sudoku.get_size()+1):
                grid[i-1].append(alg.optimalAssignment[(i,j)])
        for row in grid:
            print(row)
    else:
        print("Couldn't find any assignments.")