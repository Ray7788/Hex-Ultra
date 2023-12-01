from Hex import HexBoard
import config as cfg
import numpy as np
import random
import copy
from MCTS import MCTS
from AlphaZeroMCTS import AlphaZeroMCTS


class Agent:
    """
    define agents controlled by the user manually
    """

    def __init__(self, colour, opposite_layer=None, board=None, mode="manual"):
        # initialize colour of the agent
        self.colour = colour
        # initialize the opposite player
        self.opposite_player = opposite_layer
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

    def make_decision(self, step, iterations=1000):
        """
        make a decision by naive MCTS
        step: step of the board up-till
        board: current board situation
        """
        if self.mode == 'manual':
            x, y = self.manual_decision()
        else:
            # initialize a MCTS
            mcts = MCTS(current_player=self, opposite_player=self.opposite_player, board=self.board, step=step)
            x, y = mcts.search(iterations=iterations)
        if x is not None and y is not None:
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
        return False  # self.swap

    def returnColour(self):
        """
        return the actual colour taken by the agent
        """
        if self.swap:
            return "red" if self.colour == "blue" else "blue"
        else:
            return self.colour


class AlphaZeroAgent:
    """
    define agents controlled by AlphaZero
    """

    def __init__(self, net, colour, opposite_layer=None, board=None, mode="manual"):
        self.net = net  # AlphaZero net
        self.net.eval()
        # initialize colour of the agent
        self.colour = colour
        # initialize the opposite player
        self.opposite_player = opposite_layer
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

    def make_decision(self, step, iterations=1000):
        """
        make a decision by naive MCTS
        step: step of the board up-till
        board: current board situation
        """
        if self.mode == 'manual':
            x, y = self.manual_decision()
        else:
            # initialize a MCTS
            mcts = AlphaZeroMCTS(net=self.net, current_player=self, opposite_player=self.opposite_player, board=self.board, step=step)
            x, y, distribution = mcts.search(iterations=iterations, returnDistribution=True)
        if x is not None and y is not None:
            # update the agent's board
            self.board.drop_stone(x, y, self.returnColour())
            self.meshgrid.remove([x, y])
        return x, y, distribution

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
        return False  # self.swap

    def returnColour(self):
        """
        return the actual colour taken by the agent
        """
        if self.swap:
            return "red" if self.colour == "blue" else "blue"
        else:
            return self.colour
