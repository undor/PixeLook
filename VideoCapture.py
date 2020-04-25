import numpy as np
import tkinter as tk
import cv2
import os
import dlib
from imutils import face_utils

### General attributes for eyes recognisition
cwd = os.getcwd() + "/ReadHelper"
p = "/shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(cwd + p)
right_eye_p = np.arange(36, 42, 1, int)
left_eye_p = np.arange(42, 48, 1, int)
mouth_p = np.arange(48, 68, 1, int)
error_img = cv2.imread(cwd + "/error.jpg")

### General attributes for head pose
model_points = np.array([
    (0.0, 0.0, 0.0),  # Nose tip
    (0.0, -330.0, -65.0),  # Chin
    (-225.0, 170.0, -135.0),  # Left eye left corner
    (225.0, 170.0, -135.0),  # Right eye right corne
    (-150.0, -150.0, -125.0),  # Left Mouth corner
    (150.0, -150.0, -125.0)  # Right mouth corner

])


def head_pose_detect(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Get faces into webcam's image
    rects = detector(gray, 0)
    if(np.size(rects)>0):
        shape = predictor(gray, rects[0])
        shape = face_utils.shape_to_np(shape)
        image_points= np.array([shape[30], shape[8], shape[45], shape[36], shape[54], shape[48]], dtype="double")
        size = img.shape
        focal_length = size[1]
        center = (size[1] / 2, size[0] / 2)
        camera_matrix = np.array(
            [[focal_length, 0, center[0]],
             [0, focal_length, center[1]],
             [0, 0, 1]], dtype="double"
        )

        dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
        (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix,
                                                                        dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)

        # Project a 3D point (0, 0, 1000.0) onto the image plane.
        # We use this to draw a line sticking out of the nose

        (nose_end_point2D, jacobian) = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rotation_vector,
                                                         translation_vector, camera_matrix, dist_coeffs)

        for p in image_points:
            cv2.circle(img, (int(p[0]), int(p[1])), 3, (0, 0, 255), -1)

        p1 = (int(image_points[0][0]), int(image_points[0][1]))
        p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))

        cv2.line(img, p1, p2, (255, 0, 0), 2)

        # Display image
        cv2.imshow("Output", img)


def detector_new(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Get faces into webcam's image
    rects = detector(gray, 0)
    # For each detected face, find the landmark.
    # Make the prediction and transfom it to numpy array
    width_precent = 20
    height_precent = 50
    if (np.size(rects) > 0):
        shape = predictor(gray, rects[0])
        shape = face_utils.shape_to_np(shape)
        right_eye_width = shape[39][0] - shape[36][0]
        right_eye_height = shape[40][1] - shape[38][1]
        right_eye_width_add = int(right_eye_width * width_precent / 100)
        right_eye_height_add = int(right_eye_height * height_precent / 100)

        right_e_r = shape[36][0] - right_eye_width_add
        right_e_l = shape[39][0] + right_eye_width_add
        right_e_t = shape[38][1] - right_eye_height_add
        right_e_b = shape[40][1] + right_eye_height_add

        left_eye_width = shape[45][0] - shape[42][0]
        left_eye_height = shape[46][1] - shape[44][1]
        left_eye_width_add = int(left_eye_width * width_precent / 100)
        left_eye_height_add = int(left_eye_height * height_precent / 100)

        left_e_r = shape[42][0] - left_eye_width_add
        left_e_l = shape[45][0] + left_eye_width_add
        left_e_t = shape[44][1] - left_eye_height_add
        left_e_b = shape[46][1] + left_eye_height_add

        right_eye = img[right_e_t:right_e_b, right_e_r:right_e_l]
        left_eye = img[left_e_t:left_e_b, left_e_r:left_e_l]
        return right_eye, left_eye

    return error_img, error_img


def open_webcam():
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    while (True):
        ret, frame = cap.read()
        head_pose_detect(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        #  re, le = detector_new(frame)
        # numpy_horizontal = np.hstack((re, le))
        # numpy_horizontal_concat = np.concatenate((re, le), axis=1)
        # cv2.imshow('re', re)
        # cv2.imshow('le', le)

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
