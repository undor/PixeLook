from Logging import *
from Calibration.calibration import CalibrationManager
from UtilsAndModels.utils import capture_input_height, capture_input_width
import threading
import numpy as np
from UtilsAndModels.utils import get_screen_shot,post_screen_shot,compute_error
import cv2

fps = 4

class PixeLook:
    def __init__(self, screen_size=13.3,  camera_number=0, calib_ratio=1,mean_pixels = 1 , logs=False):
        self.camera_number = int(camera_number)
        self.__calibration_manager = CalibrationManager(camera_number=self.camera_number, screen_size=screen_size)
        self.__shots_defined = False
        self.__thread = None
        self.logs = Logging() if logs else None
        self.__stop_running = False
        self.calib_real_ratio = int(calib_ratio)
        self.screen_width = self.__calibration_manager.width_px * self.calib_real_ratio
        self.screen_height = self.__calibration_manager.height_px * self.calib_real_ratio
        self.__with_webcam = False
        self.__mean_pixels = int(mean_pixels)
        self.get_pixel = self.get_pixel_mean if self.__mean_pixels > 1 else self.get_pixel_uno
        self.pixel_linear = (0, 0)
        self.pixel_trig = (0, 0)

    def calibrate(self):
        self.__calibration_manager.calibrate()

    def capture(self, input_img=None):
        self.pixel_linear, self.pixel_trig = self.__calibration_manager.get_cur_pixel(input_img)
        return self.pixel_linear, self.pixel_trig

    def get_pixel_uno(self,cur_time=None,image=None):
        if image is not None and len(image) == 1:
            image = image[0]
            cur_time = cur_time[0]
        pixel_linear, pixel_trig = self.capture(image)
        x = self.__calibration_manager.trig_fix_sys.use_net(pixel_trig)[0] * self.calib_real_ratio
        y = pixel_linear[1] * self.calib_real_ratio
        res = (x,y)
        if self.logs is not None:
            self.logs.add_pixel(res,cur_time)
        return res

    def get_pixel_mean(self, cur_times=None, images=None):
        before_net_pixels = []
        after_net_pixels = []
        if images is not None:
            for i in range(self.__mean_pixels):
                before_net_pixels.append(self.capture(images[i]))
        else:
            for i in range(self.__mean_pixels):
                before_net_pixels.append(self.capture(None))
        for i in range(self.__mean_pixels):
            pixel_linear, pixel_trig = before_net_pixels[i]
            x = self.__calibration_manager.trig_fix_sys.use_net(pixel_trig)[0] * self.calib_real_ratio
            y = pixel_linear[1] * self.calib_real_ratio
            after_net_pixels.append((x, y))
        res = np.mean(after_net_pixels, axis=0)
        cur_time = None if cur_times is None else cur_times[int(self.__mean_pixels/2)+1]
        if self.logs is not None:
            self.logs.add_pixel(res, cur_time)
        return res

    def test_run(self, test_size=20):
        test_logs = Logging_test()
        import random
        # load any other image to test mode
        self.__calibration_manager.gui.button.config(image=self.__calibration_manager.gui.end_calib_photo)
        # print(self.__calibration_manager.width_px, self.__calibration_manager.height_px)
        for test_dot in range(test_size):
            random_test_dot = [random.randint(0, self.__calibration_manager.width_px), random.randint(0, self.__calibration_manager.height_px)]
            self.__calibration_manager.gui.print_pixel(random_test_dot, clear_prev=True, with_button=True)
            self.__calibration_manager.gui.wait_key()
            cur_pix = np.array(self.get_pixel())
            errors = compute_error(random_test_dot, cur_pix, self.__calibration_manager.pixel_per_mm)
            test_logs.add_pixel(cur_pixel=cur_pix, tag_pixel=random_test_dot, cur_time=None, errors=errors)

    def draw_live(self):
        gui = self.__calibration_manager.gui
        gui.finish = False
        while 1:
            cur_pix = np.array(self.get_pixel())
            gui.print_pixel(cur_pix)
            if gui.counter == 50:
                gui.arrange_live_draw()
                if gui.finish is True:
                    break

    def run_in_background(self, post= False , screen_shots= False):
        gui = self.__calibration_manager.gui
        gui.finish = False
        if post:
            self.__thread = threading.Thread(target=self.__capture,args=(screen_shots,))
        else:
            self.__thread = threading.Thread(target=self.__capture_calc_and_log)
        self.__thread.start()
        gui.only_exit_button() # waiting to click exit
        self.__stop_running = True
        self.__thread.join()
        if post:
            self.__log_from_images_post()

    def __capture(self, screen_shots=False):
        from datetime import datetime
        cap = self.__calibration_manager.env.cap
        self.times = []
        self.images = []
        if screen_shots:
            self.screen_shots_list=[]
        while not self.__stop_running:
            if screen_shots:
                self.screen_shots_list.append(get_screen_shot())
            ret, frame = cap.read()
            self.times.append(datetime.now())
            self.images.append(frame)


    def __log_from_images_post(self):
        self.pixels_list =[]
        self.__calibration_manager.env.reruns = 1
        n = len(self.times) - self.__mean_pixels + 1
        if self.__with_webcam:
            self.webcam_post_list = []
        for i in range(n):
            self.pixels_list.append(self.get_pixel(self.times[i:i+self.__mean_pixels], self.images[i:i+self.__mean_pixels]))
            if self.__with_webcam:
                self.webcam_post_list.append(self.__calibration_manager.env.webcam_shot)
            if i % 10 == 0:
                self.__calibration_manager.gui.post_process((i/n)*100)

    def __capture_calc_and_log(self):
        self.pixels_list =[]
        while not self.__stop_running:
            self.pixels_list.append(self.get_pixel())

    def init_webcam_video(self):
        self.__with_webcam = True
        self.__calibration_manager.env.screen_record_mode = self.__with_webcam
        self.__out_webcam = cv2.VideoWriter(create_time_file_name("PixeLookWebcamShot", "avi"), 0,fps,(capture_input_width, capture_input_height))

    def start_screen_shots(self,resize_factor = 1,post = False,webcam=False):
        if webcam:
            self.init_webcam_video()
        if post:
            self.run_in_background(post,screen_shots=True) #get captures and pixels and log it.
            self.__screen_shot_loop(post=post)
        else:
            self.__stop_running = False
            self.__thread = threading.Thread(target=self.__screen_shot_loop, args=(resize_factor,post,))
            self.__thread.start()
            self.__calibration_manager.gui.only_exit_button() #waiting to click exit
            self.__stop_running = True
            self.__thread.join()

    def stop_screen_shots(self):
        self.__stop_running = True
        self.__thread.join()

    def __screen_shot_loop(self, resize_factor=1 , post=False,max_frmaes= 10*60*30):
        __out_screen = cv2.VideoWriter(create_time_file_name("PixeLookScreenShot", "avi"), 0, fps, (int(self.screen_width * resize_factor), int(self.screen_height * resize_factor)))

        circle_size = int(150 * resize_factor)
        n = max_frmaes if post is False else len(self.pixels_list)
        for i in range(n):
            if post:
                got_pix = self.pixels_list[i]
                got_screen = self.screen_shots_list[i]
            else:
                got_pix = self.get_pixel()
                got_screen = get_screen_shot()

            screen_shot = post_screen_shot(got_screen)
            cur_pix = np.array(got_pix)
            cur_pix = cur_pix*resize_factor

            # edit the screenshot
            frame = screen_shot
            width = int(frame.shape[1] * resize_factor)
            height = int(frame.shape[0] * resize_factor)

            # resize image
            frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            overlay = frame.copy()
            overlay = cv2.circle(overlay, (int(cur_pix[0]), int(cur_pix[1])), circle_size, (255, 50, 50), -1)
            final_frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)

            # write the frames

            __out_screen.write(final_frame)
            if self.__with_webcam:
                webcam_shot = self.webcam_post_list[i] if post else self.__calibration_manager.env.webcam_shot
                self.__out_webcam.write(webcam_shot)
            if not post and self.__stop_running:
                break
            if post and i%10 == 0:
                self.__calibration_manager.gui.post_process((i/n)*100,"Videos Creation")
        # make sure everything is closed when exited
        self.__calibration_manager.env.cap.release()
        __out_screen.release()
        if self.__with_webcam:
            self.__out_webcam.release()