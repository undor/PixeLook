from Calibration.gui_manager import *
from FullFaceSolution.FullFaceBasedSolution import *
import HeadPoseBasedSolution.HeadPoseBasedSolution as HeadPoseBasedSolution
from Defines import *
import cv2




class calib_data():
    left_gaze = (0, 0)
    right_gaze = (0, 0)
    up_gaze = (0, 0)
    down_gaze = (0, 0)
    center_gaze = (0, 0)

class calib_manager():
    def __init__(self):
        print ("starting calib manager constructor")
        self.cur_stage = 0
        self.gui = FullScreenApp()
        self.calib_data = calib_data()
        self.finished = 0
        self.flag =0

    def next_step(self):
        if self.cur_stage != stages['FINISH_CALIBRATION']:
            self.cur_stage = self.cur_stage+1

    def wait_key(self):
        while self.flag == 0:
            pass
        self.flag = 0
        self.next_step()
        print("key was pressed key was pressed key was pressed")
        return

    def print_gazes(self):
        print("right gaze: ", self.calib_data.right_gaze)
        print("left gaze: ", self.calib_data.left_gaze)
        print("up gaze: ", self.calib_data.up_gaze)
        print("down gaze: ", self.calib_data.down_gaze)

    def gaze_to_pixel(self, gaze):

        calib_data = self.calib_data
        width_length = abs(calib_data.right_gaze[1] - calib_data.left_gaze[1])
        height_length = abs(calib_data.down_gaze[0] - calib_data.up_gaze[0])

        width_ratio = abs(gaze[1] - calib_data.left_gaze[1]) / (0.95*width_length)
        height_ratio = abs(gaze[0] - calib_data.up_gaze[0]) / (0.95*height_length)

        x_location = width_ratio.item() * self.gui.width
        y_location = height_ratio.item() * self.gui.height

        #print("x location: ", x_location, "y location: ", y_location)
        if 0 <= x_location <= self.gui.width and self.gui.height >= y_location >= 0:
            pixel = (x_location, y_location)
            return pixel
        return 0, 0
    # TODO: add indicatores for right calibrating. need to know if stuck \ work, what captured etc.

    def play_stage(self):
        stage = self.cur_stage
        self.gui.print_stage(stage)
        width = self.gui.width
        height = self.gui.height
        self.gui.update_window()
        if stage == stages['WAIT_FOR_LEFT']:
            self.gui.print_pixel((10, height / 2))
            self.wait_key()
        if stage == stages['LEFT_CALIBRATION']:
            self.calib_data.left_gaze = my_env.find_gaze()
            self.next_step()
        if stage == stages['WAIT_FOR_RIGHT']:
                self.gui.print_pixel((width - 10, height / 2))
        elif stage == stages['RIGHT_CALIBRATION']:
            self.calib_data.right_gaze = my_env.find_gaze()
            self.next_step()
        elif stage == stages['WAIT_FOR_UP']:
                self.gui.print_pixel((width / 2, 10))
        elif stage == stages['UP_CALIBRATION']:
            self.calib_data.up_gaze = my_env.find_gaze()
            self.next_step()
        elif stage == stages['WAIT_FOR_DOWN']:
                self.gui.print_pixel((width / 2, height - 10))
        elif stage == stages['DOWN_CALIBRATION']:
            self.calib_data.down_gaze = my_env.find_gaze()
            self.next_step()
        elif stage == stages['WAIT_FOR_CENTER']:
                self.gui.print_pixel((width / 2, height / 2))
        elif stage == stages['CENTER_CALIBRATION']:
            self.calib_data.center_gaze = my_env.find_gaze()
            self.next_step()
        elif stage == stages['CHECK_CALIBRATION']:
            # self.gui.print_pixel(self.gaze_to_pixel(gaze))
            # self.print_gazes()
            self.gui.print_calib_points(self.gaze_to_pixel(self.calib_data.up_gaze),
                                        self.gaze_to_pixel(self.calib_data.down_gaze),
                                        self.gaze_to_pixel(self.calib_data.left_gaze),
                                        self.gaze_to_pixel(self.calib_data.right_gaze),
                                        self.gaze_to_pixel(self.calib_data.center_gaze))
            self.next_step()
        elif stage == stages['FINISH_CALIBRATION']:
            self.gui.print_pixel(self.gaze_to_pixel(gaze))
        self.gui.update_window()



calibration_manager = calib_manager()