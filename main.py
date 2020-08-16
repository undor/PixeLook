import FullFaceSolution.FullFaceBasedSolution as FullFaceSolution
import HeadPoseBasedSolution.HeadPoseBasedSolution as HeadPoseBasedSolution
from Calibration.gui_manager import *
from Calibration.calibration import *

dataset_path = 'RES/MPIIGaze.h5'


def __main__():
    print("hello world!")

    calibration_manager.play_stage()

    FullFaceSolution.find_gaze()
    FullFaceSolution.start_camera_sol()

#  HeadPoseBasedSolution.start_camera_sol()


if __name__ == "__main__":
    __main__()
