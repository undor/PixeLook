from FullFaceSolution.model.FullFaceModel import *
from SolutionEnv import *


# Full Face solution Env
class environment_ff(SolutionEnv):
    def __init__(self):
        SolutionEnv.__init__(self)
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
        shape = cur_frame.landmarks_6

        rcenter_x = (shape[0][0] + shape[1][0]) / 2
        rcenter_y = (shape[0][1] + shape[1][1]) / 2

        lcenter_x = (shape[2][0] + shape[3][0]) / 2
        lcenter_y = (shape[2][1] + shape[3][1]) / 2

        lcenter = tuple([rcenter_x, rcenter_y])
        rcenter = tuple([lcenter_x, lcenter_y])

        gaze_origin = (int((lcenter[0] + rcenter[0]) / 2), int((lcenter[1] + rcenter[1]) / 2))
        # compute the angle between the eye centers
        dY = rcenter[1] - lcenter[1]
        dX = rcenter[0] - lcenter[0]
        angle = np.degrees(np.arctan2(dY, dX)) - 180

        # desired x-coordinate of the left and right eye
        left_eye_desired_percent = (0.70, 0.35)
        right_eye_x_desired_percent = 1.0 - left_eye_desired_percent[0]

        # determine the scale of the new resulting image
        dist_px = np.sqrt((dX ** 2) + (dY ** 2))
        new_dist_px = (right_eye_x_desired_percent - left_eye_desired_percent[0]) * self.img_size_for_net
        scale = new_dist_px / dist_px

        # get rotation matrix for rotating and scaling the face
        M = cv2.getRotationMatrix2D(gaze_origin, angle, scale)

        # update the translation component of the matrix
        tX = self.img_size_for_net * 0.5
        tY = self.img_size_for_net * left_eye_desired_percent[1]
        M[0, 2] += (tX - gaze_origin[0])
        M[1, 2] += (tY - gaze_origin[1])

        # apply the affine transformation
        cur_frame.flip()
        cur_frame.img_for_net = cv2.warpAffine(cur_frame.debug_img, M, (self.img_size_for_net, self.img_size_for_net), flags=cv2.INTER_CUBIC)
        # cur_frame.img_for_net = cv2.cvtColor(cur_frame.img_for_net, cv2.COLOR_BGR2GRAY)
        # cur_frame.img_for_net = cv2.equalizeHist(cur_frame.img_for_net)
        # cv2.imshow("before", img)
        # cv2.waitKey()
        # cv2.imshow("after", img)
        # cv2.waitKey()
        cur_frame.gaze_origin = gaze_origin
        return cur_frame


my_env_ff = environment_ff()
