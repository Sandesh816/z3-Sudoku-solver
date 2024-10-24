import numpy as np
from z3 import Solver, Bool, And, Or, Not, Implies, sat, unsat
class SudokuSolver:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.solver = None
        self.variables = None
        self.rows = 9
        self.cols = 9
        self.possible_values = 9

    def create_variables(self):
        """
        Set self.variables as a 3D list containing the Z3 variables. 
        self.variables[i][j][k] is true if cell i,j contains the value k+1.
        """
        self.variables = np.empty((9,9,9), dtype = object)
        for i in range(self.rows):
            for j in range(self.cols):
                for k in range(self.possible_values):
                    self.variables[i][j][k] = Bool(f"b_{i}_{j}_{k+1}") #not sure syntax is correcy (check)


    def encode_rules(self):
        """
        Encode the rules of Sudoku into the solver.
        The rules are:
        1. Each cell must contain a value between 1 and 9.
        2. Each row must contain each value exactly once.
        3. Each column must contain each value exactly once.
        4. Each 3x3 subgrid must contain each value exactly once.
        """
        # first, let's make sure that each cell has at exactly one value assigned
        for i in range(self.rows):
            for j in range(self.cols):
                # for at least one number part
                self.solver.add(Or(*[self.variables[i][j][k] for k in range(self.possible_values)]))
                # for no more than one number part
                for k in range(self.possible_values):
                    for x in range(k + 1, self.possible_values):
                        self.solver.add(Not(And(self.variables[i][j][k], self.variables[i][j][x])))

        # Second, let's make sure that each number appears only once per row and col and subrectangles
        for k in range(self.possible_values):
            for i in range(self.rows):
                row_vars = []
                col_vars = []
                for j in range(self.cols):
                    row_vars.append(self.variables[i][j][k]) # each row onlu once
                    col_vars.append(self.variables[j][i][k]) # each col only once

                self.solver.add(Or(*row_vars))  # each row at least once
                self.solver.add(Or(*col_vars))  # each col at least once
                for a in range(self.cols):
                    for b in range(a + 1, self.cols):
                        self.solver.add(Not(And(self.variables[i][a][k], self.variables[i][b][k]))) # not twice in a row
                        self.solver.add(Not(And(self.variables[a][i][k], self.variables[b][i][k]))) # not twice in a col

            for sub_row in range(0, self.rows, 3):# 3,3,3
                for sub_col in range(0, self.cols, 3):
                    sub_vars = []
                    for i in range(3):
                        for j in range(3):
                            sub_vars.append(self.variables[sub_row + i][sub_col + j][k]) # classical sudoku

                    self.solver.add(Or(*sub_vars))  # at least once in a subrectangle
                    for a in range(9):
                        for b in range(a + 1, 9):
                            self.solver.add(Not(And(sub_vars[a], sub_vars[b]))) # not twice in a subrectangle



    def encode_puzzle(self):
        """
        Encode the initial puzzle into the solver.
        """
        for i in range(self.rows):
            for j in range(self.cols):
                if (self.puzzle[i][j] != 0): # if has a number assigned
                    self.solver.add(self.variables[i][j][self.puzzle[i][j] - 1] == True) # k = puzzle[i][j]-1

    def extract_solution(self, model):
        """
        Extract the satisfying assignment from the given model and return it as a 
        9x9 list of lists.
        Args:
            model: The Z3 model containing the satisfying assignment.
        Returns:
            A 9x9 list of lists of integers representing the Sudoku solution.
        Hint:
            To access the value of a variable in the model, you can use:
            value = model.evaluate(var)
            where `var` is the Z3 variable whose value you want to retrieve.
        """
        bools = [[[model.evaluate(self.variables[i][j][k]) for k in range(self.possible_values)] for j in range(self.cols)] for i in
                 range(self.rows)]
        toReturn = [[0 for _ in range(self.rows)] for _ in range(self.cols)]
        for i in range(self.rows):
            for j in range(self.cols):
                toReturn[i][j] = next((k + 1 for k in range(self.possible_values) if bools[i][j][k]), 0) # get the first true value

        return toReturn
    
    def solve(self):
        """
        Solve the Sudoku puzzle.
        
        :return: A 9x9 list of lists representing the solved Sudoku puzzle, or None if no solution exists.
        """
        self.solver = Solver()
        self.create_variables()
        self.encode_rules()
        self.encode_puzzle()
        
        if self.solver.check() == sat:
            model = self.solver.model()
            solution = self.extract_solution(model)
            return solution
        else:
            return None

def main():
    print("Attempting to solve:")
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    # puzzle = [
    #     [0, 2, 0, 6, 0, 8, 0, 0, 0], # 2,0,0
    #     [5, 8, 0, 0, 0, 9, 7, 0, 0],
    #     [0, 0, 0, 0, 4, 0, 0, 0, 0],
    #     [3, 7, 0, 0, 0, 0, 5, 0, 0],
    #     [6, 0, 0, 0, 0, 0, 0, 0, 4],
    #     [0, 0, 8, 0, 0, 0, 0, 1, 3],
    #     [0, 0, 0, 0, 2, 0, 0, 0, 0],
    #     [0, 0, 9, 8, 0, 0, 0, 3, 6],
    #     [0, 0, 0, 3, 0, 6, 0, 9, 0]#...0,0,9
    # ]
    for row in puzzle:
        print(row)

    solver = SudokuSolver(puzzle)
    solution = solver.solve()

    if solution:
        print("Solution found:")
        for row in solution:
            print(row)
    else:
        print("No solution exists.")

if __name__ == "__main__":
    main()
