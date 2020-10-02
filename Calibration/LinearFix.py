import numpy as np
import torch
from torch import Tensor
from torch.autograd import Variable
from torch.nn import Linear, MSELoss, init, ReLU, functional as F
from torch.optim import SGD, Adam, RMSprop


class FixNet(torch.nn.Module):
    def __init__(self):
        super(FixNet, self).__init__()
        self.fc1 = Linear(2, 2, True)
        self.relu = ReLU()
        self.init_weights()
        self.init_bias()

    def forward(self, x):
        return self.relu(self.fc1(x))

    def init_weights(self):
        init.eye_(self.fc1.weight)

    def init_bias(self):
        init.constant_(self.fc1.bias, 0)


class FixNetCalibration:
    def __init__(self):
        self.model = FixNet()
        self.loss_f = MSELoss()
        self.optimizer = SGD(self.model.parameters(), lr=0.000001)
        self.is_trained = False

    def train_model(self, epochs, real, res):
        print("enter train model")
        self.model.train()
        print("pixel_real data is", real)
        print("res data is", res)
        data_size = int(np.size(res)/2)
        print("data size", data_size)
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

        self.is_trained = True
        if self.model.fc1.weight[0, 0] > 1.5:
            self.model.fc1.weight[0, 0] = 1.5
        if self.model.fc1.weight[1, 1] > 1.5:
            self.model.fc1.weight[1, 1] = 1.5

    def use_net(self, pixel):
        if self.is_trained:
            with torch.no_grad():
                self.model.eval()
                prediction = self.model(Variable(Tensor(pixel)))
                prediction = prediction.detach().numpy()
                return prediction
        else:
            return pixel
