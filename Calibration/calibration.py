import FullFaceSolution.FullFaceBasedSolution as FullFaceSolution
import HeadPoseBasedSolution.HeadPoseBasedSolution as HeadPoseBasedSolution
from Calibration.LinearFix import *
from Calibration.gui_manager import *
from utils import *


class gaze_manager:

    def __init__(self, model_method, screen_size, name):
        # screen size and pix init
        self.gui = FullScreenApp()
        self.pixel_per_mm = get_mm_pixel_ratio(screen_size)
        self.screen_size = screen_size
        self.height_px = self.gui.height
        self.width_px = self.gui.width
        # model method init
        self.model_method = model_method
        if self.model_method == "FullFace":
            self.env = FullFaceSolution.my_env_ff
        elif self.model_method == "HeadPose":
            self.env = HeadPoseBasedSolution.my_env_hp
        # calib data init
        self.calib_data = [[(0., 0.), np.zeros(3)], [(0., 0.), np.zeros(3)], [(0., 0.), np.zeros(3)],
                           [(0., 0.), np.zeros(3)], [(0., 0.), np.zeros(3)], [(0., 0.), np.zeros(3)],
                           [(0., 0.), np.zeros(3)], [(0., 0.), np.zeros(3)], [(0., 0.), np.zeros(3)],
                           [(0., 0.), np.zeros(3)]]
        self.user_name = name
        self.height_calib_ratio = 1
        self.width_calib_ratio = 1
        self.height_gaze_scale = 0
        self.width_gaze_scale = 0
        self.last_distance = 0
        self.cur_stage = 0
        # train init
        self.fix_sys = FixNetCalibration()
        self.train_set_real = []
        self.train_set = []

    def gaze_to_pixel_linear(self, gaze):
        gaze = gaze.numpy()
        width_ratio = abs(gaze[1] - self.calib_data[CALIB_LEFT][0][1]) / self.width_gaze_scale
        height_ratio = abs(gaze[0] - self.calib_data[CALIB_UP][0][0]) / self.height_gaze_scale
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

    def gaze_to_pixel_trig(self, gaze, ht):
        x, y = self.gaze_to_mm(gaze, ht)
        x = x * self.width_calib_ratio
        y = y * self.height_calib_ratio

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
        if ht[0] == 0 or ht[1] == 0 or ht[2] == 0:
            # error in find gaze - didn't detect face
            return error_in_detect
        self.last_distance = ht[2][0]
        return self.gaze_to_pixel_linear(gaze), self.gaze_to_pixel_trig(gaze, ht)

    # def get_cur_pixel_mean(self):
    #     cur_sum = np.array([0.0, 0.0])
    #     num = 0
    #     error = 0
    #     num_to_mean = 2
    #     change num_to_mean in order to change number of pixels to mean from
    #     change tries_to_error in order to change how many times until error
    #     tries_to_error = 2 * num_to_mean
    #     while num < num_to_mean and error < tries_to_error:
    #         cur_pixel = np.array(self.get_cur_pixel())
    #         # out of bounds or didn't detect face
    #         if (cur_pixel[0] == error_in_detect[0] or cur_pixel[1] == error_in_detect[1] or
    #                 cur_pixel[0] == error_in_pixel[0] or cur_pixel[1] == error_in_pixel[1]):
    #             error += 1
    #         # good pixel
    #         else:
    #             num += 1
    #             cur_sum += cur_pixel
    #     if error >= tries_to_error:
    #         return error_in_pixel
    #     return np.round(np.true_divide(cur_sum, num))


    def compute_scale(self):
        self.width_gaze_scale = abs(self.calib_data[CALIB_RIGHT][0][1] - self.calib_data[CALIB_LEFT][0][1])
        self.height_gaze_scale = abs(self.calib_data[CALIB_DOWN][0][0] - self.calib_data[CALIB_UP][0][0])

    # else:
    #     right_gaze_mm_x = self.gaze_to_mm(self.calib_data.right_gaze[0], self.calib_data.right_gaze[1])[0]
    #     left_gaze_mm_x = self.gaze_to_mm(self.calib_data.left_gaze[0], self.calib_data.left_gaze[1])[0]
    #     up_gaze_mm_y = self.gaze_to_mm(self.calib_data.up_gaze[0], self.calib_data.up_gaze[1])[1]
    #     down_gaze_mm_y = self.gaze_to_mm(self.calib_data.down_gaze[0], self.calib_data.down_gaze[1])[1]
    #
    #     width_length = abs(right_gaze_mm_x - left_gaze_mm_x)
    #     height_length = abs(up_gaze_mm_y - down_gaze_mm_y)
    #     self.width_calib_ratio = self.gui.width / (width_length * self.pixel_per_mm)
    #     self.height_calib_ratio = self.gui.height / (height_length * self.pixel_per_mm)

    def train_fix_model(self):
        self.fix_sys.train_model(epochs, self.train_set_real, self.train_set)

    def print_center_pixel(self):
        # linear
        # self.calib_data[CALIB_CENTER] = self.get_cur_pixel()[0]
        # trig
        print("inside print center pixel")
        self.calib_data[CALIB_CENTER] = self.get_cur_pixel()[1]
        print("got this pixel to print: ", self.calib_data[CALIB_CENTER])
        self.gui.print_calib_points(self.calib_data[CALIB_CENTER])

    def is_ok_for_net(self,point_a,point_b):
        threshold_px = max_distance_for_net_mm * self.pixel_per_mm
        if abs(point_a[0] -point_b[0]) > threshold_px or abs(point_a[1]-point_b[1]) > threshold_px:
            print("too far for net")
            return False
        else:
            return True

    def step_calib_stage(self):
        print("stage is: ", self.cur_stage)
        if self.cur_stage == 9:
            self.print_center_pixel()
        self.gui.print_calib_stage(self.cur_stage)
        self.gui.wait_key()
        self.calib_data[self.cur_stage] = self.env.find_gaze()

        if self.cur_stage == 9:
            return
        # TODO: if re-calibrate, still train? or init the train set and real?

        cur_res_pixel = self.gaze_to_pixel_trig(self.calib_data[self.cur_stage][0],
                                                          self.calib_data[self.cur_stage][1])
        cur_real_pixel = [stage_dot_locations[self.cur_stage][0] * self.gui.width,
                                        stage_dot_locations[self.cur_stage][1] * self.gui.height]

        if self.is_ok_for_net(cur_res_pixel, cur_real_pixel):
            self.train_set.append(cur_res_pixel)
            self.train_set_real.append(cur_real_pixel)
        self.cur_stage += 1

    def calibrate_process(self):
        self.gui.master.update()
        for self.cur_stage in range(10):
            self.step_calib_stage()
        self.compute_scale()
        self.train_fix_model()

    def re_calibration(self):
        self.gui.w.delete("all")
        self.gui.button.place(relx=.5, rely=.5, anchor="c")
        self.gui.button.config(text=text_for_capture)
        self.gui.second_button.place_forget()
        self.gui.w.master.update()
        self.cur_stage = 0

    def calibrate(self):
        while self.gui.finish is not True:
            self.calibrate_process()
            self.re_calibration()
        self.gui.button.config(text=text_for_capture)
