from Calibration.calibration import *
from Calibration import Choose_Methods
dataset_path = 'DataSetPreProcess/RES/MPIIGaze.h5'


def __main__():
    print("hello world!")
    configuration_manager = Configuration()
    model_method, convert_method = configuration_manager.config_model()
    print("Chosen model method is: ", model_method)
    print("Chosen convert method is: ", convert_method)
    main_gaze_manager = gaze_manager(model_method, convert_method)
    main_gaze_manager.set_screen_sizes(13.3)
    main_gaze_manager.calibrate()
    while True:
        main_gaze_manager.gui.print_pixel(main_gaze_manager.get_cur_pixel_mean())
        # un-comment if you want to wait for mouse-clicks to capture
        # main_gaze_manager.gui.wait_key()


if __name__ == "__main__":
    __main__()
