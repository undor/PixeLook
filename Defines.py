# relevant imports

import numpy as np
import cv2
import dlib
from helpers.math_helper import *
import torch
import os
import dlib

### Project Defines

device = 'cuda' if torch.cuda.is_available() else 'cpu'
font = cv2.FONT_HERSHEY_SIMPLEX

NOSE_INDEX: int = 30
REYE_INDICES: np.ndarray = np.array([36, 39])
LEYE_INDICES: np.ndarray = np.array([42, 45])
MOUTH_INDICES: np.ndarray = np.array([48, 54])

rvec = np.zeros(3, dtype=np.float)
tvec = np.array([0, 0, 1], dtype=np.float)

## General attributes for eyes recognisition
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(os.getcwd() + "/HeadPoseBasedSolution/model/shape_predictor_68_face_landmarks.dat")
error_img = cv2.imread(os.getcwd() + "/error.jpg")

### General attributes for head pose
width_precent = 20
height_precent = 50

### Calibration attributes
stages = {'WAIT_FOR_LEFT': 0,
          'LEFT_CALIBRATION': 1,
          'WAIT_FOR_RIGHT': 2,
          'RIGHT_CALIBRATION': 3,
          'WAIT_FOR_UP': 4,
          'UP_CALIBRATION': 5,
          'WAIT_FOR_DOWN': 6,
          'DOWN_CALIBRATION': 7,
          'WAIT_FOR_CENTER': 8,
          'CENTER_CALIBRATION': 9,
          'CHECK_CALIBRATION': 10,
          'FINISH_CALIBRATION': 11}

