import threading
import time
import numpy as np
from Calibration.configure import Configuration
from Calibration.calibration import CalibrationManager
from ScreenRecorder import *


class PixelGetter:
    def __init__(self, screen_size = 13.3 , screen_record_mode = False, camera_number = 0):
        self.calibration_manager = CalibrationManager(camera_number= camera_number, screen_size=screen_size)
        self.calibration_manager.env.screen_record_mode = screen_record_mode
        self.screen_width = self.calibration_manager.width_px
        self.screen_height = self.calibration_manager.width_px
        self.shots_define=False
        self.__thread = None

    def calibrate(self):
        self.calibration_manager.calibrate()

    def capture(self):
        self.pixel_linear, self.pixel_trig = self.calibration_manager.get_cur_pixel()
        return self.pixel_linear, self.pixel_trig

    def get_pixel(self):
        pixel_linear, pixel_trig = self.capture()
        x = self.calibration_manager.trig_fix_sys.use_net(pixel_trig)[0]
        y = pixel_linear[1]
        return (x, y)

    def set_screen_shots(self , file_name = "output_screen.avi", with_webcam = False , webcam_file_name="output_webcam.avi" ):
        self.out_screen = cv2.VideoWriter(file_name, 0, 2, (self.screen_width * 2, self.screen_height * 2))
        if with_webcam:
            self.out_webcam = cv2.VideoWriter(webcam_file_name, 0, 2, (capture_input_width, capture_input_height))
        self.shots_define = True
        self.with_webcam = with_webcam


    def start_screen_shots(self,max_frames= 500):
        self.stop_runing = False
        if self.shots_define == False:
            print("Cant run without set_screen_shots defined!")
        self.__thread = threading.Thread(target=self.__screen_shot_loop,args=(max_frames,))
        self.__thread.start()
        self.__thread.join()

    def stop_screen_shots(self):
        self.stop_runing = True
        self.__thread.join()

    def __screen_shot_loop(self,max_frames):
        tkinter_to_real_ratio = 2
        for i in range(max_frames):
            cur_pix = np.array(self.get_pixel())
            # Fix ratio from tkinter to real screen
            cur_pix = cur_pix * tkinter_to_real_ratio
            # get shots
            screen_shot = pyautogui.screenshot()
            webcam_shot = self.calibration_manager.env.webcam_shot
            # edit the screenshot
            frame = np.array(screen_shot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            overlay = frame.copy()
            overlay = cv2.circle(overlay, (int(cur_pix[0]), int(cur_pix[1])), 300, (255, 0, 0), -1)
            final_frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)
            # write the frames
            self.out_screen.write(final_frame)
            if self.with_webcam:
                self.out_webcam.write(webcam_shot)
            if self.stop_runing:
                break
        # make sure everything is closed when exited
        self.out_screen.release()
        if self.with_webcam:
            self.out_webcam.release()