from utils import *

#
# def new_log_session(model_method, convert_method, screen_size, DB):
#     log_file = open('Test_Log', "a")
#     time = datetime.now()
#     time = "\n" + "starting new session at: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n"
#     details = "Chosen methods are:" + model_method + "," + convert_method + ",screen size(inches):" \
#               + str(screen_size) + ",DB is:" + DB + "\n"
#     log_file.write(time)
#     log_file.write(details)
#     log_file.close()


def new_csv_session(name):
    csv_file = open(name+".csv", "a")
    csv_file.write("person,screen_size,err_mm,err_mm_x,err_mm_y,dist_screen_mm, convert_pixel_method, model_method,net_improve\n")
    return csv_file


def log_sample_csv(smp, csv_file):
    csv_file.write(str(smp.person_name) + ",")
    csv_file.write(str(smp.screen_size)+",")
    csv_file.write(str(smp.err_mm) + ",")
    csv_file.write(str(smp.err_mm_x) + ",")
    csv_file.write(str(smp.err_mm_y) + ",")
    csv_file.write(str(smp.dist_screen) + ",")
    csv_file.write(str(smp.convert_method) + ",")
    csv_file.write(str(smp.improve) + ",")
    csv_file.write(str(smp.model_method) + " \n")
    return


def log_error(csv_file, error_type):
    s = "a " + error_type + " error has been occurred \n"
    csv_file.write(s)


class Sample:
    def __init__(self):
        self.img_path = ""
        self.true_pixel = np.zeros(2)
        self.true_ht_vec = np.zeros(3)
        self.true_gaze = np.zeros(2)
        self.head_points = np.array([[0., 0.], [0., 0.], [0., 0.], [0., 0.], [0., 0.], [0., 0.]])
        self.res_pixel = np.zeros(2)
        self.screen_size = 0
        self.err_mm = 0
        self.err_mm_x = 0
        self.err_mm_y = 0
        self.dist_screen = 0
        self.screen_size = 0
        self.person_name = "Default name"
        self.convert_method = "None"
        self.model_method = "None"
        self.improve = 0
        return

    def set_from_ff_db(self, d):
        self.img_path = d[0]
        self.true_pixel = (int(d[1]), int(d[2]))
        self.true_ht_vec = (-float(d[21]), float(d[22]), -float(d[23]))
        true_gaze_target = (float(d[24]), float(d[25]), float(d[26]))
        self.true_gaze = np.array(true_gaze_target) - np.array(self.true_ht_vec)
        return

    def set_from_hp_db(self, d):
        self.img_path = d[0]
        self.head_points = np.array([[float(d[1]), float(d[2])], [float(d[3]), float(d[4])],
                                     [float(d[5]), float(d[6])], [float(d[7]), float(d[8])],
                                     [float(d[9]), float(d[10])], [float(d[11]), float(d[12])]])
        return

    def set_from_session(self, true_pixel, res_pixel, screen_size, dist_screen, name, convert_method, model_method):
        self.true_pixel = true_pixel
        self.res_pixel = res_pixel
        self.screen_size = screen_size
        self.dist_screen = abs(round(dist_screen))
        self.person_name = name
        self.convert_method = convert_method
        self.model_method = model_method
        return

    def compute_error(self, pixel_per_mm):
        x = abs(self.true_pixel[0] - self.res_pixel[0])
        y = abs(self.true_pixel[1] - self.res_pixel[1])
        d = np.sqrt(x**2+y**2)
        self.err_mm = int(np.true_divide(d, pixel_per_mm))
        self.err_mm_x = int(np.true_divide(x, pixel_per_mm))
        self.err_mm_y = int(np.true_divide(y, pixel_per_mm))
        # TODO: ask Dor why this size won't be 1 ? what's this weird test?
        if np.size(self.err_mm) != 1:
            self.err_mm = self.err_mm[0][0]
            self.err_mm_x = self.err_mm_x[0][0]
            self.err_mm_y = self.err_mm_y[0][0]
