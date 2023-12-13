#!/usr/bin/env python3
from trained_agent_board import Board
from trained_agent_game import MultiHexGame
from trained_agent_utils import load_model


class InteractiveGame:
    """
    allows to play a game against a model
    """

    def __init__(self):
        self.model = load_model('agents/Group073/Pretrained_model_old_version1/models/11_2w4_2000.pt')
        self.board = Board(size=self.model.board_size)
        self.game = MultiHexGame(
            boards=(self.board,),
            models=(self.model,),
            temperature=0.1,
            temperature_decay=1.0
        )

    def play_move(self, move):
        self.board.set_stone(move)

    def play_ai_move(self):
        correct_position = self.game.batched_single_move(self.model)
        return correct_position
