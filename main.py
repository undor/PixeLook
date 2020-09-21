# import HeadPoseBasedSolution.HeadPoseBasedSolution as HeadPoseBasedSolution
from Calibration.calibration import *

dataset_path = 'DataSetPreProcess/RES/MPIIGaze.h5'


def __main__():
    main_gaze_manager.set_screen_sizes()
    main_gaze_manager.calibrate()
    while True:
        main_gaze_manager.gui.print_pixel(main_gaze_manager.get_cur_pixel_mean())
        main_gaze_manager.gui.wait_key()


if __name__ == "__main__":
    __main__()
