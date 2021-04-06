from datetime import datetime
import os.path


def create_time_file_name(init, file_type):
    if not os.path.exists("outputs/"):
        os.mkdir("outputs/")
    return "outputs/" + init + "_" + datetime.now().strftime("%d_%m_%H_%M") + "." + file_type


class Logging:
    def __init__(self):
        self.file = open(create_time_file_name("PixeLookLogging", "csv"), "a")
        self.file.write("time,x,y\n")

    def add_pixel(self, pixel,cur_time):
        time = datetime.now() if cur_time is None else cur_time
        cur_time_str = time.strftime("%H:%M:%S:%f")
        self.file.write(cur_time_str + "," + str(int(pixel[0])) + "," + str(int(pixel[1])) + "\n")

    def close(self):
        self.file.close()


class Logging_test():
    def __init__(self):
        self.file = open(create_time_file_name("PixelookTestLog","csv"), "a")
        self.file.write("time,x target,y target,x res,y res,error_x(px),error_y(px),total_error(px),error_x(mm),error_y(mm),total_error(mm)\n")

    def add_pixel(self, tag_pixel,cur_pixel,cur_time,errors):
        time = datetime.now() if cur_time is None else cur_time
        cur_time_str = time.strftime("%H:%M:%S:%f")
        self.file.write(cur_time_str + "," + str(int(tag_pixel[0])) + "," + str(int(tag_pixel[1])))
        self.file.write("," + str(int(cur_pixel[0])) + "," + str(int(cur_pixel[1])))
        for e in errors:
            self.file.write(","+str(int(e)))
        self.file.write("\n")

    def close(self):
        self.file.close()