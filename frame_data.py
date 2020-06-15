from Defines import *
from helpers.math_helper import *
from HeadPose.face_landmarks import face_model
from NewImgPreProcess.NormalizeData import *
import cv2
import numpy as np


dist_coeff_a = np.array([0., 0., 0., 0., 0.]).reshape(-1, 1)

norm_matrix = np.array([1600., 0., 112.,
                        0., 1600., 112.,
                        0., 0., 1.]).reshape(3, 3)
rvec = np.zeros(3, dtype=np.float)
tvec = np.array([0, 0, 1], dtype=np.float)


class FrameData():
    def __init__(self, img,is_debug = True):
        self.orig_img = img
        self.is_face = False
        self.shape = 0
        self.rect = 0
        self.rotation_vector = np.zeros(3)
        self.translation_vector = np.zeros(3)
        self.debug_img = img
        self.is_debug= is_debug

    def get_head_pose(self):
        return self.head_pose

    def get_eye_img(self):
        return self.r_eye_img


    def face_landmark_detect(self):
        gray = cv2.cvtColor(self.orig_img, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)
        if (np.size(rects) > 0):
            shape = predictor(gray, rects[0])
            shape = face_utils.shape_to_np(shape)
            self.is_face = True
            self.shape = shape
            self.rect = rects[0]
        return self.is_face

    def eyes_detect(self):
        self.r_eye, self.l_eye = eye_detector(self.orig_img, self.shape)


    def head_pose_detect(self):
        image_points = np.array(self.shape, dtype="double")
        size = self.orig_img.shape
        focal_length = size[1]
        center = (size[1] / 2, size[0] / 2)
        camera_matrix = np.array(
            [[focal_length, 0, center[0]],
             [0, focal_length, center[1]],
             [0, 0, 1]], dtype="double"
        )
        dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
        (success, self.rotation_vector, self.translation_vector) = cv2.solvePnP(face_model, image_points, camera_matrix,
                                                                                dist_coeffs, rvec, tvec,
                                                                                flags=cv2.SOLVEPNP_ITERATIVE)
        # Project a 3D point (0, 0, 1000.0) onto the image plane.
        (nose_end_point2D, jacobian) = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), self.rotation_vector,
                                                         self.translation_vector, camera_matrix, dist_coeffs)

        p1 = (int(image_points[NOSE_INDEX][0]), int(image_points[NOSE_INDEX][1]))
        p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))

        if(self.is_debug):
            cv2.line(self.debug_img, p1, p2, (255, 0, 0), 2)

        # rot = Rotation.from_rotvec(self.rotation_vector)
        # model3d = camera_matrix_a @ self.rotation_vector.T + self.translation_vector
        # self.angles = rot.as_euler('XYZ')[:2] * np.array([1, -1])

    def pre_proccess_for_net(self):
        self.r_eye_img = normalize_eye(self.orig_img, self.r_eye)
        self.l_eye_img = normalize_eye(self.orig_img, self.l_eye)
        self.head_pose,  self.r_eye_img  = normalize_data(self.r_eye_img,self.rotation_vector,self.translation_vector)