import FullFaceSolution.FullFaceBasedSolution as FullFaceSolution
import HeadPoseBasedSolution.HeadPoseBasedSolution as HeadPoseBasedSolution
from Calibration.LinearFix import *
from Calibration.gui_manager import *
from UtilsAndModels.utils import *


class CalibrationManager:

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
        self.height_gaze_scale = 0
        self.width_gaze_scale = 0
        self.last_distance = 0
        self.cur_stage = 0
        # train init
        self.trig_fix_sys = FixNetCalibration(self.width_px, self.height_px)
        self.linear_fix_sys = FixNetCalibration(self.width_px, self.height_px)
        self.train_set_linear_real = []
        self.train_set_linear = []
        self.train_set_trig_real = []
        self.train_set_trig = []

    def gaze_to_pixel_linear(self, gaze):
        width_ratio = abs(gaze[1] - self.calib_data[CALIB_LEFT][0][1]) / self.width_gaze_scale
        height_ratio = abs(gaze[0] - self.calib_data[CALIB_UP][0][0]) / self.height_gaze_scale
        x_location = width_ratio * self.width_px
        y_location = height_ratio * self.height_px
        pixel = (x_location, y_location)
        return pixel


    def gaze_to_pixel_trig(self, gaze, ht , extra_data =None):
        x, y = self.gaze_to_mm(gaze, ht , extra_data)
        x_location = (x * self.pixel_per_mm + self.width_px / 2)
        y_location = -y * self.pixel_per_mm
        pixel = (x_location, y_location)
        return pixel


    def gaze_to_mm(self, gaze, ht,extra_data=None):
        v = convert_to_unit_vector_np(gaze)
        if extra_data is not None:
            v = v @ extra_data
        t = - ht[2] / v[2]
        x = ht[0] + t * v[0]
        y = ht[1] + t * v[1]
        return x[0], y[0]


    def get_cur_pixel(self):
        gaze, ht = self.env.find_gaze()
        if ht[0] == 0 or ht[1] == 0 or ht[2] == 0:
            # error in find gaze - didn't detect face
            return error_in_detect
        self.last_distance = ht[2]
        return self.gaze_to_pixel_linear(gaze), self.gaze_to_pixel_trig(gaze,ht,self.env.extra_data)

    def compute_scale(self):
        self.width_gaze_scale = abs(self.calib_data[CALIB_RIGHT][0][1] - self.calib_data[CALIB_LEFT][0][1])
        self.height_gaze_scale = abs(self.calib_data[CALIB_DOWN][0][0] - self.calib_data[CALIB_UP][0][0])


    def print_center_pixel(self):
        cur_pix = self.get_cur_pixel()
        self.gui.print_calib_points((int(cur_pix[0][0]), int(cur_pix[0][1])), "green") # linear = green
        self.gui.print_calib_points((int(cur_pix[1][0]),(int(cur_pix[1][1]))))

    def step_calib_stage(self):
        if self.cur_stage == 9:
            self.compute_scale()
            self.print_center_pixel()
            self.gui.print_calib_stage(self.cur_stage)
            self.gui.wait_key()
            return
        self.gui.print_calib_stage(self.cur_stage)
        self.gui.wait_key()
        self.calib_data[self.cur_stage] = self.env.find_gaze()
        self.cur_stage += 1

    def is_ok_for_net(self, point_a, point_b):
        threshold_px = max_distance_for_net_mm * self.pixel_per_mm
        if abs(point_a[0] - point_b[0]) > threshold_px or abs(point_a[1] - point_b[1]) > threshold_px:
            return False
        else:
            return True

    def train_data(self):
        print("threshold for using net is ", max_distance_for_net_mm/10, "cm")
        for i in range(9):
            linear_pixel = self.gaze_to_pixel_linear(self.calib_data[i][0])
            trig_pixel = self.gaze_to_pixel_trig(self.calib_data[i][0],
                                                 self.calib_data[i][1], self.env.extra_data)
            res_pixel = [stage_dot_locations[i][0] * self.gui.width,
                         stage_dot_locations[i][1] * self.gui.height]

            if self.is_ok_for_net(res_pixel, linear_pixel):
                self.train_set_linear.append(linear_pixel)
                self.train_set_linear_real.append(res_pixel)
            if self.is_ok_for_net(res_pixel, trig_pixel):
                self.train_set_trig.append(trig_pixel)
                self.train_set_trig_real.append(res_pixel)

        self.trig_fix_sys.train_model(epochs, self.train_set_trig_real, self.train_set_trig)
        self.linear_fix_sys.train_model(epochs, self.train_set_linear_real, self.train_set_linear)

        print("weights for trig net: ", self.trig_fix_sys.model.fc1.weight, "bias is: ", self.trig_fix_sys.model.fc1.bias, "\n at pixels its: ", self.trig_fix_sys.model.fc1.bias[0]*self.width_px, self.trig_fix_sys.model.fc1.bias[1]*self.height_px)
        print("weights for linear net: ", self.linear_fix_sys.model.fc1.weight, "bias is: ", self.linear_fix_sys.model.fc1.bias, "\n at pixels its: ", self.linear_fix_sys.model.fc1.bias[0]*self.width_px, self.linear_fix_sys.model.fc1.bias[1]*self.height_px)

    def calibrate_process(self):
        self.gui.master.update()
        for self.cur_stage in range(10):
            self.step_calib_stage()
        self.train_data()

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
