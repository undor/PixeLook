from UtilsAndModels.Defines import *
from mss import mss


def get_screen_shot():
    with mss() as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        return sct_img


def post_screen_shot(im):
    frame = np.array(im, dtype=np.uint8)
    return np.flip(frame[:, :, :3], 2)


# vectors and geometric methods
def _normalize_vector(vector: np.ndarray) -> np.ndarray:
    return vector / np.linalg.norm(vector)


def convert_to_unit_vector(angles):
    x = -torch.cos(angles[0]) * torch.sin(angles[1])
    y = -torch.sin(angles[0])
    z = -torch.cos(angles[1]) * torch.cos(angles[1])
    norm = torch.sqrt(x ** 2 + y ** 2 + z ** 2)
    x /= norm
    y /= norm
    z /= norm
    return x, y, z


def convert_to_unit_vector_np(angles):
    x = -np.cos(angles[0]) * np.sin(angles[1])
    y = -np.sin(angles[0])
    z = -np.cos(angles[1]) * np.cos(angles[1])
    norm = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    x /= norm
    y /= norm
    z /= norm
    return x, y, z


# capture
def set_camera(width, height, camera_number=0):
    cap = cv2.VideoCapture(camera_number)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return cap


# gui and calibration  methods
def from_wh_mm_to_diag_inch(x, y):
    res = (np.sqrt(x ** 2 + y ** 2) * MM_TO_IN)
    return round(res[0][0], 1)

def get_mm_pixel_ratio(screen_size_inch):
    from tkinter import Tk
    root = Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    diagonal_pixel = np.sqrt(np.square(width) + np.square(height))
    diagonal_mm = screen_size_inch / MM_TO_IN
    pixel_per_mm = diagonal_pixel/diagonal_mm
    return pixel_per_mm

def draw_gaze(image_in, eye_pos, pitchyaw, length=200, thickness=1, color=(255, 0, 0)):
    image_out = image_in
    if len(image_out.shape) == 2 or image_out.shape[2] == 1:
        image_out = cv2.cvtColor(image_out, cv2.COLOR_GRAY2BGR)

    dx = -length * np.sin(pitchyaw[1])
    dy = -length * np.sin(pitchyaw[0])
    cv2.arrowedLine(image_out, tuple(np.round(eye_pos).astype(np.int32)),
                    tuple(np.round([eye_pos[0] + dx, eye_pos[1] + dy]).astype(int)), color,
                    thickness, cv2.LINE_AA, tipLength=0.5)
    return image_out


## check errors
def compute_error(true_pixel,res_pixel, pixel_per_mm):
    x = abs(true_pixel[0] - res_pixel[0])
    y = abs(true_pixel[1] - res_pixel[1])
    d = np.sqrt(x ** 2 + y ** 2)
    err_mm = int(np.true_divide(d, pixel_per_mm))
    err_mm_x = int(np.true_divide(x, pixel_per_mm))
    err_mm_y = int(np.true_divide(y, pixel_per_mm))

    return [x,y,d,err_mm_x,err_mm_y,err_mm]
