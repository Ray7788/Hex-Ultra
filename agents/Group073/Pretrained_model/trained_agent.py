import socket
import torch
import torch.nn as nn
from torch.distributions.categorical import Categorical


class ResNetBlock(nn.Module):
    def __init__(self, channels, reach, scale=1):
        super(ResNetBlock, self).__init__()
        self.conv = nn.Conv2d(channels, channels, kernel_size=reach * 2 + 1, padding=reach, bias=False)
        self.bn = nn.BatchNorm2d(channels)
        self.scale = scale

    def forward(self, x):
        residual = x
        out = self.conv(x)
        out = self.bn(out)
        out = self.scale * out + residual
        return out * torch.sigmoid(out)


class OriginalModel(nn.Module):
    def __init__(self, board_size, layers, intermediate_channels, reach):
        super(OriginalModel, self).__init__()
        self.board_size = board_size
        self.conv = nn.Conv2d(2, intermediate_channels, kernel_size=2 * reach + 1, padding=reach - 1)
        # Creates a new instance for each iteration in the range of layers, resulting in distinct instances.
        self.skiplayers = nn.ModuleList([ResNetBlock(intermediate_channels, 1) for _ in range(layers)])
        self.policyconv = nn.Conv2d(intermediate_channels, 1, kernel_size=2 * reach + 1, padding=reach, bias=False)
        self.bias = nn.Parameter(torch.zeros(board_size ** 2))

    def forward(self, x):
        x_sum = torch.sum(x[:, :, 1:-1, 1:-1], dim=1).view(-1, self.board_size ** 2)
        x = self.conv(x)
        for skiplayer in self.skiplayers:
            x = skiplayer(x)
        illegal = x_sum * torch.exp(torch.tanh((x_sum.sum(dim=1) - 1) * 1000) * 10).unsqueeze(1).expand_as(
            x_sum) - x_sum
        return self.policyconv(x).view(-1, self.board_size ** 2) + self.bias - illegal


class RotatedModel(nn.Module):
    def __init__(self, model):
        super(RotatedModel, self).__init__()
        self.board_size = model.board_size
        self.internal_model = model

    def forward(self, x):
        x_flip = torch.flip(x, [2, 3])
        y_flip = self.internal_model(x_flip)
        y = torch.flip(y_flip, [1])
        return (self.internal_model(x) + y) / 2


def model():
    model_file_name = 'agents/Group073/Pretrained_model/models/11_2w4_2000.pt'
    model_info = torch.load(model_file_name, map_location=torch.device('cpu'))
    model = OriginalModel(
        board_size=model_info['config'].getint('board_size'),
        layers=model_info['config'].getint('layers'),
        intermediate_channels=model_info['config'].getint('intermediate_channels'),
        reach=model_info['config'].getint('reach')
    )

    if model_info['config'].getboolean('rotation_model'):
        model = RotatedModel(model)

    model.load_state_dict(model_info['model_state_dict'])
    model.eval()
    torch.no_grad()
    return model


def create_border(board_tensor):
    border = torch.zeros([2, 11 + 2, 11 + 2])
    border[0, 0, 1:-1] = 1
    border[0, -1, 1:-1] = 1
    border[1, 1:-1, 0] = 1
    border[1, 1:-1, -1] = 1
    border[:, 1:-1, 1:-1] = board_tensor
    return border


class TrainedAgent():
    """This class describes the default Hex agent. It will randomly send a
    valid move at each turn, and it will choose to swap with a 50% chance.
    """

    HOST = "127.0.0.1"
    PORT = 1234

    def __init__(self):
        self._board_size = 0
        self._board = []
        self._colour = ""
        self._turn_count = 1
        self._choices = []

        self.last_move = None
        self.opponent_move = None

        torch.set_num_threads(4)
        self.logical_board_tensor = torch.zeros([2, 11, 11])
        self.board_tensor = create_border(self.logical_board_tensor)
        self.model = model()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.current_player = 0

    def ai_move_coordinate(self, temp=0.1, temp_decay=1.0):
        board_tensor = torch.Tensor()
        board_tensor = torch.cat((board_tensor, self.board_tensor.unsqueeze(0)))
        board_tensor = board_tensor.to(self.device)
        made_moves = 121 - len(self._choices)
        with torch.no_grad():
            output_tensor = self.model(board_tensor)
        if temp < 0.1:
            p = output_tensor.argmax(1)
        else:
            p = Categorical(logits=output_tensor / (temp*temp_decay**made_moves)).sample()
        p = p.item()
        if self.current_player:
            p = p // 11 + (p % 11) * 11
        return p // 11, p % 11

    def run(self):
        """A finite-state machine that cycles through waiting for input
        and sending moves.
        """
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
            pos = self.ai_move_coordinate()
            self.last_move = pos  # must keep
            print('our move', pos)
            self._s.sendall(bytes(f"{pos[0]},{pos[1]}\n", "utf-8"))
        elif self._turn_count == 2:  # 我们是后手
            print("we make the second move")
            pos = self.ai_move_coordinate()
            if pos == self.opponent_move:  # 这里证明 ai agent选择了swap
                print("ai agent swapped")
                self._s.sendall(bytes("SWAP\n", "utf-8"))
            else:  # 这里证明 ai agent没有选择swap
                print("ai agent did not swap")
                self.last_move = pos
                print('our move', pos)
                self._s.sendall(bytes(f"{pos[0]},{pos[1]}\n", "utf-8"))
        else:  # 之后的回合
            pos = self.ai_move_coordinate()
            self.last_move = pos
            print('our move', pos)
            self._s.sendall(bytes(f"{pos[0]},{pos[1]}\n", "utf-8"))

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
                # if anyone swaps
                self.logical_board_tensor[1][self.last_move] = 0.001
                self.board_tensor = torch.transpose(torch.roll(create_border(self.logical_board_tensor), 1, 0), 1, 2)
                # if opponent calls swap, that means opponent makes our last move, we need to do that on the ai board as well
                # 为什么这里是用！=去检查是不是对手的move，而后面却用==呢？这是因为在swap的指令里，data【-1】是我们即将变成的colour，如果我们现在的colour不等于data【-1】的colour，证明我们被swap了
                if data[-1] != self._colour:
                    print("Our opponent has swapped，our last move is", self.last_move)
                self._colour = self.opp_colour()
            else:
                x, y = data[1].split(",")
                self.logical_board_tensor[self.current_player][int(x), int(y)] = 1
                self.current_player = 1 - self.current_player
                self._choices.remove((int(x), int(y)))
                if data[-1] == self._colour:
                    self.opponent_move = int(x), int(y)
                    print('oppo', self.opponent_move)
            if self.current_player:
                self.board_tensor = torch.transpose(torch.roll(create_border(self.logical_board_tensor), 1, 0), 1, 2)
            else:
                self.board_tensor = create_border(self.logical_board_tensor)

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
    agent.run()
