import torch
from Hex import HexBoard
import config as cfg
import numpy as np
import random
import copy
import torch.nn.functional as F
import torch.nn as nn


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


class ResBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(ResBlock, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(),
            nn.Conv2d(in_channels=out_channels, out_channels=out_channels, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(out_channels)
        )

    def forward(self, x):
        y = self.conv(x)
        y = y + x
        y = F.relu(y)
        return y


class AlphaZeroNet(nn.Module):
    def __init__(self):
        super(AlphaZeroNet, self).__init__()

        # initialize input layer
        self.input = nn.Sequential(
            nn.Conv2d(in_channels=cfg.MEMORY_LENGTH * 2 + 2, out_channels=cfg.MIDDLE_CHANNEL, kernel_size=3, stride=1,
                      padding=1),
            nn.BatchNorm2d(cfg.MIDDLE_CHANNEL),
            nn.ReLU()
        )

        # initialize middle layers
        self.middle = nn.Sequential(
            ResBlock(cfg.MIDDLE_CHANNEL, cfg.MIDDLE_CHANNEL),
            ResBlock(cfg.MIDDLE_CHANNEL, cfg.MIDDLE_CHANNEL),
            ResBlock(cfg.MIDDLE_CHANNEL, cfg.MIDDLE_CHANNEL),
            ResBlock(cfg.MIDDLE_CHANNEL, cfg.MIDDLE_CHANNEL),
            ResBlock(cfg.MIDDLE_CHANNEL, cfg.MIDDLE_CHANNEL)
        )

        # initialize fully conencted layers
        self.MLP = nn.Sequential(
            nn.Linear(in_features=cfg.MIDDLE_CHANNEL * cfg.BOARD_COL * cfg.BOARD_ROW, out_features=256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(in_features=256, out_features=256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.5)
        )

        # initialize value head
        self.value_head = nn.Sequential(
            nn.Linear(in_features=256, out_features=256),
            nn.ReLU(),
            nn.Linear(in_features=256, out_features=1),
            nn.Tanh()
        )

        # initialize policy head
        self.policy_head = nn.Sequential(
            nn.Linear(in_features=256, out_features=256),
            nn.ReLU(),
            nn.Linear(in_features=256, out_features=cfg.BOARD_ROW * cfg.BOARD_COL + 1)
        )

    def forward(self, x):
        x = self.input(x)
        x = self.middle(x)
        x = self.MLP(x.reshape(x.size(0), -1))
        value = self.value_head(x)
        policy = self.policy_head(x)
        return policy, value


if __name__ == "__main__":
    from torchsummary import summary

    model = AlphaZeroNet()
    # model.cuda()
    summary(model, input_size=(2 * cfg.MEMORY_LENGTH + 2, cfg.BOARD_ROW, cfg.BOARD_COL), device='cpu')
