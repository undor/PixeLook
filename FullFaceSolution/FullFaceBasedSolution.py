from FullFaceSolution.model import gazenet
from FrameData import *


class environment_ff:
    def __init__(self):
        self.model = self.load_face_model()
        self.cap = utils.set_camera(1280, 720)
        utils.global_camera_matrix = np.array([960., 0., 640., 0., 960., 360., 0., 0., 1.]).reshape(3, 3)
        utils.global_camera_coeffs = np.zeros((5, 1))

    def find_gaze(self, input_img=None):
        reruns = 100
        for counter_error in range(1, reruns):
            if input_img is None:
                ret, frame = self.cap.read()
            else:
                frame = input_img
                reruns = 2
            cur_frame = FrameData(frame[:, :, ::-1])
            cur_frame.flip()
            if cur_frame.face_landmark_detect():
                cur_frame.head_pose_detect()
                cur_frame = self.normalize_face(cur_frame)
                with torch.no_grad():
                    gaze = self.model.get_gaze(cur_frame.debug_img)
                    gaze = gaze[0].data.cpu()
                    return gaze, cur_frame.translation_vector
        print("Find Gaze was unable to detect your face!")
        return -1, np.array([0, 0, 0])

    def load_face_model(self):
        torch.manual_seed(0)
        device = torch.device("cpu")
        model = gazenet.GazeNet(device)
        state_dict = torch.load('FullFaceSolution/model/weights/gazenet.pth', map_location=device)
        model.load_state_dict(state_dict)
        model.eval()
        return model

    def normalize_face(self,cur_frame):
        # Adapted from imutils package
        shape = cur_frame.shape
        # 36, 39, 42, 45, 48, 54

        rcenter_x = (shape[0][0] + shape[1][0]) / 2
        rcenter_y = (shape[0][1] + shape[1][1]) / 2

        lcenter_x = (shape[2][0] + shape[3][0]) / 2
        lcenter_y = (shape[2][1] + shape[3][1]) / 2

        lcenter = tuple([rcenter_x, rcenter_y])
        rcenter = tuple([lcenter_x, lcenter_y])

        left_eye_coord = (0.70, 0.35)

        gaze_origin = (int((lcenter[0] + rcenter[0]) / 2), int((lcenter[1] + rcenter[1]) / 2))
        # compute the angle between the eye centroids
        dY = rcenter[1] - lcenter[1]
        dX = rcenter[0] - lcenter[0]
        angle = np.degrees(np.arctan2(dY, dX)) - 180
        # compute the desired right eye x-coordinate based on the
        # desired x-coordinate of the left eye
        right_eye_x = 1.0 - left_eye_coord[0]

        # determine the scale of the new resulting image by taking
        # the ratio of the distance between eyes in the *current*
        # image to the ratio of distance between eyes in the
        # *desired* image
        dist = np.sqrt((dX ** 2) + (dY ** 2))
        new_dist = (right_eye_x - left_eye_coord[0])
        new_dist *= 112
        scale = new_dist / dist
        # grab the rotation matrix for rotating and scaling the face
        M = cv2.getRotationMatrix2D(gaze_origin, angle, scale)

        # update the translation component of the matrix
        tX = 112 * 0.5
        tY = 112 * left_eye_coord[1]
        M[0, 2] += (tX - gaze_origin[0])
        M[1, 2] += (tY - gaze_origin[1])
        cur_frame.flip()
        # apply the affine transformation
        cur_frame.img_for_net = cv2.warpAffine(cur_frame.debug_img, M, (112, 112), flags=cv2.INTER_CUBIC)
        cur_frame.gaze_origin = gaze_origin
        return img_for_net


my_env_ff = environment_ff()
