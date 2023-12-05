import copy
from Hex import HexBoard
import config as cfg
from Agent import Agent, AlphaZeroAgent
from net import AlphaZeroNet


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
            x, y = self.current_player.make_decision(step, iterations=1000)
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


class GameState:
    """
    game state for a specific time
    """

    def __init__(self, board, initial_colour, current_player, distribution):
        self.board = copy.deepcopy(board)  # board situation at this time
        self.initial_colour = initial_colour  # colour held by the player when the state happened
        self.current_player = current_player  # player of the state
        self.reward = 0  # reward for the state
        self.pi = distribution  # soft label

    def updateReward(self, winner_colour):
        if winner_colour == self.current_player.returnColour():
            self.reward = 1
        else:
            self.reward = -1


class AlphaZeroSimulator:
    """
    define the simulator of Hex
    """

    def __init__(self, net1, net2, visualization=False, device="cuda:0"):
        # initialize model
        self.net1 = net1
        self.net2 = net2
        # initialize the board
        self.board = HexBoard(cfg.BOARD_ROW, cfg.BOARD_COL)
        # initialize the red player (initially red before swap if required)
        self.player1 = AlphaZeroAgent(colour="red", opposite_layer=None, mode="auto", net=self.net1, train=True, device=device)
        # initialize the blue player (initially blue before swap if required)
        self.player2 = AlphaZeroAgent(colour="blue", opposite_layer=self.player1, mode="auto", net=self.net2, train=True, device=device)
        self.player1.opposite_player = self.player2
        # initialize current player to play, red first by default, and opposite player
        self.current_player = self.player1
        # initialize state queue to store the game in sequence
        self.state_queue = []
        # visualization
        self.visualization = visualization

    def simulate(self):
        """
        a simulation until end of the game
        """
        for step in range(cfg.BOARD_ROW * cfg.BOARD_COL):
            # obtain decision of the current player
            x, y, distribution = self.current_player.make_decision(step, iterations=500)
            # save the state of the step
            self.state_queue.append(GameState(board=self.board, initial_colour=self.current_player.returnColour(),
                                              current_player=self.current_player, distribution=distribution))
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
            if self.visualization:
                self.board.visualization()
            # end the game if a winner is found
            if winner is not None:
                break
        # initialize winner colour
        winner_colour = "red" if winner else "blue"
        if self.visualization:
            if self.player1.returnColour() == winner_colour:
                print(f"Player1 ({self.player1.returnColour()}) wins!!!")
            else:
                print(f"Player2 ({self.player2.returnColour()}) wins!!!")
        # update reward for history states
        for game_state in self.state_queue:
            game_state.updateReward(winner_colour)


class AlphaZeroTestSimulator:
    """
    define the simulator of Hex
    """

    def __init__(self, net1, net2, visualization=True, device="cuda:0"):
        # initialize model
        self.net1 = net1
        self.net2 = net2
        # initialize device
        self.device = device
        # initialize the board
        self.board = HexBoard(cfg.BOARD_ROW, cfg.BOARD_COL)
        # initialize the red player (initially red before swap if required)
        self.player1 = AlphaZeroAgent(colour="red", opposite_layer=None, mode="auto", net=self.net1, device=self.device, train=False)
        # initialize the blue player (initially blue before swap if required)
        self.player2 = AlphaZeroAgent(colour="blue", opposite_layer=self.player1, mode="auto", net=self.net2, device=self.device, train=False)
        self.player1.opposite_player = self.player2
        # initialize current player to play, red first by default, and opposite player
        self.current_player = self.player1
        # initialize state queue to store the game in sequence
        self.state_queue = []
        # visualization
        self.visualization = visualization

    def simulate(self):
        """
        a simulation until end of the game
        """
        for step in range(cfg.BOARD_ROW * cfg.BOARD_COL):
            # obtain decision of the current player
            x, y, distribution = self.current_player.make_decision(step, iterations=1000)
            # save the state of the step
            self.state_queue.append(GameState(board=self.board, initial_colour=self.current_player.returnColour(),
                                              current_player=self.current_player, distribution=distribution))
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
            if self.visualization:
                self.board.visualization()
            # end the game if a winner is found
            if winner is not None:
                break
        # initialize winner colour
        winner_colour = "red" if winner else "blue"
        if self.visualization:
            if self.player1.returnColour() == winner_colour:
                print(f"Player1 ({self.player1.returnColour()}) wins!!!")
            else:
                print(f"Player2 ({self.player2.returnColour()}) wins!!!")
        # update reward for history states
        for game_state in self.state_queue:
            game_state.updateReward(winner_colour)


if __name__ == "__main__":
    import torch

    net1 = AlphaZeroNet()
    net1.load_state_dict(torch.load("./module/net19000.pkl"))
    net1.cuda()
    net2 = AlphaZeroNet()
    # net2.load_state_dict(torch.load("./module/checkpoint.pth")["model_state_dict"])
    net2.load_state_dict(torch.load("./module/net18000.pkl"))
    net2.cuda()
    for _ in range(1):
        # game = HexSimulator()
        game = AlphaZeroTestSimulator(net1, net2, visualization=True, device="cuda:0")
        game.simulate()
