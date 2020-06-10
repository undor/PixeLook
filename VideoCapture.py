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
from HeadPose.face_landmarks import face_landmarks
import GazeModel
import torchvision
import datetime

## Tomer try to git

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
model_points = face_landmarks
width_precent = 20
height_precent = 50

## unsidtort to camera
camera_matrix_a=np.array([960., 0., 30,
           0., 960., 18.,
           0., 0., 1.]).reshape(3,3)
dist_coeff_a=np.array([0., 0., 0., 0., 0.]).reshape(-1,1)

norm_matrix = np.array( [1600., 0., 112.,
           0., 1600., 112.,
           0., 0., 1.]).reshape(3,3)


def face_landmark_detector(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)
    if (np.size(rects) > 0):
        shape = predictor(gray, rects[0])
        shape = face_utils.shape_to_np(shape)
        return True, shape ,rects[0]
    return False, error_img , 0


def angle_to_vector(angles):
        pitch, yaw = angles[0]
        return -np.array([
            np.cos(pitch) * np.sin(yaw),
            np.sin(pitch),
            np.cos(pitch) * np.cos(yaw)
        ])

def _normalize_vector(vector: np.ndarray) -> np.ndarray:
    return vector / np.linalg.norm(vector)


def head_pose_detect(img, shape):
        image_points = np.array(shape,dtype="double")
        size = img.shape
        focal_length = size[1]
        rvec = np.zeros(3, dtype=np.float)
        tvec = np.array([0, 0, 1], dtype=np.float)
        center = (size[1] / 2, size[0] / 2)
        camera_matrix = np.array(
            [[focal_length, 0, center[0]],
             [0, focal_length, center[1]],
             [0, 0, 1]], dtype="double"
        )

        dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
        (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix,
                                                                      dist_coeffs,rvec,tvec,flags=cv2.SOLVEPNP_ITERATIVE)

        # Project a 3D point (0, 0, 1000.0) onto the image plane.
        (nose_end_point2D, jacobian) = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rotation_vector,
                                                         translation_vector, camera_matrix, dist_coeffs)

        p1 = (int(image_points[NOSE_INDEX][0]), int(image_points[NOSE_INDEX][1]))
        p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))

        cv2.line(img, p1, p2, (255, 0, 0), 2)
        rot = Rotation.from_rotvec(rotation_vector)
        model3d = camera_matrix_a @ rotation_vector.T + translation_vector
        angles = rot.as_euler('XYZ')[:2] * np.array([1 , -1])
        return img , angles

def print_gaze_line():
    (eye_end_point2D, jacobian) = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rotation_vector,
                                                     translation_vector, camera_matrix_a, dist_coeffs_a)

    p1 = (int(image_points[REYE_INDICES][0]), int(image_points[REYE_INDICES][1]))
    p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))

    cv2.line(img, p1, p2, (255, 0, 0), 2)


def get_eye(shape,top,bottom,right,left):
    eye_width = shape[right][0] - shape[left][0]
    eye_height = shape[bottom][1] - shape[top][1]
    eye_width_add = int(eye_width * width_precent / 100)
    eye_height_add = int(eye_height * height_precent / 100)

    eye_left = shape[left][0] - eye_width_add
    eye_top = shape[top][1] - eye_height_add

    eye_height = eye_height + 2*eye_height_add
    eye_width = eye_width + 2*eye_width_add
    return [(eye_left , eye_top), (eye_left + eye_width, eye_top+ eye_height)]


def eye_detector(img, shape):
    right_eye = get_eye(shape, 38, 40, 39, 36)
    left_eye = get_eye(shape, 44, 46, 45, 42)
    return right_eye, left_eye


def normalize_eye(frame,eye):
    eye_img = frame[eye[0][1]:eye[1][1], eye[0][0]:eye[1][0]]
    # eye_img = cv2.warpPerspective(eye_img,)
    ## FIXME - WARP eye img
    eye_img = cv2.resize(eye_img, (60,36), interpolation=cv2.INTER_AREA)
    eye_img = cv2.cvtColor(eye_img, cv2.COLOR_BGR2GRAY)
    eye_img = cv2.equalizeHist(eye_img)

    return eye_img

def load_model():
    model = GazeModel.GazeNet()
    model.load_state_dict(torch.load("RES/TRAINED_NET"))
    model.to(device)
    model.eval()
    return model

def use_net(model, eye_img,head_pose):
    image = np.array(eye_img).astype(np.float32)/255
    image = torch.from_numpy(image)
    image = image.unsqueeze(0).unsqueeze(0)
    head_pose = torch.from_numpy(np.array(head_pose).astype(np.float32)).unsqueeze(0)
    with torch.no_grad():
        image = image.to(device)
        head_pose = head_pose.to(device)
        predictions = model(image, head_pose)
        predictions = predictions.cpu().numpy()
    return predictions



def print_data_on_img(img,head_angles,gaze_angles,fps):
    gaze_angles=gaze_angles[0]
    print(gaze_angles)
    cv2.putText(img, "gaze angles: " + str(gaze_angles[0])  +  "  " + str(gaze_angles[1]), (100,100) , font, 1, (0, 150, 0), 2, cv2.LINE_4)
    cv2.putText(img, "head angles: " + str(head_angles[0])  +  "  " + str(head_angles[1]), (100,200) , font, 1, (0, 150, 0), 2, cv2.LINE_4)
    cv2.putText(img, "fps  :  " + str(fps), (100, 300), font, 1,(0, 150, 0), 2, cv2.LINE_4)

def start_camera():
        model = load_model()
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        last_time = datetime.datetime.now()
        counter = 0
        fps = 0
        while True:
            ret, frame = cap.read()
            frame = cv2.undistort(frame, camera_matrix_a,dist_coeff_a)
            is_face, face_landmark, rect = face_landmark_detector(frame)
            if is_face:
                img , head_angles = head_pose_detect(frame,face_landmark)
                r_eye, l_eye = eye_detector(frame, face_landmark)
                l_eye_norm = normalize_eye(frame, l_eye)
                gaze_angles = use_net(model,l_eye_norm,head_angles)
                vector = angle_to_vector(gaze_angles)

                counter = counter+1
                time_elapsed = datetime.datetime.now() - last_time
                if (time_elapsed.seconds.real >= 1):
                    fps = (counter /time_elapsed.seconds.real)
                    counter = 0
                    last_time = datetime.datetime.now()
                    print(fps.real)
                print_data_on_img(img,head_angles,gaze_angles,fps)

                cv2.imshow("Output", img)
                cv2.imshow("eye", l_eye_norm)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()
