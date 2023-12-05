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
        self.isTerminal = state.isTerminal()
        # TODO: simplify isTerminal and isFullyExpanded
        self.isFullyExpanded = self.isTerminal  # if the no1de is terminal, no need to expand
        self.numVisits = 0
        self.totalReward = 0.0

    def get_child(self, action: Move):
        """Get the child node of the current node by the action."""
        return self.children[action]

    def get_children(self) -> List[Node]:
        """Get all the children of the current node."""
        return self.children.values()

    def __str__(self):
        """Returns a string representation of the node."""
        s = []
        s.append("totalReward: %s" % (self.totalReward))
        s.append("numVisits: %d" % (self.numVisits))
        s.append("isTerminal: %s" % (self.isTerminal))
        s.append("possibleActions: %s" % (self.children.keys()))
        return "%s: {%s}" % (self.__class__.__name__, ', '.join(s))
