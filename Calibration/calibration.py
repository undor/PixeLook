import FullFaceSolution.FullFaceBasedSolution as FullFaceSolution
import HeadPoseBasedSolution.HeadPoseBasedSolution as HeadPoseBasedSolution
from Calibration.LinearFix import *
from Calibration.gui_manager import *
from utils import *


class gaze_manager:

    def __init__(self, model_method, screen_size, name):
        self.cur_stage = 0
        if screen_size > 0:
            self.gui = FullScreenApp()
            self.width_px = self.gui.width
            self.height_px = self.gui.height
        else:
            self.width_px = 0
            self.height_px = 0
        self.calib_data = calib_data()
        self.calib_ratio_width = 1
        self.calib_ratio_height = 1
        self.width_gaze_scale = 0
        self.height_gaze_scale = 0
        self.model_method = model_method
        if self.model_method == "FullFace":
            self.env = FullFaceSolution.my_env_ff
        elif self.model_method == "HeadPose":
            self.env = HeadPoseBasedSolution.my_env_hp
        self.pixel_per_mm = get_mm_pixel_ratio(screen_size)
        self.screen_size = screen_size
        self.user_name = name
        self.last_distance = 0
        self.train_set_real = []
        self.train_set = []

    def gaze_to_pixel(self, gaze):
        gaze = gaze.numpy()
        width_ratio = abs(gaze[1] - self.calib_data.left_gaze[0][1]) / self.width_gaze_scale
        height_ratio = abs(gaze[0] - self.calib_data.up_gaze[0][0]) / self.height_gaze_scale
        x_location = width_ratio * self.width_px
        y_location = height_ratio * self.height_px
        pixel = (x_location, y_location)
        return pixel
        # if 0 <= x_location <= self.width_px and self.height_px >= y_location >= 0:
        #     pixel = (x_location, y_location)
        #     return pixel
        # return error_in_pixel

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
        x = x * self.calib_ratio_width
        y = y * self.calib_ratio_height

        x_location = (x * self.pixel_per_mm + self.width_px / 2)
        y_location = -y * self.pixel_per_mm
        pixel = (x_location, y_location)
        return pixel

        # if 0 <= x_location <= self.width_px and self.height_px >= y_location >= 0:
        #     pixel = (x_location, y_location)
        #     return pixel
        # return error_in_pixel

    def get_cur_pixel(self):
        gaze, ht = self.env.find_gaze()
        if ht[0] == 0 or ht[1] == 0 or ht[2] == 0 :
            # error in find gaze - didn't detect face
            return error_in_detect
        self.last_distance = ht[2][0]
        return self.gaze_to_pixel(gaze), self.gaze_to_pixel_math(gaze, ht)

    def get_cur_pixel_mean(self):
        cur_sum = np.array([0.0, 0.0])
        num = 0
        error = 0
        num_to_mean = 2
        # change num_to_mean in order to change number of pixels to mean from
        # change tries_to_error in order to change how many times until error
        tries_to_error = 2 * num_to_mean
        while num < num_to_mean and error < tries_to_error:
            cur_pixel = np.array(self.get_cur_pixel())
            # out of bounds or didn't detect face
            if (cur_pixel[0] == error_in_detect[0] or cur_pixel[1] == error_in_detect[1] or
                    cur_pixel[0] == error_in_pixel[0] or cur_pixel[1] == error_in_pixel[1]):
                error += 1
            # good pixel
            else:
                num += 1
                cur_sum += cur_pixel
        if error >= tries_to_error:
            return error_in_pixel
        return np.round(np.true_divide(cur_sum, num))

    def learn_fix(self):
        self.fix_sys = FixNetCalibration()
        self.fix_sys.train_model(50, self.train_set_real, self.train_set)

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
        self.width_gaze_scale = abs(self.calib_data.right_gaze[0][1] - self.calib_data.left_gaze[0][1])
        self.height_gaze_scale = abs(self.calib_data.down_gaze[0][0] - self.calib_data.up_gaze[0][0])

        # else:
        #     right_gaze_mm_x = self.gaze_to_mm(self.calib_data.right_gaze[0], self.calib_data.right_gaze[1])[0]
        #     left_gaze_mm_x = self.gaze_to_mm(self.calib_data.left_gaze[0], self.calib_data.left_gaze[1])[0]
        #     up_gaze_mm_y = self.gaze_to_mm(self.calib_data.up_gaze[0], self.calib_data.up_gaze[1])[1]
        #     down_gaze_mm_y = self.gaze_to_mm(self.calib_data.down_gaze[0], self.calib_data.down_gaze[1])[1]
        #
        #     width_length = abs(right_gaze_mm_x - left_gaze_mm_x)
        #     height_length = abs(up_gaze_mm_y - down_gaze_mm_y)
        #     self.calib_ratio_width = self.gui.width / (width_length * self.pixel_per_mm)
        #     self.calib_ratio_height = self.gui.height / (height_length * self.pixel_per_mm)

        # CENTER VALIDATION
        self.calib_data.center_pixel = self.get_cur_pixel()[1]
        self.gui.print_calib_points(self.calib_data.center_pixel)

        self.step_calib_stage()

    def collect_for_net(self):
        self.cur_stage = 0
        self.gui.print_training_stage(self.cur_stage)
        self.gui.wait_key()
        self.cur_stage += 1
        self.train_set.append(self.get_cur_pixel()[1])
        self.train_set_real.append([(0.25) * self.gui.width, 0.25 * self.gui.height])
        self.gui.print_training_stage(self.cur_stage)
        self.gui.wait_key()
        self.cur_stage += 1
        self.train_set.append(self.get_cur_pixel()[1])
        self.train_set_real.append([0.75 * self.gui.width, 0.25 * self.gui.height])
        self.gui.print_training_stage(self.cur_stage)
        self.gui.wait_key()
        self.cur_stage += 1
        self.train_set.append(self.get_cur_pixel()[1])
        self.train_set_real.append([0.25 * self.gui.width, 0.75 * self.gui.height])
        self.gui.print_training_stage(self.cur_stage)
        self.gui.wait_key()
        self.cur_stage += 1
        self.train_set.append(self.get_cur_pixel()[1])
        self.train_set_real.append([0.75 * self.gui.width, 0.75 * self.gui.height])
        self.learn_fix()

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
            self.collect_for_net()
            self.re_calibration()
        self.gui.button.config(text="Click to Capture")
