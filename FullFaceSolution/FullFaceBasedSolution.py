import utils
from Defines import *
from FullFaceSolution.models import gazenet
from frame_data import *


class environment_ff:
    def __init__(self):
        self.model = load_face_model()
        self.cap = cv2.VideoCapture(0)

    def find_gaze(self,input_img = None):
        if input_img == None:
            ret, frame = self.cap.read()
        else:
            frame = input_img
        cur_frame = FrameData(frame[:, :, ::-1])
        cur_frame.flip()
        img_h, img_w, _ = np.shape(frame)
        # Detect Faces
        for counter_error in range(1, 100):
            if cur_frame.face_landmark_detect():
                cur_frame.head_pose_detect()
                cur_frame = utils.normalize_face(cur_frame)
                # Predict gaze
                with torch.no_grad():
                    gaze = self.model.get_gaze(cur_frame.debug_img)
                    gaze = gaze[0].data.cpu()
                    return gaze, cur_frame.translation_vector
                    # Draw results
                    # display = cv2.circle(display, cur_frame.gaze_origin, 3, (0, 255, 0), -1)
                    # display = utils.draw_gaze(display, cur_frame.gaze_origin, gaze, color=(255, 0, 0), thickness=2)
        sys.exit("Find Gaze was not able to find your face!")


def load_face_model():
    torch.manual_seed(0)
    device = torch.device("cpu")
    model = gazenet.GazeNet(device)
    state_dict = torch.load('FullFaceSolution/models/weights/gazenet.pth', map_location=device)
    model.load_state_dict(state_dict)
    model.eval()
    # for param in model.parameters():
    #     print(param.data)
    return model


my_env_ff = environment_ff()
