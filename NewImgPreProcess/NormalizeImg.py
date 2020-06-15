import sys
import numpy as np
import cv2


def normalizeImg(inputImg, right_eye_center, head_rotate, gaze_c, roiSize, cameraMatrix, focal_new, distance_new):

    if len(sys.argv) < 8:
        # focal length of the virtual camera can be changed as needed
        focal_new = 960
    if len(sys.argv) < 9:
        # can't change that or else gaze label will be different [mm]
        distance_new = 600
    distance = np.norm(right_eye_center)
    #distance = np.linalg.norm(right_eye_center, 2)

    z_scale = distance_new / distance
    # check if we need this new cam_new matrix or can use the one we are using anyway
    cam_new = [[focal_new, 0, roiSize(1)/2], [0, focal_new, roiSize(2)/2], [0, 0, 1]]
    scale_mat = [[1, 0, 0], [0, 1, 0], [0, 0, z_scale]]
    head_rotate_x = head_rotate[:1]

    forward = (right_eye_center/distance)
    down = np.cross(forward, head_rotate_x)
    down = down / np.linalg.norm(down)
    right = np.cross(down, forward)
    right = right / np.linalg.norm(right)
    # [1x3]
    rot_mat = [right, down, forward]
    # super matrix
    warp_mat = (cam_new@scale_mat)@(rot_mat*np.linalg.inv(cameraMatrix))
    img_warped = cv2.warpPerspective(inputImg, warp_mat, 'DSize', roiSize)

    # rotation normalization
    cnv_mat = scale_mat@rot_mat
    head_rotate_new = cnv_mat@head_rotate
    head_rotate_new = cv2.Rodrigues(head_rotate_new)
    head_translation_new = cnv_mat @ right_eye_center

    return img_warped, head_rotate_new
