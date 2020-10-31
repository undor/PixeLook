import numpy as np
import torch
from torch import Tensor
from torch.autograd import Variable
from torch.nn import Linear, MSELoss, init, ReLU
from torch.optim import SGD

from UtilsAndModels.Defines import regulate_bias_const, regulate_weight_const


class FixNet(torch.nn.Module):
    def __init__(self, gui_width, gui_height):
        super(FixNet, self).__init__()
        self.gui_height = gui_height
        self.gui_width = gui_width
        self.fc1 = Linear(2, 2, True)
        self.relu = ReLU()
        self.init_weights()
        self.init_bias()

    def forward(self, x):
        x[0] = x[0] / self.gui_width
        x[1] = x[1] / self.gui_height
        x = self.relu(self.fc1(x))
        x[0] = x[0] * self.gui_width
        x[1] = x[1] * self.gui_height
        return x

    def init_weights(self):
        init.eye_(self.fc1.weight)

    def init_bias(self):
        init.constant_(self.fc1.bias, 0)


class FixNetCalibration:
    def __init__(self, gui_width, gui_height):
        self.model = FixNet(gui_width, gui_height)
        self.loss_f = MSELoss()
        self.optimizer = SGD(self.model.parameters(), lr=0.000001)
        self.is_trained = False

    def limit_model(self):
        with torch.no_grad():
            for i in range(2):
                if abs(1 - self.model.fc1.weight[i][i]) > 0.25:
                    self.model.fc1.weight[i][i] = 1 - 0.25 * np.sign(1 - self.model.fc1.weight[i][i])
                if abs(self.model.fc1.bias[i]) > 0.2:
                    self.model.fc1.bias[i] = 0.2 * np.sign(self.model.fc1.bias[i])

    def regularize_calc(self, const_mul=regulate_weight_const, const_bias=regulate_bias_const):
        regulate_mul_x = torch.norm(1 - self.model.fc1.weight[0][0], 1)
        regulate_mul_y = torch.norm(1 - self.model.fc1.weight[1][1], 1)
        regulate_bias = torch.norm(self.model.fc1.bias)
        return const_mul*(regulate_mul_x + regulate_mul_y) + const_bias * regulate_bias

    def train_model(self, epochs, real, res):
        self.model.train()
        data_size = int(np.size(res)/2)
        if data_size < 4:
            return
        for epoch in range(epochs):
            real_tensor = Variable(Tensor(real))
            res_tensor = Variable(Tensor(res))

            pred = self.model(res_tensor)
            loss = self.loss_f(pred, real_tensor)
            loss = loss + self.regularize_calc()

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

        self.is_trained = True

    def use_net(self, pixel):
        if self.is_trained:
            with torch.no_grad():
                self.model.eval()
                prediction = self.model(Variable(Tensor(pixel)))
                prediction = prediction.detach().numpy()
                return prediction
        else:
            return pixel
