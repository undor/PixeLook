from Calibration.Choose_Methods import Configuration
from TestInfo.TestDB import *
from TestInfo.TestIDE import *

dataset_path = 'DataSetPreProcess/RES/MPIIGaze.h5'

def __main__():
    my_test_db = TestDB("../DataBases/MPIIGaze","HeadPose")
    my_test_db.scan_db_hp()
    return

def __main__():
    configuration_manager = Configuration()
    model_method, convert_method, screen_size, user_name = configuration_manager.config_model()
    print(model_method, convert_method, screen_size, user_name)
    main_gaze_manager = gaze_manager(model_method, convert_method, screen_size, user_name)
    main_gaze_manager.calibrate()
    main_test_manager = Test_Manager(main_gaze_manager)
    for i in range(10):
        main_test_manager.collect()
        # main_gaze_manager.gui.print_pixel(main_gaze_manager.get_cur_pixel_mean())
        # un-comment if you want to wait for mouse-clicks to capture
        # main_gaze_manager.gui.wait_key()


if __name__ == "__main__":
    __main__()

