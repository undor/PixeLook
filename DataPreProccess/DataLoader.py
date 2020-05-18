import os
import sys
import h5py
import numpy as np
import pandas as pd

import torch
import torch.utils.data


class MPIIFaceGazeDataset(torch.utils.data.Dataset):
    def __init__(self, subject_id, dataset_dir):
        path = os.path.join(dataset_dir, '{}.h5'.format(subject_id))
        with h5py.File(path) as f:
            self.images = f['data'].value
            self.gazes = f['label'].value
        self.length = len(self.images)

        self.images = torch.unsqueeze(torch.from_numpy(self.images), 1)
        self.gazes = torch.from_numpy(self.images)

        def __getitem__(self, index):
            return self.images[index][[2, 1, 0], :, :].transpose((1, 2, 0)), self.gazes[index][0:2]

        def __len__(self):
            return self.length

        def __repr__(self):
            return self.__class__.__name__

    # calling get loader from main with 'MPIIFaceGaze_normalized', 0, 1, 8, True
    def get_loader(dataset_dir, test_subject_id, batch_size, num_workers, use_gpu):
        assert os.path.exists(dataset_dir)
    # 15 different people
        assert test_subject_id in range(15)

        subject_ids = ['p{:02}'.format(i) for i in range(15)]
        test_subject_id = subject_ids[test_subject_id]

        train_dataset = torch.utils.data.ConcatDataset([
            MPIIFaceGazeDataset(subject_id, dataset_dir) for subject_id in subject_ids if subject_id != test_subject_id
        ])
        test_dataset = MPIIFaceGazeDataset(test_subject_id, dataset_dir)

        assert len(train_dataset) == 42000
        assert len(test_dataset) == 3000

        train_loader = torch.utils.data.DataLoader(
            train_dataset,
            # how many samples per batch to load
            batch_size=batch_size,
            # reshuffle every epoch
            shuffle=True,
            # how many subprocesses to use for data loading
            num_workers=num_workers,
            # copy tensors into CUDA pinned memory before returning them
            pin_memory=use_gpu,
            # if last dataset size is not divisible by batch size, drop
            drop_last=True,
        )

        test_loader = torch.utils.data.DataLoader(
            test_dataset,
            batch_size=batch_size,
            num_workers=num_workers,
            shuffle=False,
            pin_memory=use_gpu,
            drop_last=False,
        )

        return train_loader, test_loader