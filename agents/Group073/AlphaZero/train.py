from DataLoader import HexStates
from net import AlphaZeroNet
from LossFunction import AlphaZeroLoss
from Simulation import AlphaZeroSimulator
import torch
import torch.utils.data as Data
import config as cfg

# hyper-parameters
BATCH_SIZE = cfg.BOARD_COL * cfg.BOARD_ROW
ITERATION = 10000
LR = 0.001  # learning rate

if __name__ == '__main__':
    # initialize model
    model = AlphaZeroNet()

    # initialize training devices
    train_device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # move the model to the training device
    model.to(train_device)

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

    # train
    for iteration in range(ITERATION):
        # get a simulation result
        game = AlphaZeroSimulator(model)
        game.simulate()
        game.board.visualization()

        # set the model to the "train" mode
        model.train()

        # initialize the dataset
        state_records = HexStates(game.state_queue)

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
        if iteration % 1000 == 0:
            # save model per epoch
            torch.save(model.state_dict(), './module/net' + str(iteration) + '.pkl')
        if iteration % 100 == 0:  # 假设每100次迭代保存一次
            checkpoint = {
                'iteration': iteration,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
            }
            torch.save(checkpoint, 'checkpoint.pth')

