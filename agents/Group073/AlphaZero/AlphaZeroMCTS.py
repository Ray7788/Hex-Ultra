import copy
import numpy as np
from Hex import HexBoard
import config as cfg
import torch
import torch.nn.functional as F
from tqdm import tqdm


class Action:
    """
    an action
    """

    def __init__(self, x=None, y=None, swap=None, board=None, current_player=None, opposite_player=None,
                 father_state=None):
        self.x = x  # horizontal coord to put the stone
        self.y = y  # vertical coord to put the stone
        self.swap = swap  # True: the action only swaps two sides without making any movements; False: the subsequent sub-state should consider swap, None: don't consider swap
        self.board = board  # the board situation before the execution of the action
        self.current_player = current_player  # the player taking the action
        self.opposite_player = opposite_player  # the opposite player
        self.father_state = father_state  # the state before the execution of the action
        self.sub_state = None  # the next state after the execution of the action
        self.Nv = 0  # the number of times that the state resulted in by the action has been visited
        self.Qv = 0  # accumulated rewards of the state resulted in by the action
        self.Uv = 0  # explore component of upper bound confidence bound resulted in by the action

    def execute(self):
        """
        execute the action and create a new state or reach the end
        """
        # copy a new board for the sub-state
        board = copy.deepcopy(self.board)
        if self.swap is None:
            # the action doesn't swap two sides
            winner = board.drop_stone(x=self.x, y=self.y, colour=self.current_player.returnColour())
            # check if a winner detected
            if winner is not None:
                # return the colour of the winner
                winner_colour = "red" if winner else "blue"
                # initialize an end sub-state
                self.sub_state = State(current_player=self.opposite_player, opposite_player=self.current_player,
                                       board=board, father_state=self.father_state, father_action=self,
                                       consider_swap=None, end=True,
                                       winner_colour=winner_colour, isLeaf=True, isRoot=False)
            else:
                # obtain the sub-state
                self.sub_state = State(current_player=self.opposite_player, opposite_player=self.current_player,
                                       board=board, father_state=self.father_state, father_action=self,
                                       consider_swap=None, isLeaf=True, isRoot=False)
        elif self.swap:
            # this action only swap the two sides
            self.current_player.swap = True
            self.opposite_player.swap = True
            # obtain the sub-state
            self.sub_state = State(current_player=self.opposite_player, opposite_player=self.current_player,
                                   board=board, father_state=self.father_state, father_action=self, consider_swap=None,
                                   isLeaf=True, isRoot=False)
        else:
            # sub-state should consider swap
            winner = board.drop_stone(x=self.x, y=self.y, colour=self.current_player.returnColour())
            # check if a winner detected
            if winner is not None:
                # this branch is not necessary unless the board is 1x1
                # return the colour of the winner
                winner_colour = "red" if winner else "blue"
                # initialize an end sub-state
                self.sub_state = State(current_player=self.opposite_player, opposite_player=self.current_player,
                                       board=board, father_state=self.father_state, father_action=self,
                                       consider_swap=True, end=True,
                                       winner_colour=winner_colour, isLeaf=True, isRoot=False)
            else:
                # obtain the sub-state
                self.sub_state = State(current_player=self.opposite_player, opposite_player=self.current_player,
                                       board=board, father_state=self.father_state, father_action=self,
                                       consider_swap=True, isLeaf=True, isRoot=False)

    def _update(self, V):
        """
        update parameters of the state
        reward: reward of this search
        N: the number of total search
        """
        self.Nv += 1
        self.Qv += V


class State:
    """
    a state of MCT
    """

    def __init__(self, current_player, opposite_player, board, father_state=None, father_action=None,
                 consider_swap=None, end=False,
                 winner_colour=None, isLeaf=True, isRoot=False):
        self.current_player = current_player  # the player of the state to make an action
        self.opposite_player = opposite_player  # the opposite player
        self.board = board  # current board situation of the state
        self.father_state = father_state  # the state before the current state
        self.father_action = father_action  # the action leading to the state
        self.actions = []  # legal actions that can be taken by the state
        self.consider_swap = consider_swap  # True: consider swap in this state, False: consider swap in the sub-state, None: don't consider swap
        self.end = end  # indicate if the state is an end of the game and no more action shall be taken
        self.winner_colour = winner_colour  # the colour of the winner at this state when the state is an end
        self.isLeaf = isLeaf  # indicates if the state is a leaf
        self.isRoot = isRoot  # indicates if the state is the root
        if not end:
            # initialization every actions
            self._initialization()

    def _initialization(self):
        """
        initialize every action can be taken by the state
        """
        # initialize meshgrid
        xs, ys = np.meshgrid(np.arange(cfg.BOARD_COL), np.arange(cfg.BOARD_ROW))
        meshgrid = np.stack([xs, ys], axis=0)
        # obtain available positions on the board
        available_coords = meshgrid[:, self.board.available_positions].T.tolist()
        # create actions
        if self.consider_swap is None:
            # don't consider swap
            self.actions = [Action(x=x, y=y, board=self.board, current_player=self.current_player,
                                   opposite_player=self.opposite_player, father_state=self, swap=None)
                            for x, y in available_coords]
        elif self.consider_swap:
            # consider swap in this state
            self.actions = [Action(x=x, y=y, board=self.board, current_player=self.current_player,
                                   opposite_player=self.opposite_player, father_state=self, swap=None)
                            for x, y in available_coords]
            self.actions.append(Action(x=None, y=None, board=self.board, current_player=self.current_player,
                                       opposite_player=self.opposite_player, father_state=self, swap=True))
        else:
            # consider swap in sub-states
            self.actions = [Action(x=x, y=y, board=self.board, current_player=self.current_player,
                                   opposite_player=self.opposite_player, father_state=self, swap=False)
                            for x, y in available_coords]

    @staticmethod
    def returnVisitedTimes(action):
        # return the visted times of an action according to the current state
        return action.Nv

    @staticmethod
    def returnUCB(action):
        # return the UCB of an action's leading result according to the current state
        return action.Qv / max(1, action.Nv) + cfg.UCB_C * action.Uv / (1 + action.Nv)

    def search(self, net, device, train=False):
        """
        conduct search for one round
        net: AlphaZero model
        N: the total of search times
        """
        if not self.end:
            if self.isLeaf:
                # expand the node if it is a leaf (including the root) and is not end of the game
                with torch.no_grad():
                    # obtain the input of the model
                    if self.current_player.returnColour() == "blue":
                        # flip the board when the colour is blue
                        board_situation = torch.from_numpy(np.flip(np.rot90(self.board.numpy_board, axes=(-2, -1)), axis=-1).copy()).type(torch.FloatTensor).unsqueeze(0).to(device)
                    else:
                        board_situation = torch.from_numpy(self.board.numpy_board).type(torch.FloatTensor).unsqueeze(0).to(device)
                    # obtain the policy and value of the node
                    policies, value = net(board_situation)
                    value = value[0, 0].detach().cpu().numpy()
                    # policies for dropping stones
                    xy_policies = policies.reshape(cfg.BOARD_ROW, cfg.BOARD_COL).detach().cpu().numpy()
                    if self.current_player.returnColour() == "blue":
                        # flip the decision when the colour is blue
                        xy_policies = np.rot90(np.flip(np.flip(np.rot90(xy_policies, axes=(-2, -1)), axis=-1), axis=-1), k=3, axes=(-2, -1))
                    xy_policies = torch.from_numpy(xy_policies)
                    # softmax on feasible actions
                    xy_policies[torch.from_numpy(self.board.available_positions)] = F.softmax(
                            xy_policies[torch.from_numpy(self.board.available_positions)])
                    xy_policies = xy_policies.numpy()
                    # policies for swap
                    swap_policies = cfg.SWAP_POLICY
                    # initialize all sub-states of the node by executing all actions of it
                    for action in self.actions:
                        # update U of the sub-state including end of the game
                        action.Uv = swap_policies if action.y is None and action.x is None else xy_policies[
                            action.y, action.x]
                    # backpropagation
                    self.backpropagation(value)
                # the root should check every actions
                if self.isRoot:
                    for action in self.actions:
                        action.execute()
                        action.sub_state.search(net, device)
                self.isLeaf = False
            else:
                # select any one visited action
                action = max(self.actions, key=self.returnUCB)
                # i the sub-state has not been visited before
                if action.sub_state is None:
                    action.execute()
                # move to the sub-state
                action.sub_state.search(net, device)
        else:
            # the node is an end of the game
            # update Q of the state if it is an end of the game
            value = 1 if self.current_player.returnColour() == self.winner_colour else -1
            # backpropagation
            self.backpropagation(value)

    def backpropagation(self, V):
        """
        update all the states on the search path
        N: the total of search times
        """
        reward = V
        # obtain the current state to be updated
        current_state = self
        while True:
            # break when reach the root
            if current_state.father_action is None:
                break
            # update
            current_state.father_action._update(V=-reward)
            # move to the father state
            reward = - reward
            current_state = current_state.father_state


class AlphaZeroMCTS:
    """
    Monte Carlo Tree Search of AlphaZero
    """

    def __init__(self, net, current_player, opposite_player, board=None, step=0, device="cuda:0"):
        self.net = net  # AlphaZero net
        self.net.eval()
        self.current_player = copy.deepcopy(current_player)  # imagine a player of the root of the tree
        self.opposite_player = copy.deepcopy(opposite_player)  # imagine the player opposite to the current player
        self.board = copy.deepcopy(board) if board is not None else HexBoard(row=cfg.BOARD_ROW,
                                                                             col=cfg.BOARD_COL)  # the board up-till
        self.step = step  # current time "stamp" of the game, starting from 0
        self.device = device  # device
        # initialize the root state of the tree
        if step == 0:
            # the root should make its sub-state consider swap
            self.root = State(current_player=self.current_player,
                              opposite_player=self.opposite_player,
                              board=self.board, consider_swap=False, isLeaf=True, isRoot=True)
        elif step == 1:
            # the root should consider swap
            self.root = State(current_player=self.current_player,
                              opposite_player=self.opposite_player,
                              board=self.board, consider_swap=True, isLeaf=True, isRoot=True)
        else:
            # without considering swap
            self.root = State(current_player=self.current_player,
                              opposite_player=self.opposite_player,
                              board=self.board, consider_swap=None, isLeaf=True, isRoot=True)

    def search(self, iterations=1000, returnDistribution=True, train=True):
        """
        MCT search
        iterations: the total number of seaches
        returnDistribution: whether to return pi
        return x, y of the position to drop the stone
        """
        for N in range(1, iterations + 1):
            self.root.search(net=self.net, device=self.device, train=train)
            if self.step == 0 or self.step == 1:
                # reset the swap of the two agents
                self.current_player.swap = False
                self.opposite_player.swap = False
        # print("\n")
        # return the action whose subsequent states give the highest reward to the current player
        # action = max(self.root.actions, key=self.root.returnVisitedTimes)
        action = max(self.root.actions, key=self.root.returnUCB)
        decesion_x, decision_y = action.x, action.y
        if not returnDistribution:
            return action.x, action.y, None
        else:
            # obtain visited times of each action
            pi_xy = np.zeros((cfg.BOARD_ROW, cfg.BOARD_COL))
            # pi_xy = - iterations * np.ones((cfg.BOARD_ROW, cfg.BOARD_COL), dtype=np.float32)
            pi_swap = 0.0
            for action in self.root.actions:
                if action.x is None and action.y is None:
                    # update pi of swap
                    pi_swap = self.root.returnVisitedTimes(action)
                else:
                    # update pi for dropping stones
                    pi_xy[action.y, action.x] = self.root.returnVisitedTimes(action)
            pi = np.append(pi_xy.reshape(-1), pi_swap)
            pi = pi ** (1 / cfg.TAO)
            # normalization
            pi = pi / np.sum(pi)
            return decesion_x, decision_y, pi
