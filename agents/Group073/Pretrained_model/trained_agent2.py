from random import choice
import socket
from trained_agent_interactive import InteractiveGame
from configparser import ConfigParser


class TrainedAgent():
    """This class describes the default Hex agent. It will randomly send a
    valid move at each turn, and it will choose to swap with a 50% chance.
    """

    HOST = "127.0.0.1"
    PORT = 1234

    def run(self):
        """A finite-state machine that cycles through waiting for input
        and sending moves.
        """

        self._board_size = 0
        self._board = []
        self._colour = ""
        self._turn_count = 1
        self._choices = []
        self.correct_position = (0, 0)
        self.last_move = None
        self.opponent_move = None

        # self.whole_board = []
        # for i in range(11):
        #     for j in range(11):
        #         self.whole_board.append((i, j))

        states = {
            1: TrainedAgent._connect,
            2: TrainedAgent._wait_start,
            3: TrainedAgent._make_move,
            4: TrainedAgent._wait_message,
            5: TrainedAgent._close
        }

        res = states[1](self)
        while (res != 0):
            res = states[res](self)

    def _connect(self):
        """Connects to the socket and jumps to waiting for the start
        message.
        """

        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect((TrainedAgent.HOST, TrainedAgent.PORT))

        return 2

    def _wait_start(self):
        """Initialises itself when receiving the start message, then
        answers if it is Red or waits if it is Blue.
        """

        data = self._s.recv(1024).decode("utf-8").strip().split(";")
        if (data[0] == "START"):
            self._board_size = int(data[1])
            for i in range(self._board_size):
                for j in range(self._board_size):
                    self._choices.append((i, j))
            self._colour = data[2]

            if (self._colour == "R"):
                return 3
            else:
                return 4

        else:
            print("ERROR: No START message received.")
            return 0

    def _make_move(self):
        """Makes a random valid move. It will choose to swap with
        a coinflip.
        """
        print('Turn count:', self._turn_count)
        if self._turn_count == 1:  # 我们是先手
            print("we make the first move")
            our_move_index = ai_agent.play_ai_move()
            pos = our_move_index // 11, our_move_index % 11
            self.last_move = pos  # must keep
            print('our move', pos)
            self._s.sendall(bytes(f"{pos[0]},{pos[1]}\n", "utf-8"))
        elif self._turn_count == 2:  # 我们是后手
            print("we make the second move")
            our_move_index = ai_agent.play_ai_move()
            pos = our_move_index // 11, our_move_index % 11
            if pos == self.opponent_move:  # 这里证明 ai agent选择了swap
                print("ai agent swapped")
                self._s.sendall(bytes("SWAP\n", "utf-8"))
            else:  # 这里证明 ai agent没有选择swap
                print("ai agent did not swap")
                self.last_move = pos
                print('our move', pos)
                self._s.sendall(bytes(f"{pos[0]},{pos[1]}\n", "utf-8"))
        else:  # 之后的回合
            our_move_index = ai_agent.play_ai_move()
            pos = our_move_index // 11, our_move_index % 11
            self.last_move = pos
            print('our move', pos)
            self._s.sendall(bytes(f"{pos[0]},{pos[1]}\n", "utf-8"))

        # # this only check if our agent swaps
        # if self._turn_count == 2 and choice([0, 1]) == 1:
        #     print('add', self.opponent_move)
        #     ai_agent.play_move(self.opponent_move)
        #     pos = "SWAP\n"
        #     self._s.sendall(bytes("SWAP\n", "utf-8"))
        # else:
        #     print(self.opponent_move)
        #     if self.opponent_move != None and self._turn_count == 2:
        #         ai_agent.play_move(self.opponent_move)
        #     print('1')
        #     our_move_index = ai_agent.play_ai_move()
        #     pos = our_move_index // 11, our_move_index % 11
        #     self.last_move = pos
        #     # must keep
        #     print('our move', pos)
        #     self._s.sendall(bytes(f"{pos[0]},{pos[1]}\n", "utf-8"))
        return 4

    def _wait_message(self):
        """Waits for a new change message when it is not its turn."""

        self._turn_count += 1

        data = self._s.recv(1024).decode("utf-8").strip().split(";")
        if data[0] == "END" or data[-1] == "END":
            return 5
        else:
            # this check if we swap or if opponent swaps;
            # 在这里，无论是我们swap还是opponent swaps，我们的colour都要变
            if data[1] == "SWAP":
                # if opponent calls swap, that means opponent makes our last move, we need to do that on the ai board as well
                # 为什么这里是用！=去检查是不是对手的move，而后面却用==呢？这是因为在swap的指令里，data【-1】是我们即将变成的colour，如果我们现在的colour不等于data【-1】的colour，证明我们被swap了
                if data[-1] != self._colour:
                    print("Our opponent has swapped，our last move is", self.last_move)
                    ai_agent.play_move(self.last_move) # 让AI board 进行swap
                # if we call swap (this is done by the AI agent), we don't need to do anything on the ai board
                self._colour = self.opp_colour()
            # 这里，如果我们或者对手都没有swap，这里就会返回我们或者对手的move，所以要检查这个move是我们的还是对手的
            # 如果是对手的move，我们便要在ai board上做这个move
            else:
                x, y = data[1].split(",")
                self._choices.remove((int(x), int(y)))
                # 如果这是对手的move，我们要在ai board上做这个move
                # 这里用==是因为假设对手下了（x，y），data【-1】代表的是下一步的colour（也就是我们的colour）
                if data[-1] == self._colour:
                    self.opponent_move = int(x), int(y)
                    print('oppo', self.opponent_move)
                    ai_agent.play_move(self.opponent_move)

            if data[-1] == self._colour:
                return 3

        return 4

    def _close(self):
        """Closes the socket."""

        self._s.close()
        return 0

    def opp_colour(self):
        """Returns the char representation of the colour opposite to the
        current one.
        """

        if self._colour == "R":
            return "B"
        elif self._colour == "B":
            return "R"
        else:
            return "None"


if (__name__ == "__main__"):
    agent = TrainedAgent()
    config = ConfigParser()
    config.read('config.ini')
    ai_agent = InteractiveGame(config)
    agent.run()
