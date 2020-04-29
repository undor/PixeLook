import numpy as np
import tkinter as tk
import cv2
import os
import dlib
from imutils import face_utils

## General attributes for eyes recognisition
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(os.getcwd() + "/shape_predictor_68_face_landmarks.dat")
error_img = cv2.imread(os.getcwd() + "/error.jpg")

### General attributes for head pose
model_points = np.loadtxt('face_model_points.csv', delimiter=',')
width_precent = 20
height_precent = 50

def face_landmark_detector(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)
    if (np.size(rects) > 0):
        shape = predictor(gray, rects[0])
        shape = face_utils.shape_to_np(shape)
        return True, shape
    return False, error_img

def head_pose_detect(img, shape):
        image_points = np.array([shape[30], shape[8], shape[45], shape[36], shape[54], shape[48]], dtype="double")
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
        (nose_end_point2D, jacobian) = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rotation_vector,
                                                         translation_vector, camera_matrix, dist_coeffs)

        for p in image_points:
            cv2.circle(img, (int(p[0]), int(p[1])), 3, (0, 0, 255), -1)

        p1 = (int(image_points[0][0]), int(image_points[0][1]))
        p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))

        cv2.line(img, p1, p2, (255, 0, 0), 2)
        return img

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
        right_eye =get_eye(shape,38,40,39,36)
        left_eye = get_eye(shape,44,46,45,42)
        return right_eye, left_eye

def start_camera():
        cap = cv2.VideoCapture(1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        while True:
            ret, frame = cap.read()
            is_face, face_landmark = face_landmark_detector(frame)
            if is_face:
                img = head_pose_detect(frame, face_landmark)
                r_eye, l_eye = eye_detector(frame, face_landmark)
                cv2.rectangle(img,r_eye[0],r_eye[1],(0,255,0), 1)
                cv2.rectangle(img, l_eye[0], l_eye[1], (0, 255, 0),1)
                cv2.imshow("Output", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()
