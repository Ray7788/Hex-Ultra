from copy import deepcopy
from typing import List
from Board import Board
from Colour import Colour
from Move import Move

# Board
class State():
    def __init__(self, board: Board, board_size: int = 11, current_player=None):
        # super().__init__(board_size)
        self.board_size =board_size
        self.board = board
        self.current_player = current_player  # 1 for blue, -1 for red，default is blue
        # self.is_terminal = self.is_terminal()
        # self.current_value = self.getReward()

    def get_current_player(self):
        return self.current_player

    # def get_possible_actions(self, colour: Colour):
    #     """
    #     Returns the list of all possible moves based on the current state(if it is coloured) of each tile.
    #     """
    #     all_moves: List[Move] = []  # Stores all moves
    #     choices: List[Move] = []  # Stores valid moves
    #
    #     for i in range(self.get_size()):
    #         for j in range(self.get_size()):
    #             all_moves.append(Move(colour=colour, x=i, y=j))
    #
    #     for m in all_moves:
    #         tile = self.get_tiles()[m.x][m.y]
    #         if tile.get_colour() is None:
    #             choices.append(m)

        return choices

    def getPossibleActions(self):
        choices = []
        for i in range(self.board._board_size):
            for j in range(self.board._board_size):

                if self.board._tiles[i][j].colour is None:
                    choices.append(Move(colour=None, x=i, y=j))
        return choices

    def takeAction(self):
        # playerColour = Colour.BLUE if self.current_player == 1 else Colour.RED
        return deepcopy(self)
        # new_state.board._tiles[action[0]][action[1]].colour = playerColour
        # new_state.current_player = -self.current_player

    def is_terminal(self):
        return self.board.has_ended()

    def getReward(self):
        # if not self.isTerminal():
            # return None  # or raise an error, since reward is only for terminal states

        winner = self.board.get_winner()  # Hypothetical method to determine the winner
        if winner is None:
            return 0  # Draw case, if applicable
        return 1 if winner == self.current_player else -1
