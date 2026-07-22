import os
import urllib.request

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

BASE_URL = (
    "https://storage.googleapis.com/quickdraw_dataset/"
    "full/numpy_bitmap/"
)

OUTPUT_DIR = "data/quickdraw"


def download_dataset():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Downloading QuickDraw numpy bitmap dataset for {len(CLASSES)} categories...")

    for category in CLASSES:
        filename = f"{category}.npy"
        url = BASE_URL + filename.replace(" ", "%20")
        output_path = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(output_path):
            print(f"[SKIP] {category}")
            continue

        print(f"[DOWNLOAD] {category} from {url}...")

        try:
            urllib.request.urlretrieve(
                url,
                output_path
            )
            print(f"[DONE] {category}")

        except Exception as e:
            print(f"[ERROR] {category}: {e}")

    print("\nDataset download process completed!")


if __name__ == "__main__":
    download_dataset()