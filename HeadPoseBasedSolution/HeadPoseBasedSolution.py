import HeadPoseBasedSolution.GazeModel as GazeModel
from frame_data import *


class environment_hp:
    def __init__(self):
        self.model = GazeModel.load_model()
        self.cap = cv2.VideoCapture(0)

    def find_gaze(self, input_img=None):
        if input_img is None:
            ___, frame = self.cap.read()
        else:
            frame = input_img
        cur_frame = FrameData(frame)
        for counter_error in range(1, 100):
            if cur_frame.face_landmark_detect():
                cur_frame.head_pose_detect()
                cur_frame.pre_process_for_net()
                gaze = GazeModel.use_net(self.model, cur_frame)

                return gaze, cur_frame.translation_vector

        sys.exit("Find Gaze was unable to detect your face!")


my_env_hp = environment_hp()
