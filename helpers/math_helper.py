from Defines import *
import tkinter
import torch
import os
# Import the libraries
import ctypes

device = 'cuda' if torch.cuda.is_available() else 'cpu'

NOSE_INDEX: int = 30
REYE_INDICES: np.ndarray = np.array([36, 39])
LEYE_INDICES: np.ndarray = np.array([42, 45])
MOUTH_INDICES: np.ndarray = np.array([48, 54])

# General attributes for eyes recognisition
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(os.getcwd() + "/HeadPoseBasedSolution/model/shape_predictor_68_face_landmarks.dat")
error_img = cv2.imread(os.getcwd() + "/error.jpg")

width_precent = 20
height_precent = 50


# Our convertion from millimeters to inches
MM_TO_IN = 0.0393700787


## TODO - handle the mm to position on screen problem - dpi of tkinter not allways = screen DPI

def get_mm_pixel_ratio(screen_size_inch):
    from tkinter import Tk
    root = Tk()
    width = root.winfo_screenwidth()*2
    height = root.winfo_screenheight()*2
    diagonal_pixel = np.sqrt(np.square(width) + np.square(height))
    print ("diagonal pixel" , diagonal_pixel)
    diagonal_mm = screen_size_inch / MM_TO_IN
    pixel_per_mm= diagonal_pixel/diagonal_mm
    print("pixel_per_mm ", pixel_per_mm)
    return pixel_per_mm

def get_dpi():
    # Set process DPI awareness
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    # Create a tkinter window
    root = tkinter.Tk()
    # Get a DC from the window's HWND
    dc = ctypes.windll.user32.GetDC(root.winfo_id())
    # The the monitor phyical width
    # (returned in millimeters then converted to inches)
    mw = ctypes.windll.gdi32.GetDeviceCaps(dc, 4) * MM_TO_IN
    # The the monitor phyical height
    mh = ctypes.windll.gdi32.GetDeviceCaps(dc, 6) * MM_TO_IN
    # Get the monitor horizontal resolution
    dw = ctypes.windll.gdi32.GetDeviceCaps(dc, 8)
    # Get the monitor vertical resolution
    dh = ctypes.windll.gdi32.GetDeviceCaps(dc, 10)
    # Destroy the window
    root.destroy()

    # Horizontal and vertical DPIs calculated
    hdpi, vdpi = dw / mw, dh / mh
    # Diagonal DPI calculated using Pythagoras
    ddpi = (dw ** 2 + dh ** 2) ** 0.5 / (mw ** 2 + mh ** 2) ** 0.5
    # Print the DPIs
    print(round(hdpi, 1), round(vdpi, 1), round(ddpi, 1))

def draw_axis(img, yaw, pitch, roll, tdx=None, tdy=None, size=100):
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

    cv2.line(img, (int(tdx), int(tdy)), (int(x1), int(y1)), (0, 0, 255), 3)
    cv2.line(img, (int(tdx), int(tdy)), (int(x2), int(y2)), (0, 255, 0), 3)
    cv2.line(img, (int(tdx), int(tdy)), (int(x3), int(y3)), (255, 0, 0), 2)

    return img


def print_gaze_line(img, eye_center, gaze_vector, r_vec, t_vec):
    length = 0.0001
    gaze_vector = gaze_vector / np.linalg.norm(gaze_vector)
    points = np.array([eye_center + length * gaze_vector])
    (eye_end_point2D, jacobian) = cv2.projectPoints(points, r_vec, t_vec, camera_matrix_a, dist_coeff_a)
    p1 = (int(eye_center[0]), int(eye_center[1]))
    p2 = (int(eye_end_point2D[0][0][0]), int(eye_end_point2D[0][0][1]))
    cv2.line(img, p1, p2, (255, 255, 0), 2)
    return img


def get_eye_center(eye):
    x_center = (eye[0][0] + eye[1][0]) / 2
    y_center = (eye[0][1] + eye[1][1]) / 2
    return np.array([x_center, y_center, 0])


def angle_to_vector(angles):
    pitch = angles[1]
    yaw = angles[0]
    return -np.array([
        np.cos(pitch) * np.cos(yaw),
        np.cos(pitch) * np.sin(yaw),
        np.sin(pitch)
    ])

def convert_to_unit_vector(angles):
    x = -torch.cos(angles[0]) * torch.sin(angles[1])
    y = -torch.sin(angles[0])
    z = -torch.cos(angles[1]) * torch.cos(angles[1])
    norm = torch.sqrt(x**2 + y**2 + z**2)
    x /= norm
    y /= norm
    z /= norm
    return np.array([x, y, z])


def _normalize_vector(vector: np.ndarray) -> np.ndarray:
    return vector / np.linalg.norm(vector)


def get_eye_center(shape, right, left):
    return np.dot(0.5, (shape[right] + shape[left])).reshape(3, 1)

def normalize_eye(frame, eye):
    eye_img = frame[eye[0][1]:eye[1][1], eye[0][0]:eye[1][0]]
    # eye_img = cv2.warpPerspective(eye_img,)
    eye_img = cv2.resize(eye_img, (60, 36), interpolation=cv2.INTER_AREA)
    eye_img = cv2.cvtColor(eye_img, cv2.COLOR_BGR2GRAY)
    eye_img = cv2.equalizeHist(eye_img)

    return eye_img


def eye_detector(img, shape):
    right_eye = get_eye(shape, 38, 40, 39, 36)
    left_eye = get_eye(shape, 44, 46, 45, 42)
    return right_eye, left_eye
