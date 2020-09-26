import FullFaceSolution.FullFaceBasedSolution as FullFaceSolution
import HeadPoseBasedSolution.HeadPoseBasedSolution as HeadPoseBasedSolution
from Calibration.gui_manager import *
from utils import *


class gaze_manager:

    def __init__(self, model_method, convert_method, screen_size):
        self.cur_stage = 0
        if screen_size > 0:
            self.gui = FullScreenApp()
            self.width_px = self.gui.width
            self.height_px = self.gui.height
        else:
            self.width_px = 0
            self.height_px = 0
        self.calib_data = calib_data()
        self.pixel_method = convert_method
        self.calib_ratio_width = 1
        self.calib_ratio_height = 1
        if model_method == "FullFace":
            self.env = FullFaceSolution.my_env_ff
        elif model_method == "HeadPose":
            self.env = HeadPoseBasedSolution.my_env_hp
        self.pixel_per_mm = get_mm_pixel_ratio(screen_size)
        self.screen_size = screen_size
        self.last_distance = 0

    def gaze_to_pixel(self, gaze):
        width_ratio = abs(gaze[1] - self.calib_data.left_gaze[1]) / self.width_gaze_scale
        height_ratio = abs(gaze[0] - self.calib_data.up_gaze[0]) / self.height_gaze_scale

        x_location = width_ratio.item() * self.gui.width
        y_location = height_ratio.item() * self.gui.height

        if 0 <= x_location <= self.gui.width and self.gui.height >= y_location >= 0:
            pixel = (x_location, y_location)
            return pixel
        return 0, 0

    def gaze_to_mm(self, gaze, ht):
        # p + t*v = (x, y, 0)
        v = convert_to_unit_vector(gaze)
        # t = -p(z)/v(z)
        t = - ht[2] / v[2].numpy()
        # x = p(x)+t*v(x)
        x = ht[0] + t * v[0].numpy()
        x = x[0]
        # y = p(y)+t*v(y)
        y = ht[1] + t * v[1].numpy()
        y = y[0]
        return x, y

    def gaze_to_pixel_math(self, gaze, ht):
        x, y = self.gaze_to_mm(gaze, ht)

        x = x*self.calib_ratio_width
        y = y*self.calib_ratio_height

        x_location = (x*self.pixel_per_mm + self.width_px/2)
        y_location = -y*self.pixel_per_mm

        if 0 <= x_location <= self.width_px and self.height_px >= y_location >= 0:
            pixel = (x_location, y_location)
            return pixel
        return 0, 0

    def get_cur_pixel(self):
        gaze, ht = self.env.find_gaze()
        self.last_distance = ht[2][0]
        if self.pixel_method == "Linear":
            return self.gaze_to_pixel(gaze)
        else:
            return self.gaze_to_pixel_math(gaze, ht)

    def get_cur_pixel_mean(self):
        cur_sum = np.array([0.0, 0.0])
        num = 0
        # change range in order to change number of pixels to mean from
        for i in range(1):
            cur_pixel = np.array(self.get_cur_pixel())
            if not(cur_pixel[0] == 0 or cur_pixel[1] == 0):
                num += 1
                cur_sum += cur_pixel
        return np.round(np.true_divide(cur_sum, num))

    def step_calib_stage(self):
        self.gui.print_calib_stage(self.cur_stage)
        self.gui.wait_key()
        self.cur_stage += 2

    def calibrate_process(self):
        self.gui.update_window()
        # WAIT FOR LEFT
        self.step_calib_stage()
        # LEFT_CALIBRATION
        self.calib_data.left_gaze = self.env.find_gaze()
        # WAIT FOR RIGHT
        self.step_calib_stage()
        # RIGHT CALIBRATION
        self.calib_data.right_gaze = self.env.find_gaze()
        # WAIT FOR UP
        self.step_calib_stage()
        # UP CALIBRATION
        self.calib_data.up_gaze = self.env.find_gaze()
        # WAIT FOR DOWN
        self.step_calib_stage()
        # DOWN CALIBRATION
        self.calib_data.down_gaze = self.env.find_gaze()
        # WAIT FOR CENTER
        self.step_calib_stage()
        # CHECK CALIBRATION
        if self.pixel_method == "Linear":
            self.width_gaze_scale = abs(self.calib_data.right_gaze[0][1] - self.calib_data.left_gaze[0][1])
            self.height_gaze_scale = abs(self.calib_data.down_gaze[0][0] - self.calib_data.up_gaze[0][0])
        else:
            right_gaze_mm_x = self.gaze_to_mm(self.calib_data.right_gaze[0], self.calib_data.right_gaze[1])[0]
            left_gaze_mm_x = self.gaze_to_mm(self.calib_data.left_gaze[0], self.calib_data.left_gaze[1])[0]
            up_gaze_mm_y = self.gaze_to_mm(self.calib_data.up_gaze[0], self.calib_data.up_gaze[1])[1]
            down_gaze_mm_y = self.gaze_to_mm(self.calib_data.down_gaze[0], self.calib_data.down_gaze[1])[1]

            width_length = abs(right_gaze_mm_x - left_gaze_mm_x)
            height_length = abs(up_gaze_mm_y-down_gaze_mm_y)
            self.calib_ratio_width = self.gui.width / (width_length * self.pixel_per_mm)
            self.calib_ratio_height = self.gui.height / (height_length * self.pixel_per_mm)


        # CENTER VALIDATION
        self.calib_data.center_pixel = self.get_cur_pixel_mean()
        self.gui.print_calib_points(self.calib_data.center_pixel)

        self.step_calib_stage()

    def re_calibration(self):
        self.gui.w.delete("all")
        self.gui.button.place(relx=.5, rely=.5, anchor="c")
        self.gui.button.config(text="Click to Capture")
        self.gui.second_button.place_forget()
        self.gui.w.master.update()
        self.cur_stage = 0

    def calibrate(self):
        while self.gui.finish is not True:
            self.calibrate_process()
            self.re_calibration()
        self.gui.button.config(text="Click to Capture")
