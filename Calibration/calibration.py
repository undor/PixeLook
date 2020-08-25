import FullFaceSolution.FullFaceBasedSolution as FullFaceSolution
from Calibration.gui_manager import *
import numpy as np

class calib_data:
    left_gaze = (0, 0)
    right_gaze = (0, 0)
    up_gaze = (0, 0)
    down_gaze = (0, 0)
    center_pixel = (0, 0)


class gaze_manager:
    def __init__(self):
        self.cur_stage = 0
        self.gui = FullScreenApp()
        self.calib_data = calib_data()
        self.env = FullFaceSolution.my_env
        self.width_length = 0
        self.height_length = 0

    def print_gazes(self):
        print("right gaze: ", self.calib_data.right_gaze)
        print("left gaze: ", self.calib_data.left_gaze)
        print("up gaze: ", self.calib_data.up_gaze)
        print("down gaze: ", self.calib_data.down_gaze)

    def gaze_to_pixel(self, gaze):
        width_ratio = abs(gaze[1] - self.calib_data.left_gaze[1]) / self.width_length
        height_ratio = abs(gaze[0] - self.calib_data.up_gaze[0]) / self.height_length

        x_location = width_ratio.item() * self.gui.width
        y_location = height_ratio.item() * self.gui.height

        # print("x location: ", x_location, "y location: ", y_location)
        if 0 <= x_location <= self.gui.width and self.gui.height >= y_location >= 0:
            pixel = (x_location, y_location)
            return pixel
        return 0, 0

    def get_cur_pixel(self):
        return self.gaze_to_pixel(self.env.find_gaze())

    def calib_stage(self):
        self.gui.print_calib_stage(self.cur_stage)
        self.gui.wait_key()
        self.cur_stage += 2

    def get_cur_pixel_mean(self):
        sum = np.array([0.0, 0.0])
        num=0
        for i in range(10):
            cur_pixel= np.array(self.get_cur_pixel())
            if not(cur_pixel[0] == 0 or cur_pixel[1] ==0):
                num +=1
                sum += cur_pixel
        return np.true_divide(sum,num)

    def calibrate_process(self):
        self.gui.update_window()
        # WAIT FOR LEFT
        self.calib_stage()
        # LEFT_CALIBRATION
        self.calib_data.left_gaze = self.env.find_gaze()
        # WAIT FOR RIGHT
        self.calib_stage()
        # RIGHT CALIBRATION
        self.calib_data.right_gaze = self.env.find_gaze()
        # WAIT FOR UP
        self.calib_stage()
        # UP CALIBRATION
        self.calib_data.up_gaze = self.env.find_gaze()
        # WAIT FOR DOWN
        self.calib_stage()
        # DOWN CALIBRATION
        self.calib_data.down_gaze = self.env.find_gaze()
        # WAIT FOR CENTER
        self.calib_stage()
        # CHECK CALIBRATION

        self.width_length = abs(self.calib_data.right_gaze[1] - self.calib_data.left_gaze[1])
        self.height_length = abs(self.calib_data.down_gaze[0] - self.calib_data.up_gaze[0])

        # CENTER VALIDATION
        self.calib_data.center_pixel = self.get_cur_pixel_mean()

        self.gui.print_calib_points(self.calib_data.center_pixel)

        self.calib_stage()

    def reorganize_calibration(self):
        self.gui.w.delete("all")
        self.gui.button.place(relx=.5, rely=.5, anchor="c")
        self.gui.button.config(text="Click to Capture")
        self.gui.second_button.place_forget()
        self.gui.w.master.update()
        self.cur_stage = 0

    def calibrate(self):
        while self.gui.finish is not True:
            self.calibrate_process()
            self.reorganize_calibration()
        self.gui.button.config(text="start drawing with your eyes")


main_gaze_manager = gaze_manager()
