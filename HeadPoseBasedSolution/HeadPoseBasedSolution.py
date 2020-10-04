from HeadPoseBasedSolution.model.HeadPoseModel import *
from FrameData import *
from scipy.spatial.transform import Rotation
from scipy.spatial.transform import Rotation

from FrameData import *
from HeadPoseBasedSolution.model.HeadPoseModel import *


class environment_hp:
    def __init__(self):
        self.init_net_model()
        self.cap = utils.set_camera(capture_input_width, capture_input_height)
        utils.global_camera_matrix = np.array([960., 0., 640., 0., 960., 360., 0., 0., 1.]).reshape(3, 3)
        utils.global_camera_coeffs = np.zeros((5, 1))

    def find_gaze(self,is_right_eye = True, input_img=None ):
        reruns = 100
        for counter_error in range(1, reruns):
            if input_img is None:
                ret, frame = self.cap.read()
            else:
                frame = input_img
                reruns= 2
            cur_frame = FrameData(frame)
            if cur_frame.face_landmark_detect():
                cur_frame.head_pose_detect(twice=False)
                cur_frame = self.pre_process_for_net(cur_frame, is_right_eye)
                with torch.no_grad():
                    gaze_net = self.model(cur_frame.img_for_net, cur_frame.head_pose_for_net)
                    if is_right_eye:
                        gaze = gaze_net * np.array([1, -1])
                    return gaze, cur_frame.translation_vector
        print("Find Gaze was unable to detect your face!")
        return 0, cur_frame.translation_vector

    def init_net_model(self):
        self.model = Model()
        state_dict = torch.load("HeadPoseBasedSolution/model/trainedHeadPoseNet.pth")
        self.model.load_state_dict(state_dict['model'])
        self.model.eval()

    def pre_process_for_net(self,cur_frame,is_right_eye):
        # normalize rortaion vector
        rot = Rotation.from_rotvec(cur_frame.rotation_vector)
        rot_mat = rot.as_matrix()
        face_model_moved = LANDMARKS_HP @ rot_mat.T + cur_frame.translation_vector
        if (is_right_eye):
            eye_center = face_model_moved[REYE_INDICES].mean(axis=0)  # center of right eye
        else:
            eye_center = face_model_moved[LEYE_INDICES].mean(axis=0)  # center of left eye


        distance = np.linalg.norm(eye_center)  # actual distance between eye and original camera
        z_axis = utils._normalize_vector(eye_center.ravel())
        head_x_axis = rot_mat[:, 0]
        y_axis = utils._normalize_vector(np.cross(z_axis, head_x_axis))
        x_axis = utils._normalize_vector(np.cross(y_axis, z_axis))

        norm_rotation = Rotation.from_martix(np.vstack([x_axis,y_axis,z_axis]))

        # normalize images
        camera_matrix_inv = np.linalg.inv(utils.global_camera_matrix)
        camera_matrix_normalize= [960., 0., 30,
                                   0., 960., 18.,
                                   0., 0., 1.]
        scale = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 0.6 / distance],
        ],
                        dtype=np.float)

        conversion_matrix = scale @ norm_rotation.as_matrix()
        projection_matrix = camera_matrix_normalize @ conversion_matrix @ camera_matrix_inv
        normalized_image = cv2.warpPerspective(
            cur_frame.debug_img, projection_matrix,
            (60, 36))
        normalized_image = cv2.cvtColor(normalized_image,
                                        cv2.COLOR_BGR2GRAY)
        normalized_image = cv2.equalizeHist(normalized_image)

        # normalize head pose
        normalized_head_rot = rot * norm_rotation
        euler_angles2d = normalized_head_rot.as_euler('XYZ')[:2]
        normalize_head_pose = euler_angles2d * np.array([1, -1])

        if (is_right_eye):
            normalized_image = normalized_image[:,::-1]
            normalize_head_pose =normalize_head_pose * np.array([1, -1])

        cur_frame.img_for_net = normalized_image
        cur_frame.head_pose_for_net = normalize_head_pose
        return cur_frame


my_env_hp = environment_hp()
