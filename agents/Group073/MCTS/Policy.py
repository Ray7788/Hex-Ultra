import random
from State import State

def randomPolicy(state):
    """This policy chooses uniformly at random from the possible moves in a state"""
    while not state.isTerminal():
        try:
            action = random.choice(state.get_possible_actions())
        except IndexError:
            raise Exception("Non-terminal state has no possible actions: " + str(state))
        state = state.takeAction(action)
    return state.getReward()


class MCTSPolicy:
    def __init__(self):
        self.visits = {}
        self.wins = {}

    def get_action(self, state):
        if state not in self.visits:
            self.visits[state] = 0
            self.wins[state] = 0

        for _ in range(1000):  # 进行1000次模拟
            self.simulate(state)

        # 选择最佳动作
        best_action = None
        best_score = float('-inf')
        for action in self.get_possible_actions(state):
            score = self.wins[state, action] / self.visits[state, action]
            if score > best_score:
                best_action = action
                best_score = score

        return best_action

    def simulate(self, state):
        # 随机选择一个动作
        action = random.choice(self.get_possible_actions(state))
        next_state = self.get_next_state(state, action)

        # 模拟游戏直到结束
        while not self.is_terminal_state(next_state):
            action = random.choice(self.get_possible_actions(next_state))
            next_state = self.get_next_state(next_state, action)

        # 更新访问次数和胜利次数
        self.visits[state, action] += 1
        if self.is_winning_state(next_state):
            self.wins[state, action] += 1

    def get_possible_actions(self, state):
        # 返回可能的动作列表
        pass

    def get_next_state(self, state, action):
        # 返回执行动作后的下一个状态
        pass

    def is_terminal_state(self, state):
        # 判断是否为终止状态
        pass

    def is_winning_state(self, state):
        # 判断是否为胜利状态
        pass
