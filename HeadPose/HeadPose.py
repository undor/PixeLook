import numpy as np
import cv2
import math
from math import cos, sin
import torch
import HeadPose.stable_hopenetlite as stable_hopenetlite
from torch.autograd import Variable
from torchvision import transforms
from PIL import Image
import dlib

### General attributes for head pose - DL
pos_net = stable_hopenetlite.shufflenet_v2_x1_0()
saved_state_dict = torch.load('./HeadPose/model/shuff_epoch_120.pkl', map_location="cpu")
pos_net.load_state_dict(saved_state_dict, strict=False)
pos_net.eval()
transformations = transforms.Compose([transforms.Scale(224),
                                      transforms.CenterCrop(224), transforms.ToTensor(),
                                      transforms.Normalize(mean={0.485, 0.456, 0.406}, std=[0.229, 0.224, 0.225])])

idx_tensor = [idx for idx in range(66)]
idx_tensor = torch.FloatTensor(idx_tensor)


def head_pose_detect_DL(img,det):
    x_min = det.left()
    y_min = det.top()
    x_max = det.right()
    y_max = det.bottom()

    frame= img
    bbox_width = abs(x_max - x_min)
    bbox_height = abs(y_max - y_min)
    x_min -= 2 * bbox_width / 4
    x_max += 2 * bbox_width / 4
    y_min -= 3 * bbox_height / 4
    y_max += bbox_height / 4
    x_min = int(max(x_min, 0))
    y_min = int(max(y_min, 0))
    x_max = int(min(frame.shape[1], x_max))
    y_max = int(min(frame.shape[0], y_max))
    # Crop image
    img = frame[y_min:y_max, x_min:x_max]
    img = Image.fromarray(img)

    # Transform
    img = transformations(img)
    img_shape = img.size()
    img = img.view(1, img_shape[0], img_shape[1], img_shape[2])
    img = Variable(img)

    yaw, pitch, roll = pos_net(img)

    yaw_predicted = torch.nn.functional.softmax(yaw)
    pitch_predicted = torch.nn.functional.softmax(pitch)
    roll_predicted = torch.nn.functional.softmax(roll)

    yaw_predicted = torch.sum(yaw_predicted.data[0] * idx_tensor) * 3 - 99
    pitch_predicted = torch.sum(pitch_predicted.data[0] * idx_tensor) * 3 - 99
    roll_predicted = torch.sum(roll_predicted.data[0] * idx_tensor) * 3 - 99

    print(yaw_predicted)
    draw_axis(frame, yaw_predicted, pitch_predicted, roll_predicted, tdx = (x_min + x_max) / 2, tdy= (y_min + y_max) / 2, size = bbox_height/2)
    return frame


def draw_axis(img, yaw, pitch, roll, tdx=None, tdy=None, size = 100):

    pitch = pitch * np.pi / 180
    yaw = -(yaw * np.pi / 180)
    roll = roll * np.pi / 180

    if tdx != None and tdy != None:
        tdx = tdx
        tdy = tdy
    else:
        height, width = img.shape[:2]
        tdx = width / 2
        tdy = height / 2

    # X-Axis pointing to right. drawn in red
    x1 = size * (cos(yaw) * cos(roll)) + tdx
    y1 = size * (cos(pitch) * sin(roll) + cos(roll) * sin(pitch) * sin(yaw)) + tdy

    # Y-Axis | drawn in green
    #        v
    x2 = size * (-cos(yaw) * sin(roll)) + tdx
    y2 = size * (cos(pitch) * cos(roll) - sin(pitch) * sin(yaw) * sin(roll)) + tdy

    # Z-Axis (out of the screen) drawn in blue
    x3 = size * (sin(yaw)) + tdx
    y3 = size * (-cos(yaw) * sin(pitch)) + tdy

    cv2.line(img, (int(tdx), int(tdy)), (int(x1),int(y1)),(0,0,255),3)
    cv2.line(img, (int(tdx), int(tdy)), (int(x2),int(y2)),(0,255,0),3)
    cv2.line(img, (int(tdx), int(tdy)), (int(x3),int(y3)),(255,0,0),2)

    return img
