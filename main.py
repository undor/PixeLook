import FullFaceSolution.FullFaceBasedSolution as FullFaceSolution
import HeadPoseBasedSolution.HeadPoseBasedSolution as HeadPoseBasedSolution
dataset_path = 'RES/MPIIGaze.h5'


def __main__():
    print("hello world!")

    FullFaceSolution.start_camera_sol()
    #  HeadPoseBasedSolution.start_camera_sol()


if __name__ == "__main__":
    __main__()
