from datetime import datetime


def create_time_file_name(init, file_type):
    return "outputs/" +init + "_" + datetime.now().strftime("%d_%m_%H_%M") + "." +file_type

class Logging:
    def __init__(self):
        self.file = open(create_time_file_name("PixeLookLogging","csv"), "a")
        self.file.write("time,x,y\n")

    def add_pixel(self, pixel,cur_time):
        time = datetime.now() if cur_time is None else cur_time
        cur_time_str = time.strftime("%H:%M:%S:%f")
        self.file.write(cur_time_str + "," + str(int(pixel[0])) + "," + str(int(pixel[1])) + "\n")

    def close(self):
        self.file.close()

