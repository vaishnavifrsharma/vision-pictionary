import numpy as np
import matplotlib.pyplot as plt
import os


DATA_DIR = "data/quickdraw"

CLASSES = [
    "apple",
    "banana",
    "cat",
    "dog",
    "fish",
    "house",
    "tree",
    "car",
    "cup",
    "clock",
    "star",
    "flower",
    "pizza",
    "book",
    "chair",
    "phone",
    "key",
    "light bulb",
    "ice cream",
    "guitar",
]


def inspect_category(category):

    path = os.path.join(
        DATA_DIR,
        f"{category}.npy"
    )

    data = np.load(path)

    print(f"\nCategory: {category}")
    print(f"Shape: {data.shape}")
    print(f"Dtype: {data.dtype}")
    print(f"Min: {data.min()}")
    print(f"Max: {data.max()}")

    fig, axes = plt.subplots(
        2,
        5,
        figsize=(12, 5)
    )

    for image, ax in zip(data[:10], axes.flat):

        ax.imshow(
            image.reshape(28, 28),
            cmap="gray"
        )

        ax.axis("off")

    plt.suptitle(category)
    plt.tight_layout()

    plt.show()


if __name__ == "__main__":

    inspect_category("apple")