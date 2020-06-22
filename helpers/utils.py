import cv2
import json
import torch
import numpy as np
from  helpers.math_helper import *

def add_data_on_img(frame, gaze_angles, fps):
    gaze_angles=gaze_angles[0]
    head_angles = frame.get_head_pose()
    cv2.putText(frame.debug_img , "gaze angles: " + str(gaze_angles[0])  +  "  " + str(gaze_angles[1]), (100,100) , font, 1, (0, 150, 0), 2, cv2.LINE_4)
    cv2.putText(frame.debug_img , "head angles: " + str(head_angles[0])  +  "  " + str(head_angles[1]), (100,200) , font, 1, (0, 150, 0), 2, cv2.LINE_4)
    cv2.putText(frame.debug_img , "fps  :  " + str(fps), (100, 300), font, 1,(0, 150, 0), 2, cv2.LINE_4)


def set_camera(width,height):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return cap



def draw_gaze(image_in, eye_pos, pitchyaw, length=200, thickness=1, color=(0, 0, 255)):
    """Draw gaze angle on given image with a given eye positions."""
    image_out = image_in
    if len(image_out.shape) == 2 or image_out.shape[2] == 1:
        image_out = cv2.cvtColor(image_out, cv2.COLOR_GRAY2BGR)

    dx = -length * np.sin(pitchyaw[1])
    dy = -length * np.sin(pitchyaw[0])
    cv2.arrowedLine(image_out, tuple(np.round(eye_pos).astype(np.int32)),
                    tuple(np.round([eye_pos[0] + dx, eye_pos[1] + dy]).astype(int)), color,
                    thickness, cv2.LINE_AA, tipLength=0.5)
    return image_out


def convert_to_unit_vector(angles):
    x = -torch.cos(angles[:, 0]) * torch.sin(angles[:, 1])
    y = -torch.sin(angles[:, 0])
    z = -torch.cos(angles[:, 1]) * torch.cos(angles[:, 1])
    norm = torch.sqrt(x ** 2 + y ** 2 + z ** 2)
    x /= norm
    y /= norm
    z /= norm
    return x, y, z


def compute_angle_error(preds, labels):
    pred_x, pred_y, pred_z = convert_to_unit_vector(preds)
    label_x, label_y, label_z = convert_to_unit_vector(labels)
    angles = pred_x * label_x + pred_y * label_y + pred_z * label_z
    return torch.acos(angles) * 180 / np.pi


def normalize_face(cur_frame):
    # Adapted from imutils package
    shape=cur_frame.shape
    rcenter_x=(shape[38][0]+shape[40][0]+shape[36][0]+shape[39][0])/4
    rcenter_y=(shape[38][1]+shape[40][1]+shape[36][1]+shape[39][1])/4

    lcenter_x=(shape[42][0]+shape[44][0]+shape[45][0]+shape[46][0])/4
    lcenter_y=(shape[42][1]+shape[44][1]+shape[45][1]+shape[46][1])/4

    lcenter=tuple([rcenter_x ,rcenter_y])
    rcenter=tuple([lcenter_x ,lcenter_y])

    left_eye_coord = (0.70, 0.35)

    gaze_origin = (int((lcenter[0] + rcenter[0]) / 2), int((lcenter[1] + rcenter[1]) / 2))
    # compute the angle between the eye centroids
    dY = rcenter[1] - lcenter[1]
    dX = rcenter[0] - lcenter[0]
    angle = np.degrees(np.arctan2(dY, dX)) - 180
    # compute the desired right eye x-coordinate based on the
    # desired x-coordinate of the left eye
    right_eye_x = 1.0 - left_eye_coord[0]

    # determine the scale of the new resulting image by taking
    # the ratio of the distance between eyes in the *current*
    # image to the ratio of distance between eyes in the
    # *desired* image
    dist = np.sqrt((dX ** 2) + (dY ** 2))
    new_dist = (right_eye_x - left_eye_coord[0])
    new_dist *= 112
    scale = new_dist / dist
    # grab the rotation matrix for rotating and scaling the face
    M = cv2.getRotationMatrix2D(gaze_origin, angle, scale)

    # update the translation component of the matrix
    tX = 112 * 0.5
    tY = 112 * left_eye_coord[1]
    M[0, 2] += (tX - gaze_origin[0])
    M[1, 2] += (tY - gaze_origin[1])
    cur_frame.flip()
    # apply the affine transformation
    cur_frame.debug_img = cv2.warpAffine(cur_frame.debug_img, M, (112, 112),
                          flags=cv2.INTER_CUBIC)
    cur_frame.gaze_origin=gaze_origin
    return cur_frame