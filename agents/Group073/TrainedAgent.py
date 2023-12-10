import socket
from AlphaZero.Hex import HexBoard
import AlphaZero.config as cfg
from AlphaZero.Agent import Agent, AlphaZeroAgent
from AlphaZero.network import HexNetwork
import torch


class AZAgent:
    """This class describes the default Hex agent. It will randomly send a
    valid move at each turn, and it will choose to swap with a 50% chance.
    """

    HOST = "127.0.0.1"
    PORT = 1234

    def __init__(self, board_size=11):
        self.s = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )

        self.s.connect((self.HOST, self.PORT))

        self.board_size = board_size
        self.colour = ""
        self.turn_count = 0
        self.step = 0

        self.net = HexNetwork()
        self.net.load_state_dict(
            torch.load("agents/Group073/AlphaZero/hex11-20180712-3362.policy.pth")['policy']['net'])
        # print(self.net.keys())

        # initialize the board
        self.board = HexBoard(cfg.BOARD_ROW, cfg.BOARD_COL)
        # initialize the red player (initially red before swap if required)
        self.player1 = AlphaZeroAgent(colour="red", opposite_layer=None, mode="auto", net=self.net,
                                      device='cpu', train=False)
        # initialize the blue player (initially blue before swap if required)
        self.player2 = Agent(colour="blue", opposite_layer=self.player1, mode="auto", board=self.board)
        self.player1.opposite_player = self.player2
        # initialize current player to play, red first by default, and opposite player
        self.current_player = self.player1

    def run(self):
        """Reads data until it receives an END message or the socket closes."""

        while True:
            data = self.s.recv(1024)
            if not data:
                break
            # print(f"{self.colour} {data.decode('utf-8')}", end="")
            if self.interpret_data(data):
                break

        # print(f"Naive agent {self.colour} terminated")

    def interpret_data(self, data):
        """
        Checks the type of message and responds accordingly. Returns True
        if the game ended, False otherwise.
        """

        messages = data.decode("utf-8").strip().split("\n")
        messages = [x.split(";") for x in messages]
        print(messages)
        for s in messages:
            if s[0] == "START":
                self.board_size = int(s[1])
                self.colour = s[2]
                if self.colour == "R":
                    self.player1.colour = "red"
                    self.player2.colour = "blue"
                else:
                    self.player1.colour = "blue"
                    self.player2.colour = "red"
                self.board = HexBoard(self.board_size, self.board_size)

                if self.colour == "R":
                    self.make_move()

            elif s[0] == "END":
                return True

            elif s[0] == "CHANGE":
                if s[3] == "END":
                    return True

                elif s[1] == "SWAP":
                    self.colour = self.opp_colour()
                    self.player1.swap = True
                    self.player2.swap = True
                    if s[3] == self.colour:
                        self.make_move()

                elif s[3] == self.colour:
                    action = [int(x) for x in s[1].split(",")]
                    print(action)
                    self.board.drop_stone(action[1], action[0], self.player2.returnColour())
                    self.player1.updateBoard(action[1], action[0], self.player2.returnColour())
                    # please commend out the following line before submission
                    self.player1.board.visualization()
                    # self.board[action[0]][action[1]] = self.opp_colour()

                    self.make_move()
            self.step += 1
            # self.board.visualization()
            # print("step: ", self.step)

        return False

    def make_move(self):
        """
        Make move/swap base on network
        x/y is the coordinate of the move, so x is the column and y is the row
        """
        print("step: ", self.step)
        col, row, distribution = self.player1.make_decision(self.step, iterations=800)
        print("Want", row, col)
        if row is None and col is None:
            self.s.sendall(bytes("SWAP\n", "utf-8"))
        self.player1.board.visualization()
        self.board.drop_stone(col, row, self.player1.returnColour())
        print("dropped")
        self.board.visualization()
        self.player2.updateBoard(col, row, self.player1.returnColour())
        print("updated p2")
        self.player2.board.visualization()
        self.s.sendall(bytes(f"{row},{col}\n", "utf-8"))

    def opp_colour(self):
        """Returns the char representation of the colour opposite to the
        current one.
        """
        if self.colour == "R":
            return "B"
        elif self.colour == "B":
            return "R"
        else:
            return "None"


if __name__ == "__main__":
    agent = AZAgent()
    agent.run()
