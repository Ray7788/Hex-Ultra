import socket
from random import choice
from time import sleep
from BasicAgent import NaiveAgent
import copy
import state
from mcts import mcts


class Node:
    def __init__(self, game_state, parent=None):
        self.game_state = game_state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.rewards = 0
        
class MCTS:
    def __init__(self, game_state, colour, max_depth=10):
        self.root = Node(game_state)
        self.max_depth = max_depth
        self.colour = colour

    def select(self, node):
        # Implement your selection strategy here
        pass

    def expand(self, node: Node):
        # Implement your expansion strategy here
        current_state = node.game_state
        choices = []
        for i in range(len(current_state)):
            for j in range(len(current_state)):
                if current_state[i][j] == 0:
                    choices.append((i, j))
        new_state = copy.deepcopy(current_state)
        
        pass

    def simulate(self, node):
        # Implement your simulation strategy here
        pass

    def backpropagate(self, node, reward):
        # Implement your backpropagation strategy here
        pass

    def run_search(self):
        for _ in range(self.max_depth):
            node = self.select(self.root)
            if not self.is_terminal(node):
                node = self.expand(node)
            reward = self.simulate(node)
            self.backpropagate(node, reward)

    def get_best_move(self):
        # Implement your move selection strategy here
        pass

class MCTSAgent(NaiveAgent):
    """This class describes the Hex agent using MCTS strategy.
    """
    def make_move(self):
        if self.colour == "B" and self.turn_count == 0:
            # self.mcts = MCTS(game_state=self.board, colour=self.colour)
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
        return
        
if (__name__ == "__main__"):
    agent = MCTSAgent()
    agent.run()