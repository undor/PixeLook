import UtilsAndModels.utils as utils
from UtilsAndModels.Defines import *


class FrameData:
    def __init__(self, img, is_debug=True):
        self.orig_img = img
        self.debug_img = img
        self.is_face = False
        self.landmarks_6 = 0
        self.landmarks_all = 0
        self.relevant_locations = np.array([36, 39, 42, 45, 48, 54])
        self.rotation_vector = np.zeros(3)
        self.translation_vector = np.zeros(3)
        self.is_debug = is_debug
        self.gaze_origin = 0
        self.net_input = 0
        self.img_for_net = 0
        self.head_pose_for_net = 0

    def flip(self):
        self.debug_img = cv2.flip(self.debug_img, 1)

    def get_eye_centers(self):
        shape = self.landmarks_6

        rcenter_x = (shape[0][0] + shape[1][0]) / 2
        rcenter_y = (shape[0][1] + shape[1][1]) / 2

        lcenter_x = (shape[2][0] + shape[3][0]) / 2
        lcenter_y = (shape[2][1] + shape[3][1]) / 2

        lcenter = tuple([rcenter_x, rcenter_y])
        rcenter = tuple([lcenter_x, lcenter_y])
        return rcenter,lcenter

    def face_landmark_detect(self, head_loc=None, debug_img=None):
        if head_loc is not None:
            return True
        gray = cv2.cvtColor(self.orig_img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray)
        
        if np.size(faces) > 0:
            _, self.landmarks_all = landmark_detector.fit(gray, faces)
            self.landmarks_6 = self.landmarks_all[0][0][self.relevant_locations, :]
            if debug_img is not None:
                for landmark in self.landmarks_6:
                    cv2.circle(img=debug_img, center=(landmark[0], landmark[1]), radius=3, color=(0, 0, 255), thickness=1)
                for face in faces:
                    cv2.rectangle(debug_img, pt1=(face[0], face[1]), pt2=((face[0]+face[2]), (face[1]+face[3])), color=(127, 127, 0), thickness=3)
                cv2.imshow("gray", debug_img)
                cv2.waitKey(0)
            self.is_face = True
        return self.is_face

    def head_pose_detect(self, head_loc=None):
        if head_loc is None:
            landmarks = self.landmarks_6
        else:
            landmarks = head_loc
        mini_face_model_adj = LANDMARKS_6_PNP.T.reshape(LANDMARKS_6_PNP.shape[1], 1, 3)
        dist_coeffs = utils.global_camera_coeffs
        camera_matrix = utils.global_camera_matrix
        (success, self.rotation_vector, self.translation_vector) = cv2.solvePnP(mini_face_model_adj, landmarks,
                                                                                camera_matrix,
                                                                                dist_coeffs,
                                                                                True)

        (success, self.rotation_vector, self.translation_vector) = cv2.solvePnP(mini_face_model_adj, landmarks,
                                                                                camera_matrix,
                                                                                dist_coeffs, self.rotation_vector,
                                                                                self.translation_vector,
                                                                                True)

    def create_show_img(self,pitchyaw):
        r_eye_center , ___  = self.get_eye_centers()
        img = utils.draw_gaze(self.orig_img, eye_pos=r_eye_center, pitchyaw=pitchyaw,thickness=4,length=300)
        # for (x, y) in self.landmarks_all:
        #     cv2.circle(img, (x, y), 2, (0, 255, 0), -1)
        img = cv2.flip(img,1)
        return img