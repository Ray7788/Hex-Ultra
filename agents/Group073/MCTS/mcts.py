from __future__ import division
from Colour import Colour
from TreeNode import TreeNode
from Policy import randomPolicy
import time
import math
import random


class mcts():
    def __init__(self, 
                timeLimit=None, 
                iterationLimit=None, 
                explorationConstant=1 / math.sqrt(2),
                rolloutPolicy=randomPolicy,
                colour: Colour = None
                ):
        
        if timeLimit != None:
            if iterationLimit != None:
                raise ValueError("Cannot have both a time limit and an iteration limit")
            # time taken for each MCTS search in milliseconds
            self.timeLimit = timeLimit
            self.limitType = 'time'
        else:
            if iterationLimit == None:
                raise ValueError("Must have either a time limit or an iteration limit")
            # number of iterations of the search
            if iterationLimit < 1:
                raise ValueError("Iteration limit must be greater than one")
            self.searchLimit = iterationLimit
            self.limitType = 'iterations'

        self.colour = colour
        self.explorationConstant = explorationConstant
        self.rollout = rolloutPolicy

    def search(self, initialState, needDetails=False):
        # start at the root node of the tree
        self.root = TreeNode(initialState, None, None, self.colour)

        if self.limitType == 'time':
            # convert milliseconds to seconds
            timeLimit = time.time() + self.timeLimit / 1000 
            while time.time() < timeLimit:
                self.executeRound()
        else:
            for i in range(self.searchLimit):
                self.executeRound()

        # change the 2nd parameter is_exploration 
        bestChild = self.get_best_child(self.root, 0)
        
        # choose action based on the best child's node
        action = (action for action, node in self.root.children.items() if node is bestChild).__next__()
        
        # for Debug
        if needDetails:
            return {"action": action, "expectedReward": bestChild.totalReward / bestChild.numVisits}
        else:
            return action

    def executeRound(self):
        """
        Helper function for search function: execute a selection-expansion-simulation-backpropagation round
        """
        node = self.selectNode(self.root)
        reward = self.rollout(node.state)
        self.back_propogate(node, reward)

    def selectNode(self, node):
        """
        select a leaf node in the tree (Tree policy)
        """
        # TODO: simplify isTerminal and isFullyExpanded
        while not node.state.has_ended():
            if node.state.is_terminal:
                node = self.get_best_child(node, self.explorationConstant)
            elif not node.isFullyExpanded:
                return self.expand(node)
        return node

    def expand(self, node):
        actions = node.state.get_possible_actions()
        for action in actions:
            if action not in node.children:
                newNode = TreeNode(node.state.takeAction(action), node)
                node.children[action] = newNode
                if len(actions) == len(node.children):
                    node.isFullyExpanded = True
                return newNode

        raise Exception("Should never reach here")

    def back_propogate(self, node, reward):
        """ 
        back up the tree from the expanded node and update the node statistics
        """
        while node is not None:
            node.numVisits += 1
            node.totalReward += reward
            node = node.parent

    def get_best_child(self, node, explorationValue):
        """
        return the child with the highest UCB score
        """
        bestValue = float("-inf")
        bestNodes = []

        # TODO: check if is_exploaration is needed
        for child in node.children.values():
            exploit = node.state.getCurrentPlayer() * child.totalReward / child.numVisits
            # node.state.getCurrentPlayer() * child.totalReward / child.numVisits + 
            explore = explorationValue * math.sqrt(2.0 * math.log(node.numVisits) / child.numVisits)
            # explorationValue * math.sqrt(2 * math.log(node.numVisits) / child.numVisits)
            nodeValue = exploit + explore
            
            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNodes = [child]
            elif nodeValue == bestValue:
                bestNodes.append(child)

        return random.choice(bestNodes)