from helpers import utils
import numpy as np
from frame_data import *
from FullFaceSolution.models import gazenet
from Defines import *
import cv2
from Calibration.gui_manager import *
from Calibration.calibration import *

def load_face_model():
    device = torch.device("cpu")
    model = gazenet.GazeNet(device)
    state_dict = torch.load('FullFaceSolution/models/weights/gazenet.pth', map_location=device)
    model.load_state_dict(state_dict)
    model.eval()
    return model

def start_camera_sol():
    model =load_face_model()
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
                    cur_frame= utils.normalize_face(cur_frame)
                    # Predict gaze
                    with torch.no_grad():
                        gaze = model.get_gaze(cur_frame.debug_img)
                        gaze = gaze[0].data.cpu()
                    # Draw results
                    display = cv2.circle(display, cur_frame.gaze_origin, 3, (0, 255, 0), -1)
                    display = utils.draw_gaze(display, cur_frame.gaze_origin, gaze, color=(255, 0, 0), thickness=2)
                    # play_stage
                    calibration_manager.play_stage(gaze)

            # cv2.imshow('Gaze Demo', display)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

