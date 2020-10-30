from typing import Any

from FrameData import *


# General solution Env

class SolutionEnv:
    def __init__(self, input_mode="camera", screen_record_mode=False):
        self.init_net_model()
        self.input_mode = input_mode
        if self.input_mode == "camera":
            self.cap = utils.set_camera(capture_input_width, capture_input_height)
            self.reruns = 50
        else:
            self.reruns = 1
        utils.global_camera_matrix = np.array([capture_input_width, 0., capture_input_width/2,
                                               0., capture_input_height, capture_input_height/2,
                                               0., 0., 1.]).reshape(3, 3)
        utils.global_camera_coeffs = np.zeros((5, 1))
        self.extra_data = None
        self.screen_record_mode = screen_record_mode
        self.webcam_shot = np.zeros((capture_input_width, capture_input_height))

    def get_img(self, input_img=None):
        if self.input_mode == "camera":
            ret, img = self.cap.read()
            return img
        else:
            return input_img

    def find_gaze(self, input_img=None):
        for counter_error in range(self.reruns):
            img = self.get_img(input_img)
            cur_frame: FrameData = self.create_frame(img)
            if cur_frame.face_landmark_detect():
                cur_frame.head_pose_detect()
                cur_frame = self.pre_process_for_net(cur_frame)
                gaze = self.use_net(cur_frame)
                if self.screen_record_mode:
                    self.webcam_shot = cur_frame.create_show_img(gaze)
                return gaze, cur_frame.translation_vector
        print("Find Gaze was unable to detect your face!")
        return -1, np.array([0, 0, 0])
