from __future__ import division

from Move import Move
from State import State
from Board import Board
from Colour import Colour
from TreeNode import TreeNode
import time
import math
from random import choice
import random
from copy import deepcopy
from typing import List


class mcts:
    def __init__(self,
                 timeLimit=None,
                 iterationLimit=None,
                 exploration_constant=1 / math.sqrt(2.0),
                 colour: Colour = None,
                 board_size: int = 11
                 ):

        if timeLimit is not None:
            if iterationLimit is not None:
                raise ValueError("Cannot have both a time limit and an iteration limit")
            # time taken for each MCTS search in milliseconds
            self.timeLimit = timeLimit
            self.limitType = 'time'
        else:
            if iterationLimit is None:
                raise ValueError("Must have either a time limit or an iteration limit")
            # number of iterations of the search
            if iterationLimit < 1:
                raise ValueError("Iteration limit must be greater than one")
            self.searchLimit = iterationLimit
            self.limitType = 'iterations'

        self.exploration_constant = exploration_constant
        self.colour = colour
        self.board_size = board_size

    def search(self, initial_state: State) -> [int, int]:
        """
        Search the tree for the best move
        """
        # start at the root node of the tree, action未定义
        root = TreeNode(initial_state, None, None, self.colour)
        # print("A",root.children)
        # if the time limit is not set, then run the search for the specified number of iterations
        if self.limitType == 'time':
            # convert milliseconds to seconds
            time_limit = time.time() + self.timeLimit / 1000
            while time.time() < time_limit:
                self.execute_round(root)
        else:
            for i in range(self.searchLimit):
                self.execute_round(root)

        # change the 2nd parameter to decide if is exploration: 1 or 2
        best_child = self.get_best_child(root)

        # choose action(x, y) based on the best child's node
        action: [] = [best_child.action.x, best_child.action.y]

        return action

    def execute_round(self, node: TreeNode):
        """
        Helper function for search function: execute a selection-expansion-simulation-backpropagation round
        """
        next_node = self.select_node(node)  # Tree policy
        reward = self.rollout_policy(next_node)  # Default policy
        self.back_propagate(next_node, reward)  # Backup

    def select_node(self, node: TreeNode) -> TreeNode:
        """
        select a leaf node in the tree for the simulation(Tree policy)
        """
        while not node.state.is_terminal():
            valid_actions = node.state.getPossibleActions()
            # valid_actions = node.state.get_valid_actions(11)

            print("Valid", len(valid_actions))
            print("Children", len(node.children))
            # If they have the same number, the tree reaches the leaf.
            if len(valid_actions) != len(node.children):
                return self.expand(node)
            else:
                node = self.get_best_child(node)

            return node

    def rollout_policy(self, node: TreeNode) -> float:
        """
        This policy chooses uniformly at random from the possible moves in a state
        Also called rollout and simulation, a part of default_policy
        """
        # print(type(node.state))
        while not node.state.is_terminal():
            try:
                # action = choice(node.get_possible_actions(node.colour, self.board_size))
                action = choice(node.state.getPossibleActions())
            except IndexError:
                raise Exception("Non-terminal state has no possible actions: " + str(node.state))

            new_state = node.state.takeAction()
            action.move(new_state.board)
            new_child = TreeNode(new_state, node, action, action.colour)
            # Colour.opposite(node.colour)
            return new_child.state.getReward()

    def expand(self, node: TreeNode):
        next_player_colour = Colour.opposite(node.colour)
        actions = node.state.getPossibleActions()
        # print("-------------")
        for action in actions:
            if action not in node.children:
                # Create a copy of state s
                s_prime = node.state.takeAction()
                # Apply the move's colour to board
                action.move(s_prime.board)

                new_node = TreeNode(
                    s_prime,
                    node,
                    action,
                    node.colour
                )

                node.children.append(new_node)

                return new_node

        raise Exception("Should never reach here")

    def back_propagate(self, node: TreeNode, reward):
        """
        back up the tree from the expanded node and update the node statistics
        """
        while node is not None:
            node.numVisits += 1
            node.totalReward += reward
            node = node.parent

    def get_best_child(self, node: TreeNode) -> TreeNode:
        """
        return the child with the highest UCB score, if there are multiple nodes with the same score, return a random one
        """
        best_value = float("-inf")
        best_nodes = []

        children = node.get_children()
        for child in children:
            exploit = child.totalReward / child.numVisits
            # node.state.getCurrentPlayer() * child.totalReward / child.numVisits +
            explore = self.exploration_constant * math.sqrt((2.0 * math.log(node.numVisits)) / child.numVisits)
            # explorationValue * math.sqrt(2 * math.log(node.numVisits) / child.numVisits)
            node_value = exploit + explore

            if node_value > best_value:
                best_value = node_value
                best_nodes = [child]
            elif node_value == best_value:
                best_nodes.append(child)

        return best_nodes[0]
