from torch.utils.data import Dataset
import torch
import config as cfg


class HexStates(Dataset):
    def __init__(self, state_queue):
        """
        training set
        """
        super(HexStates, self).__init__()
        self.state_queue = state_queue

    def __getitem__(self, index):
        """
        according to index obtain state
        :param index:
        :return:
        """
        game_state = self.state_queue[index]
        # obtain input of the model
        torch_input = torch.cat(

            [
                torch.from_numpy(game_state.board.numpy_board).type(torch.FloatTensor),
                torch.zeros(2, cfg.BOARD_ROW, cfg.BOARD_COL)
            ],

            dim=0)
        if game_state.initial_colour == "blue":
            # indicator channel for current player's colour: red=0, blue=1
            torch_input[-2, :, :] = 1
        if index == 1:
            # indicator for considering swap, 1 to consider swap at this state
            torch_input[-1, :, :] = 1
        # obtain labels
        pi = torch.from_numpy(game_state.pi)
        reward = game_state.reward
        return torch_input, pi, reward

    def __len__(self):
        return len(self.state_queue)