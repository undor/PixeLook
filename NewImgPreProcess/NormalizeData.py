import sys
import numpy as np
import cv2
from NewImgPreProcess.NormalizeImg import normalizeImg


def normalize_data(img, annotation, camera_calibrate, face_model, roisize):
    # annotation , camera calibrate and face model we have in different files need to get it from there and not from
    # input to function
    # get head pose
    # need to add it to defines
    head_rotate_indices = [30, 31, 32]
    headpose_head_rotation = [annotation[x] for x in head_rotate_indices]
    head_translation_indices = [33, 34, 35]
    headpose_head_translation = [annotation[x] for x in head_translation_indices]
    # when sending to Rodrigues, we sent a [x,y,z] vector and got :
    head_rotate = cv2.Rodrigues(headpose_head_rotation)
    # most important variable : what the fuck is this facial landmark?
    # [3x3] * [3x6] = [3x6]
    facial_landmark = head_rotate@face_model
    facial_landmark = facial_landmark + headpose_head_translation
    # get eye center in the original camera coordinate system
    right_eye_center = 0.5*(facial_landmark[:1]+facial_landmark[:2])
    left_eye_center = 0.5*(facial_landmark[:3]+facial_landmark[:4])
    # get the gaze target
    #gaze_target_indices = [27, 28, 29]
    #gaze_target = np.transpose([annotation[x] for x in gaze_target_indices])
    # set size of normalized image - put in defines
    eye_image_width = 60
    eye_image_height = 36
    # normalizing only right eye - for left eye replace centers
    img, headpose_rotation = normalizeImg(img, right_eye_center, head_rotate, roisize,
                                                           [eye_image_width, eye_image_height], camera_calibrate)

    # convert the gaze direction and head pose in the camera coordinate system to the angle in the polar
    # coordinate system. got to understand what the hell happens here

    M = cv2.Rodrigues(headpose_rotation)
    zv = M[:, 3]
    # vertical angle
    head_pose_theta = np.asin(zv[2])
    # horizontal angle
    head_pose_phi = np.atan2(zv[1], zv[3])




