from Defines import *
import torch

device = 'cuda' if torch.cuda.is_available() else 'cpu'

NOSE_INDEX: int = 30
REYE_INDICES: np.ndarray = np.array([36, 39])
LEYE_INDICES: np.ndarray = np.array([42, 45])
MOUTH_INDICES: np.ndarray = np.array([48, 54])

## General attributes for eyes recognisition
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(os.getcwd() + "/HeadPoseBasedSolution/model/shape_predictor_68_face_landmarks.dat")
error_img = cv2.imread(os.getcwd() + "/error.jpg")

width_precent = 20
height_precent = 50


def draw_axis(img, yaw, pitch, roll, tdx=None, tdy=None, size = 100):

    pitch = pitch * np.pi / 180
    yaw = -(yaw * np.pi / 180)
    roll = roll * np.pi / 180

    if tdx != None and tdy != None:
        tdx = tdx
        tdy = tdy
    else:
        height, width = img.shape[:2]
        tdx = width / 2
        tdy = height / 2

    # X-Axis pointing to right. drawn in red
    x1 = size * (cos(yaw) * cos(roll)) + tdx
    y1 = size * (cos(pitch) * sin(roll) + cos(roll) * sin(pitch) * sin(yaw)) + tdy

    # Y-Axis | drawn in green
    #        v
    x2 = size * (-cos(yaw) * sin(roll)) + tdx
    y2 = size * (cos(pitch) * cos(roll) - sin(pitch) * sin(yaw) * sin(roll)) + tdy

    # Z-Axis (out of the screen) drawn in blue
    x3 = size * (sin(yaw)) + tdx
    y3 = size * (-cos(yaw) * sin(pitch)) + tdy

    cv2.line(img, (int(tdx), int(tdy)), (int(x1),int(y1)),(0,0,255),3)
    cv2.line(img, (int(tdx), int(tdy)), (int(x2),int(y2)),(0,255,0),3)
    cv2.line(img, (int(tdx), int(tdy)), (int(x3),int(y3)),(255,0,0),2)

    return img


def print_gaze_line(img,eye_center,gaze_vector,r_vec,t_vec):
    length = 0.0001
    gaze_vector = gaze_vector / np.linalg.norm(gaze_vector)
    points =np.array ([eye_center  + length*gaze_vector])
    (eye_end_point2D, jacobian) = cv2.projectPoints(points, r_vec, t_vec, camera_matrix_a, dist_coeff_a)
    p1 = (int(eye_center[0]), int(eye_center[1]))
    p2 = (int(eye_end_point2D[0][0][0]), int(eye_end_point2D[0][0][1]))
    cv2.line(img, p1, p2, (255, 255, 0), 2)
    return img

def get_eye_center(eye):
    x_center = (eye[0][0]+eye[1][0])/2
    y_center = (eye[0][1]+eye[1][1])/2
    return np.array([x_center,y_center,0])

def angle_to_vector(angles):
        pitch, yaw = angles[0]
        return -np.array([
            np.cos(pitch) * np.sin(yaw),
            np.sin(pitch),
            np.cos(pitch) * np.cos(yaw)
        ])

def _normalize_vector(vector: np.ndarray) -> np.ndarray:
    return vector / np.linalg.norm(vector)

def get_eye(shape,top,bottom,right,left):
    eye_width = shape[right][0] - shape[left][0]
    eye_height = shape[bottom][1] - shape[top][1]
    eye_width_add = int(eye_width * width_precent / 100)
    eye_height_add = int(eye_height * height_precent / 100)

    eye_left = shape[left][0] - eye_width_add
    eye_top = shape[top][1] - eye_height_add

    eye_height = eye_height + 2*eye_height_add
    eye_width = eye_width + 2*eye_width_add
    return [(eye_left , eye_top), (eye_left + eye_width, eye_top+ eye_height)]

def normalize_eye(frame,eye):
    eye_img = frame[eye[0][1]:eye[1][1], eye[0][0]:eye[1][0]]
    # eye_img = cv2.warpPerspective(eye_img,)
    ## FIXME - WARP eye img
    eye_img = cv2.resize(eye_img, (60,36), interpolation=cv2.INTER_AREA)
    eye_img = cv2.cvtColor(eye_img, cv2.COLOR_BGR2GRAY)
    eye_img = cv2.equalizeHist(eye_img)

    return eye_img

def eye_detector(img, shape):
        right_eye =get_eye(shape,38,40,39,36)
        left_eye = get_eye(shape,44,46,45,42)
        return right_eye, left_eye
