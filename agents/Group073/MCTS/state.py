from copy import deepcopy

class State:
    def __init__(self, board, current_player=1, last_move=(0, 0)):
        self.board = board
        # 1 for blue, -1 for red
        self.current_player = current_player
        self.last_move = last_move

    def getCurrentPlayer(self):
        return self.current_player

    def getPossibleActions(self):
        choices = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] == 0:
                    choices.append((i, j))
        return choices
    
    def takeAction(self, action):
        playerColour = "B" if self.current_player == 1 else "R"
        new_state = deepcopy(self)
        new_state.board[action[0]][action[1]] = playerColour
        new_state.current_player = -self.current_player
        return new_state
    
    def isTerminal(self):
        pass
    
    def getReward(self):
        pass
    