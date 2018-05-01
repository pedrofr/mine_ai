import numpy as np
from scipy import optimize as opt
from scipy import linalg as la
from lsqlin import cvxopt_to_numpy_matrix, lsqlin
from board import Board

class Player :

    def __init__(self, board) :

        self.board = board
        self.unknowns = {(y, x) for x in range(board.width) for y in range(board.height)}
        self.borders = []
        self.influencingTiles = {}
        self.classes = []
        self.P = np.zeros((board.height, board.width))

    def createClasses(self) :
        self.influencingTiles = {}

        for unknown in self.unknowns :
            self.influencingTiles[unknown] = self.board.getNeighbours(unknown) & frozenset(self.borders)

        s = set()
        for tileSet in self.influencingTiles.values() :
            s = s.union(tileSet)

        self.borders = list(s)

        classes = {}
        for k in self.influencingTiles :
            if self.influencingTiles[k] in classes :
                classes[self.influencingTiles[k]].add(k)
            else :
                classes[self.influencingTiles[k]] = {k}

        self.classes = list(classes.items())

        # print(self.influencingTiles)

    def resolveProbabilities(self) :
        A = np.zeros((len(self.borders) + 1, len(self.classes)))

        for y in range(len(self.borders)) :
            for x in range(len(self.classes)) :
                if self.borders[y] in self.classes[x][0] :
                    A[y][x] = len(self.classes[x][1])

        A[len(self.borders)] = [len(tileClass[1]) for tileClass in self.classes]

        b = np.array(self.board.getNumber(self.borders)) - np.array(self.board.getNeighbouringFlagsCount(self.borders))

        b = np.append(b, np.array([self.board.getRemainingMines()]))

        P, L, U = la.lu(A)
        y = la.solve(P@L, b)

        sol = opt.nnls(A, b)
        # sol = opt.nnls(U, y)
        p = sol[0]

        np.set_printoptions(precision=3, linewidth=1000)
        
        p[np.isclose(p, 0.0)] = 0.0
        p[np.isclose(p, 1.0)] = 1.0

        if np.any(p > 1):
            print(p)
            p = np.atleast_1d(cvxopt_to_numpy_matrix(lsqlin(A, b, lb=np.zeros(A.shape[1]), ub=np.ones(A.shape[1]), opts={'show_progress': False})['x']))
            p[np.isclose(p, 0.0, atol=0.005)] = 0.0
            p[np.isclose(p, 1.0, atol=0.005)] = 1.0
            print(p)

        for i in range(len(self.classes)) :
            for tile in self.classes[i][1] :
                self.P[tile] = p[i]

        print("A:\n", A)
        print("b:", b)
        print("u:\n", U)
        print("y:", y)
        print("p:", p)
        print("A:", A.shape)
        print("rest:", sol[1])
        print("P\n", self.P)
        print("hiddenGrid\n", self.board.hiddenGrid)

        if np.any(p > 1) :
            print("A", A)
            print("b", b)
            print("p", p)
            print("P", self.P)

            raise RuntimeError("p > 1")

    def makeMove(self) :
        min_value = self.P.min()

        min_positions = np.where(self.P == min_value)
        min_positions = {(min_positions[0][i], min_positions[1][i]) for i in range(len(min_positions[0]))}

        ones = np.where(self.P == 1.0)        
        ones = {(ones[0][i], ones[1][i]) for i in range(len(ones[0]))}

        self.board.flagTiles(ones)

        self.unknowns -= ones
        min_positions -= ones

        min_positions = list(min_positions)
        
        if min_positions :
            if min_value == 0.0 :

                print("Guess at", min_positions, "with probability", [self.P[position] for position in min_positions])

                try:
                    triedTiles = self.board.tryTiles(min_positions)

                    self.unknowns -= triedTiles
                    self.borders.extend(triedTiles)
                    for position in triedTiles :
                        self.P[position] = np.inf
                except :
                    raise

            else :
                probOfZero = []

                for position in min_positions :
                    neighbours = self.board.getNeighbours(position) | {position}
                    # print(neighbours)
                    probabilities = 1 - np.array([self.P[neighbour] for neighbour in neighbours])
                    # print(probabilities)
                    probOfZero.append(np.prod(probabilities))

                argmax_probOfZero = np.argmax(probOfZero)
                
                print("Guess at", [min_positions[argmax_probOfZero]], "with probability", min_value, "and probability of zero", probOfZero[argmax_probOfZero])

                try:
                    triedTiles = self.board.tryTiles([min_positions[argmax_probOfZero]])

                    self.unknowns -= triedTiles
                    self.borders.extend(triedTiles)
                    for position in triedTiles :
                        self.P[position] = np.inf
                except :
                    raise

        # print(self.borders)
        # print(self.unknowns)

    def makeMoveAt(self, positions) :

        print("Guess at", positions)

        try:
            triedTiles = self.board.tryTiles(positions)

            self.unknowns -= triedTiles
            self.borders.extend(triedTiles)
            for position in triedTiles :
                self.P[position] = np.inf
            
            print("Tried", triedTiles)

        except :
            raise

    def printP(self):
        print(self.P)