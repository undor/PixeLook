import HeadPoseBasedSolution.GazeModel as GazeModel
from frame_data import *


class environment_hp:
    def __init__(self):
        self.model = GazeModel.load_model()
        self.cap = cv2.VideoCapture(0)

    def find_gaze(self):
        ret, img = self.cap.read()
        cur_frame = FrameData(img)
        for counter_error in range(1, 100):
            if cur_frame.face_landmark_detect():
                cur_frame.head_pose_detect()
                cur_frame.pre_proccess_for_net()
                gaze = GazeModel.use_net(self.model, cur_frame)
                print("final gaze is ", gaze)
                print("with shape : ", gaze.shape)
                return gaze,cur_frame.translation_vector,cur_frame.rotation_vector

        sys.exit("didn't detect face for hundred tries")


my_env_hp = environment_hp()
