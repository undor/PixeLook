from Calibration.Choose_Methods import Configuration
from Tests.TestDB import *
from Tests.TestIDE import *

dataset_path = 'DataSetPreProcess/RES/MPIIGaze.h5'


# def __main__():
#     my_test_db = TestDB("../DataBases/MPIIGaze","HeadPose")
#     my_test_db.scan_db_hp()
#     return


def __main__():
    configuration_manager = Configuration()
    model_method, screen_size, user_name = configuration_manager.config_model()
    print("working on: ", model_method, screen_size, user_name)
    main_gaze_manager = gaze_manager(model_method, screen_size, user_name)
    main_gaze_manager.calibrate()
    main_test_manager = Test_Manager(main_gaze_manager)
    # print the pixels you are looking at:
    # main_test_manager.self_check()
    main_test_manager.collect()


if __name__ == "__main__":
    __main__()
