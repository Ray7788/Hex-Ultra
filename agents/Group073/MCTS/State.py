from copy import deepcopy
from typing import List
from Board import Board
from Colour import Colour
from Move import Move
from random import choice
import random


class State(Board):
    def __init__(self, current_player=1):
        super().__init__()
        self.current_player = current_player  # 1 for blue, -1 for red，default is blue
        # self.is_terminal = self.is_terminal()
        self.current_value = self.get_reward()
        self.current_round_index = 0
        self.cumulative_choices = []

    def get_current_player(self):
        return self.current_player

    def get_possible_actions(self, colour: Colour):
        """
        Returns the list of all possible moves based on the current state(if it is coloured) of each tile.
        """
        all_moves: List[Move] = []  # Stores all moves
        choices: List[Move] = []  # Stores valid moves

        for i in range(self.get_size()):
            for j in range(self.get_size()):
                all_moves.append(Move(colour=colour, x=i, y=j))

        for m in all_moves:
            # tiles = self.board.get_tiles()
            # if tiles[i][j].colour is None:
            #     choices.append(Move(colour=colour, x=i, y=j))
            tile = self.get_tiles()[m.x][m.y]
            if tile.get_colour() is None:
                choices.append(m)

        return choices

    def take_action(self, action):
        # player_colour = Colour.BLUE if self.current_player == 1 else Colour.RED
        new_state = deepcopy(action)
        action.move(new_state)
        v = TreeNode(new_state, node, action, node.colour.opposite())
        # new_state.board._tiles[action[0]][action[1]].colour = player_colour
        # new_state.current_player = -self.current_player
        return action

    def is_terminal(self):
        return self.has_ended()

    def get_reward(self):
        """
        Returns the reward for the current state.
        """
        if not self.is_terminal():
            return None  # or raise an error, since reward is only for terminal states

        winner = self.get_winner()  # Hypothetical method to determine the winner
        if winner is None:
            return 0  # Draw case, if applicable
        return 1 if winner == self.current_player else -1
