from torch.utils.data import Dataset
import torch
import config as cfg
import numpy as np


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
        if game_state.initial_colour == "blue":
            # flip the board when the colour is blue
            board_situation = np.flip(np.rot90(game_state.board.numpy_board, axes=(-2, -1)), axis=-1).copy()
            board_situation[board_situation != 0] = 3 - board_situation[board_situation != 0]
            torch_input = torch.from_numpy(board_situation).type(torch.FloatTensor)
            # obtain labels
            pi = torch.from_numpy(np.flip(np.rot90(game_state.pi.reshape(cfg.BOARD_ROW, cfg.BOARD_COL), axes=(-2, -1)), axis=-1).copy().reshape(-1))
        else:
            torch_input = torch.from_numpy(game_state.board.numpy_board).type(torch.FloatTensor)
            # obtain labels
            pi = torch.from_numpy(game_state.pi)
        reward = game_state.reward
        return torch_input, pi, reward

    def __len__(self):
        return len(self.state_queue)