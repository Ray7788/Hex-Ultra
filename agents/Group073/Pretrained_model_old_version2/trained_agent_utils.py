#!/usr/bin/env python3

import torch

import hexconvolution

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def create_model(config):
    board_size = config.getint('board_size')
    print(board_size)
    switch_model = config.getboolean('switch_model')
    rotation_model = config.getboolean('rotation_model')

    print(switch_model, rotation_model)
    print("layers", config.getint('layers'))
    print("reach", config.getint('reach'))

    model = hexconvolution.Conv(
        board_size=board_size,
        layers=config.getint('layers'),
        intermediate_channels=config.getint('intermediate_channels'),
        reach=config.getint('reach')
    )

    if not switch_model:
        model = hexconvolution.NoSwitchWrapperModel(model)

    if rotation_model:
        model = hexconvolution.RotationWrapperModel(model)

    return model


def correct_position1d(position1d, board_size, player):
    if player:
        print("if player", position1d // board_size + (position1d % board_size) * board_size)
        return position1d // board_size + (position1d % board_size) * board_size
    else:
        print("else player", position1d)
        return position1d


def load_model(model_file):
    checkpoint = torch.load(model_file, map_location=device)
    model = create_model(checkpoint['config'])
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    torch.no_grad()
    return model
