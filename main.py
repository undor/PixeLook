from VideoCapture import *
import DataSetPreProccess.MPIIDataLoader as MPIIDataLoader
import DataSetPreProccess.trainNet as trainNet
import h5py
import numpy as np
import Defines
dataset_path = 'RES/MPIIGaze.h5'

def __main__():
    print("hello world!")
    start_camera()
    #trainNet.train_and_validate_aux(10)




if __name__ == "__main__":
    __main__()
