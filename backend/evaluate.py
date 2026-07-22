import os

import torch
import matplotlib.pyplot as plt
import seaborn as sns

from torch.utils.data import DataLoader
from torch.utils.data import random_split

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score
)

from dataset import QuickDrawDataset
from model import SketchCNN


# Configuration

DATA_DIR = "data/quickdraw"

CLASSES = [
    "apple",
    "banana",
    "book",
    "car",
    "cat",
    "chair",
    "clock",
    "cloud",
    "cup",
    "dog",
    "fish",
    "flower",
    "guitar",
    "house",
    "ice cream",
    "key",
    "light bulb",
    "pizza",
    "star",
    "tree",
]

NUM_CLASSES = len(CLASSES)

SAMPLES_PER_CLASS = 1000

BATCH_SIZE = 64

MODEL_PATH = "models/best_model.pth"

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

print("\n" + "=" * 60)

print("MODEL EVALUATION")

print("=" * 60)

print(
    f"Number of classes: {NUM_CLASSES}"
)

print(
    f"Device: {DEVICE}"
)

print(
    f"Model path: {MODEL_PATH}"
)


# Load dataset

print("\nLoading dataset...")

dataset = QuickDrawDataset(
    data_dir=DATA_DIR,
    classes=CLASSES,
    samples_per_class=SAMPLES_PER_CLASS
)

print(
    f"Total images: {len(dataset)}"
)


# Recreate the same train, val, and test split

total_size = len(dataset)

train_size = int(
    0.8 * total_size
)

val_size = int(
    0.1 * total_size
)

test_size = (
    total_size
    - train_size
    - val_size
)


# IMPORTANT:
# This must be the same random seed used during training.

generator = torch.Generator().manual_seed(42)


train_dataset, val_dataset, test_dataset = random_split(
    dataset,
    [
        train_size,
        val_size,
        test_size
    ],
    generator=generator
)


print(
    f"Training images: {len(train_dataset)}"
)

print(
    f"Validation images: {len(val_dataset)}"
)

print(
    f"Test images: {len(test_dataset)}"
)


# Create test dataloader

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False
)


# Create model

print("\nLoading model...")

model = SketchCNN(
    num_classes=NUM_CLASSES
)


# Load trained weights

checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE
)


model.load_state_dict(
    checkpoint[
        "model_state_dict"
    ]
)


model = model.to(
    DEVICE
)


model.eval()


print(
    "Model loaded successfully."
)


# Run test set

print("\nRunning evaluation...")

all_predictions = []

all_labels = []

top5_correct = 0

total_samples = 0


with torch.no_grad():

    for images, labels in test_loader:

        # Move images and labels
        # to the selected device

        images = images.to(
            DEVICE
        )

        labels = labels.to(
            DEVICE
        )


        # ----------------------------------------
        # Forward pass
        # ----------------------------------------

        outputs = model(
            images
        )


        # ----------------------------------------
        # Top-1 prediction
        # ----------------------------------------

        predictions = torch.argmax(
            outputs,
            dim=1
        )


        # ----------------------------------------
        # Store predictions
        # ----------------------------------------

        all_predictions.extend(
            predictions.cpu().numpy()
        )


        all_labels.extend(
            labels.cpu().numpy()
        )


        # ----------------------------------------
        # Top-5 accuracy
        # ----------------------------------------

        top5_predictions = torch.topk(
            outputs,
            k=5,
            dim=1
        ).indices


        correct_top5 = (
            top5_predictions
            == labels.unsqueeze(1)
        ).any(
            dim=1
        )


        top5_correct += (
            correct_top5
            .sum()
            .item()
        )


        total_samples += (
            labels.size(0)
        )


# Top-1 accuracy

top1_accuracy = accuracy_score(
    all_labels,
    all_predictions
)


# Top-5 accuracy

top5_accuracy = (
    top5_correct
    / total_samples
)


# Print accuracy results

print("\n" + "=" * 60)

print("ACCURACY RESULTS")

print("=" * 60)

print(
    f"Top-1 Accuracy: "
    f"{top1_accuracy * 100:.2f}%"
)

print(
    f"Top-5 Accuracy: "
    f"{top5_accuracy * 100:.2f}%"
)


# Classification report

print("\n" + "=" * 60)

print("CLASSIFICATION REPORT")

print("=" * 60)


report = classification_report(
    all_labels,
    all_predictions,
    target_names=CLASSES,
    digits=4
)


print(
    report
)


# Confusion matrix

print("\nGenerating confusion matrix...")


cm = confusion_matrix(
    all_labels,
    all_predictions
)


# Plot confusion matrix

plt.figure(
    figsize=(14, 12)
)


sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    xticklabels=CLASSES,
    yticklabels=CLASSES
)


plt.xlabel(
    "Predicted Class"
)


plt.ylabel(
    "Actual Class"
)


plt.title(
    "QuickDraw CNN Confusion Matrix"
)


plt.xticks(
    rotation=45,
    ha="right"
)


plt.yticks(
    rotation=0
)


plt.tight_layout()


# Create experiments directory

os.makedirs(
    "experiments",
    exist_ok=True
)


# Save confusion matrix

save_path = (
    "experiments/"
    "confusion_matrix.png"
)


plt.savefig(
    save_path,
    dpi=300
)


print(
    f"\nConfusion matrix saved to:"
)

print(
    save_path
)


plt.show()


# Final summary

print("\n" + "=" * 60)

print("EVALUATION COMPLETE")

print("=" * 60)

print(
    f"Top-1 Accuracy: "
    f"{top1_accuracy * 100:.2f}%"
)

print(
    f"Top-5 Accuracy: "
    f"{top5_accuracy * 100:.2f}%"
)

print("=" * 60)