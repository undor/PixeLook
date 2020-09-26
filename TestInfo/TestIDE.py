from TestInfo.TestUtils import *


class Test_Manager:
    def __init__(self, gaze_manager, person_name):
        self.tag = np.zeros(2)
        self.pixel = np.zeros(2)
        self.error_mm = 0
        self.gaze_manager = gaze_manager
        self.width = gaze_manager.width_px
        self.height = gaze_manager.height_px
        self.test_csv = new_csv_session(None)
        self.person_name = person_name

    def draw_target(self):
        self.tag = [random.randint(0, self.width), random.randint(0, self.height)]
        self.gaze_manager.gui.print_pixel(self.tag)
        return self.tag
        # wanted the button to move with the tag, but it's not working atm
        # self.gaze_manager.gui.print_capture_button(self.tag)

    def capture(self):
        self.gaze_manager.gui.wait_key()
        self.pixel = self.gaze_manager.get_cur_pixel_mean()

    def collect(self):
        cur_smp = Sample()
        self.draw_target()
        self.capture()
        cur_smp.set_from_session(self.tag, self.pixel, self.gaze_manager.screen_size, self.gaze_manager.last_distance)
        cur_smp.compute_error()
        log_sample_csv(cur_smp, self.person_name, self.test_csv)
        print("logged ", self.person_name, " real_pixel:", self.tag, "result_pixel:", self.pixel)

    def finish_test(self):
        self.test_csv.close()



