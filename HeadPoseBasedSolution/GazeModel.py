import torch.nn as nn
import torch.nn.functional as F
from Defines import *

device = 'cuda' if torch.cuda.is_available() else 'cpu'


class GazeNet(nn.Module):
    def __init__(self):
        super(GazeNet, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=20, kernel_size=5, stride=1, bias=False)
        self.conv2 = nn.Conv2d(in_channels=20, out_channels=50, kernel_size=5, stride=1, bias=False)
        self.fc1 = nn.Linear(3600, 500, bias=True)
        self.fc2 = nn.Linear(502, 2, bias=True)

    def init_weights(self):
        nn.init.normal_(self.conv1.weight, mean=0, std=0.1)
        nn.init.normal_(self.conv2.weight, mean=0, std=0.01)
        nn.init.xavier_normal_(self.fc1.weight)
        nn.init.xavier_normal_(self.fc2.weight)

    def forward(self, eye_img, head_pose):
        x = F.max_pool2d(self.conv1(eye_img), kernel_size=2, stride=2)
        x = F.max_pool2d(self.conv2(x), kernel_size=2, stride=2)
        x = F.relu(self.fc1(x.view(x.size(0), -1)), inplace=True)
        x = torch.cat([x, head_pose], dim=1)
        x = self.fc2(x)
        return x


def load_model():
    model = GazeNet()
    model.load_state_dict(torch.load("DataSetPreProcess/RES/TRAINED_NET_30_EPOCH"))
    model.to(device)
    model.eval()
    return model


def use_net(model, frame):
    image = np.array(frame.r_eye[0].astype(np.float32)/255)
    image = torch.from_numpy(image)
    image = image.unsqueeze(0).unsqueeze(0)
    head_pose = torch.from_numpy(frame.r_eye[1].astype(np.float32))

    with torch.no_grad():
        image = image.to(device)
        head_pose = head_pose.to(device)

        predictions = model(image, head_pose)
        # predictions = predictions.cpu().numpy()
        predictions = predictions[0].cpu()
    return predictions
