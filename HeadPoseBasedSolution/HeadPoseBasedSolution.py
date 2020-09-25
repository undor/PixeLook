import HeadPoseBasedSolution.GazeModel as GazeModel
import utils
from frame_data import *


class environment_hp:
    def __init__(self):
        self.model = GazeModel.load_model()
        self.cap = cv2.VideoCapture(0)
        utils.global_camera_matrix = np.array([960., 0., 640., 0., 960., 360., 0., 0., 1.]).reshape(3, 3)
        utils.global_camera_coeffs = np.zeros((5, 1))

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

        print("Find Gaze was unable to detect your face!")
        return -1, [[0][0][0]]


my_env_hp = environment_hp()
