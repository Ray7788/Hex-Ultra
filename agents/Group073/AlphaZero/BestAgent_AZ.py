from Hex import HexBoard
from Agent import AlphaZeroAgent
from net import AlphaZeroNet
from Simulation import GameState
import config as cfg


from BasicAgent import NaiveAgent
import torch

class AZAgent(NaiveAgent):
    
    def __init__(self, board_size=11):
        super().__init__(board_size)
        self.board = HexBoard(cfg.BOARD_ROW, cfg.BOARD_COL)
        self.net = AlphaZeroNet()
        self.net.load_state_dict(torch.load("agents/Group073/AlphaZero/module/net1000.pkl"))
        self.net.cuda()
        self.agent = AlphaZeroAgent(colour=self.colour, opposite_layer=None, mode="auto", net=self.net)
        self.opsite_colour = self.opp_colour()
        self.agent2 = AlphaZeroAgent(colour=self.opsite_colour, opposite_layer=self.agent, net=self.net)
        self.agent.opposite_player = self.agent2
        self.total_step = 0
        self.state_queue = []
        
    def interpret_data(self, data):
        """Checks the type of message and responds accordingly. Returns True
        if the game ended, False otherwise.
        """

        messages = data.decode("utf-8").strip().split("\n")
        messages = [x.split(";") for x in messages]
        print(messages)
        for s in messages:
            if s[0] == "START":
                self.board_size = int(s[1])
                self.colour = 'red' if s[2] == 'R' else 'blue'
                self.agent.colour = self.colour
                self.board = HexBoard(self.board_size, self.board_size)

                if self.colour == "red":
                    self.make_move()

            elif s[0] == "END":
                return True

            elif s[0] == "CHANGE":
                self.total_step = self.total_step + self.turn_count
                if s[3] == "END":
                    return True

                elif s[1] == "SWAP":
                    self.colour = self.opp_colour()
                    self.agent.colour = self.colour
                    self.agent2.colour = self.opp_colour()
                    if s[3] == self.colour:
                        self.make_move()

                elif s[3] == self.colour:
                    action = [int(x) for x in s[1].split(",")]
                    self.board.drop_stone(action[0], action[1], self.opp_colour())

                    self.make_move()

        return False
    
    def make_move(self):
        x, y, distribution = self.agent.make_decision(self.total_step, iterations=10)
        self.state_queue.append(GameState(board=self.board, initial_colour=self.agent.colour, current_player=self.agent, distribution=distribution))
        if x is None and y is None:
            self.s.sendall(bytes("SWAP\n", "utf-8"))
        # update the board and obtain the winner
        winner = self.board.drop_stone(x, y, self.agent.returnColour())
        self.s.sendall(bytes(f"{x},{y}\n", "utf-8"))
        
    def opp_colour(self):
        """Returns the char representation of the colour opposite to the
        current one.
        """
        if self.colour == "red":
            return "blue"
        elif self.colour == "blue":
            return "red"
        else:
            return "None"
        
if (__name__ == "__main__"):
    agent = AZAgent()
    agent.run()