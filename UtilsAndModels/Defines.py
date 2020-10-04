# relevant imports
import cv2
import dlib
import numpy as np
import os
import random
import scipy.io as sio
import torch

# Project Defines - Net
np.random.seed(0)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
epochs: int = 60

# Project Defines - Head Detection
global global_camera_matrix
global global_camera_coeffs

NOSE_INDEX: int = 30
REYE_INDICES: np.ndarray = np.array([36, 39])
LEYE_INDICES: np.ndarray = np.array([42, 45])
MOUTH_INDICES: np.ndarray = np.array([48, 54])

rvec = np.zeros(3, dtype=np.float)
tvec = np.array([0, 0, 1], dtype=np.float)

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(os.getcwd() + "/UtilsAndModels/shape_predictor_68_face_landmarks.dat")

mini_face_model = sio.loadmat('faceModelGeneric.mat')['model']

# Gui
font = cv2.FONT_HERSHEY_SIMPLEX
text_for_capture = "#"

# Our convert from millimeters to inches
MM_TO_IN = 0.0393700787

# Calibration
max_distance_for_net_mm: int = 60

error_in_detect = np.array([-1, -1])
error_in_pixel = np.zeros(2)

# Calibration attributes
CALIB_LEFT: int = 0
CALIB_UP_LEFT: int = 1
CALIB_UP: int = 2
CALIB_UP_RIGHT: int = 3
CALIB_RIGHT: int = 4
CALIB_DOWN_RIGHT: int = 5
CALIB_DOWN: int = 6
CALIB_DOWN_LEFT: int = 7
CALIB_CENTER: int = 8
CHECK_CALIBRATION: int = 9
FINISH_CALIBRATION: int = 10

stages = {'CALIB_LEFT': 0,
          'CALIB_UP_LEFT': 1,
          'CALIB_UP': 2,
          'CALIB_UP_RIGHT': 3,
          'CALIB_RIGHT': 4,
          'CALIB_DOWN_RIGHT': 5,
          'CALIB_DOWN': 6,
          'CALIB_DOWN_LEFT': 7,
          'CALIB_CENTER': 8,
          'CHECK_CALIBRATION': 9,
          'FINISH_CALIBRATION': 10}
stage_dot_locations = [(0.035, 0.5), (0.25, 0.25), (0.5, 0.035), (0.75, 0.25), (0.965, 0.5), (0.75, 0.75), (0.5, 0.965),
                       (0.25, 0.75), (0.5, 0.5), (0., 0.)]