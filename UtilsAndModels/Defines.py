import os
import cv2
import numpy as np
import scipy.io as sio
import torch
import dlib

# Linear Fix Net hyper parameters
epochs: int = 40
regulate_weight_const = 100
regulate_bias_const = 1000
max_distance_for_net_mm: int = 65

# Camera attributes
capture_input_width = 1280
capture_input_height = 720
global global_camera_matrix
global global_camera_coeffs

# PNP attributes
NOSE_INDEX: int = 30
REYE_INDICES: np.ndarray = np.array([36, 39])
LEYE_INDICES: np.ndarray = np.array([42, 45])
MOUTH_INDICES: np.ndarray = np.array([48, 54])
LANDMARKS_6_PNP = sio.loadmat('UtilsAndModels/faceModelGeneric.mat')['model']

# Head Pose Detect attributes
rvec = np.zeros(3, dtype=np.float)
tvec = np.array([0, 0, 1], dtype=np.float)


# Gui attributes
font = cv2.FONT_HERSHEY_SIMPLEX
text_for_capture = "."
eyes_image = str(os.getcwd() + "/UtilsAndModels/eyes.png")

face_cascade = cv2.CascadeClassifier()
face_cascade.load("UtilsAndModels/frontal_face_detector.xml")

landmark_detector  = cv2.face.createFacemarkLBF()
landmark_detector.loadModel("UtilsAndModels/lbfmodel.yaml")


# Gaze to pixel attributes
MM_TO_IN = 0.0393700787

# Generic project usage
num_pics_per_session = 30

error_in_detect = np.array([[-1, -1],[-1,-1]])
error_in_pixel = np.zeros(2)

np.random.seed(0)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"device used is: {device}")

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
