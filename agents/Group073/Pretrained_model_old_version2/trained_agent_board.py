import torch

def to_move(move_idx, board_size):
    return move_idx // board_size, move_idx % board_size
def get_neighbours(position, size):
    x = int(position[0])
    y = int(position[1])

    assert 0 <= x < size
    assert 0 <= y < size

    neighbours = set([(x-1, y), (x-1, y+1), (x, y-1), (x, y+1), (x+1, y-1), (x+1, y)])

    if x == 0:
        neighbours.discard((x-1, y))
        neighbours.discard((x-1, y+1))
    elif x == size-1:
        neighbours.discard((x+1, y-1))
        neighbours.discard((x+1, y))

    if y == 0:
        neighbours.discard((x, y-1))
        neighbours.discard((x+1, y-1))
    elif y == size-1:
        neighbours.discard((x-1, y+1))
        neighbours.discard((x, y+1))

    return neighbours


def update_connected_sets_check_win(connected_sets, player, position, size):
    '''
    save a set of tuple of sets:
    the first set is a connected component of stones
    the second set is the indices of these stones in the direction of the player > change to intervall [,]
    thus the winning condition is having 0 and (size-1) in one of the second sets
    '''
    new_connected_sets = []

    if player == 0:
        new_connected_set = (set([position]), set([position[0]]))
    elif player == 1:
        new_connected_set = (set([position]), set([position[1]]))

    neighbours = get_neighbours(position, size)

    for connected_set in connected_sets:
        if not connected_set[0].isdisjoint(neighbours):
            new_connected_set[0].update(connected_set[0])
            new_connected_set[1].update(connected_set[1])
        else:
            new_connected_sets.append(connected_set)

    new_connected_sets.append(new_connected_set)

    if set([0, size-1]).issubset(new_connected_set[1]):
        return new_connected_sets, [player]
    else:
        return new_connected_sets, False


class Board:
    """
    Board is in quadratic shape. This means diagonal neighbours are upper right and lower left, but not the other two.
    There are three layers: The first layer is for stones of the first player, second layer for second player and the third layer stores indicates whose turn it is.
    First player has to connect his stones on the first dimension (displayed top to bottom), second player on the second dimension (displayed left to right).
    If the second player decides to switch, a stone is set in the second layer that is only information.
    The second player becomes the first player and now plays the first layer and vice-versa.
    """
    def __init__(self, size, switch_allowed=True):
        self.size = size
        self.logical_board_tensor = torch.zeros([2, self.size, self.size])
        self.board_tensor = self.set_border(self.logical_board_tensor)
        self.made_moves = set()
        self.legal_moves = set([(idx1, idx2) for idx1 in range(self.size) for idx2 in range(self.size)])
        self.connected_sets = [[], []]
        self.player = 0
        self.switch = False
        self.winner = False
        self.switch_allowed = switch_allowed

    def set_border(self, board_tensor):
        border = torch.zeros([2, self.size+2, self.size+2])
        border[0, 0, 1:-1] = 1
        border[0, -1, 1:-1] = 1
        border[1, 1:-1, 0] = 1
        border[1, 1:-1, -1] = 1
        border[:, 1:-1, 1:-1] = board_tensor
        return border

    def set_stone(self, position):
        if type(position) is int:
            print("1")
            position = to_move(position, self.size)

        if position in self.legal_moves:
            print("2")
            if len(self.made_moves) > 1:
                print("3")
                self.legal_moves.remove(position)

            elif len(self.made_moves) == 1:
                print("4")
                if set([position]) == self.made_moves:
                    print("5")
                    self.switch = True
                    self.legal_moves.remove(position)
                    self.logical_board_tensor[1][position] = 0.001
                    self.board_tensor = torch.transpose(torch.roll(self.set_border(self.logical_board_tensor), 1, 0), 1, 2)
                    return

                else:
                    print("6")
                    self.legal_moves -= self.made_moves
                    self.legal_moves.remove(position)

            elif len(self.made_moves) == 0 and not self.switch_allowed:
                print("7")
                self.legal_moves.remove(position)
                self.logical_board_tensor[1][position] = 0.001
            print("8")
            self.made_moves.update([position])
            self.logical_board_tensor[self.player][position] = 1
            self.connected_sets[self.player], self.winner = update_connected_sets_check_win(self.connected_sets[self.player], self.player, position, self.size)

            if self.winner:
                print("9")
                if self.switch:
                    print("10")
                    self.winner = [[1], [0]][self.winner[0]]
                self.legal_moves = set()
            print("11")
            self.player = 1-self.player
            if self.player:
                print("12")
                self.board_tensor = torch.transpose(torch.roll(self.set_border(
                    self.logical_board_tensor), 1, 0), 1, 2)
            else:
                print("13")
                self.board_tensor = self.set_border(self.logical_board_tensor)