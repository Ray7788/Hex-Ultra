from __future__ import division

from typing import List

from Board import Board
from Colour import Colour
from TreeNode import TreeNode
import time
import math
from random import choice
import random
from copy import deepcopy

from Move import Move


class mcts():
    def __init__(self,
                 timeLimit=None,
                 iterationLimit=None,
                 exploration_constant=1 / math.sqrt(2),
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

    def search(self, initial_state: str) -> [int]:
        """
        Search the tree for the best move
        """
        # Initialise state from the beginning signal
        state = Board.from_string(string_input=initial_state, board_size=self.board_size)
        # start at the root node of the tree
        root = TreeNode(state, None, None, self.colour)

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

    def execute_round(self, node):
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
        while not node.state.has_ended():
            valid_actions = node.get_possible_actions(
                colour=node.colour.opposite(),
                board_size=self.board_size
            )

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
        while not node.state.has_ended():
            try:
                action = choice(node.get_possible_actions(node.colour, self.board_size))
            except IndexError:
                raise Exception("Non-terminal state has no possible actions: " + str(node.state))

            new_state = deepcopy(node.state)
            action.move(new_state)
            v = TreeNode(new_state, node, action, node.colour.opposite())   # opposite player's node
            # v = TreeNode(v, action, new_state, v.colour.opposite()) original

            return self.get_reward(v)

    def get_reward(self, node: TreeNode) -> float:
        """
        Returns the reward for the current state.
        """

        winner = node.state.get_winner()  # Hypothetical method to determine the winner
        if winner is None:
            return 0  # Draw case, if applicable

        return 1.0 if winner == self.colour else -1.0

    def expand(self, node: TreeNode) -> TreeNode:
        # Find untried actions
        untried_actions = self.get_untried_actions(node)

        # Randomly choose one action as the next step
        action_chosen = untried_actions[random.randint(0, len(untried_actions) - 1)]

        # Create a deepcopy of state s
        s_prime = deepcopy(node.state)
        # Apply the move
        action_chosen.move(s_prime)

        v_prime = TreeNode(
            parent=node,
            action=action_chosen,
            state=s_prime,
            colour=node.colour.opposite()
        )
        node.children.append(v_prime)

        # Return the new child
        return v_prime

    def get_untried_actions(self, node: TreeNode) -> List[Move]:
        """
        Helper function for 'expand': Returns all untried actions of a node v.
        """

        all_possible_actions = node.get_possible_actions(self.colour, self.board_size)  # Get all valid actions from v

        # Check if v has children
        if len(node.children) != 0:
            untried_actions: List[Move] = []  # Contains all untried actions

            for action in all_possible_actions:
                is_tried = False  # Mark this action as untried

                for child in node.children:
                    if action.x == child.action.x and action.y == child.action.y:
                        is_tried = True  # Action was already applied
                        break

                if not is_tried:  # Add untried action to untried list
                    untried_actions.append(action)

            return untried_actions

        return all_possible_actions

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
            node_value = exploit + 2*explore

            if node_value > best_value:
                best_value = node_value
                best_nodes = [child]
            elif node_value == best_value:
                best_nodes.append(child)

        return choice(best_nodes)
