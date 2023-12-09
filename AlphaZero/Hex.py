import numpy as np
import config as cfg


class Node:
    """
    define a point on the board
    """

    def __init__(self, x, y):
        self.x = x  # horizontal coord
        self.y = y  # vertical coord
        self.colour = None  # red, blue or None
        self.occupied = False  # indicates if the position is occupied
        self.neighbours = []  # saving indices of neighbours of the position
        self.source = None  # 0 for start, 1 for end

    def occupy(self, colour):
        # occupy the node
        self.occupied = True
        self.colour = colour
        # update source of the node
        self.update_source()

    def update_source(self):
        """
        update the source of the node
        """
        if self.colour == "blue":
            # blue for horizontal connection
            if self.x == 0:
                # the node is at the start end
                self.source = 0
            elif self.x == cfg.BOARD_COL - 1:
                # the node is at the end
                self.source = 1
            else:
                # the node share the same source with its neighbours
                for neighbour in self.neighbours:
                    if neighbour.occupied and self.colour == neighbour.colour and neighbour.source is not None:
                        # update the node's source
                        self.source = neighbour.source
                        break
        elif self.colour == "red":
            # red for vertical connection
            if self.y == 0:
                # the node is at the start end
                self.source = 0
            elif self.y == cfg.BOARD_ROW - 1:
                # the node is at the end
                self.source = 1
            else:
                # the node share the same source with its neighbours
                for neighbour in self.neighbours:
                    if neighbour.occupied and self.colour == neighbour.colour and neighbour.source is not None:
                        # update the node's source
                        self.source = neighbour.source
                        break
        # if the node has a source now, then update the source of its neighbours which don't have any source
        if self.source is not None:
            for neighbour in self.neighbours:
                if neighbour.occupied and self.colour == neighbour.colour and neighbour.source is None:
                    # update the neighbour's source
                    neighbour.update_source()

    def checkConnection(self):
        """
        return true if a connection detected, otherwise return false
        """
        for neighbour in self.neighbours:
            if neighbour.occupied and self.colour == neighbour.colour and self.source != neighbour.source:
                return True
        return False


class HexBoard:
    """
    define the board represented by a graph
    """

    def __init__(self, row, col):
        self.row = row
        self.col = col
        # initialize an empty board
        # self.numpy_board = np.zeros((cfg.MEMORY_LENGTH * 2, row,
        #                              col), dtype=np.uint8)  # (upper_half, :, :) for red stones where 1 indicates existence in the latest up_half rounds , otherwise 0, and (lower_half, :, :) for blue stones
        # initialize a numpy array to store available positions on the board
        self.available_positions = np.ones((cfg.BOARD_ROW, cfg.BOARD_COL), dtype=np.bool_)
        # initialize the board graph
        self.board_graph = []
        self._initialization()

    def _initialization(self):
        """
        initialization of the board
        """

        def _isValid(x, y):
            """
            judge if a coord is valid
            x: horizontal coord
            y: vertical coord
            """
            if 0 <= x <= self.col - 1 and 0 <= y <= self.row - 1:
                return True
            else:
                return False

        # create nodes
        for i in range(self.row):
            rows = []
            for j in range(self.col):
                # initialize a node for the position
                node = Node(x=j, y=i)
                rows.append(node)
            self.board_graph.append(rows)
        # link neighbours
        for i in range(self.row):
            for j in range(self.col):
                for y, x in [(i, j - 1), (i, j + 1), (i - 1, j), (i + 1, j), (i + 1, j - 1), (i - 1, j + 1)]:
                    if _isValid(x, y):
                        self.board_graph[i][j].neighbours.append(self.board_graph[y][x])

    def drop_stone(self, x, y, colour):
        """
        drop a stone at an unoccupied position, return True if red wins, False if blue wins, otherwise return None
        """
        # assert the position is not occupied
        assert self.board_graph[y][x].occupied is False and self.available_positions[y, x], f"({x}, {y}) has been occupied!"

        # update the board
        self.board_graph[y][x].occupy(colour)
        self.available_positions[y, x] = False

        # check if the game ends after the drop
        if self.board_graph[y][x].checkConnection():
            return colour == "red"
        else:
            return None

    def updateNumpyBoard(self, x, y, colour):
        """
        update the input of the AlphaZero
        """
        # assert the position is not occupied
        assert self.numpy_board[0, y, x] == 0 and self.numpy_board[
            cfg.MEMORY_LENGTH, y, x] == 0, f"({x}, {y}) has been occupied!"

        # update the board
        if colour == "red":
            self.numpy_board[1:cfg.MEMORY_LENGTH, :, :] = self.numpy_board[0:cfg.MEMORY_LENGTH - 1, :, :]
            self.numpy_board[0, y, x] = 1
        else:
            self.numpy_board[cfg.MEMORY_LENGTH + 1:, :, :] = self.numpy_board[
                                                             cfg.MEMORY_LENGTH: cfg.MEMORY_LENGTH * 2 - 1, :, :]
            self.numpy_board[cfg.MEMORY_LENGTH, y, x] = 1

    def visualization(self):
        """
        print the board on the screen
        """
        for i in range(self.row):
            rows = []
            for j in range(self.col):
                if self.board_graph[i][j].occupied:
                    if self.board_graph[i][j].colour == "red":
                        rows.append("R")
                    else:
                        rows.append("B")
                else:
                    rows.append("*")
            rows = ' '.join(rows)
            print(" " * i + rows)

if __name__ == "__main__":
    from net import StupidAgent
    for _ in range(1):
        player1 = StupidAgent(colour="red")
        player2 = StupidAgent(colour="blue")
        board = HexBoard(cfg.BOARD_ROW, cfg.BOARD_COL)
        current_player = player1
        for step in range(cfg.BOARD_ROW * cfg.BOARD_COL):
            # obtain decision of the current player
            x, y = current_player.random_decision()
            # update the board and obtain the winner
            winner = board.drop_stone(x, y, current_player.returnColour())
            # end the game if a winner is found
            if winner is not None:
                break
            # update the opposite player's board
            opposite_player = player1 if player2 == current_player else player2
            opposite_player.updateBoard(x, y, current_player.returnColour())
            # update current player
            current_player = opposite_player
            # visualization
            board.visualization()

        if winner:
            print("red")
            if player1.returnColour() == "red":
                print(f"Player1 ({player1.returnColour()}) wins!!!")
            else:
                print(f"Player2 ({player2.returnColour()}) wins!!!")
        else:
            print("blue")
            if player1.returnColour() == "blue":
                print(f"Player1 ({player1.returnColour()}) wins!!!")
            else:
                print(f"Player2 ({player2.returnColour()}) wins!!!")
        board.visualization()