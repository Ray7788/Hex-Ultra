from random import choice
from time import sleep
from BasicAgent import NaiveAgent
from State import State
from mcts import mcts
from Board import Board

class MCTSAgent(NaiveAgent):
    """
    This class describes the Hex agent using MCTS strategy.
    """
    def make_move(self):
        if self.colour == "B" and self.turn_count == 0:
            # random choose if swap, should be changed later
            if choice([0, 1]) == 1:
                self.s.sendall(bytes("SWAP\n", "utf-8"))
            else:
                # All legal moves
                choices = []
                for i in range(self.board_size):
                    for j in range(self.board_size):
                        if self.board[i][j] == 0:
                            choices.append((i, j))
                pos = choice(choices)
                self.s.sendall(bytes(f"{pos[0]},{pos[1]}\n", "utf-8"))
                self.board[pos[0]][pos[1]] = self.colour
        else:
            # print(self.board)
            converted_string = str(','.join(''.join(str(item) for item in row) for row in self.board))
            # print("converted_string---->>>", converted_string)
            b = Board.from_string(string_input=converted_string)
            myColour = 1 if self.colour == "B" else -1
            current_state = State(board=b, current_player=myColour)
            # print("current_state---->>>", current_state.board.print_board())
            searcher = mcts(timeLimit=1000)
            action = searcher.search(initialState=current_state)
            # print("go", action)
            self.s.sendall(bytes(f"{action[0]},{action[1]}\n", "utf-8"))
            self.board[action[0]][action[1]] = self.colour
        self.turn_count += 1
        
if (__name__ == "__main__"):
    agent = MCTSAgent()
    agent.run()