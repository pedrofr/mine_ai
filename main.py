from board import Board
from player import Player
import numpy as np

def main():
    board = Board(8, 8, {(2, 2), (2, 4), (4, 6), (6, 3), (5, 2)})
    player = Player(board)

    board.printHidden()

    i = 0
    # player.makeMoveAt([(4,4)])

    while True :
        i += 1
        print(i)
        player.createClasses()
        player.resolveProbabilities()
        player.makeMove()
        board.printGrid()

if __name__ == '__main__':
    main()