import numpy as np
import cv2
from HeadPoseBasedSolution.NewImgPreProcess.NormalizeImg import *
from HeadPoseBasedSolution.HeadPoseBasedSolution import face_model


def normalize_data(img,headpose_head_rotation,headpose_head_translation):
    # annotation , camera calibrate and face model we have in different files need to get it from there and not from
    # input to function
    # get head pose
    # need to add it to defines
    # when sending to Rodrigues, we sent a [x,y,z] vector and got :
    headpose_head_rotation =headpose_head_rotation.T
    head_rotate , jacobian =cv2.Rodrigues(headpose_head_rotation)
    # most important variable : what the fuck is this facial landmark?
    # [3x3] * [3x68] = [3x68]

    facial_landmark = head_rotate @ face_model.T
    headpose_head_translation = np.array(headpose_head_translation)
    headpose_head_translation= np.expand_dims(headpose_head_translation,axis=0)
    facial_landmark = facial_landmark + headpose_head_translation.T
    # get eye center in the original camera coordinate system
    right_eye_center = 0.5*(facial_landmark[:,37]+facial_landmark[:,40])
    left_eye_center = 0.5*(facial_landmark[:,43]+facial_landmark[:,46])
    # get the gaze target
    #gaze_target = np.transpose([annotation[x] for x in gaze_target_indices])
    # set size of normalized image - put in defines
    # normalizing only right eye - for left eye replace centers
    img, headpose_rotation = normalizeImg(img, right_eye_center, head_rotate)

    # convert the gaze direction and head pose in the camera coordinate system to the angle in the polar
    # coordinate system. got to understand what the hell happens here
    M , jacobian= cv2.Rodrigues(headpose_rotation)
    zv = M[:, 2]
    # vertical angle
    head_pose_theta = np.arcsin(zv[1])
    # horizontal angle
    head_pose_phi = np.arctan2(zv[0], zv[2])
    head_pose = np.array([head_pose_theta,head_pose_phi])
    return head_pose,img




