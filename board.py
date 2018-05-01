import numpy as np
import random as rand

class Board :

    neighbours = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def __init__(self, height, width, mines) :
        self.height = height
        self.width = width

        self.hiddenGrid = np.zeros((height, width), dtype=np.int_)
        self.mines = set()
        self.grid = np.zeros((height, width), dtype=np.int_)

        self.flags = 0

        if isinstance(mines, int) :
            self.mine_num = mines
            while len(self.mines) < self.mine_num :
                pos = (rand.randrange(0, self.height), rand.randrange(0, self.width))
                self.mines.add(pos)
            
        elif isinstance(mines, (set, frozenset)) :
            self.mines = mines
            self.mine_num = len(self.mines)

        else :
            raise ValueError("mines argument must be an integer, a set or a frozenset")
        
        for mine in self.mines :
            self.hiddenGrid[mine] = -1

        for mine in self.mines :
            for neighbour in self.getNeighbours(mine) :
                if self.hiddenGrid[neighbour] != -1:
                    self.hiddenGrid[neighbour] += 1

    def printHidden(self) :
        print(self.hiddenGrid)

    def printGrid(self) :
        for y in range(self.height) :
            printable = ""
            for x in range(self.width) :
                if self.grid[y][x] == 0:
                    printable += '#'

                elif self.grid[y][x] == 1:
                    printable += str(self.hiddenGrid[y][x])

                else :
                    printable += '*'
    
            print(printable)


    def getNeighbours(self, position) :
        neighbours = set()
        for relativeNeighbour in self.neighbours :
            neighbour = tuple(map(sum, zip(relativeNeighbour, position)))
            if ((neighbour[0] >= 0) and (neighbour[0] < self.height)) and ((neighbour[1] >= 0) and (neighbour[1] < self.width)) :
                neighbours.add(neighbour)

        return frozenset(neighbours)

    def tryTiles(self, tiles) :
        nextTiles = set(tiles)
        triedTiles = set()

        grid = self.grid.copy()

        while nextTiles :
            currentTiles = set(nextTiles)
            for tile in currentTiles :
                if self.grid[tile] == 0 :
                    self.grid[tile] = 1
                    if self.hiddenGrid[tile] == -1 :
                        raise RuntimeError("killed at {} with state {} and {} neighbouring flags".format(tile, grid[tile], self.getNeighbouringFlagsCount([tile])))
                    elif self.hiddenGrid[tile] == 0 :
                        nextTiles |= self.getNeighbours(tile)
            nextTiles -= currentTiles
            triedTiles |= currentTiles

        return frozenset(triedTiles)


    def flagTiles(self, tiles) :
        for tile in tiles :
            if self.grid[tile] == 0 :
                self.grid[tile] = -1
                self.flags += 1

    def unflagTiles(self, tiles) :
        for tile in tiles :
            if self.grid[tile] == -1 :
                self.grid[tile] = 0
                self.flags -= 1

    def getNumber(self, tiles) :
        numbers = []
        for tile in tiles :
            if self.grid[tile] == 1 :
                numbers.append(self.hiddenGrid[tile])
                
        return numbers

    def getNeighbouringFlagsCount(self, tiles) :
        count = []

        for i in range(len(tiles)) :
            tile = tiles[i]
            count.append(0)
            for neighbour in self.getNeighbours(tile) :
                if self.grid[neighbour] == -1 :
                    count[i] += 1
        
        return count

    def getRemainingMines(self) :
        return self.mine_num - self.flags