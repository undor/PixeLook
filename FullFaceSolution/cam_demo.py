from helpers import utils
import numpy as np
from frame_data import *
from FullFaceSolution.models import gazenet
from Defines import *
import cv2
from Graphics.screen_game import *


class Calibration_Data():
    left_gaze = (0, 0)
    right_gaze = (0, 0)
    up_gaze = (0, 0)
    down_gaze = (0, 0)
    center_gaze = (0, 0)
    

calibration = Calibration_Data()
gui = FullScreenApp()


def gaze_to_pixel(gaze):
    right_gaze = calibration.right_gaze
    left_gaze = calibration.left_gaze
    up_gaze = calibration.up_gaze
    down_gaze = calibration.down_gaze

    width_length = abs(right_gaze[1] - left_gaze[1])
    print("Gaze: ", gaze, " and up_gaze: ", up_gaze, "and down_gaze: ", down_gaze)
    height_length = abs(down_gaze[0] - up_gaze[0])
    print("width len: ", width_length, "height len: ", height_length)

    width_ratio = (gaze[1] - left_gaze[1]) / width_length
    height_ratio = (gaze[0] - up_gaze[0]) / height_length
    print("width_ratio: ", width_ratio, "height_ratio: ", height_ratio)

    x_location = width_ratio.item() * gui.width
    y_location = height_ratio.item() * gui.height
    print("x location: ", x_location, "y location: ", y_location)

    if 0 < x_location < gui.width and 0 < y_location < gui.height:
        pixel = (x_location, y_location)
        return pixel
    return 0, 0


def play_stage(gui, gaze):
    stage = my_stages.cur_stage
    if stage == WAIT_FOR_LEFT:
        gui.print_pixel((10, gui.height/2))
    if stage == LEFT_CALIBRATION:
        calibration.left_gaze = gaze
        my_stages.next_step()

    if stage == WAIT_FOR_RIGHT:
        gui.print_pixel((gui.width - 10, gui.height / 2))
    if stage == RIGHT_CALIBRATION:
        calibration.right_gaze = gaze
        my_stages.next_step()

    if stage == WAIT_FOR_UP:
        gui.print_pixel((gui.width/2, 10))
    if stage == UP_CALIBRATION:
        calibration.up_gaze = gaze
        my_stages.next_step()

    if stage == WAIT_FOR_DOWN:
        gui.print_pixel((gui.width/2, gui.height - 10))
    if stage == DOWN_CALIBRATION:
        calibration.down_gaze = gaze
        my_stages.next_step()
    if stage == WAIT_FOR_CENTER:
        gui.print_pixel((gui.width/2, gui.height / 2))
    if stage == CENTER_CALIBRATION:
        calibration.center_gaze = gaze
        print("right gaze: ", calibration.right_gaze)
        print("left gaze: ", calibration.left_gaze)
        print("up gaze: ", calibration.up_gaze)
        print("down gaze: ", calibration.down_gaze)
        my_stages.next_step()
    if stage == FINISH_CALIBRATION:
        gui.print_pixel(gaze_to_pixel(gaze))


def calibrate():
    device = torch.device("cpu")
    model = gazenet.GazeNet(device)
    state_dict = torch.load('FullFaceSolution/models/weights/gazenet.pth', map_location=device)
    model.load_state_dict(state_dict)
    model.eval()
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        cur_frame = FrameData(frame[:, :, ::-1])
        cur_frame.flip()
        img_h, img_w, _ = np.shape(frame)
        # Detect Faces
        display = frame.copy()
        if cur_frame.face_landmark_detect():
            cur_frame.eyes_detect()
            # Crop and normalize face Face
            cur_frame = utils.normalize_face(cur_frame)
            face = cur_frame.debug_img

            # Predict gaze
            with torch.no_grad():
                gaze = model.get_gaze(face)
                gaze = gaze[0].data.cpu()
            # Draw results
            display = cv2.circle(display, cur_frame.gaze_origin, 3, (0, 255, 0), -1)
            display = utils.draw_gaze(display, cur_frame.gaze_origin, gaze, color=(255, 0, 0), thickness=2)
            play_stage(gui, gaze)
            gui.update_window()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()



def start_camera_sol2():
    gui= FullScreenApp()
    device = torch.device("cpu")
    model = gazenet.GazeNet(device)
    state_dict = torch.load('FullFaceSolution/models/weights/gazenet.pth', map_location=device)
    model.load_state_dict(state_dict)
    model.eval()
    cap = cv2.VideoCapture(0)
    while True:
            ret, frame = cap.read()
            cur_frame=FrameData(frame[:,:,::-1])
            cur_frame.flip()
            img_h, img_w, _ = np.shape(frame)
            # Detect Faces
            display = frame.copy()
            if cur_frame.face_landmark_detect():
                    cur_frame.eyes_detect()
                    # Crop and normalize face Face
                    cur_frame= utils.normalize_face(cur_frame)
                    face=cur_frame.debug_img

                    # Predict gaze
                    with torch.no_grad():
                        gaze = model.get_gaze(face)
                        gaze = gaze[0].data.cpu()
                    # Draw results
                    display = cv2.circle(display, cur_frame.gaze_origin, 3, (0, 255, 0), -1)
                    display = utils.draw_gaze(display, cur_frame.gaze_origin, gaze, color=(255, 0, 0), thickness=2)

            gui.update_window()
            cv2.imshow('Gaze Demo', display)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

