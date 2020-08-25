# import HeadPoseBasedSolution.HeadPoseBasedSolution as HeadPoseBasedSolution
from Calibration.calibration import *

dataset_path = 'RES/MPIIGaze.h5'


def __main__():
    print("hello world!")
    main_gaze_manager.calibrate()
    while True:
        i = 0
        while i != 10:
            main_gaze_manager.gui.print_pixel(main_gaze_manager.get_cur_pixel())
            i += 1
        main_gaze_manager.gui.wait_key()


if __name__ == "__main__":
    __main__()
