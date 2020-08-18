import FullFaceSolution.FullFaceBasedSolution as FullFaceSolution
from Defines import *
from Calibration.gui_manager import *


class calib_data:
    left_gaze = (0, 0)
    right_gaze = (0, 0)
    up_gaze = (0, 0)
    down_gaze = (0, 0)
    center_gaze = (0, 0)


class calib_manager:
    def __init__(self):
        self.cur_stage = 0
        self.gui = FullScreenApp()
        self.calib_data = calib_data()
        self.env = FullFaceSolution.my_env

    def next_step(self):
        if self.cur_stage != stages['FINISH_CALIBRATION']:
            self.cur_stage += 2

    # def print_gazes(self):
    #     print("right gaze: ", self.calib_data.right_gaze)
    #     print("left gaze: ", self.calib_data.left_gaze)
    #     print("up gaze: ", self.calib_data.up_gaze)
    #     print("down gaze: ", self.calib_data.down_gaze)

    def gaze_to_pixel(self, gaze):
        # TODO: add indicatores for right calibrating. need to know if stuck \ work, what captured etc.

        calib_data = self.calib_data

        width_length = abs(calib_data.right_gaze[1] - calib_data.left_gaze[1])
        height_length = abs(calib_data.down_gaze[0] - calib_data.up_gaze[0])

        width_ratio = abs(gaze[1] - calib_data.left_gaze[1]) / (0.95*width_length)
        height_ratio = abs(gaze[0] - calib_data.up_gaze[0]) / (0.95*height_length)

        x_location = width_ratio.item() * self.gui.width
        y_location = height_ratio.item() * self.gui.height

        # print("x location: ", x_location, "y location: ", y_location)
        if 0 <= x_location <= self.gui.width and self.gui.height >= y_location >= 0:
            pixel = (x_location, y_location)
            return pixel
        return 0, 0

    def stage(self, x_cor, y_cor):
        self.gui.print_stage(self.cur_stage)
        # TODO: only change place of button, instead of printing pixel
        self.gui.print_pixel((x_cor, y_cor))
        self.gui.update_window()
        self.gui.wait_key()
        self.next_step()

    def play_stage(self):
        self.gui.update_window()
        # WAIT FOR LEFT
        self.stage(10, self.gui.height/2)
        # LEFT_CALIBRATION
        self.calib_data.left_gaze = self.env.find_gaze()
        # WAIT FOR RIGHT
        self.stage(self.gui.width - 10, self.gui.height / 2)
        # RIGHT CALIBRATION
        #self.calib_data.right_gaze = self.env.find_gaze()
        # WAIT FOR UP
        self.stage(self.gui.width / 2, 10)
        # UP CALIBRATION
        #self.calib_data.up_gaze = self.env.find_gaze()
        # WAIT FOR DOWN
        self.stage(self.gui.width / 2, self.gui.height - 10)
        # DOWN CALIBRATION
        #self.calib_data.down_gaze = FullFaceSolution.my_env.find_gaze()
        # WAIT FOR CENTER
        self.stage(self.gui.width / 2, self.gui.height / 2)
        # CENTER CALIBRATION
        #self.calib_data.center_gaze = FullFaceSolution.my_env.find_gaze()
        # CHECK CALIBRATION
        # self.gui.print_pixel(self.gaze_to_pixel(gaze))
        # self.print_gazes()

        self.gui.print_calib_points(self.gaze_to_pixel(self.calib_data.up_gaze),
                                    self.gaze_to_pixel(self.calib_data.down_gaze),
                                    self.gaze_to_pixel(self.calib_data.left_gaze),
                                    self.gaze_to_pixel(self.calib_data.right_gaze),
                                    self.gaze_to_pixel(self.calib_data.center_gaze))
        self.gui.wait_key()
        # FINISH CALIBRATION
        # self.gui.print_pixel(self.gaze_to_pixel(gaze))


calibration_manager = calib_manager()
