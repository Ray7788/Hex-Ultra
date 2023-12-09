from Hex import HexBoard
import config as cfg
import numpy as np
import random
import copy


class StupidAgent:
    """
    agents that can only make random decisions
    """

    def __init__(self, colour, board=None, mode="auto"):
        # initialize colour of the agent
        self.colour = colour
        # initialize a board maintained by the agent itself
        self.board = copy.deepcopy(board) if board is not None else HexBoard(cfg.BOARD_ROW, cfg.BOARD_COL)
        # initialize meshgrid for the user
        xs, ys = np.meshgrid(np.arange(cfg.BOARD_COL), np.arange(cfg.BOARD_ROW))
        meshgrid = np.stack([xs, ys], axis=0)
        self.meshgrid = meshgrid[:, self.board.available_positions].T.tolist()
        # initialize the decision of swap
        self.swap = False
        self.mode = mode

    def manual_decision(self):
        # obtain decision from the user
        x = input(f"{self.colour}: type in x: ")
        y = input(f"{self.colour}: type in y: ")
        return int(x), int(y)

    def random_decision(self):
        if self.mode == 'manual':
            x, y = self.manual_decision()
        else:
            # make a random decision
            x, y = random.choice(self.meshgrid)
        # update the agent's board
        self.board.drop_stone(x, y, self.returnColour())
        self.meshgrid.remove([x, y])
        return x, y

    def updateBoard(self, x, y, colour):
        """
        update the board after another player dropped a stone
        """
        self.board.drop_stone(x, y, colour)
        self.meshgrid.remove([x, y])

    def respondToSwap(self):
        """
        give a response to the simulator about whether to swap sides
        """
        self.swap = random.choice([True, False])
        return self.swap

    def returnColour(self):
        """
        return the actual colour taken by the agent
        """
        if self.swap:
            return "red" if self.colour == "blue" else "blue"
        else:
            return self.colour