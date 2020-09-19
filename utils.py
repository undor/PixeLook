from Defines import *
import tkinter
import ctypes


def shape_to_np(shape, dtype="float32"):
    # initialize the list of (x, y)-coordinates
    relevant_locations = [36, 39, 42, 45, 48, 54]
    coords = np.zeros((len(relevant_locations), 2), dtype=dtype)
    j = 0
    # loop over all facial landmarks and convert them
    # to a 2-tuple of (x, y)-coordinates
    for i in relevant_locations:
        coords[j] = (shape.part(i).x, shape.part(i).y)
        j = j + 1
    # return the list of (x, y)-coordinates
    return coords


# TODO - handle the mm to position on screen problem - dpi of tkinter not allways = screen DPI
def get_mm_pixel_ratio(screen_size_inch):
    from tkinter import Tk
    root = Tk()
    width = root.winfo_screenwidth() * 2
    height = root.winfo_screenheight() * 2
    print("screen width is: ", width, "and height is: ", height)
    diagonal_pixel = np.sqrt(np.square(width) + np.square(height))
    print("diagonal pixel: ", diagonal_pixel)
    diagonal_mm = screen_size_inch / MM_TO_IN
    pixel_per_mm = diagonal_pixel/diagonal_mm
    print("pixel_per_mm ", pixel_per_mm)
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


def convert_to_unit_vector(angles):
    v = np.zeros(3)
    v[0] = -torch.cos(angles[0]) * torch.sin(angles[1])
    v[1] = -torch.sin(angles[0])
    v[2] = -torch.cos(angles[1]) * torch.cos(angles[1])

    norm = np.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

    v[0] /= norm
    v[1] /= norm
    v[2] /= norm

    return v


def normalize_face(cur_frame):
    # Adapted from imutils package
    shape = cur_frame.shape
    # 36, 39, 42, 45, 48, 54

    rcenter_x = (shape[0][0]+shape[1][0])/2
    rcenter_y = (shape[0][1]+shape[1][1])/2

    lcenter_x = (shape[2][0]+shape[3][0])/2
    lcenter_y = (shape[2][1]+shape[3][1])/2

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
    cur_frame.debug_img = cv2.warpAffine(cur_frame.debug_img, M, (112, 112), flags=cv2.INTER_CUBIC)
    # cv2.imshow("mhymym",cur_frame.debug_img)
    # cv2.waitKey()
    cur_frame.gaze_origin = gaze_origin
    return cur_frame


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


# def angle_to_vector(angles):
#     pitch = angles[1]
#     yaw = angles[0]
#     return -np.array([
#         np.cos(pitch) * np.cos(yaw),
#         np.cos(pitch) * np.sin(yaw),
#         np.sin(pitch)
#     ])


# def _normalize_vector(vector: np.ndarray) -> np.ndarray:
#     return vector / np.linalg.norm(vector)
#
#
# def get_eye_center(shape, right, left):
#     return np.dot(0.5, (shape[right] + shape[left])).reshape(3, 1)
#
#  def normalize_eye(frame, eye):
#     eye_img = frame[eye[0][1]:eye[1][1], eye[0][0]:eye[1][0]]
#     # eye_img = cv2.warpPerspective(eye_img,)
#     eye_img = cv2.resize(eye_img, (60, 36), interpolation=cv2.INTER_AREA)
#     eye_img = cv2.cvtColor(eye_img, cv2.COLOR_BGR2GRAY)
#     eye_img = cv2.equalizeHist(eye_img)
#
#     return eye_img



#
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
# def set_camera(width, height):
#     cap = cv2.VideoCapture(0)
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
#     return cap


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
# def compute_angle_error(preds, labels):
#     pred_x, pred_y, pred_z = convert_to_unit_vector(preds)
#     label_x, label_y, label_z = convert_to_unit_vector(labels)
#     angles = pred_x * label_x + pred_y * label_y + pred_z * label_z
#     return torch.acos(angles) * 180 / np.pi
#

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
#         if time_elapsed.seconds.real >= 1:
#             self.fps = (self.counter / time_elapsed.seconds.real)
#             self.counter = 0
#             self.last_time = datetime.datetime.now()
#
#     def get_fps(self):
#         return self.fps
#
