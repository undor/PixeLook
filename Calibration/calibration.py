import FullFaceSolution.FullFaceBasedSolution as FullFaceSolution
import HeadPoseBasedSolution.HeadPoseBasedSolution as HeadPoseBasedSolution
from Calibration.gui_manager import *
from Calibration.Choose_Methods import *
from utils import *


class gaze_manager:

    def __init__(self, model_method, convert_method):
        self.cur_stage = 0
        self.gui = FullScreenApp()
        self.calib_data = calib_data()
        if model_method == "FullFace":
            self.env = FullFaceSolution.my_env_ff
        elif model_method == "HeadPose":
            self.env = HeadPoseBasedSolution.my_env_hp
        else:
            print("Method isn't known. USE: FullFace / HeadPose")
            exit(-1)
        self.width_length = 0
        self.height_length = 0
        self.pixel_per_mm = 0

    def set_screen_sizes(self, screen_size_inch):
        self.pixel_per_mm = get_mm_pixel_ratio(screen_size_inch)

    def gaze_to_pixel(self, gaze):
        width_ratio = abs(gaze[1] - self.calib_data.left_gaze[1]) / self.width_length
        height_ratio = abs(gaze[0] - self.calib_data.up_gaze[0]) / self.height_length

        x_location = width_ratio.item() * self.gui.width
        y_location = height_ratio.item() * self.gui.height

        if 0 <= x_location <= self.gui.width and self.gui.height >= y_location >= 0:
            pixel = (x_location, y_location)
            return pixel
        return 0, 0

    def gaze_to_pixel_math(self, gaze, ht, hr):
        # p + t*v = (x, y, 0)
        v = convert_to_unit_vector(gaze)
        # t = -p(z)/v(z)
        t = - ht[2]/v[2].numpy()
        # x = p(x)+t*v(x)
        x = ht[0] + t*v[0].numpy()
        x = x[0]
        # y = p(y)+t*v(y)
        y = ht[1] + t*v[1].numpy()
        y = y[0]

        x_location = x*self.pixel_per_mm + self.gui.width
        y_location = -y*self.pixel_per_mm

        if 0 <= x_location <= self.gui.width and self.gui.height >= y_location >= 0:
            pixel = (x_location, y_location)
            return pixel
        return 0, 0

    def get_cur_pixel(self):
        gaze, ht, hr = self.env.find_gaze()
        self.gaze_to_pixel_math(gaze, ht, hr)
        return self.gaze_to_pixel(gaze)

    def get_cur_pixel_mean(self):
        cur_sum = np.array([0.0, 0.0])
        num = 0
        # change range in order to change number of pixels to mean from
        for i in range(3):
            cur_pixel = np.array(self.get_cur_pixel())
            if not(cur_pixel[0] == 0 or cur_pixel[1] == 0):
                num += 1
                cur_sum += cur_pixel
        return np.true_divide(cur_sum, num)

    def step_calib_stage(self):
        self.gui.print_calib_stage(self.cur_stage)
        self.gui.wait_key()
        self.cur_stage += 2

    def calibrate_process(self):
        self.gui.update_window()
        # WAIT FOR LEFT
        self.step_calib_stage()
        # LEFT_CALIBRATION
        self.calib_data.left_gaze = self.env.find_gaze()[0]
        # WAIT FOR RIGHT
        self.step_calib_stage()
        # RIGHT CALIBRATION
        self.calib_data.right_gaze = self.env.find_gaze()[0]
        # WAIT FOR UP
        self.step_calib_stage()
        # UP CALIBRATION
        self.calib_data.up_gaze = self.env.find_gaze()[0]
        # WAIT FOR DOWN
        self.step_calib_stage()
        # DOWN CALIBRATION
        self.calib_data.down_gaze = self.env.find_gaze()[0]
        # WAIT FOR CENTER
        self.step_calib_stage()
        # CHECK CALIBRATION
        self.width_length = abs(self.calib_data.right_gaze[1] - self.calib_data.left_gaze[1])
        self.height_length = abs(self.calib_data.down_gaze[0] - self.calib_data.up_gaze[0])

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
        self.gui.button.config(text="start drawing with your eyes")

    # def print_gazes(self):
    #     print("right gaze: ", self.calib_data.right_gaze)
    #     print("left gaze: ", self.calib_data.left_gaze)
    #     print("up gaze: ", self.calib_data.up_gaze)
    #     print("down gaze: ", self.calib_data.down_gaze)


# main_gaze_manager = gaze_manager("HeadPose")
# main_gaze_manager = gaze_manager("FullFace")
