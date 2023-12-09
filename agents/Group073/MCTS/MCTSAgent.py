from random import choice
from time import sleep
from BasicAgent import NaiveAgent
from State import State
from mcts import mcts
from Board import Board
from Colour import Colour

class MCTSAgent(NaiveAgent):
    """
    This class describes the Hex agent using MCTS strategy.
    """

    def __init__(self, board_size=11):
        super().__init__(board_size)
        self.mct = mcts(timeLimit=1000, iterationLimit=None, colour=self.colour, board_size=self.board_size)

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
            # ---------------------------------------------------------------
            # print(self.board)
            converted_string = str(','.join(''.join(str(item) for item in row) for row in self.board))
            # print("converted_string---->>>", converted_string)

            # myColour = 1 if self.colour == "B" else -1
            # current_state = State(current_player=myColour)
            # print("current_state---->>>", current_state.board.print_board())
            action = mcts(timeLimit=1000, colour=Colour.from_char(self.colour)).search(initial_state=converted_string)
            # ---------------------------------------------------------------
            self.s.sendall(bytes(f"{action[0]},{action[1]}\n", "utf-8"))    # coordinate (x, y)
            self.board[action[0]][action[1]] = self.colour
        self.turn_count += 1


if (__name__ == "__main__"):
    agent = MCTSAgent()
    agent.run()
