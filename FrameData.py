import UtilsAndModels.utils as utils
from HeadPoseBasedSolution.NewImgPreProcess.NormalizeData import *
from scipy.spatial.transform import Rotation

class FrameData:
    def __init__(self, img, is_debug=True):
        self.orig_img = img
        self.debug_img = img
        self.is_face = False
        self.shape = 0
        self.rotation_vector = np.zeros(3)
        self.translation_vector = np.zeros(3)
        self.is_debug = is_debug
        self.gaze_origin = 0
        self.net_input = 0
        self.img_for_net = 0
        self.head_pose_for_net = 0

    def flip(self):
        self.debug_img = cv2.flip(self.debug_img, 1)

    def shape_to_np(self, shape, dtype="float32"):
        # initialize the list of (x, y)-coordinates
        relevant_locations = [36, 39, 42, 45, 48, 54]
        coords = np.zeros((len(relevant_locations), 2), dtype=dtype)
        j = 0
        # loop over all facial landmarks and convert them
        # to a 2-tuple of (x, y)-coordinates
        for i in relevant_locations:
            coords[j] = (shape.part(i).x, shape.part(i).y)
            j = j + 1
        # return the list of (x, y)-coordinates
        return coords

    def face_landmark_detect(self, head_loc=None):
        if head_loc is not None:
            return True
        gray = cv2.cvtColor(self.orig_img, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)
        if np.size(rects) > 0:
            self.shape = self.shape_to_np(predictor(gray, rects[0]))
            self.is_face = True
        return self.is_face

    def head_pose_detect(self, head_loc=None):
        if head_loc is None:
            landmarks = self.shape
        else:
            landmarks = head_loc
        mini_face_model_adj = mini_face_model.T.reshape(mini_face_model.shape[1], 1, 3)
        # check for distortion
        dist_coeffs = utils.global_camera_coeffs
        camera_matrix = utils.global_camera_matrix
        rvec = np.zeros(3, dtype=np.float)
        tvec = np.array([0, 0, 1], dtype=np.float)
        (success, self.rotation_vector, self.translation_vector) = cv2.solvePnP(mini_face_model_adj, landmarks,
                                                                                camera_matrix,
                                                                                dist_coeffs,rvec,tvec,
                                                                                useExtrinsicGuess=True,
                                                                                flags=cv2.SOLVEPNP_ITERATIVE )


    def pre_process_for_net(self):
        rotation_hp = Rotation.from_rotvec(self.rotation_vector)
        net_input = normalizeData(self.orig_img, mini_face_model, self.rotation_vector, self.translation_vector,
                                  utils.global_camera_matrix)
        # show results of right eye image
        self.r_eye = net_input[0]
        self.l_eye = net_input[1]

    # def eyes_detect(self):
    #      self.r_eye, self.l_eye = eye_detector(self.orig_img, self.shape)
