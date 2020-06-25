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

## General attributes for eyes recognisition
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(os.getcwd() + "/HeadPoseBasedSolution/model/shape_predictor_68_face_landmarks.dat")
error_img = cv2.imread(os.getcwd() + "/error.jpg")

### General attributes for head pose
width_precent = 20
height_precent = 50

