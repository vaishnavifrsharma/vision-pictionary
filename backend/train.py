import os
import time
import torch
import torch.nn as nn
import torchvision.transforms as T
from torch.utils.data import DataLoader, random_split

from dataset import QuickDrawDataset
from model import SketchCNN

DATA_DIR = "data/quickdraw"

CLASSES = [
    # Original 20 Classes
    "apple", "banana", "book", "car", "cat",
    "chair", "clock", "cloud", "cup", "dog",
    "fish", "flower", "guitar", "house", "ice cream",
    "key", "light bulb", "pizza", "star", "tree",
    # 30 New Visually Distinct Classes
    "airplane", "bicycle", "bridge", "bus", "camera",
    "candle", "cookie", "diamond", "door", "drums",
    "envelope", "eye", "eyeglasses", "hammer", "hat",
    "headphones", "ladder", "lightning", "moon", "mountain",
    "mushroom", "pants", "pencil", "rainbow", "scissors",
    "shoe", "skull", "snake", "snowflake", "spider"
]

NUM_CLASSES = len(CLASSES)
SAMPLES_PER_CLASS = 1500
BATCH_SIZE = 256
EPOCHS = 10
LEARNING_RATE = 0.002
PATIENCE = 3

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def main():
    print("=" * 60)
    print(f"TRAINING SKETCH CNN V2: {NUM_CLASSES} CLASSES")
    print(f"Device: {DEVICE}")
    print(f"Samples Per Class: {SAMPLES_PER_CLASS} (Total: {NUM_CLASSES * SAMPLES_PER_CLASS})")
    print("=" * 60)

    # Fast Data augmentation
    train_transform = T.RandomRotation(degrees=8)

    # Base dataset loading (75,000 images total)
    dataset = QuickDrawDataset(
        data_dir=DATA_DIR,
        classes=CLASSES,
        samples_per_class=SAMPLES_PER_CLASS,
        transform=train_transform
    )

    total_size = len(dataset)
    train_size = int(0.8 * total_size)
    val_size = int(0.1 * total_size)
    test_size = total_size - train_size - val_size

    generator = torch.Generator().manual_seed(42)
    train_dataset, val_dataset, test_dataset = random_split(
        dataset,
        [train_size, val_size, test_size],
        generator=generator
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0
    )

    model = SketchCNN(num_classes=NUM_CLASSES).to(DEVICE)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    best_val_accuracy = 0.0
    epochs_without_improvement = 0
    os.makedirs("models", exist_ok=True)

    for epoch in range(EPOCHS):
        start_time = time.time()
        print(f"\nStarting Epoch {epoch + 1}/{EPOCHS}...", flush=True)

        model.train()
        running_loss = 0.0
        train_correct = 0
        train_total = 0

        for step, (images, labels) in enumerate(train_loader):
            images, labels = images.to(DEVICE), labels.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, predicted = torch.max(outputs, 1)
            train_total += labels.size(0)
            train_correct += (predicted == labels).sum().item()

            if (step + 1) % 50 == 0 or (step + 1) == len(train_loader):
                acc = 100.0 * train_correct / train_total
                print(f"  Batch [{step + 1}/{len(train_loader)}] Loss: {loss.item():.4f} | Acc: {acc:.2f}%", flush=True)

        train_loss = running_loss / train_total
        train_accuracy = 100.0 * train_correct / train_total

        # Validation phase
        model.eval()
        val_loss_total = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(DEVICE), labels.to(DEVICE)
                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss_total += loss.item() * images.size(0)
                _, predicted = torch.max(outputs, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()

        val_loss = val_loss_total / val_total
        val_accuracy = 100.0 * val_correct / val_total
        elapsed = time.time() - start_time

        print("=" * 60, flush=True)
        print(f"Epoch [{epoch + 1}/{EPOCHS}] completed in {elapsed:.1f}s", flush=True)
        print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_accuracy:.2f}%", flush=True)
        print(f"Val Loss:   {val_loss:.4f} | Val Acc:   {val_accuracy:.2f}%", flush=True)
        print("=" * 60, flush=True)

        if val_accuracy > best_val_accuracy:
            best_val_accuracy = val_accuracy
            epochs_without_improvement = 0

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "classes": CLASSES,
                    "val_accuracy": val_accuracy,
                    "epoch": epoch + 1
                },
                "models/best_model.pth"
            )
            print(f"New best model saved! Best Validation Accuracy: {best_val_accuracy:.2f}%", flush=True)
        else:
            epochs_without_improvement += 1
            print(f"No improvement for {epochs_without_improvement} epoch(s).", flush=True)

        if epochs_without_improvement >= PATIENCE:
            print(f"\nEarly stopping triggered after {epoch + 1} epochs!", flush=True)
            break

    print("=" * 60)
    print("TRAINING COMPLETE")
    print(f"Best Validation Accuracy: {best_val_accuracy:.2f}%")
    print("Best model saved at: models/best_model.pth")
    print("=" * 60)


if __name__ == "__main__":
    main()