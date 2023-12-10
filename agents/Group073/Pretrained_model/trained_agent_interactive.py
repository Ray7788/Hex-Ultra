#!/usr/bin/env python3
from trained_agent_board import Board
from trained_agent_game import MultiHexGame
from trained_agent_utils import load_model


class InteractiveGame:
    """
    allows to play a game against a model
    """

    def __init__(self, config):
        self.config = config
        self.model = load_model('agents/Group073/Pretrained_model/models/11_2w4_2000.pt')
        self.switch_allowed = self.config.getboolean("INTERACTIVE", 'switch', fallback=True)
        self.board = Board(size=self.model.board_size, switch_allowed=self.switch_allowed)
        self.game = MultiHexGame(
            boards=(self.board,),
            models=(self.model,),
            noise=None,
            noise_parameters=None,
            temperature=self.config.getfloat("INTERACTIVE", 'temperature', fallback=0.1),
            temperature_decay=self.config.getfloat("INTERACTIVE", 'temperature_decay', fallback=1.)
        )

    def play_move(self, move):
        self.board.set_stone(move)

    def undo_move(self):
        self.board.undo_move_board()
        # forgot know what the ratings were better not show anything

    def play_ai_move(self):
        move_ratings, correct_position = self.game.batched_single_move(self.model)
        return correct_position
