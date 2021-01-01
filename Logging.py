from datetime import datetime


class Logging:
    def __init__(self):
        file_name = "PixeLookLogging_" + datetime.now().strftime("%d_%m_%H_%M") + ".csv"
        self.file = open(file_name, "a")
        self.file.write("time,x,y\n")

    def add_pixel(self, pixel):
        cur_time_str = datetime.now().strftime("%H:%M:%S:%f")
        self.file.write(cur_time_str + "," + str(int(pixel[0])) + "," + str(int(pixel[1])) + "\n")

    def close(self):
        self.file.close()
