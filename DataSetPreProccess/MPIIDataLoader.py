import  torch
import numpy as np
from torch.utils.data import Dataset
from typing import Callable, Tuple
import torchvision
from torch.utils.data import DataLoader
import h5py

data_dir= "RES/MPIIGaze.h5"

class OnePersonDataset(Dataset):
    def __init__(self, person_id_str: str, dataset_path: str,
                 transform: Callable):
        self.transform = transform

        # In case of the MPIIGaze dataset, each image is so small that
        # reading image will become a bottleneck even with HDF5.
        # So, first load them all into memory.
        with h5py.File(dataset_path, 'r') as f:
            images = f.get(f'{person_id_str}/image')[()]
            poses = f.get(f'{person_id_str}/pose')[()]
            gazes = f.get(f'{person_id_str}/gaze')[()]
        assert len(images) == 3000
        assert len(poses) == 3000
        assert len(gazes) == 3000
        self.images = images
        self.poses = poses
        self.gazes = gazes

    def __getitem__(self, index: int
                    ) -> Tuple[torch.tensor, torch.tensor, torch.tensor]:
        image = self.transform(self.images[index])
        pose = torch.from_numpy(self.poses[index])
        gaze = torch.from_numpy(self.gazes[index])
        return image, pose, gaze

    def __len__(self) -> int:
        return len(self.images)


def create_dataset():
    person_ids = [f'p{index:02}' for index in range(15)]
    scale = torchvision.transforms.Lambda(lambda x: x.astype(np.float32) / 255)
    transform = torchvision.transforms.Compose([
        scale,
        torch.from_numpy,
        torchvision.transforms.Lambda(lambda x: x[None, :, :]),
    ])
    test_person_id = person_ids[0]
    train_dataset = torch.utils.data.ConcatDataset([
        OnePersonDataset(person_id, data_dir, transform)
        for person_id in person_ids if person_id != test_person_id
    ])
    val_ratio = 0.1
    val_num = int(len(train_dataset) * val_ratio)
    train_num = len(train_dataset) - val_num
    lengths = [train_num, val_num]
    print (lengths)
    return torch.utils.data.dataset.random_split(train_dataset, lengths)

def create_test_dataset():
    person_ids = [f'p{index:02}' for index in range(15)]
    test_person_id = person_ids[0]
    scale = torchvision.transforms.Lambda(lambda x: x.astype(np.float32) / 255)
    transform = torchvision.transforms.Compose([
        scale,
        torch.from_numpy,
        torchvision.transforms.Lambda(lambda x: x[None, :, :]),
    ])
    test_dataset = OnePersonDataset(test_person_id, data_dir, transform)
    return test_dataset

def create_dataloader():
        train_dataset, val_dataset = create_dataset()
        test_dataset = create_test_dataset()
        train_loader = DataLoader(
            train_dataset,
            batch_size=128,
            shuffle=True,
            drop_last= True
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=64,
            shuffle=False,
            drop_last=False
        )
        test_loader = DataLoader(
            test_dataset,
            batch_size=64,
            shuffle=False,
            drop_last=False,
        )
        return train_loader, val_loader , test_loader