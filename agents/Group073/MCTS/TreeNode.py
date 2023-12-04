class TreeNode():
    def __init__(self, state, parent):
        self.state = state
        self.parent = parent
        self.children = {}
        self.isTerminal = state.isTerminal()
        self.isFullyExpanded = self.isTerminal  # if the node is terminal, no need to expand
        self.numVisits = 0              
        self.totalReward = 0.0
        

    def __str__(self):
        s=[]
        s.append("totalReward: %s"%(self.totalReward))
        s.append("numVisits: %d"%(self.numVisits))
        s.append("isTerminal: %s"%(self.isTerminal))
        s.append("possibleActions: %s"%(self.children.keys()))
        return "%s: {%s}"%(self.__class__.__name__, ', '.join(s))
