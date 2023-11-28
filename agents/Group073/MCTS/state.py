from copy import deepcopy
from Board import Board
from Colour import Colour

class State:
    def __init__(self, board:Board, current_player=1):
        self.board = board
        # 1 for blue, -1 for red
        self.current_player = current_player

    def getCurrentPlayer(self):
        return self.current_player

    def getPossibleActions(self):
        choices = []
        for i in range(self.board._board_size):
            for j in range(self.board._board_size):
                if self.board._tiles[i][j].colour == None:
                    choices.append((i, j))
        return choices
    
    def takeAction(self, action):
        playerColour = Colour.BLUE if self.current_player == 1 else Colour.RED
        new_state = deepcopy(self)
        new_state.board._tiles[action[0]][action[1]].colour = playerColour
        new_state.current_player = -self.current_player
        return new_state
    
    def isTerminal(self):
        return self.board.has_ended()

    def getReward(self):
        if not self.isTerminal():
            return None  # or raise an error, since reward is only for terminal states

        winner = self.board.get_winner()  # Hypothetical method to determine the winner
        if winner is None:
            return 0  # Draw case, if applicable
        return 1 if winner == self.current_player else -1
    