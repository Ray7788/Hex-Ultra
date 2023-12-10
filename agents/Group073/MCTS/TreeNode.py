from typing import List

from Board import Board
from Colour import Colour
from Board import Board
from Move import Move
from State import State


class TreeNode:
    def __init__(self, state: State, parent, action: Move, colour: Colour):
        self.state = state
        self.parent = parent
        self.action = action
        self.colour = colour

        self.children: List[TreeNode] = []  # a list which saves all children TreeNode
        self.numVisits = 0      # N(s, a) the number of times that action a has been taken from state s
        self.totalReward = 0.0      # Q(s, a) the total reward of all the simulations that started from state s and took action a

        # self.is_terminal = state.is_terminal()
        # self.isFullyExpanded = self.is_terminal

    def get_children(self):
        """Get all the children of the current node."""
        return self.children

    def get_possible_actions(self, colour: Colour, board_size: int) -> List[Move]:
        """
        Returns the list of all possible moves based on the current state(if it is coloured) of each tile.
        """
        all_moves: List[Move] = []  # Stores all moves
        choices: List[Move] = []  # Stores valid moves

        for i in range(board_size):
            for j in range(board_size):
                all_moves.append(Move(colour=colour, x=i, y=j))
                # tiles = self.state.get_tiles()
                # if tiles[i][j].colour is None:
                #     choices.append(Move(colour=colour, x=i, y=j))

        for m in all_moves:
            tile = self.state.board.get_tiles()[m.x][m.y]
            if tile.get_colour() is None:
                choices.append(m)

        return choices

    def __str__(self):
        """
        Returns a string representation of the node.
        TEST ONLY!!
        """
        s = []
        s.append("totalReward: %s" % (self.totalReward))
        s.append("numVisits: %d" % (self.numVisits))
        s.append("isTerminal: %s" % (self.is_terminal))
        s.append("possibleActions: %s" % (self.children))
        return "%s: {%s}" % (self.__class__.__name__, ', '.join(s))
