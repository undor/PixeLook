import UtilsAndModels.utils as utils
from UtilsAndModels.Defines import *
# import time


class FrameData:
    def __init__(self, img, is_debug=True):
        self.orig_img = img
        self.debug_img = img
        self.is_face = False
        self.landmarks_6_points = 0
        self.landmarks_all_points = 0
        self.relevant_locations = [36, 39, 42, 45, 48, 54]
        self.rotation_vector = np.zeros(3)
        self.translation_vector = np.zeros(3)
        self.is_debug = is_debug
        self.gaze_origin = 0
        self.net_input = 0
        self.img_for_net = 0
        self.head_pose_for_net = 0

    def flip(self):
        self.debug_img = cv2.flip(self.debug_img, 1)

    def get_landmarks(self, shape, specific_locations=False):
        if specific_locations:
            landmarks_number = len(self.relevant_locations)
            landmarks_list = self.relevant_locations
        else:
            landmarks_number = 68
            landmarks_list = range(landmarks_number)
        coordinates = np.zeros((landmarks_number, 2), dtype="float32")
        j = 0
        for i in landmarks_list:
            coordinates[j] = (shape.part(i).x, shape.part(i).y)
            j = j + 1
        return coordinates

    def face_landmark_detect(self, head_loc=None):
        if head_loc is not None:
            return True
        gray = cv2.cvtColor(self.orig_img, cv2.COLOR_BGR2GRAY)
        rectangles = face_cascade.detectMultiScale(gray)
        if np.size(rectangles) > 0:
            rect_to_dlib_form = dlib.rectangle(rectangles[0][0], rectangles[0][1], rectangles[0][0] + rectangles[0][2],
                                               rectangles[0][1] + rectangles[0][3])
            # start_time = time.perf_counter()
            prediction = predictor(gray, rect_to_dlib_form)
            # print(time.perf_counter() - start_time)
            # print("2. predict face landmarks took: ", time.perf_counter()-start_time)
            self.landmarks_all_points = self.get_landmarks(prediction, False)
            self.landmarks_6_points = self.landmarks_all_points[self.relevant_locations]
            self.is_face = True
        return self.is_face

    def head_pose_detect(self, head_loc=None):
        if head_loc is None:
            landmarks = self.landmarks_6_points
        else:
            landmarks = head_loc
        mini_face_model_adj = LANDMARKS_6_PNP.T.reshape(LANDMARKS_6_PNP.shape[1], 1, 3)
        distortion_coefficients = utils.global_camera_coeffs
        camera_matrix = utils.global_camera_matrix
        (success, self.rotation_vector, self.translation_vector) = cv2.solvePnP(mini_face_model_adj, landmarks,
                                                                                camera_matrix, distortion_coefficients,
                                                                                True)

        (success, self.rotation_vector, self.translation_vector) = cv2.solvePnP(mini_face_model_adj, landmarks,
                                                                                camera_matrix, distortion_coefficients,
                                                                                self.rotation_vector,
                                                                                self.translation_vector,
                                                                                True)
