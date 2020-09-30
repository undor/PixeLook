import numpy as np
import torch
from torch import Tensor
from torch.autograd import Variable
from torch.nn import Linear, MSELoss, init, functional as F
from torch.optim import SGD, Adam, RMSprop


class FixNet(torch.nn.Module):
    def __init__(self):
        super(FixNet, self).__init__()
        self.fc1 = Linear(2, 2, True)

    def forward(self, x):
        return abs(self.fc1(x))

    def init_weights(self):
        init.eye_(self.fc1.weight)

    def init_bias(self):
        init.constant_(self.fc1.bias, 0)


class FixNetCalibration:
    def __init__(self):
        self.model = FixNet()
        self.loss_f = MSELoss()
        self.model.init_weights()
        self.model.init_bias()
        self.optimizer = SGD(self.model.parameters(), lr=0.000001)


    def train_model(self,epoches,real,res):
        self.model.train()
        print("real data is",real)
        print("res data is", res)
        data_size = int(np.size(res)/2)
        print("data size",data_size)
        # create our training loop
        for epoch in range(epoches):
            real_tensor = Variable(Tensor(real))
            res_tensor = Variable(Tensor(res))

            pred = self.model(res_tensor)
            print("prediction: ",pred.data)
            loss = self.loss_f(pred, real_tensor)

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            print("Epoch: {} Loss: {}".format(epoch, loss.data))

    def use_net(self, input):
        self.model.eval()
        prediction = self.model(Variable(Tensor(input)))
        print('a & b:', self.model.fc1.weight)
        print('c:', self.model.fc1.bias)
        return prediction