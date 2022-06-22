import copy

##############################################################################
class CSP:
    """
    A class to represent a weighted CSP (Constrained Satisfaction Problem).

    """
    def __init__(self):
        # number of variables in the CSP
        self.numVariables = 0
        # a list containing the name of the variables
        self.variables = []
        # a dict for storing the domain values for each of the variables.
        # key=variable name, value=list of domain values that the variable
        # can take.
        self.values = {}

        # a dict to hold the unary factors of the variables.
        # self.unaryFactors[var] will hold a factor table (python dict)
        # representing the weight distribution of the variables values
        # self.unaryFactors[var][val] = weight of value val for variable var
        # when more than one factor applies, they are 'aggregated' using
        # element-wise multiplication
        self.unaryFactors = {}

        # a dict containing the information about the cross-weight of val1
        # of var1 and val2 of var2.
        # self.binaryFactors[var1][var2][val1][val2] = weight of assigning
        # var1 the value val1 and var2 the value val2
        self.binaryFactors = {}

    def add_variable(self, var, domain):
        """
        Add a new variable to the CSP
        """

        if var in self.variables:
            raise Exception(f"Variable name already exists: {str(var)}")

        self.numVariables += 1
        self.variables.append(var)
        self.values[var] = domain
        self.binaryFactors[var] = {}

    def get_neighbor_variables(self, var):
        """
        Returns a list of neighboring variables to variable var according to
        the factor graph described through binaryFactors.
        """
        return list(self.binaryFactors[var].keys())

    def add_unary_factor(self, var, factor_func):
        """
        Add a unary factor to variable var according to function
        factor_func(val) for every value val in var's domain.
        If variable var already have a unary factor, the two functions will
        be merged using element-wise multiplication.
        """
        factor = {val: factor_func(val) for val in self.values[var]}

        # if self.unaryFactors[var] is None:
        if var not in self.unaryFactors:
            self.unaryFactors[var] = factor
        else:
            # if there's already a unary factor for that variable, add by
            # element-wise multiplication
            self.unaryFactors[var] = {val: self.unaryFactors[var][val] *
                                           factor[val] for val in factor}

    def add_binary_factor(self, var1, var2, factor_func):
        """
        Add a binary factor for the variables var1 and var2 according to
        function factor_func(val1, val2).
        If the two variables already have a binary factor between them,
        the two factors will be merged using element-wise multiplication.
        """
        if var1 == var2:
            raise Exception(
                f"Error: trying to add a binary factor with the same "
                f"variable {va1r}")

        newTable1 = {val1: {val2: factor_func(val1, val2)
                            for val2 in self.values[var2]
                            }
                     for val1 in self.values[var1]
                     }
        self._update_binary_factor_table(var1, var2, newTable1)

        newTable2 = {val2: {val1: factor_func(val2, val1)
                            for val1 in self.values[var1]
                            }
                     for val2 in self.values[var2]
                     }
        self._update_binary_factor_table(var2, var1, newTable2)

    def _update_binary_factor_table(self, var1, var2, table):
        """
        Internal helper function.
        Updates the binary factor table according to the new factor function.
        If variables already 'neighbors', add the new factor using element-wise
        multiplication.
        """

        if var2 not in self.binaryFactors[var1]:
            self.binaryFactors[var1][var2] = table

        else:
            for v1 in table:
                for v2 in table[v1]:
                    assert v1 in self.binaryFactors[var1][var2]
                    assert v2 in self.binaryFactors[var1][var2][v1]
                    self.binaryFactors[var1][var2][v1][v2] *= table[v1][v2]

##############################################################################
class Backtracking:
    """
    A backtracking algorithm for solving weighted CSP.
    Using Most Constraint Variable (MCV) heuristic and/or Arc Consistency
    enforcement (AC3 algorithm) as option.

    Usage:
    alg = Backtracking()
    alg.solve(mcv=True, ac3=True)
    alg.print_stats()

    optimalAssignment = alg.optimalAssignment
    """
    def reset_results(self):
        """
        Keep track of various statistics of the CSP solver.
        Kind of __init__(), but can be 'recalled' to enable repeated solver
        calls.
        """
        self.numOptimalAssignments = 0
        self.optimalWeight = 0
        self.optimalAssignment = {}

        self.numAssignments = 0

        # keep track of number of calls to self.backtrack() to compare
        # complexity when using mcv/ac3.
        self.numOperations = 0

        self.firstAssignmentNumOperations = 0

        self.allAssignments = []

    def print_stats(self):

        if self.optimalAssignment:
            print(f"Found {self.numOptimalAssignments} optimal assignments "
                  f"with weight {self.optimalWeight} in {self.numOperations} "
                  f"operations")
            print(f"First assignment took "
                  f"{self.firstAssignmentNumOperations} operations")
        else:
            print("No solution was found")

    def get_delta_weight(self, assignment, var, val):
        """
        given a partial assignment and a proposed variable var with value
        val, return the marginal weight expanding the assignment with
        variable var with value val.
        :param assignment: a dict containing the previously assigned
        variables and their values. (key=variable name, value=assigned value)
        :param var: name of proposed variable to be assigned.
        :param val: value to be assigned to variable var
        :return: the marginal factor to be multiplied by current assignment
        total weight when expanding it to include variable var with value val.
        """
        # make sure variable var not already in assignment
        assert var not in assignment

        w = 1.0
        if var in self.csp.unaryFactors.keys():
            w *= self.csp.unaryFactors[var][val]
            if w == 0: return 0
        for var2, factor in self.csp.binaryFactors[var].items():
            if var2 not in assignment: continue
            val2 = assignment[var2]
            # cumulative weight with all assigned variables
            w *= factor[val][val2]
            # return the first time we see in-alignment with other assigned
            # variables
            if w == 0: return 0

        return w

    def solve(self, csp, mcv=True, ac3=True):
        """
        Solves the given weighted CSP using optional heuristics (mcv / ac3).
        This function will keep searching for satisfied assignments (for
        enabling the 'weighted CSP'.
        Results are stored the initialization (/reset_results) variables.

        :param csp: A weighted CSP
        :param mcv: True for using the Most Constraint Variable heuristic.
        :param ac3: True for applying arc-consistency (AC-3).
        """
        self.csp = csp
        self.mcv = mcv
        self.ac3 = ac3
        self.reset_results()

        self.domains = {var: list(self.csp.values[var])
                        for var in self.csp.variables
                        }

        self.backtrack({}, 1)

    def backtrack(self, assignment, weight):
        """
        Preforming the backtracking algorithm to find all valid assignments
        to the factor graph (weigted CSP).

        :param assignment: A dict of current assignment. Entries include
        only assigned variables. key= name of assigned variable; value=
        assigned value to the variable
        :param weight: The weight of the given assignment. To be updated
        with get_delta_weight().
        :return:
        """
        self.numOperations += 1

        # first, handle complete assignment
        if len(assignment) == self.csp.numVariables:
            # final assignment
            self.numAssignments += 1
            newAssignment = {var: assignment[var] for var in
                             self.csp.variables}
            self.allAssignments.append(newAssignment)

            # update statistics
            if self.numOptimalAssignments == 0 or weight > self.optimalWeight:
                if weight == self.optimalWeight:
                    self.numOptimalAssignments += 1
                else:
                    self.numOptimalAssignments = 1
                self.optimalWeight = weight

                self.optimalAssignment = newAssignment
                if self.firstAssignmentNumOperations == 0:
                    self.firstAssignmentNumOperations = self.numOperations

            return

        # if partial assignment, get next variable. The first unassigned if
        # mcv is disables.
        var = self.get_unassigned_variable(assignment)
        values = self.domains[var]

        for val in values:
            deltaWeight = self.get_delta_weight(assignment, var, val)
            if deltaWeight > 0:
                assignment[var] = val

                if self.ac3:
                    # perform arc-consistency check

                    # keep original copy of domains (ac-3 alters domain when
                    # 'checking')
                    domainsCopy = copy.deepcopy(self.domains)

                    # temporary update domains of variable var to the
                    # proposed value val
                    self.domains[var] = [val]

                    # enforce arc-consistency on neighbors (and their
                    # neighbors, etc (updating self.domains in the process,
                    # hopefully shrinking number of possible values to
                    # unassigned variables.
                    self.arc_consistency(var)

                    # recursively call backtrack on possible children
                    self.backtrack(assignment, weight * deltaWeight)

                    # restore unassigned variables' domain
                    self.domains = domainsCopy

                else:
                    # arc consistency is disabled
                    self.backtrack(assignment, weight * deltaWeight)

                del assignment[var]

    def get_unassigned_variable(self, assignment):
        """
        Given a partial assignment, return a variable to be assigned next.

        In case of mcv enabled (=True), count number of possible valid values
        of each of the variables (among those that are consistent with
        current assignment-- weight>0) and return the variable with the
        least number of these values.
        """
        if self.mcv:
            result = []

            for var in self.csp.variables:
                if var not in assignment:
                    count = sum(self.get_delta_weight(assignment, var,
                                                      val) != 0
                                for val in self.domains[var]
                                )
                    result.append((count, var))

            return min(result, key=lambda t: t[0])[1]

        else:
            for var in self.csp.variables:
                if var not in assignment:
                    return var

    def arc_consistency(self, var):
        """
        Apply arc consistency on the neighbors of variable var.
        Note variable var is already assigned a value.

        Using a queue, each of the variables with updated domain (with some
        values being removed), the algorithm runs as deep as possible to
        enforce the constraint.
        """
        queue = [var]

        while queue:
            var1 = queue.pop(0)
            neighbors = self.csp.get_neighbor_variables(var1)

            for var2 in neighbors:
                inconsistent = []
                for val2 in self.domains[var2]:
                    CONSISTENT = False
                    # find a consistent value in var1's domain with val2
                    for val1 in self.domains[var1]:
                        if self.csp.binaryFactors[var1][var2][val1][val2] != 0:
                            CONSISTENT = True
                            break

                    if not CONSISTENT:
                        # do not alter domains until end of the for loop (
                        # for not messing-up with the condition)
                        inconsistent.append(val2)

                if inconsistent:
                    # remove inconsistent values from domain
                    for val2 in inconsistent:
                        self.domains[var2].remove(val2)

                    # since the domain of var2 has changed, add to queue for
                    # further exploration of consistency changes
                    queue.append(var2)

