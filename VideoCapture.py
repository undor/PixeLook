import numpy as np
import tkinter as tk
import cv2
import os
import dlib
from imutils import face_utils


### general attributes for eyes recognisition
cwd = os.getcwd()+"/ReadHelper"
p = "/shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(cwd+p)
right_eye_p = np.arange(36, 42, 1, int)
left_eye_p = np.arange(42, 48, 1, int)
mouth_p = np.arange(48, 68, 1, int)
error_img = cv2.imread(cwd+"/error.jpg")



def detector_new(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Get faces into webcam's image
    rects = detector(gray, 0)
    # For each detected face, find the landmark.
        # Make the prediction and transfom it to numpy array
    width_precent = 20
    height_precent = 50
    if (np.size(rects) >0):
        shape = predictor(gray, rects[0])
        shape = face_utils.shape_to_np(shape)
        right_eye_width =  shape[39][0] - shape[36][0]
        right_eye_height = shape[40][1] - shape[38][1]
        right_eye_width_add= int (right_eye_width * width_precent /100 )
        right_eye_height_add= int (right_eye_height * height_precent /100 )

        right_e_r= shape[36][0] - right_eye_width_add
        right_e_l= shape[39][0] +right_eye_width_add
        right_e_t=shape[38][1] -right_eye_height_add
        right_e_b=shape[40][1] + right_eye_height_add

        left_eye_width =  shape[45][0] - shape[42][0]
        left_eye_height = shape[46][1] - shape[44][1]
        left_eye_width_add=  int (left_eye_width * width_precent /100 )
        left_eye_height_add= int (left_eye_height * height_precent /100 )


        left_e_r= shape[42][0] -left_eye_width_add
        left_e_l= shape[45][0] + left_eye_width_add
        left_e_t= shape[44][1] -left_eye_height_add
        left_e_b= shape[46][1] +left_eye_height_add

        right_eye = img [right_e_t :right_e_b , right_e_r:right_e_l]
        left_eye = img[left_e_t:left_e_b , left_e_r:left_e_l]
        return right_eye,left_eye

    return error_img,error_img


def open_webcam():
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    while (True):
        ret, frame = cap.read()
        re,le = detector_new(frame)
        # numpy_horizontal = np.hstack((re, le))
        # numpy_horizontal_concat = np.concatenate((re, le), axis=1)
        cv2.imshow('re', re)
        cv2.imshow('le', le)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
