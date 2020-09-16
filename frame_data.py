from HeadPoseBasedSolution.NewImgPreProcess.NormalizeData import *


def shape_to_np(shape, dtype="float32"):
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
        self.camera_matrix = np.array([960., 0., 640., 0., 960., 360., 0., 0., 1.]).reshape(3, 3)
        self.net_input = 0

    # def get_head_pose(self):
    #     return self.head_pose

    def flip(self):
        self.debug_img = cv2.flip(self.debug_img, 1)

    def face_landmark_detect(self):
        gray = cv2.cvtColor(self.orig_img, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)
        if np.size(rects) > 0:
            self.shape = shape_to_np(predictor(gray, rects[0]))
            self.is_face = True
        return self.is_face

    # def eyes_detect(self):
    #     self.r_eye, self.l_eye = eye_detector(self.orig_img, self.shape)

    def head_pose_detect(self):
        landmarks = self.shape
        mini_face_model_adj = mini_face_model.T.reshape(mini_face_model.shape[1], 1, 3)
        # check for distortion
        dist_coeffs = np.zeros((5, 1))  # Assuming no lens distortion
        # TODO: check how to enable flags=cv2.SOLVEPNP_EPNP
        (success, self.rotation_vector, self.translation_vector) = cv2.solvePnP(mini_face_model_adj, landmarks,
                                                                                self.camera_matrix,
                                                                                dist_coeffs,  True)
        (success, self.rotation_vector, self.translation_vector) = cv2.solvePnP(mini_face_model_adj, landmarks,
                                                                                self.camera_matrix,
                                                                                dist_coeffs, self.rotation_vector,
                                                                                self.translation_vector, True)

        print("hr is ", self.rotation_vector)
        print("ht is ", self.translation_vector)

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

    def pre_proccess_for_net(self):
        net_input = normalizeData(self.orig_img, mini_face_model, self.rotation_vector, self.translation_vector,
                                  self.camera_matrix)
        # show results of right eye image
        self.r_eye = net_input[0]
        self.l_eye = net_input[1]
        # show normalized image