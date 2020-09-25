import utils
from HeadPoseBasedSolution.NewImgPreProcess.NormalizeData import *


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

    def flip(self):
        self.debug_img = cv2.flip(self.debug_img, 1)

    def face_landmark_detect(self, head_loc=None):
        if head_loc is not None:
            return True
        gray = cv2.cvtColor(self.orig_img, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)
        if np.size(rects) > 0:
            self.shape = utils.shape_to_np(predictor(gray, rects[0]))
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
        # TODO: check how to enable flags=cv2.SOLVEPNP_EPNP
        (success, self.rotation_vector, self.translation_vector) = cv2.solvePnP(mini_face_model_adj, landmarks,
                                                                                camera_matrix,
                                                                                dist_coeffs,  True)
        (success, self.rotation_vector, self.translation_vector) = cv2.solvePnP(mini_face_model_adj, landmarks,
                                                                                camera_matrix,
                                                                                dist_coeffs, self.rotation_vector,
                                                                                self.translation_vector, True)
        # print("hr is ", self.rotation_vector)
        # print("ht is ", self.translation_vector)
        # Project a 3D point (0, 0, 1000.0) onto the image plane.
        # (nose_end_point2D, jacobian) = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), self.rotation_vector,
        #                                                  self.translation_vector, camera_matrix, dist_coeffs)
        #
        # p1 = (int(image_points[NOSE_INDEX][0]), int(image_points[NOSE_INDEX][1]))
        # p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))
        # if self.is_debug:
        #     cv2.line(self.debug_img, p1, p2, (255, 0, 0), 2)
        # rot = Rotation.from_rotvec(self.rotation_vector)
        # model3d = camera_matrix_a @ self.rotation_vector.T + self.translation_vector
        # self.angles = rot.as_euler('XYZ')[:2] * np.array([1, -1])

    def pre_process_for_net(self):
        net_input = normalizeData(self.orig_img, mini_face_model, self.rotation_vector, self.translation_vector,
                                  self.camera_matrix)
        # show results of right eye image
        self.r_eye = net_input[0]
        self.l_eye = net_input[1]

    # def eyes_detect(self):
    #      self.r_eye, self.l_eye = eye_detector(self.orig_img, self.shape)
