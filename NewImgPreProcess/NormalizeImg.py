import sys
import numpy as np
import cv2
## unsidtort to camera
camera_matrix_a = np.array([960., 0., 30,
                            0., 960., 18.,
                            0., 0., 1.]).reshape(3, 3)

def normalizeImg(inputImg, right_eye_center, head_rotate):
    print("head rotate is ", head_rotate)
    focal_new = 960
    distance_new = 600
    # distance = np.norm(right_eye_center)
    distance = np.linalg.norm(right_eye_center, 2) # check it (?)

    z_scale = distance_new / distance
    # check if we need this new cam_new matrix or can use the one we are using anyway
    cam_new = camera_matrix_a
    scale_mat = [[1, 0, 0], [0, 1, 0], [0, 0, z_scale]]
    head_rotate_x = head_rotate[:, 0]

    forward = (right_eye_center/distance)
    down = np.cross(forward, head_rotate_x)
    down = down / np.linalg.norm(down)
    right = np.cross(down, forward)
    right = right / np.linalg.norm(right)
    # [1x3]
    rot_mat = [right, down, forward]
    # super matrix
    warp_mat = (cam_new@scale_mat)@(rot_mat@np.linalg.inv(camera_matrix_a))
    img_warped = cv2.warpPerspective(inputImg, warp_mat, (36,60))

    # rotation normalization
    cnv_mat = np.array(scale_mat) @ np.array(rot_mat)
    head_rotate_new = cnv_mat@head_rotate
    print("head_rotate_new ", head_rotate_new)
    head_rotate_new , jacobian = cv2.Rodrigues(head_rotate_new)
    print("head_rotate_new after rogridez ", head_rotate_new)
    head_translation_new = cnv_mat @ right_eye_center

    return img_warped, head_rotate_new
