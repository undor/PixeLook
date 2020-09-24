from TestInfo.TestIDE import *
from Calibration.calibration import *
from Calibration.Choose_Methods import Configuration


dataset_path = 'DataSetPreProcess/RES/MPIIGaze.h5'


def __main__():
    print("hello world!")
    configuration_manager = Configuration()
    model_method, convert_method, screen_size = configuration_manager.config_model()
    # print("Chosen methods are: ", model_method, ", ", convert_method, "and screen size is: ", screen_size)
    # model_method = "FullFace"
    # convert_method = "Trigonometric"
    # screen_size = 14
    main_gaze_manager = gaze_manager(model_method, convert_method, screen_size)
    main_gaze_manager.calibrate()
    new_log_session(model_method, convert_method, screen_size)
    main_test_manager = Test_Manager(main_gaze_manager)
    while True:
        main_test_manager.collect()
        # main_gaze_manager.gui.print_pixel(main_gaze_manager.get_cur_pixel_mean())
        # un-comment if you want to wait for mouse-clicks to capture
        # main_gaze_manager.gui.wait_key()


if __name__ == "__main__":
    __main__()
