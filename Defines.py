# relevant imports

import numpy as np
import torch
from torch.autograd import Variable
import tkinter as tk
import cv2
import os
import dlib
from scipy.spatial.transform import Rotation
import HeadPose
from HeadPose.HeadPose import head_pose_detect_DL
from imutils import face_utils
import GazeModel
import torchvision
from helpers.fps import fpsHelper
from helpers.math_helper import *
from frame_data import *


### Project Defines


device = 'cuda' if torch.cuda.is_available() else 'cpu'
font = cv2.FONT_HERSHEY_SIMPLEX

NOSE_INDEX: int = 30
REYE_INDICES: np.ndarray = np.array([36, 39])
LEYE_INDICES: np.ndarray = np.array([42, 45])
MOUTH_INDICES: np.ndarray = np.array([48, 54])

## General attributes for eyes recognisition
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(os.getcwd() + "/HeadPose/model/shape_predictor_68_face_landmarks.dat")
error_img = cv2.imread(os.getcwd() + "/error.jpg")

### General attributes for head pose
width_precent = 20
height_precent = 50

