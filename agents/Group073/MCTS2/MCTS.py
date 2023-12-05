import copy
import numpy as np
import math
from MCTS2.Hex import HexBoard
import MCTS2.config as cfg
import random
from MCTS2.StupidAgent import StupidAgent
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
        self.winner_colour = None  # winner's colour of the state taking this action when the action directly leads to an end

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
                self.winner_colour = "red" if winner else "blue"
                return self.winner_colour
            else:
                # obtain the sub-state
                self.sub_state = State(current_player=self.opposite_player, opposite_player=self.current_player,
                                       board=board, father_state=self.father_state, consider_swap=None)
                return None
        elif self.swap:
            # this action only swap the two sides
            self.current_player.swap = True
            self.opposite_player.swap = True
            # obtain the sub-state
            self.sub_state = State(current_player=self.opposite_player, opposite_player=self.current_player,
                                   board=board, father_state=self.father_state, consider_swap=None)
            return None
        else:
            # sub-state should consider swap
            winner = board.drop_stone(x=self.x, y=self.y, colour=self.current_player.returnColour())
            # check if a winner detected
            if winner is not None:
                # this branch is not necessary unless the board is 1x1
                # return the colour of the winner
                self.winner_colour = "red" if winner else "blue"
                return self.winner_colour
            else:
                # obtain the sub-state
                self.sub_state = State(current_player=self.opposite_player, opposite_player=self.current_player,
                                       board=board, father_state=self.father_state, consider_swap=True)
                return None


class State:
    """
    a state of MCT
    """

    def __init__(self, current_player, opposite_player, board, father_state=None, consider_swap=None):
        self.current_player = current_player  # the player of the state to make an action
        self.opposite_player = opposite_player  # the opposite player
        self.board = board  # current board situation of the state
        self.father_state = father_state  # the state before the current state
        self.unseen_actions = []  # actions which have not been searched
        self.visited_actions = []  # actions have been searched
        self.Nv = 0  # the number of times that the state has been visited
        self.Qv = 0  # accumulated rewards of the state
        self.explore = 0  # explore component of upper bound confidence bound
        self.consider_swap = consider_swap  # True: consider swap in this state, False: consider swap in the sub-state, None: don't consider swap
        # initialization every unseen actions
        self._initialization()

    def _update(self, reward, N):
        """
        update parameters of the state
        reward: reward of this search
        N: the number of total search
        """
        self.Nv += 1
        self.Qv += reward
        self.explore = cfg.UCB_C * math.sqrt(2 * math.log(self.Nv) / N)

    def _initialization(self):
        """
        initialize every action can be taken by the state
        """
        # initialize meshgrid
        xs, ys = np.meshgrid(np.arange(cfg.BOARD_COL), np.arange(cfg.BOARD_ROW))
        meshgrid = np.stack([xs, ys], axis=0)
        # obtain available positions on the board
        available_coords = meshgrid[:, self.board.available_positions].T.tolist()
        # print(f"available_coords: {available_coords}")
        # create actions
        if self.consider_swap is None:
            # don't consider swap
            self.unseen_actions = [Action(x=x, y=y, board=self.board, current_player=self.current_player,
                                          opposite_player=self.opposite_player, father_state=self, swap=None)
                                   for x, y in available_coords]
        elif self.consider_swap:
            # consider swap in this state
            self.unseen_actions = [Action(x=x, y=y, board=self.board, current_player=self.current_player,
                                          opposite_player=self.opposite_player, father_state=self, swap=None)
                                   for x, y in available_coords]
            self.unseen_actions.append(Action(x=None, y=None, board=self.board, current_player=self.current_player,
                                              opposite_player=self.opposite_player, father_state=self, swap=True))
        else:
            # consider swap in sub-states
            self.unseen_actions = [Action(x=x, y=y, board=self.board, current_player=self.current_player,
                                          opposite_player=self.opposite_player, father_state=self, swap=False)
                                   for x, y in available_coords]
        # shuffle these actions
        random.shuffle(self.unseen_actions)

    @staticmethod
    def returnAverageReward(action):
        # return the UCB of an action's leading result according to the current state
        if action.sub_state is None:
            # this action leads to an end
            return 1 if action.winner_colour == action.father_state.current_player.returnColour() else -1
        else:
            return - action.sub_state.Qv / action.sub_state.Nv

    @staticmethod
    def returnUCB(action):
        # return the UCB of an action's leading result according to the current state
        if action.sub_state is None:
            # this action leads to an end
            return 1 if action.winner_colour == action.father_state.current_player.returnColour() else -1
        else:
            return - action.sub_state.Qv / action.sub_state.Nv + action.sub_state.explore

    def search(self, N, step):
        """
        conduct search for one round
        N: the total of search times
        """

        if self.father_state is not None and self.Nv == 0:
            # simulation if the node is a leaf and not the root
            reward = self.simulation(step=step)
            # backpropagation
            self.backpropagation(reward, N)
        elif len(self.unseen_actions) > 0:
            # select an unseen action
            action = self.unseen_actions.pop()
            self.visited_actions.append(action)
            # expansion (it may reach the end)
            winner_colour = action.execute()
            # if a winner generated
            if winner_colour is not None:
                # judge the reward
                reward = 1 if self.current_player.returnColour() == winner_colour else -1
                # backpropagation
                self.backpropagation(reward, N)
            else:
                # move to the sub-state if it is not the end
                action.sub_state.search(N, step=step+1)
        else:
            # select any one visited action
            action = max(self.visited_actions, key=self.returnUCB)
            if action.sub_state is None:
                # if the action leads to an end
                # judge the reward
                reward = 1 if self.current_player.returnColour() == action.winner_colour else -1
                # backpropagation
                self.backpropagation(reward, N)
            else:
                # move to the sub-state if it is not the end
                action.sub_state.search(N, step=step+1)

    def simulation(self, step):
        """
        conduct simulation from the current state until an end
        """
        # initialize a board inheriting from the board of the current state for simulation
        board = copy.deepcopy(self.board)
        # initialize two agents which can only take random decisions
        player1 = StupidAgent(colour=self.current_player.returnColour(), board=board)
        player2 = StupidAgent(colour=self.opposite_player.returnColour(), board=board)
        # initialize current player to play, red first by default, and opposite player
        current_player = player1
        # swap happens in this simulation
        swap = False

        # initialize current step since the start of the game (not the start of the simulation)
        current_step = step
        # simulation
        for _ in range(board.row * board.col):
            # ask the current agent if it chooses swap
            if current_step == 1 and current_player.respondToSwap():
                player1.swap = True
                player2.swap = True
                swap = True
                # update current player
                current_player = player1 if player2 == current_player else player2
            # obtain decision of the current player
            x, y = current_player.random_decision()
            # update the board and obtain the winner
            winner = board.drop_stone(x, y, current_player.returnColour())
            # end the game if a winner is found
            if winner is not None:
                # if current player wins, make the value of the state 1
                if winner:
                    # red wins
                    if not swap:
                        return 1 if self.current_player.returnColour() == "red" else -1
                    else:
                        return -1 if self.current_player.returnColour() == "red" else 1
                else:
                    # blue wins
                    if not swap:
                        return 1 if self.current_player.returnColour() == "blue" else -1
                    else:
                        return -1 if self.current_player.returnColour() == "blue" else 1
            # update the opposite player's board
            opposite_player = player1 if player2 == current_player else player2
            opposite_player.updateBoard(x, y, current_player.returnColour())
            # update current player
            current_player = opposite_player
            # update step
            current_step += 1

    def backpropagation(self, reward, N):
        """
        update all the states on the search path
        N: the total of search times
        """
        # obtain the current state to be updated
        current_state = self
        while True:
            # break when reach the root
            if current_state.father_state is None:
                break
            # update
            current_state._update(reward=reward, N=N)
            # move to the father state
            reward = - reward
            current_state = current_state.father_state


class MCTS:
    """
    Naive Monte Carlo Tree Search
    """

    def __init__(self, current_player, opposite_player, board=None, step=0):
        self.current_player = copy.deepcopy(current_player)  # imagine a player of the root of the tree
        self.opposite_player = copy.deepcopy(opposite_player)  # imagine the player opposite to the current player
        self.board = copy.deepcopy(board) if board is not None else HexBoard(row=cfg.BOARD_ROW,
                                                                             col=cfg.BOARD_COL)  # the board up-till
        self.step = step    # current time "stamp" of the game, starting from 0
        # initialize the root state of the tree
        if step == 0:
            # the root should make its sub-state consider swap
            self.root = State(current_player=self.current_player,
                              opposite_player=self.opposite_player,
                              board=self.board, consider_swap=False)
        elif step == 1:
            # the root should consider swap
            self.root = State(current_player=self.current_player,
                              opposite_player=self.opposite_player,
                              board=self.board, consider_swap=True)
        else:
            # without considering swap
            self.root = State(current_player=self.current_player,
                              opposite_player=self.opposite_player,
                              board=self.board, consider_swap=None)

    def search(self, iterations=1000):
        """
        MCT search
        iterations: the total number of seaches
        return x, y of the position to drop the stone
        """
        xs, ys = np.meshgrid(np.arange(cfg.BOARD_COL), np.arange(cfg.BOARD_ROW))
        meshgrid = np.stack([xs, ys], axis=0)
        available_coords = meshgrid[:, self.board.available_positions].T.tolist()
        print(f"available_coords: {available_coords}")
        for N in tqdm(range(1, iterations + 1)):
            self.root.search(N=N, step=self.step)
            if self.step == 0 or self.step == 1:
                # reset the swap of the two agents
                self.current_player.swap = False
                self.opposite_player.swap = False
        print("\n")
        # return the action whose subsequent states give the highest reward to the current player
        action = max(self.root.visited_actions, key=self.root.returnAverageReward)
        return action.x, action.y
