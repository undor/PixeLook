from utils import *


class Test_Manager:
    def __init__(self, gaze_manager):
        self.tag = np.zeros(2)
        self.pixel = np.zeros(2)
        self.error_mm = 0
        self.gaze_manager = gaze_manager
        self.width = 1280
        self.height = 720

    def draw_target(self):
        self.tag = [random.randint(0, self.width), random.randint(0, self.height)]
        self.gaze_manager.gui.print_pixel(self.tag)
        # wanted the button to move with the tag, but it's not working atm
        # self.gaze_manager.gui.print_capture_button(self.tag)

    def capture(self):
        self.gaze_manager.gui.wait_key()
        self.pixel = self.gaze_manager.get_cur_pixel_mean()

    def compute_error(self):
        x = abs(self.pixel[0] - self.tag[0])
        y = abs(self.pixel[1] - self.pixel[1])
        d = np.sqrt(x**2+y**2)
        self.error_mm = np.true_divide(d, self.gaze_manager.pixel_per_mm)

    def printer(self):
        # open and close each iteration because we don't have normal "exit" procedure, so text file is not updating well
        log_file = open('Test_Log', "a")
        tag = "tag: " + str(self.tag)
        target = "target: " + str(self.pixel)
        error = " error: " + str(self.error_mm) + "\n"
        log_file.write(tag.ljust(20) + target.ljust(20) + error)
        log_file.close()

    def collect(self):
        self.draw_target()
        self.capture()
        self.compute_error()
        self.printer()



