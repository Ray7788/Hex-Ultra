import socket
from random import choice
from time import sleep
from BasicAgent import NaiveAgent


class Node:
    def __init__(self, game_state, parent=None):
        self.game_state = game_state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.rewards = 0
        
class MCTS:
    def __init__(self, game_state, max_depth=10):
        self.root = Node(game_state)
        self.max_depth = max_depth

    def select(self, node):
        # Implement your selection strategy here
        pass

    def expand(self, node: Node):
        # Implement your expansion strategy here
        current_state = node.game_state
        
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

    def is_terminal(self, node):
        # Implement your terminal check here
        pass

class MCTSAgent(NaiveAgent):
    """This class describes the Hex agent using MCTS strategy.
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
        return
        
if (__name__ == "__main__"):
    agent = MCTSAgent()
    agent.run()