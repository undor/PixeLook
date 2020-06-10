import datetime

class fpsHelper():
    def __init__(self):
        self.last_time = datetime.datetime.now()
        self.counter = 0
        self.fps = 0

    def reg_time(self):
        self.counter = self.counter+1
        time_elapsed = datetime.datetime.now() - self.last_time
        if (time_elapsed.seconds.real >= 1):
            self.fps = (self.counter /time_elapsed.seconds.real)
            self.counter = 0
            self.last_time = datetime.datetime.now()

    def get_fps(self):
        return self.fps