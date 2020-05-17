from VideoCapture import *
import MPIIDataLoader
import trainNet
import h5py
import numpy as np

dataset_path = 'RES/MPIIGaze.h5'

def __main__():
    print("hello world!")
    trainNet.train_and_validate_aux(7)




if __name__ == "__main__":
    __main__()
