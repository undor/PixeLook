import os

import cv2
import scipy

import utils
from Calibration.calibration import *
from TestInfo.TestUtils import *


class TestDB:
    def __init__(self, ff_db_location, hp_db_location):
        self.ff_db_location = ff_db_location
        self.hp_db_location = hp_db_location + "/Data/Original"
        self.gaze_manager_ff = gaze_manager("FullFace", "NOT_LINEAR", -1)
        self.gaze_manager_hp = gaze_manager("HeadPose", "NOT_LINEAR", -1)


    def set_people_calib_ff(self, path):
        screen_size_mat = scipy.io.loadmat(path+"/screenSize.mat")
        camera_intrinsic_mat = scipy.io.loadmat(path + "/Camera.mat")

        self.gaze_manager_ff.pixel_per_mm = (screen_size_mat['height_pixel']/screen_size_mat['height_mm'])
        self.gaze_manager_ff.width_px = screen_size_mat['width_pixel']
        self.gaze_manager_ff.height_px = screen_size_mat['height_pixel']
        self.cur_screen_size = from_wh_mm_to_diag_inch(screen_size_mat['width_mm'],screen_size_mat['height_mm'])
        utils.global_camera_matrix = camera_intrinsic_mat['cameraMatrix']
        utils.global_camera_coeffs = camera_intrinsic_mat['distCoeffs']
        return

    def get_people_db(self,txt_file_path):
        fd = open(txt_file_path, "r")
        p_db = []
        for line in fd:
            cur_s = Sample()
            cur_s.set_from_ff_db(line.split(" "))
            cur_s.screen_size = self.cur_screen_size
            p_db.append(cur_s)
        return p_db

    def scan_db_ff(self):
        csv_file_ff = new_csv_session("FullFace")
        for people in os.listdir(self.ff_db_location):
            cur_p_path = self.ff_db_location+"/"+people
            if os.path.isdir(cur_p_path):
                self.set_people_calib_ff(cur_p_path+"/Calibration")
                cur_p_db = self.get_people_db(cur_p_path+"/"+people+".txt")
                for sample in cur_p_db:
                    cur_img = cv2.imread(cur_p_path+"/"+sample.img_path)
                    cur_gaze, cur_ht = self.gaze_manager_ff.env.find_gaze(cur_img)
                    if cur_ht[2] == 0:
                        continue
                    sample.res_pixel = self.gaze_manager_ff.gaze_to_pixel_math(cur_gaze, cur_ht)
                    sample.dist_screen = abs(int(cur_ht[2]))
                    sample.compute_error(self.gaze_manager_ff.pixel_per_mm)
                    self.log_sample_csv(sample, csv_file_ff)
        csv_file_ff.close()

    def scan_db_hp(self):
        csv_file_ff = new_csv_session("HeadPose")
        for people in os.listdir(self.hp_db_location):
            cur_p_path = self.hp_db_location+"/"+people
            if os.path.isdir(cur_p_path):
                self.set_people_calib_ff(cur_p_path+"/Calibration")
                for day in os.listdir(cur_p_path):
                    cur_p_db = self.get_people_db(cur_p_path+"/"+day+".txt")
                    for sample in cur_p_db:
                        cur_img = cv2.imread(cur_p_path+"/"+sample.img_path)
                        cur_gaze, cur_ht = self.gaze_manager_ff.env.find_gaze(cur_img)
                        if cur_ht[2] == 0:
                            continue
                        sample.res_pixel = self.gaze_manager_ff.gaze_to_pixel_math(cur_gaze, cur_ht)
                        sample.dist_screen = abs(int(cur_ht[2]))
                        sample.compute_error(self.gaze_manager_ff.pixel_per_mm)
                        self.log_sample_csv(sample, csv_file_ff)
        csv_file_ff.close()




