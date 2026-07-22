import os
import torch
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader, random_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

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
BATCH_SIZE = 128
MODEL_PATH = "models/best_model.pth"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def main():
    print("\n" + "=" * 60)
    print("MODEL EVALUATION V2: 50 CLASSES")
    print("=" * 60)
    print(f"Number of classes: {NUM_CLASSES}")
    print(f"Device: {DEVICE}")
    print(f"Model path: {MODEL_PATH}")

    print("\nLoading dataset...")
    dataset = QuickDrawDataset(
        data_dir=DATA_DIR,
        classes=CLASSES,
        samples_per_class=SAMPLES_PER_CLASS
    )
    print(f"Total images: {len(dataset)}")

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

    print(f"Test images: {len(test_dataset)}")
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

    print("\nLoading model...")
    model = SketchCNN(num_classes=NUM_CLASSES)
    checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)
    model.load_state_dict(checkpoint["model_state_dict"])
    model = model.to(DEVICE)
    model.eval()

    print("Model loaded successfully.")

    print("\nRunning evaluation...")
    all_predictions = []
    all_labels = []
    top5_correct = 0
    total_samples = 0

    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            outputs = model(images)

            predictions = torch.argmax(outputs, dim=1)
            all_predictions.extend(predictions.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

            top5_predictions = torch.topk(outputs, k=5, dim=1).indices
            correct_top5 = (top5_predictions == labels.unsqueeze(1)).any(dim=1)
            top5_correct += correct_top5.sum().item()
            total_samples += labels.size(0)

    top1_accuracy = accuracy_score(all_labels, all_predictions)
    top5_accuracy = top5_correct / total_samples

    print("\n" + "=" * 60)
    print("ACCURACY RESULTS (50 CLASSES)")
    print("=" * 60)
    print(f"Top-1 Accuracy: {top1_accuracy * 100:.2f}%")
    print(f"Top-5 Accuracy: {top5_accuracy * 100:.2f}%")

    print("\nGenerating confusion matrix...")
    cm = confusion_matrix(all_labels, all_predictions)

    fig, ax = plt.subplots(figsize=(18, 16))
    cax = ax.imshow(cm, cmap="Blues")
    fig.colorbar(cax)

    ax.set_xticks(range(NUM_CLASSES))
    ax.set_yticks(range(NUM_CLASSES))
    ax.set_xticklabels(CLASSES, rotation=90, fontsize=8)
    ax.set_yticklabels(CLASSES, fontsize=8)
    ax.set_xlabel("Predicted Class", fontsize=12)
    ax.set_ylabel("Actual Class", fontsize=12)
    ax.set_title("QuickDraw CNN 50-Class Confusion Matrix", fontsize=14, fontweight="bold")
    plt.tight_layout()

    os.makedirs("experiments", exist_ok=True)
    save_path = "experiments/confusion_matrix.png"
    plt.savefig(save_path, dpi=300)
    print(f"\nConfusion matrix saved to: {save_path}")

    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)
    print(f"Top-1 Accuracy: {top1_accuracy * 100:.2f}%")
    print(f"Top-5 Accuracy: {top5_accuracy * 100:.2f}%")
    print("=" * 60)

if __name__ == "__main__":
    main()