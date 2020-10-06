import ctypes
import tkinter

from UtilsAndModels.Defines import *


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
def set_camera(width, height):
    cap = cv2.VideoCapture(0)
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
    # print("width",width)
    # print("height", height)
    diagonal_pixel = np.sqrt(np.square(width) + np.square(height))
    # print("diagonal pixel: ", diagonal_pixel)
    diagonal_mm = screen_size_inch / MM_TO_IN
    pixel_per_mm = diagonal_pixel/diagonal_mm
    # print("pixel_per_mm ", pixel_per_mm)
    return pixel_per_mm

def get_dpi():
    # Set process DPI awareness
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    # Create a tkinter window
    root = tkinter.Tk()
    # Get a DC from the window's HWND
    dc = ctypes.windll.user32.GetDC(root.winfo_id())
    # The the monitor phyical width
    # (returned in millimeters then converted to inches)
    mw = ctypes.windll.gdi32.GetDeviceCaps(dc, 4) * MM_TO_IN
    # The the monitor phyical height
    mh = ctypes.windll.gdi32.GetDeviceCaps(dc, 6) * MM_TO_IN
    # Get the monitor horizontal resolution
    dw = ctypes.windll.gdi32.GetDeviceCaps(dc, 8)
    # Get the monitor vertical resolution
    dh = ctypes.windll.gdi32.GetDeviceCaps(dc, 10)
    # Destroy the window
    root.destroy()

    # Horizontal and vertical DPIs calculated
    hdpi, vdpi = dw / mw, dh / mh
    # Diagonal DPI calculated using Pythagoras
    ddpi = (dw ** 2 + dh ** 2) ** 0.5 / (mw ** 2 + mh ** 2) ** 0.5
    # Print the DPIs
    print(round(hdpi, 1), round(vdpi, 1), round(ddpi, 1))


#
# def eye_detector(img, shape):
#     right_eye = get_eye(shape, 38, 40, 39, 36)
#     left_eye = get_eye(shape, 44, 46, 45, 42)
#     return right_eye, left_eye
#
#
# def get_eye_center(eye):
#      x_center = (eye[0][0] + eye[1][0]) / 2
#      y_center = (eye[0][1] + eye[1][1]) / 2
#      return np.array([x_center, y_center, 0])

# def draw_axis(img, yaw, pitch, roll, tdx=None, tdy=None, size=100):
#     pitch = pitch * np.pi / 180
#     yaw = -(yaw * np.pi / 180)
#     roll = roll * np.pi / 180
#
#     if tdx != None and tdy != None:
#         tdx = tdx
#         tdy = tdy
#     else:
#         height, width = img.shape[:2]
#         tdx = width / 2
#         tdy = height / 2
#
#     # X-Axis pointing to right. drawn in red
#     x1 = size * (np.cos(yaw) * np.cos(roll)) + tdx
#     y1 = size * (np.cos(pitch) * np.sin(roll) + np.cos(roll) * np.sin(pitch) * np.sin(yaw)) + tdy
#
#     # Y-Axis | drawn in green
#     #        v
#     x2 = size * (-np.cos(yaw) * np.sin(roll)) + tdx
#     y2 = size * (np.cos(pitch) * np.cos(roll) - np.sin(pitch) * np.sin(yaw) * np.sin(roll)) + tdy
#
#     # Z-Axis (out of the screen) drawn in blue
#     x3 = size * (np.sin(yaw)) + tdx
#     y3 = size * (-np.cos(yaw) * np.sin(pitch)) + tdy
#
#     cv2.line(img, (int(tdx), int(tdy)), (int(x1), int(y1)), (0, 0, 255), 3)
#     cv2.line(img, (int(tdx), int(tdy)), (int(x2), int(y2)), (0, 255, 0), 3)
#     cv2.line(img, (int(tdx), int(tdy)), (int(x3), int(y3)), (255, 0, 0), 2)
#
#     return img

# def print_gaze_line(img, eye_center, gaze_vector, r_vec, t_vec):
#     length = 0.0001
#     gaze_vector = gaze_vector / np.linalg.norm(gaze_vector)
#     points = np.array([eye_center + length * gaze_vector])
#     (eye_end_point2D, jacobian) = cv2.projectPoints(points, r_vec, t_vec, camera_matrix_a, dist_coeff_a)
#     p1 = (int(eye_center[0]), int(eye_center[1]))
#     p2 = (int(eye_end_point2D[0][0][0]), int(eye_end_point2D[0][0][1]))
#     cv2.line(img, p1, p2, (255, 255, 0), 2)
#     return img

# def add_data_on_img(frame, gaze_angles, fps):
#     gaze_angles = gaze_angles[0]
#     head_angles = frame.get_head_pose()
#     cv2.putText(frame.debug_img, "gaze angles: " + str(gaze_angles[0]) + "  " + str(gaze_angles[1]),
#                 (100, 100), font, 1, (0, 150, 0), 2, cv2.LINE_4)
#     cv2.putText(frame.debug_img, "head angles: " + str(head_angles[0]) + "  " + str(head_angles[1]),
#                 (100, 200), font, 1, (0, 150, 0), 2, cv2.LINE_4)
#     cv2.putText(frame.debug_img, "fps  :  " + str(fps), (100, 300), font, 1, (0, 150, 0), 2, cv2.LINE_4)
#
#

# def draw_gaze(image_in, eye_pos, pitchyaw, length=200, thickness=1, color=(0, 0, 255)):
#     image_out = image_in
#     if len(image_out.shape) == 2 or image_out.shape[2] == 1:
#         image_out = cv2.cvtColor(image_out, cv2.COLOR_GRAY2BGR)
#
#     dx = -length * np.sin(pitchyaw[1])
#     dy = -length * np.sin(pitchyaw[0])
#     cv2.arrowedLine(image_out, tuple(np.round(eye_pos).astype(np.int32)),
#                     tuple(np.round([eye_pos[0] + dx, eye_pos[1] + dy]).astype(int)), color,
#                     thickness, cv2.LINE_AA, tipLength=0.5)
#     return image_out

#
# class fpsHelper:
#
#     def __init__(self):
#         self.last_time = datetime.datetime.now()
#         self.counter = 0
#         self.fps = 0
#
#     def reg_time(self):
#         self.counter = self.counter+1
#         time_elapsed = datetime.datetime.now() - self.last_time
#         if time_elapsed.seconds.pixel_real >= 1:
#             self.fps = (self.counter / time_elapsed.seconds.pixel_real)
#             self.counter = 0
#             self.last_time = datetime.datetime.now()
#
#     def get_fps(self):
#         return self.fps
#
