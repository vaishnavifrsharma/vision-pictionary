import os
import numpy as np
import torch
from torch.utils.data import Dataset


class QuickDrawDataset(Dataset):
    """
    Dataset loader for Google QuickDraw numpy bitmap dataset (.npy files).
    Supports 50 categories, uniform per-class sampling, and optional PyTorch data augmentation transforms.
    """
    def __init__(
        self,
        data_dir,
        classes,
        samples_per_class=3000,
        transform=None
    ):
        self.data = []
        self.labels = []
        self.classes = classes
        self.transform = transform

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

        print(
            f"Loaded {len(self.data)} images across {len(classes)} classes "
            f"({len(self.data) // len(classes)} samples/class)."
        )

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        image = self.data[idx].reshape(1, 28, 28)
        image = torch.tensor(image, dtype=torch.float32) / 255.0

        if self.transform is not None:
            image = self.transform(image)

        label = torch.tensor(self.labels[idx], dtype=torch.long)

        return image, label
