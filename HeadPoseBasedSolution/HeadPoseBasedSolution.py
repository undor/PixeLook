from HeadPoseBasedSolution.model.HeadPoseModel import *
from SolutionEnv import *

#Head Pose solution solution Env
class environment_hp(SolutionEnv):
    def __init__(self,is_right_eye=True):
        SolutionEnv.__init__(self)
        self.is_right_eye = is_right_eye

    def use_net(self,cur_frame):
        with torch.no_grad():
            gaze = self.model.get_gaze(cur_frame.img_for_net, cur_frame.head_pose_for_net)
        if self.is_right_eye:
            gaze = gaze * np.array([1, -1])
        return gaze

    def create_frame(self,img):
        cur_frame = FrameData(img)
        return cur_frame

    def init_net_model(self):
        self.model = Model()
        state_dict = torch.load("HeadPoseBasedSolution/model/trainedHeadPoseNet.pth")
        self.model.load_state_dict(state_dict['model'])
        self.model.eval()

    def head_pose_detect_for_net(self,cur_frame):
            rvec = np.zeros(3, dtype=np.float)
            tvec = np.array([0, 0, 1], dtype=np.float)
            return cv2.solvePnP(LANDMARKS_HP, cur_frame.landmarks_all,utils.global_camera_matrix,
                                utils.global_camera_coeffs, rvec, tvec,useExtrinsicGuess=True,
                                flags=cv2.SOLVEPNP_ITERATIVE)

    def pre_process_for_net(self,cur_frame):
        # get head pose vectors
        ___ , rotation_vector_hp_net, translation_vector_hp_net = self.head_pose_detect_for_net(cur_frame)

        # set model eye center
        rot = Rotation.from_rotvec(rotation_vector_hp_net)
        rot_mat = rot.as_matrix()
        face_model_moved = LANDMARKS_HP @ rot_mat.T + translation_vector_hp_net
        if self.is_right_eye:
            eye_center = face_model_moved[REYE_INDICES].mean(axis=0)  # center of right eye
        else:
            eye_center = face_model_moved[LEYE_INDICES].mean(axis=0)  # center of left eye

        # create relevant
        distance = np.linalg.norm(eye_center)  # actual distance between eye and original camera
        z_axis = utils._normalize_vector(eye_center.ravel())
        head_x_axis = rot_mat[:, 0]
        y_axis = utils._normalize_vector(np.cross(z_axis, head_x_axis))
        x_axis = utils._normalize_vector(np.cross(y_axis, z_axis))

        norm_rotation = Rotation.from_dcm(np.vstack([x_axis,y_axis,z_axis]))

        # save data for outside
        self.extra_data = norm_rotation.as_matrix()

        camera_matrix_inv = np.linalg.inv(utils.global_camera_matrix)
        camera_matrix_normalize= np.array([[960., 0., 30],
                                   [0., 960., 18.],
                                  [ 0., 0., 1.],],  dtype=np.float)
        scale = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 0.6 / distance],
        ],
                        dtype=np.float)


        conversion_matrix = scale @ norm_rotation.as_matrix()
        projection_matrix = camera_matrix_normalize @ conversion_matrix @ camera_matrix_inv

        # normalize images
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

        if self.is_right_eye:
            normalized_image = normalized_image[:,::-1]
            normalize_head_pose = normalize_head_pose * np.array([1, -1])

        cur_frame.img_for_net = normalized_image
        cur_frame.head_pose_for_net = normalize_head_pose
        return cur_frame

my_env_hp = environment_hp()
