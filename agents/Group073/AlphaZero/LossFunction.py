import torch
import torch.nn as nn


class AlphaZeroLoss(nn.Module):
    def __init__(self):
        super(AlphaZeroLoss, self).__init__()

    def forward(self, policies, values, distributions, rewards):
        """
        calculate loss function
        :param policies: policies given by the model
        :param values: values given by the model
        :param distributions: label of policies
        :param rewards: label of values
        :return:
        """
        # obtain batch size
        batch_size = policies.size(0)
        return torch.sum((values.squeeze(1) - rewards)**2) / batch_size - torch.sum(distributions * torch.log(torch.softmax(policies, dim=1))) / batch_size