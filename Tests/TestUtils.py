from UtilsAndModels.utils import *


def new_csv_session(name):
    csv_file = open("Results/"+name+".csv", "a")
    csv_file.write("person,screen_size,err_mm,err_mm_x,err_mm_y,dist_screen_mm, convert_pixel_method, gaze_net_method,"
                   "net_improve,true_pixel_location\n")
    return csv_file


def log_sample_csv(smp, csv_file):
    csv_file.write(str(smp.person_name) + ", ")
    csv_file.write(str(smp.screen_size)+", ")
    csv_file.write(str(smp.err_mm) + ", ")
    csv_file.write(str(smp.err_mm_x) + ", ")
    csv_file.write(str(smp.err_mm_y) + ", ")
    csv_file.write(str(smp.dist_screen) + ", ")
    csv_file.write(str(smp.convert_method) + ", ")
    csv_file.write(str(smp.gaze_net_method) + ", ")
    csv_file.write(str(smp.improve) + ", ")
    csv_file.write(str(smp.true_pixel) + " \n")
    csv_file.flush()
    return


def log_error(csv_file, error_type):
    s = "a " + error_type + " error has been occurred \n"
    csv_file.write(s)


def compute_error_mm(pixel_a, pixel_b, pixel_per_mm):
    x = abs(pixel_a[0] - pixel_b[0])
    y = abs(pixel_a[1] - pixel_b[1])
    d = np.sqrt(x**2+y**2)
    err_mm = int(np.true_divide(d, pixel_per_mm))
    err_mm_x = int(np.true_divide(x, pixel_per_mm))
    err_mm_y = int(np.true_divide(y, pixel_per_mm))
    return err_mm, err_mm_x, err_mm_y


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

    def set_from_session(self, true_pixel, res_pixel, screen_size, dist_screen, name, convert_method, model_method, err):
        self.true_pixel = true_pixel
        self.res_pixel = res_pixel
        self.screen_size = screen_size
        self.dist_screen = abs(np.round(dist_screen))
        self.person_name = name
        self.convert_method = convert_method
        self.model_method = model_method
        self.err_mm = err[0]
        self.err_mm_x = err[1]
        self.err_mm_y = err[2]
        return
