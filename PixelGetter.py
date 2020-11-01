import threading
import time
import numpy as np
from Calibration.configure import Configuration
from Calibration.calibration import CalibrationManager
from ScreenRecorder import *


class PixelGetter:
    def __init__(self, screen_size = 13.3 ,  camera_number = 0):
        self.__calibration_manager = CalibrationManager(camera_number= camera_number, screen_size=screen_size)
        self.__shots_defined= False
        self.__thread = None
        self.calib_real_ratio = 2
        self.screen_width = self.__calibration_manager.width_px * self.calib_real_ratio
        self.screen_height = self.__calibration_manager.height_px * self.calib_real_ratio


    def calibrate(self):
        self.__calibration_manager.calibrate()

    def capture(self):
        self.pixel_linear, self.pixel_trig = self.__calibration_manager.get_cur_pixel()
        return self.pixel_linear, self.pixel_trig

    def get_pixel(self):
        pixel_linear, pixel_trig = self.capture()
        x = self.__calibration_manager.trig_fix_sys.use_net(pixel_trig)[0] * self.calib_real_ratio
        y = pixel_linear[1] * self.calib_real_ratio
        return (x, y)

    def set_screen_shots(self , file_name = "output_screen.avi", with_webcam = False , webcam_file_name="output_webcam.avi" , resize_factor = 0.5):
        self.__out_screen = cv2.VideoWriter(file_name, 0, 2, (int(self.screen_width * resize_factor) , int(self.screen_height * resize_factor)))
        self.__resize_factor = resize_factor
        if with_webcam:
            self.__out_webcam = cv2.VideoWriter(webcam_file_name, 0, 2, (capture_input_width, capture_input_height))
        self.__shots_defined = True
        self.__with_webcam = with_webcam
        self.__calibration_manager.env.screen_record_mode = self.__with_webcam


    def start_screen_shots(self,max_frames= 500):
        self.__stop_runing = False
        if self.__shots_defined == False:
            print("Cant run without set_screen_shots defined!")
        self.__thread = threading.Thread(target=self.__screen_shot_loop,args=(max_frames,))
        self.__thread.start()
        self.__thread.join()

    def stop_screen_shots(self):
        self.__stop_runing = True
        self.__thread.join()

    def __screen_shot_loop(self,max_frames):
        tkinter_to_real_ratio = 2
        circle_size = int(300 * self.__resize_factor)
        for i in range(max_frames):
            cur_pix = np.array(self.get_pixel())
            cur_pix = cur_pix*self.__resize_factor
            # get shots
            screen_shot = pyautogui.screenshot()
            webcam_shot = self.__calibration_manager.env.webcam_shot
            # edit the screenshot
            frame = np.array(screen_shot)
            width = int(frame.shape[1] * self.__resize_factor)
            height = int(frame.shape[0] * self.__resize_factor)
            # resize image
            frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            overlay = frame.copy()
            overlay = cv2.circle(overlay, (int(cur_pix[0]), int(cur_pix[1])), circle_size, (255, 0, 0), -1)
            final_frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)
            # write the frames
            self.__out_screen.write(final_frame)
            if self.__with_webcam:
                self.__out_webcam.write(webcam_shot)
            if self.__stop_runing:
                break
        # make sure everything is closed when exited
        self.__out_screen.release()
        if self.__with_webcam:
            self.__out_webcam.release()