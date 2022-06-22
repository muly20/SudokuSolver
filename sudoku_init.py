import math
from util import CSP

##############################################################################
class SudokuCSPConstructor:
    """
    A constructor of A Sudoku pazzle.
    """
    def __init__(self, sudoku):
        """
        Given a sudoku initialization object (containing the size as well as
        the initial (partial) grid values.
        """
        self.size = sudoku.get_size()
        self.init_setup = sudoku.get_init_dict()

    def add_variables(self, csp):
        """
        Given a CSP, add the Sudoku variables.
        The Soduko variables are defined as each of the grid cells, including
        the initially assigned.

        Variable name will be its 2D coordinates in a tuple structure,
        with each index, as well as the variable's domain values, runs from
        1 to |grid size|.
        """
        for i in range(1, self.size + 1):
            for j in range(1, self.size + 1):
                csp.add_variable((i, j), domain=list(range(1, self.size + 1)))

    def add_init_constraints(self, csp):
        """
        Apply the constraints given by the grid initialization values. Each
        of these variables can only be assigned a single value.
        """
        for loc, value in self.init_setup.items():
            assert type(value) == int and 0 < value <= self.size

            # factor_func: return 1 if val==value else 0
            csp.add_unary_factor(loc, lambda x: x == value)

    def add_sudoku_constraints(self, csp):
        """
        Apply the constraints of the Sudoku game: each row, each column and
        each consecutive square box contains |grid size| unique numbers.
        """
        # each variable in a given row should have a unique value
        for row in range(1, self.size + 1):
            for col1 in range(1, self.size):
                for col2 in range(col1 + 1, self.size+ 1):
                    csp.add_binary_factor((row, col1), (row, col2),
                                          lambda val1, val2: val1 != val2)
        # each variable in a given column should have a unique value
        for col in range(1, self.size + 1):
            for row1 in range(1, self.size):
                for row2 in range(row1 + 1, self.size + 1):
                    csp.add_binary_factor((row1, col), (row2, col),
                                          lambda val1, val2: val1 != val2
                                          )

        # each variable in a given box should have a unique value
        box_size = int(math.sqrt(self.size))
        for box_i in range(box_size):
            for box_j in range(box_size):
                # iterate over rows and columns within the box
                locations = [(i, j)
                             for i in range(box_i * box_size + 1,
                                            (box_i + 1) * box_size + 1)
                             for j in range(box_j * box_size + 1,
                                            (box_j + 1) * box_size + 1)
                             ]
                for p in range(len(locations) - 1):
                    for q in range(p + 1, len(locations)):
                        var1 = locations[p]
                        var2 = locations[q]
                        csp.add_binary_factor(var1, var2,
                                              lambda val1, val2: val1 != val2)

    def get_csp(self):
        """
        Initialize the CSP according to the Sudoku size, rules and initial
        values.
        """
        csp = CSP()
        self.add_variables(csp)
        self.add_init_constraints(csp)
        self.add_sudoku_constraints(csp)

        return csp

##############################################################################
class SudokuInit:
    """
    A Sudoku object, defined by a given size and an initialization grid.
    Assumes a text file ('initFilePath') that contains first a single
    integer as the size of the grid (should be 9, but could be also any
    number that satisfies sqrt(size)=integer), followed by three
    space-separated integers corresponding to the initial grid values:
    index i, index j, value
    """
    def __init__(self, initFilePath):

        self.size = None
        self.initValues = {}

        self._load_file(initFilePath)

    def _load_file(self, path):
        for line in open(path):
            if line[0] == '#': continue

            if self.size is None:
                self.size = int(line.strip('\n'))
                assert math.sqrt(self.size).is_integer()
            else:
                i, j, v = list(map(int, line.strip('\n').split(' ')))
                self.initValues[(i, j)] = v

    def print_initial_grid(self):
        grid = [[0 for _ in range(self.size)] for _ in range(self.size)]

        for (i, j), v in self.initValues.items():
            grid[i - 1][j - 1] = v

        print(f"Initial Board of size {self.size}:")
        for row in grid:
            print(row)

    def get_init_dict(self):
        return self.initValues

    def get_size(self):
        return self.size