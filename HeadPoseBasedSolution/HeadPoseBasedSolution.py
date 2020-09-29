import HeadPoseBasedSolution.GazeModel as GazeModel
from frame_data import *


class environment_hp:
    def __init__(self):
        self.model = GazeModel.load_model()
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        utils.global_camera_matrix = np.array([960., 0., 640., 0., 960., 360., 0., 0., 1.]).reshape(3, 3)
        utils.global_camera_coeffs = np.zeros((5, 1))

    def find_gaze(self, input_img=None, head_loc=None):
        if input_img is None:
            ret, frame = self.cap.read()
            reruns = 100
        else:
            frame = input_img
            reruns = 2
        cur_frame = FrameData(frame)
        for counter_error in range(1, reruns):
            if cur_frame.face_landmark_detect(head_loc):
                cur_frame.head_pose_detect(head_loc)
                cur_frame.pre_process_for_net()
                gaze = GazeModel.use_net(self.model, cur_frame)

                return gaze, cur_frame.translation_vector
        print("Find Gaze was unable to detect your face!")
        return 0, cur_frame.translation_vector


my_env_hp = environment_hp()
