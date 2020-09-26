import scipy

import utils
from Calibration.calibration import *
from TestInfo.TestUtils import *


class TestDB:
    def __init__(self, ff_db_location, hp_db_location):
        self.ff_db_location = ff_db_location
        self.hp_db_location = hp_db_location
        self.gaze_manager_ff = gaze_manager("FullFace", "NOT_LINEAR", -1)
        self.gaze_manager_hp = gaze_manager("HeadPose", "NOT_LINEAR", -1)
        self.cur_screen_size = 0
        self.cur_db = []

    def set_people_calib(self, path):
        screen_size_mat = scipy.io.loadmat(path+"/screenSize.mat")
        camera_intrinsic_mat = scipy.io.loadmat(path + "/Camera.mat")

        self.gaze_manager_ff.pixel_per_mm = (screen_size_mat['height_pixel']/screen_size_mat['height_mm'])
        self.gaze_manager_ff.width_px = screen_size_mat['width_pixel']
        self.gaze_manager_ff.height_px = screen_size_mat['height_pixel']
        self.cur_screen_size = from_wh_mm_to_diag_inch(screen_size_mat['width_mm'], screen_size_mat['height_mm'])
        utils.global_camera_matrix = camera_intrinsic_mat['cameraMatrix']
        utils.global_camera_coeffs = camera_intrinsic_mat['distCoeffs']
        return

    def set_people_db_ff(self, txt_file_path):
        fd = open(txt_file_path, "r")
        self.cur_db = []
        for line in fd:
            cur_s = Sample()
            cur_s.set_from_ff_db(line.split(" "))
            cur_s.screen_size = self.cur_screen_size
            self.cur_db.append(cur_s)

    def scan_db_ff(self):
        csv_file_ff = new_csv_session("FullFace")
        for people in os.listdir(self.ff_db_location):
            cur_p_path = self.ff_db_location+"/"+people
            if not os.path.isdir(cur_p_path):
                continue
            self.set_people_calib(cur_p_path+"/Calibration")
            self.set_people_db_ff(cur_p_path+"/"+people+".txt")
            for sample in self.cur_db:
                cur_img = cv2.imread(cur_p_path+"/"+sample.img_path)
                cur_gaze, cur_ht = self.gaze_manager_ff.env.find_gaze(cur_img)
                if cur_ht[2] == 0:
                    continue
                sample.res_pixel = self.gaze_manager_ff.gaze_to_pixel_math(cur_gaze, cur_ht)
                sample.dist_screen = abs(int(cur_ht[2]))
                sample.compute_error(self.gaze_manager_ff.pixel_per_mm)
                log_sample_csv(sample, people, csv_file_ff)
                print("logged ", cur_p_path+"/"+sample.img_path)
        csv_file_ff.close()

    def set_people_db_hp(self, txt_file_path):
        fd = open(txt_file_path, "r")
        self.cur_db = []
        for line in fd:
            cur_s = Sample()
            cur_s.set_from_hp_db(line.split(" "))
            cur_s.screen_size = self.cur_screen_size
            self.cur_db.append(cur_s)

    def get_pixel_from_img_path_hp(self,img_path,cur_p_path):
        img_path_break=img_path.split("/")
        day_path = img_path_break[0]
        fd_annotate = open(cur_p_path+"/"+day_path+"/annotation.txt")
        number = int((img_path_break[1].split("."))[0])
        line = fd_annotate.readlines()[number-1]
        return np.array(line[24],line[25])

    #TODO :see how we get head pose from data!ßß
    def scan_db_hp(self):
        csv_file_hp = new_csv_session("HeadPose")
        for people in range(1, 14):
            people_str = "p"+f'{people:02}'
            cur_p_path = self.hp_db_location + "/Data/Original/"+people_str
            self.set_people_calib(cur_p_path + "/Calibration")
            self.set_people_db_hp(self.hp_db_location + "/Annotation Subset/" + people_str + ".txt")
            for sample in self.cur_db:
                sample.true_pixel = get_pixel_from_img_path_hp(sample.img_path, cur_p_path)
                cur_img = cv2.imread(cur_p_path + "/" + sample.img_path)
                cur_gaze, cur_ht = self.gaze_manager_hp.env.find_gaze(cur_img, sample.head_points)
                if cur_ht[2] == 0:
                    continue
                sample.res_pixel = self.gaze_manager_hp.gaze_to_pixel_math(cur_gaze, cur_ht)
                sample.dist_screen = abs(int(cur_ht[2]))
                sample.compute_error(self.gaze_manager_hp.pixel_per_mm)
                log_sample_csv(sample, people, csv_file_hp)
                print("logged ", cur_p_path + "/" + sample.img_path)
            print("logged ", cur_p_path+"/" + day + "/" + sample.img_path)
        csv_file_hp.close()
