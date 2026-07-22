import os

import numpy as np
import torch

from torch.utils.data import Dataset


class QuickDrawDataset(Dataset):

    def __init__(
        self,
        data_dir,
        classes,
        samples_per_class=None
    ):

        self.data = []
        self.labels = []

        self.classes = classes

        self.class_to_idx = {
            class_name: idx
            for idx, class_name in enumerate(classes)
        }

        for class_name in classes:
            path = os.path.join(
                data_dir,
                f"{class_name}.npy"
            )

            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"Could not find dataset file: {path}"
                )

            images = np.load(path)

            if samples_per_class is not None:
                images = images[:samples_per_class]

            label = self.class_to_idx[class_name]

            self.data.append(images)
            self.labels.extend([label] * len(images))

        self.data = np.concatenate(self.data, axis=0)
        self.labels = np.array(self.labels)

        print(f"Loaded {len(self.data)} images")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        image = self.data[idx]
        label = self.labels[idx]

        image = image.reshape(1, 28, 28)
        image = torch.tensor(image, dtype=torch.float32)
        image = image / 255.0
        label = torch.tensor(label, dtype=torch.long)

        return image, label
