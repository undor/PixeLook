from FullFaceSolution.model.FullFaceModel import *
from SolutionEnv import *


# Full Face solution Env
class environment_ff(SolutionEnv):
    def __init__(self):
        SolutionEnv.__init__(self)
        self.model = GazeNet(device)
        self.img_size_for_net = 112

    def use_net(self, cur_frame):
        with torch.no_grad():
            gaze = self.model.get_gaze(cur_frame.img_for_net)
        return gaze.cpu().numpy()[0]

    def init_net_model(self):
        torch.manual_seed(0)
        self.model = GazeNet(device)
        state_dict = torch.load('FullFaceSolution/model/trainedFullFaceNet.pth', map_location=device)
        self.model.load_state_dict(state_dict)
        self.model.eval()

    def create_frame(self, img):
        cur_frame = FrameData(img[:, :, ::-1])
        cur_frame.flip()
        return cur_frame

    def pre_process_for_net(self, cur_frame):
        facial_landmarks = cur_frame.landmarks_6_points

        right_eye_center_x = (facial_landmarks[0][0] + facial_landmarks[1][0]) / 2
        right_eye_center_y = (facial_landmarks[0][1] + facial_landmarks[1][1]) / 2

        left_eye_center_x = (facial_landmarks[2][0] + facial_landmarks[3][0]) / 2
        left_eye_center_y = (facial_landmarks[2][1] + facial_landmarks[3][1]) / 2

        left_eye_center = tuple([right_eye_center_x, right_eye_center_y])
        right_eye_center = tuple([left_eye_center_x, left_eye_center_y])

        gaze_origin = (int((left_eye_center[0] + right_eye_center[0]) / 2),
                       int((left_eye_center[1] + right_eye_center[1]) / 2))

        # compute the angle between the eye centers
        eyes_dist_y = right_eye_center[1] - left_eye_center[1]
        eyes_dist_x = right_eye_center[0] - left_eye_center[0]
        eyes_angle = np.degrees(np.arctan2(eyes_dist_y, eyes_dist_x)) - 180

        # desired x-coordinate of the left and right eye
        left_eye_desired_percent = (0.70, 0.35)
        right_eye_x_desired_percent = 1.0 - left_eye_desired_percent[0]

        # determine the scale of the new resulting image
        dist_px = np.sqrt((eyes_dist_x ** 2) + (eyes_dist_y ** 2))
        new_dist_px = (right_eye_x_desired_percent - left_eye_desired_percent[0]) * self.img_size_for_net
        scale_distance = new_dist_px / dist_px

        # get rotation matrix for rotating and scaling the face
        rotation_matrix = cv2.getRotationMatrix2D(gaze_origin, eyes_angle, scale_distance)

        # update the translation component of the matrix
        translation_x = self.img_size_for_net * 0.5
        translation_y = self.img_size_for_net * left_eye_desired_percent[1]
        rotation_matrix[0, 2] += (translation_x - gaze_origin[0])
        rotation_matrix[1, 2] += (translation_y - gaze_origin[1])

        # apply the affine transformation
        cur_frame.flip()
        cur_frame.img_for_net = cv2.warpAffine(cur_frame.debug_img, rotation_matrix,
                                               (self.img_size_for_net, self.img_size_for_net), flags=cv2.INTER_CUBIC)
        cur_frame.gaze_origin = gaze_origin
        return cur_frame


my_env_ff = environment_ff()
