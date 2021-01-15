import os
import cv2
import dlib
import numpy as np
import scipy.io as sio
import torch

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

face_cascade = cv2.CascadeClassifier()
face_cascade.load("UtilsAndModels/frontal_face_detector.xml")

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(os.getcwd() + "/UtilsAndModels/shape_predictor_68_face_landmarks_new.dat")


LANDMARKS_HP: np.ndarray = np.array([
    [-0.07141807, -0.02827123, 0.08114384],
    [-0.07067417, -0.00961522, 0.08035654],
    [-0.06844646, 0.00895837, 0.08046731],
    [-0.06474301, 0.02708319, 0.08045689],
    [-0.05778475, 0.04384917, 0.07802191],
    [-0.04673809, 0.05812865, 0.07192291],
    [-0.03293922, 0.06962711, 0.06106274],
    [-0.01744018, 0.07850638, 0.04752971],
    [0., 0.08105961, 0.0425195],
    [0.01744018, 0.07850638, 0.04752971],
    [0.03293922, 0.06962711, 0.06106274],
    [0.04673809, 0.05812865, 0.07192291],
    [0.05778475, 0.04384917, 0.07802191],
    [0.06474301, 0.02708319, 0.08045689],
    [0.06844646, 0.00895837, 0.08046731],
    [0.07067417, -0.00961522, 0.08035654],
    [0.07141807, -0.02827123, 0.08114384],
    [-0.05977758, -0.0447858, 0.04562813],
    [-0.05055506, -0.05334294, 0.03834846],
    [-0.0375633, -0.05609241, 0.03158344],
    [-0.02423648, -0.05463779, 0.02510117],
    [-0.01168798, -0.04986641, 0.02050337],
    [0.01168798, -0.04986641, 0.02050337],
    [0.02423648, -0.05463779, 0.02510117],
    [0.0375633, -0.05609241, 0.03158344],
    [0.05055506, -0.05334294, 0.03834846],
    [0.05977758, -0.0447858, 0.04562813],
    [0., -0.03515768, 0.02038099],
    [0., -0.02350421, 0.01366667],
    [0., -0.01196914, 0.00658284],
    [0., 0., 0.],
    [-0.01479319, 0.00949072, 0.01708772],
    [-0.00762319, 0.01179908, 0.01419133],
    [0., 0.01381676, 0.01205559],
    [0.00762319, 0.01179908, 0.01419133],
    [0.01479319, 0.00949072, 0.01708772],
    [-0.045, -0.032415, 0.03976718],
    [-0.0370546, -0.0371723, 0.03579593],
    [-0.0275166, -0.03714814, 0.03425518],
    [-0.01919724, -0.03101962, 0.03359268],
    [-0.02813814, -0.0294397, 0.03345652],
    [-0.03763013, -0.02948442, 0.03497732],
    [0.01919724, -0.03101962, 0.03359268],
    [0.0275166, -0.03714814, 0.03425518],
    [0.0370546, -0.0371723, 0.03579593],
    [0.045, -0.032415, 0.03976718],
    [0.03763013, -0.02948442, 0.03497732],
    [0.02813814, -0.0294397, 0.03345652],
    [-0.02847002, 0.03331642, 0.03667993],
    [-0.01796181, 0.02843251, 0.02335485],
    [-0.00742947, 0.0258057, 0.01630812],
    [0., 0.0275555, 0.01538404],
    [0.00742947, 0.0258057, 0.01630812],
    [0.01796181, 0.02843251, 0.02335485],
    [0.02847002, 0.03331642, 0.03667993],
    [0.0183606, 0.0423393, 0.02523355],
    [0.00808323, 0.04614537, 0.01820142],
    [0., 0.04688623, 0.01716318],
    [-0.00808323, 0.04614537, 0.01820142],
    [-0.0183606, 0.0423393, 0.02523355],
    [-0.02409981, 0.03367606, 0.03421466],
    [-0.00756874, 0.03192644, 0.01851247],
    [0., 0.03263345, 0.01732347],
    [0.00756874, 0.03192644, 0.01851247],
    [0.02409981, 0.03367606, 0.03421466],
    [0.00771924, 0.03711846, 0.01940396],
    [0., 0.03791103, 0.0180805],
    [-0.00771924, 0.03711846, 0.01940396],
],
    dtype=np.float)

# Gui attributes
font = cv2.FONT_HERSHEY_SIMPLEX
text_for_capture = "@"
eyes_image = str(os.getcwd() + "/UtilsAndModels/eyes.png")

# code for saving jpg image and convert it to ppm , for using it at tkinter.
# from PIL import Image
# image = Image.open("<path to jpg image>")
# image = image.resize((150, 100), Image.ANTIALIAS)
# image.save("<path to desired saved location>.ppm", "ppm")

# image = Image.open("Calibration/eyes.png")
# image = image.resize((75, 75), Image.ANTIALIAS)
# image.save("Calibration/morty.ppm", "ppm")

# self.photo = tk.PhotoImage(file="Calibration/eyes.png")
# Gaze to pixel attributes
MM_TO_IN = 0.0393700787

# Generic project usage
num_pics_per_session = 30

error_in_detect = np.array([-1, -1])
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
