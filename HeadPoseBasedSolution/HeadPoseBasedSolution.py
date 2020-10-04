import HeadPoseBasedSolution.model.GazeModel as GazeModel
from FrameData import *


class environment_hp:
    def __init__(self):
        self.model = GazeModel.Model()
        checkpoint = torch.load("/HeadPoseBasedSolution/model/checkpoint_0040.pth",
                                map_location='cpu')
        model.load_state_dict(checkpoint['model'])
        model.eval()
        self.cap = utils.set_camera(1280,720)
        utils.global_camera_matrix = np.array([960., 0., 640., 0., 960., 360., 0., 0., 1.]).reshape(3, 3)
        utils.global_camera_coeffs = np.zeros((5, 1))

    def find_gaze(self, input_img=None):
        reruns = 100
        for counter_error in range(1, reruns):
            if input_img is None:
                ret, frame = self.cap.read()
            else:
                frame = input_img
            cur_frame = FrameData(frame)
            if cur_frame.face_landmark_detect():
                cur_frame.head_pose_detect()
                cur_frame = cur_frame.pre_process_for_net_hp()
                with torch.no_grad():
                    gaze_net = self.model(cur_frame.img_for_net,cur_frame.head_pose_for_net)
                    # reye!
                    gaze = gaze_net * np.array([1, -1])
                    return gaze, cur_frame.translation_vector
        print("Find Gaze was unable to detect your face!")
        return 0, cur_frame.translation_vector

    def pre_process_for_net_hp (self,cur_frame):
        # normalize rortaion vector
        rot = Rotation.from_rotvec(cur_frame.rotation_vector)
        rot_mat = rot.as_matrix()
        Fc = cur_frame.shape @ rot_mat.T + cur_frame.translation_vector
        re = 0.5 * (Fc[:, 0] + Fc[:, 1]).reshape((3, 1))  # center of left eye
        le = 0.5 * (Fc[:, 2] + Fc[:, 3]).reshape((3, 1))  # center of right eye

        distance = np.linalg.norm(re)  # actual distance between eye and original camera
        z_axis = utils._normalize_vector(re.ravel())
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
        normalized_head_rot2d = euler_angles2d * np.array([1, -1])

        # prepare for net - only for REYE!!!
        normalized_image = normalized_image[:,::-1]
        normalize_head_pose =normalized_head_rot2d * np.array([1, -1])

        cur_frame.img_for_net = normalized_image
        cur_frame.head_pose_for_net = normalize_head_pose
        return cur_frame


my_env_hp = environment_hp()
