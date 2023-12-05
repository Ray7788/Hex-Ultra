import copy
import os

from DataLoader import HexStates
from net import AlphaZeroNet
from LossFunction import AlphaZeroLoss
from Simulation import AlphaZeroSimulator
import torch
import torch.utils.data as Data
import config as cfg
import multiprocessing
import random
import time
import warnings

warnings.filterwarnings("ignore")


def returnGame(model1, model2, queue, device):
    """
    return one simulation with the model
    """
    model1.eval()
    model1.to(device)
    model2.eval()
    model2.to(device)
    game = AlphaZeroSimulator(model1, model2, device=device)
    game.simulate()
    game.board.visualization()
    queue.put(game.state_queue)


def history_model_manager(model_queue, state_queue, process_num, model_num, device):
    """
    process_num: the upper number of sub-processes
    model_num: the upper number of models
    """
    # initialize model list
    models = []
    # initialize sub-processes list
    processes = []
    # generate simulation games with multiprocessing
    while True:
        # load a model
        try:
            new_model = model_queue.get(timeout=1)
            if new_model == "end":
                # finish when the training is finished
                break
            models.append(new_model)
        except:
            # load a history model with a probability of 1%
            if random.randint(0, 99) == 1:
                # initialize existing list of history nets
                history_models = []
                for net_name in os.listdir("./module"):
                    if "net" in net_name:
                        history_models.append(net_name)
                if len(history_models) > 0:
                    new_model = AlphaZeroNet()
                    new_model.load_state_dict(torch.load("./module/" + random.choice(history_models)))
                    new_model.cpu()
                    models.append(new_model)
        # remove old models
        if len(models) > model_num:
            models = models[-model_num:]
        # remove subprocesses which have finished
        for process in processes[:]:
            if not process.is_alive():
                processes.remove(process)
        # start new sub-process to simulate games
        if len(processes) < process_num:
            for _ in range(process_num - len(processes)):
                # create a new sub-process
                p = multiprocessing.Process(target=returnGame,
                                            args=(random.choice(models), random.choice(models), state_queue, device))
                p.start()
                processes.append(p)


# hyper-parameters
BATCH_SIZE = cfg.BOARD_COL * cfg.BOARD_ROW
ITERATION = 1000000
LR = 0.0001  # learning rate

if __name__ == '__main__':
    print("training start")
    start = 0

    # initialize queue for model and state transformation
    model_queue = multiprocessing.Queue()
    state_queue = multiprocessing.Queue()

    # initialize model
    model = AlphaZeroNet()
    if start != 0:
        model.load_state_dict(torch.load("./module/net" + str(start) + ".pkl"))

    # initialize training devices
    train_device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # put the model in the model queue
    model.cpu()
    model_queue.put(copy.deepcopy(model))
    # move the model to the training device
    model.to(train_device)

    # initialize the simulation manager
    process_num = 1
    model_num = 12
    simulation_manager = multiprocessing.Process(target=history_model_manager,
                                                 args=(model_queue, state_queue, process_num, model_num, "cpu",))
    # start the simulation
    print("start simulation")
    simulation_manager.start()

    # set the model to the "train" mode
    model.train()

    # initialize loss function
    loss_func = AlphaZeroLoss()

    # initialize optimizer
    weight_params = []
    bias_params = []
    for name, param in model.named_parameters():
        if 'bias' in name:
            bias_params.append(param)
        else:
            weight_params.append(param)
    optimizer = torch.optim.Adam([
        {'params': weight_params, 'weight_decay': 0.001},
        {'params': bias_params, 'weight_decay': 0.0}
    ], lr=LR)
    if start != 0:
        optimizer.load_state_dict(torch.load("./module/optimizer" + str(start) + ".pkl"))

    # train
    for iteration in range(start + 1, ITERATION):
        # get a simulation result
        states = state_queue.get()

        # set the model to the "train" mode
        model.train()

        # initialize the dataset
        state_records = HexStates(states)

        # initialize the dataloader
        loader = Data.DataLoader(
            dataset=state_records,  # torch TensorDataset format
            batch_size=BATCH_SIZE,  # mini batch size
            shuffle=True,  # it is good to shuffle the dataset
            pin_memory=True,
            drop_last=False,
            num_workers=1,  # load the data with multiple threads
        )

        # go through every states
        for torch_inputs, pis, rewards in loader:
            # move the images to the training device
            torch_inputs = torch_inputs.to(train_device)
            pis = pis.to(train_device)
            rewards = rewards.to(train_device)
            # obtain the output of the model
            policies, values = model(torch_inputs)
            # calculate loss function
            loss = loss_func(policies, values, pis, rewards)
            # update parameters
            optimizer.zero_grad()  # clear the history accumulated gradients
            loss.backward()  # back propagation
            optimizer.step()  # gradient decent
            # print process
            print('iteration:', iteration, '|train loss:%.4f' % loss)
        if iteration % 4 == 0:
            # update model queue
            model.cpu()
            model_queue.put(copy.deepcopy(model))
            model.to(train_device)
        if iteration % 1000 == 0:
            # save model per epoch
            model.cpu()
            torch.save(model.state_dict(), './module/net' + str(iteration) + '.pkl')
            torch.save(optimizer.state_dict(), './module/optimizer' + str(iteration) + '.pkl')
            model.to(train_device)
    model_queue.put("end")
