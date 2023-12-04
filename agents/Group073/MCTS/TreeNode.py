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

        self.children = {}
        self.isTerminal = state.isTerminal()
        self.isFullyExpanded = self.isTerminal  # if the node is terminal, no need to expand
        self.numVisits = 0              
        self.totalReward = 0.0

    def get_child(self, action: Move):
        """Get the child node of the current node by the action."""
        return self.children[action]
        
    def __str__(self):
        """Returns a string representation of the node."""
        s=[]
        s.append("totalReward: %s"%(self.totalReward))
        s.append("numVisits: %d"%(self.numVisits))
        s.append("isTerminal: %s"%(self.isTerminal))
        s.append("possibleActions: %s"%(self.children.keys()))
        return "%s: {%s}"%(self.__class__.__name__, ', '.join(s))
