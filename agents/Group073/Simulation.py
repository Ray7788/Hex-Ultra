from MCTS2.Hex import HexBoard
import MCTS2.config as cfg
from MCTS2.Agent import Agent


class HexSimulator:
    """
    define the simulator of Hex
    """

    def __init__(self):
        # initialize the board
        self.board = HexBoard(cfg.BOARD_ROW, cfg.BOARD_COL)
        # initialize the red player (initially red before swap if required)
        self.player1 = Agent(colour="red", opposite_layer=None, mode="auto")
        # initialize the blue player (initially blue before swap if required)
        self.player2 = Agent(colour="blue", opposite_layer=self.player1, mode="auto")
        self.player1.opposite_player = self.player2
        # initialize current player to play, red first by default, and opposite player
        self.current_player = self.player1

    def simulate(self):
        """
        a simulation until end of the game
        """
        for step in range(cfg.BOARD_ROW * cfg.BOARD_COL):
            # obtain decision of the current player
            x, y = self.current_player.make_decision(step, iterations=500)
            if x is None and y is None:
                print("#### SWAP ####")
                # player2 choose to swap
                self.player1.swap = True
                self.player2.swap = True
                # update current player
                self.current_player = self.player1 if self.player2 == self.current_player else self.player2
                continue
            # update the board and obtain the winner
            winner = self.board.drop_stone(x, y, self.current_player.returnColour())
            # update the opposite player's board
            opposite_player = self.player1 if self.player2 == self.current_player else self.player2
            opposite_player.updateBoard(x, y, self.current_player.returnColour())
            # update current player
            self.current_player = opposite_player
            # visualization
            self.board.visualization()
            # end the game if a winner is found
            if winner is not None:
                break
        if winner:
            print("red")
            if self.player1.returnColour() == "red":
                print(f"Player1 ({self.player1.returnColour()}) wins!!!")
            else:
                print(f"Player2 ({self.player2.returnColour()}) wins!!!")
        else:
            print("blue")
            if self.player1.returnColour() == "blue":
                print(f"Player1 ({self.player1.returnColour()}) wins!!!")
            else:
                print(f"Player2 ({self.player2.returnColour()}) wins!!!")



if __name__ == "__main__":
    for _ in range(1):
        game = HexSimulator()
        game.simulate()
