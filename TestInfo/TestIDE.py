from TestInfo.TestUtils import *


class Test_Manager:
    def __init__(self, gaze_manager):

        self.real = np.zeros(2)
        self.pixel_linear = np.zeros(2)
        self.pixel_trig = np.zeros(2)
        self.error_mm = 0

        self.gaze_manager = gaze_manager
        self.width = gaze_manager.width_px
        self.height = gaze_manager.height_px
        self.person_name = gaze_manager.user_name
        self.model_method = gaze_manager.model_method

        self.iteration = 0
        self.test_csv = new_csv_session("OurDB")

    def self_check(self):
        self.gaze_manager.gui.print_pixel(self.gaze_manager.get_cur_pixel())
        # un-comment if you want to wait for mouse-clicks to capture
        # self.gaze_manager.gui.wait_key()

    def not_valid_pixel(self):

        log_error(self.test_csv, "pixel")
        self.gaze_manager.gui.button.config(text="pixel was out of bounds! Click to continue")
        self.gaze_manager.gui.wait_key()
        self.gaze_manager.gui.button.config(text="Click to Capture")
        self.iteration -= 1

    def not_valid_detect(self):
        log_error(self.test_csv, "detect")
        self.gaze_manager.gui.button.config(text="Re-center your face to the camera! Click only when ready")
        self.gaze_manager.gui.wait_key()
        self.gaze_manager.gui.button.config(text="Click to Capture")
        self.iteration -= 1

    def draw_target(self):
        self.real = [random.randint(0, self.width), random.randint(0, self.height)]
        self.gaze_manager.gui.print_pixel(self.real)
        # wanted the button to move with the tag, but it's not working atm
        # self.gaze_manager.gui.print_capture_button(self.tag)

    def capture(self):
        self.gaze_manager.gui.wait_key()
        self.pixel_linear, self.pixel_trig = self.gaze_manager.get_cur_pixel()
        return self.pixel_linear, self.pixel_trig

    def collect(self):
        for self.iteration in range(30):
            cur_smp = Sample()
            self.draw_target()
            is_valid_pixel = self.capture()
            if is_valid_pixel[1] is not error_in_detect:
                trig_fixed = self.gaze_manager.fix_sys.use_net(self.pixel_trig)
                print("real pixel is: ", self.real, " and captured is: ", self.pixel_trig, "and captured after net is: ", trig_fixed)
                self.gaze_manager.gui.print_pixel(self.pixel_trig, "green")
                self.gaze_manager.gui.print_pixel(trig_fixed, "blue")
                cur_smp.set_from_session(self.real, self.pixel_linear, self.gaze_manager.screen_size,
                                         self.gaze_manager.last_distance, self.person_name,
                                         "Linear", self.model_method)
                cur_smp.compute_error(self.gaze_manager.pixel_per_mm)
                log_sample_csv(cur_smp, self.test_csv)
                cur_smp.set_from_session(self.real, self.pixel_trig, self.gaze_manager.screen_size,
                                         self.gaze_manager.last_distance, self.person_name,
                                         "Trigonometric", self.model_method)
                cur_smp.compute_error(self.gaze_manager.pixel_per_mm)
                log_sample_csv(cur_smp, self.test_csv)
                self.gaze_manager.gui.wait_key()
                self.gaze_manager.gui.w.delete("all")
            # not valid
            else:
                self.not_valid_detect()
        self.finish_test()

    def finish_test(self):
        self.test_csv.close()
