import os

import torch
import torch.nn as nn

from torch.utils.data import DataLoader
from torch.utils.data import random_split

from dataset import QuickDrawDataset
from model import SketchCNN

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

CLASSES = [
    class_name
    for class_name in CLASSES
    if os.path.exists(
        os.path.join(
            DATA_DIR,
            f"{class_name}.npy"
        )
    )
]

NUM_CLASSES = len(CLASSES)

SAMPLES_PER_CLASS = 1000

BATCH_SIZE = 64

EPOCHS = 15

LEARNING_RATE = 0.001

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

dataset = QuickDrawDataset(
    data_dir=DATA_DIR,
    classes=CLASSES,
    samples_per_class=SAMPLES_PER_CLASS
)

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

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False
)

model = SketchCNN(
    num_classes=NUM_CLASSES
)
model = model.to(
    DEVICE
)

criterion = nn.CrossEntropyLoss()

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE
)

best_val_accuracy = 0.0

epochs_without_improvement = 0

PATIENCE = 3
# Create models directory
os.makedirs(
    "models",
    exist_ok=True
)

# Training loop with early stopping

for epoch in range(EPOCHS):

    print(
        f"\nStarting Epoch {epoch + 1}/{EPOCHS}...",
        flush=True
    )

    # Training phase

    model.train()

    running_loss = 0.0

    train_correct = 0

    train_total = 0


    # --------------------------------------------------------
    # Process every batch in the training dataset
    # --------------------------------------------------------

    for images, labels in train_loader:

        # Move images and labels to device
        images = images.to(
            DEVICE
        )

        labels = labels.to(
            DEVICE
        )


        # ----------------------------------------------------
        # 1. Reset gradients
        # ----------------------------------------------------

        optimizer.zero_grad()


        # ----------------------------------------------------
        # 2. Forward pass
        # ----------------------------------------------------

        outputs = model(
            images
        )


        # ----------------------------------------------------
        # 3. Calculate loss
        # ----------------------------------------------------

        loss = criterion(
            outputs,
            labels
        )


        # ----------------------------------------------------
        # 4. Backpropagation
        # ----------------------------------------------------

        loss.backward()


        # ----------------------------------------------------
        # 5. Update model weights
        # ----------------------------------------------------

        optimizer.step()


        # ----------------------------------------------------
        # 6. Track training loss
        # ----------------------------------------------------

        running_loss += (
            loss.item()
            * images.size(0)
        )


        # ----------------------------------------------------
        # 7. Get predicted class
        # ----------------------------------------------------

        _, predicted = torch.max(
            outputs,
            1
        )


        # ----------------------------------------------------
        # 8. Track number of samples
        # ----------------------------------------------------

        train_total += (
            labels.size(0)
        )


        # ----------------------------------------------------
        # 9. Track correct predictions
        # ----------------------------------------------------

        train_correct += (
            predicted == labels
        ).sum().item()


    # Calculate training metrics

    train_loss = (
        running_loss
        / train_total
    )

    train_accuracy = (
        100.0
        * train_correct
        / train_total
    )


    # Validation phase

    model.eval()

    val_loss_total = 0.0

    val_correct = 0

    val_total = 0


    # --------------------------------------------------------
    # Disable gradient calculation
    # --------------------------------------------------------

    with torch.no_grad():

        for images, labels in val_loader:

            # Move images and labels to device
            images = images.to(
                DEVICE
            )

            labels = labels.to(
                DEVICE
            )


            # ------------------------------------------------
            # Forward pass
            # ------------------------------------------------

            outputs = model(
                images
            )


            # ------------------------------------------------
            # Calculate validation loss
            # ------------------------------------------------

            loss = criterion(
                outputs,
                labels
            )


            # ------------------------------------------------
            # Track validation loss
            # ------------------------------------------------

            val_loss_total += (
                loss.item()
                * images.size(0)
            )


            # ------------------------------------------------
            # Get predicted class
            # ------------------------------------------------

            _, predicted = torch.max(
                outputs,
                1
            )


            # ------------------------------------------------
            # Track total validation samples
            # ------------------------------------------------

            val_total += (
                labels.size(0)
            )


            # ------------------------------------------------
            # Track correct predictions
            # ------------------------------------------------

            val_correct += (
                predicted == labels
            ).sum().item()


    # Calculate validation metrics

    val_loss = (
        val_loss_total
        / val_total
    )

    val_accuracy = (
        100.0
        * val_correct
        / val_total
    )


    # Print epoch results

    print(
        "\n" + "=" * 60,
        flush=True
    )

    print(
        f"Epoch [{epoch + 1}/{EPOCHS}]",
        flush=True
    )

    print(
        f"Train Loss: "
        f"{train_loss:.4f}",
        flush=True
    )

    print(
        f"Train Accuracy: "
        f"{train_accuracy:.2f}%",
        flush=True
    )

    print(
        f"Validation Loss: "
        f"{val_loss:.4f}",
        flush=True
    )

    print(
        f"Validation Accuracy: "
        f"{val_accuracy:.2f}%",
        flush=True
    )

    print(
        "=" * 60,
        flush=True
    )


    # Early stopping check

    if val_accuracy > best_val_accuracy:

        # ----------------------------------------------------
        # Validation accuracy improved
        # ----------------------------------------------------

        best_val_accuracy = val_accuracy

        # Reset patience counter
        epochs_without_improvement = 0


        # ----------------------------------------------------
        # Save best model
        # ----------------------------------------------------

        torch.save(
            {
                "model_state_dict":
                    model.state_dict(),

                "classes":
                    CLASSES,

                "val_accuracy":
                    val_accuracy,

                "epoch":
                    epoch + 1
            },

            "models/best_model.pth"
        )


        print(
            f"New best model saved!",
            flush=True
        )

        print(
            f"Best Validation Accuracy: "
            f"{best_val_accuracy:.2f}%",
            flush=True
        )


    else:

        # ----------------------------------------------------
        # Validation accuracy did NOT improve
        # ----------------------------------------------------

        epochs_without_improvement += 1


        print(
            f"No improvement for "
            f"{epochs_without_improvement} "
            f"epoch(s).",
            flush=True
        )


    # Check early stopping condition

    if (
        epochs_without_improvement
        >= PATIENCE
    ):

        print(
            "\nEarly stopping triggered!",
            flush=True
        )

        print(
            f"Validation accuracy did not improve "
            f"for {PATIENCE} consecutive epochs.",
            flush=True
        )

        break


# Training complete

print(
    "\n" + "=" * 60
)

print(
    "TRAINING COMPLETE"
)

print(
    "=" * 60
)

print(
    f"Best Validation Accuracy: "
    f"{best_val_accuracy:.2f}%"
)

print(
    "Best model saved at:"
)

print(
    "models/best_model.pth"
)

print(
    "=" * 60
)