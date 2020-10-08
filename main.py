from Calibration.configure import Configuration
from ScreenRecorder import *
from Tests.TestDB import *


def __main__():
    configuration_manager = Configuration()
    model_method, screen_size, user_name = configuration_manager.config_model()
    print("working on: ", model_method, screen_size, user_name)
    main_gaze_manager = CalibrationManager(model_method, screen_size, user_name)
    main_gaze_manager.calibrate()
    main_test_manager = Test_Manager(main_gaze_manager)
    screen_record(main_test_manager)


if __name__ == "__main__":
    __main__()
