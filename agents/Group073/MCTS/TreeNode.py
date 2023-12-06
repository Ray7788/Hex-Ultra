from typing import List

from Board import Board
from Colour import Colour
from Board import Board
from Move import Move


class TreeNode:
    def __init__(self, state: Board, parent, action: Move, colour: Colour):
        self.state = state
        self.parent = parent
        self.action = action
        self.colour = colour

        self.children = {}  # a map from action to TreeNode
        self.numVisits = 0      # N(s, a)   the number of times that action a has been taken from state s
        self.totalReward = 0.0      # Q(s, a)   the total reward of all the simulations that started from state s and took action a

    def get_child(self, action: Move):
        """Get the child node of the current node by the action."""
        return self.children[action]

    def get_children(self) -> {}:
        """Get all the children of the current node."""
        return self.children.items()

    def __str__(self):
        """Returns a string representation of the node."""
        s = []
        s.append("totalReward: %s" % (self.totalReward))
        s.append("numVisits: %d" % (self.numVisits))
        s.append("isTerminal: %s" % (self.isTerminal))
        s.append("possibleActions: %s" % (self.children.keys()))
        return "%s: {%s}" % (self.__class__.__name__, ', '.join(s))
