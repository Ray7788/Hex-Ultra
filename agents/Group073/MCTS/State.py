from copy import deepcopy
from typing import List
from Board import Board
from Colour import Colour
from Move import Move


class State:
    def __init__(self, board: Board, current_player=1):
        self.board = board
        self.current_player = current_player  # 1 for blue, -1 for red，default is blue
        self.is_terminal = self.is_terminal()
        self.current_value = self.getReward()
        self.current_round_index = 0
        self.cumulative_choices = []

    def get_current_player(self):
        return self.current_player

    def get_possible_actions(self, colour: Colour):
        """
        Returns the list of all possible moves based on the current state(if it is coloured) of each tile.
        """
        choices = List[Move] = []  # Stores valid moves

        for i in range(self.board.get_size()):
            for j in range(self.board.get_size()):
                tiles = self.board.get_tiles()
                if tiles[i][j].colour is None:
                    choices.append(Move(colour=colour, x=i, y=j))

        return choices

    def takeAction(self, action):
        playerColour = Colour.BLUE if self.current_player == 1 else Colour.RED
        new_state = deepcopy(self)
        new_state.board._tiles[action[0]][action[1]].colour = playerColour
        new_state.current_player = -self.current_player
        return new_state

    def is_terminal(self):
        return self.board.has_ended()

    def getReward(self):
        if not self.is_terminal():
            return None  # or raise an error, since reward is only for terminal states

        winner = self.board.get_winner()  # Hypothetical method to determine the winner
        if winner is None:
            return 0  # Draw case, if applicable
        return 1 if winner == self.current_player else -1
