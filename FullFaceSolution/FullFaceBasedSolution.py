from helpers import utils
import numpy as np
from frame_data import *
from FullFaceSolution.models import gazenet
from Defines import *
import cv2
from Calibration.gui_manager import *
from Calibration.calibration import *

class enviornment:
    def __init__(self):
        self.model = self.load_face_model()
        self.cap = cv2.VideoCapture(0)

    def load_face_model(self):
        device = torch.device("cpu")
        model = gazenet.GazeNet(device)
        state_dict = torch.load('FullFaceSolution/models/weights/gazenet.pth', map_location=device)
        model.load_state_dict(state_dict)
        model.eval()
        return model

    def find_gaze(self):
        ret, frame = self.cap.read()
        cur_frame = FrameData(frame[:, :, ::-1])
        cur_frame.flip()
        img_h, img_w, _ = np.shape(frame)
        # Detect Faces
        display = frame.copy()
        for counter_error in range(1, 10):
            if cur_frame.face_landmark_detect():
                cur_frame.eyes_detect()
                cur_frame = utils.normalize_face(cur_frame)
                # Predict gaze
                with torch.no_grad():
                    gaze = self.model.get_gaze(cur_frame.debug_img)
                    gaze = gaze[0].data.cpu()
                    return gaze
                    # Draw results
                    # display = cv2.circle(display, cur_frame.gaze_origin, 3, (0, 255, 0), -1)
                    # display = utils.draw_gaze(display, cur_frame.gaze_origin, gaze, color=(255, 0, 0), thickness=2)
        return -1

my_env = enviornment()