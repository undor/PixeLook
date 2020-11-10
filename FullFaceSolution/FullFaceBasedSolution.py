from FullFaceSolution.model.FullFaceModel import *
from SolutionEnv import *


# Full Face solution Env
class environment_ff(SolutionEnv):
    def __init__(self, camera_number):
        SolutionEnv.__init__(self, camera_number=camera_number)
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
        cur_frame = FrameData(img)
        cur_frame.debug_img = img[:, :, ::-1]
        cur_frame.flip()
        return cur_frame

    def pre_process_for_net(self, cur_frame: FrameData):
        rcenter , lcenter = cur_frame.get_eye_centers()

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
        cur_frame.gaze_origin = gaze_origin

        #
        # deb_img =  cv2.resize(cur_frame.debug_img,(0,0),False , 0.5,0.5)
        # deb_img[0:112,0:112] = cur_frame.img_for_net
        # cv2.imshow("fdsfs",deb_img)
        # cv2.waitKey()
        return cur_frame