import numpy as np
import torch
from torch import Tensor
from torch.autograd import Variable
from torch.nn import Linear, MSELoss, init, ReLU
from torch.optim import SGD


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
                if abs( 1 - self.model.fc1.weight[i][i]) > 0.15 :
                    self.model.fc1.weight[i][i] = 1 - 0.15 * np.sign(1- self.model.fc1.weight[i][i])
                if abs(self.model.fc1.bias[i]) > 0.1:
                    self.model.fc1.bias[i] = 0.1 * np.sign(self.model.fc1.bias[i])


    def train_model(self, epochs, real, res):
        self.model.train()
        print("res data is", res)
        print("real data is", real)
        data_size = int(np.size(res)/2)
        # print("data size", data_size)
        if data_size < 4:
            return
        # create our training loop
        for epoch in range(epochs):
            real_tensor = Variable(Tensor(real))
            res_tensor = Variable(Tensor(res))

            pred = self.model(res_tensor)
            loss = self.loss_f(pred, real_tensor)

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            if epoch % 10 == 0:
                print("Epoch: {} Loss: {}".format(epoch, loss.data))

        self.limit_model()
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
