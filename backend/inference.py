import os

import numpy as np
import torch

from PIL import Image, ImageDraw

from model import SketchCNN


MODEL_PATH = os.path.join(
    "models",
    "best_model.pth"
)

IMAGE_SIZE = 28
RASTER_SIZE = 112
PADDING = 12

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE
)

CLASSES = checkpoint["classes"]

NUM_CLASSES = len(CLASSES)

model = SketchCNN(
    num_classes=NUM_CLASSES
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(DEVICE)

model.eval()

print(
    f"Loaded {NUM_CLASSES} classes:"
)

print(CLASSES)

print(
    "Model loaded successfully!"
)

print(
    f"Device: {DEVICE}"
)


def preprocess_image(image: Image.Image) -> tuple[torch.Tensor, Image.Image]:
    """
    Preprocess raw canvas image into standard 28x28 QuickDraw tensor format:
    1. Flatten RGBA onto white background.
    2. Convert to Grayscale & invert white background to black.
    3. Trim outer 2% margin to strip outer canvas borders/frames.
    4. Detect stroke bounding box and crop tightly.
    5. Aspect-ratio preserving square pad with ~14% relative padding.
    6. Adaptively thicken stroke (MaxFilter) so line width at 28x28 matches QuickDraw (~1.8-2.2px).
    7. Downscale to 28x28 Bilinear, normalize intensity, and convert to (1, 1, 28, 28) float tensor.
    """
    # 1. Flatten RGBA / Alpha onto white background if needed
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        bg = Image.new("RGB", image.size, (255, 255, 255))
        if image.mode == "RGBA":
            bg.paste(image, mask=image.split()[3])
        else:
            bg.paste(image.convert("RGBA"), mask=image.convert("RGBA").split()[3])
        gray = bg.convert("L")
    else:
        gray = image.convert("L")

    arr = np.array(gray)

    # 2. Invert: ensure background is 0 (black) and stroke is >0 (white)
    if np.mean(arr) > 127:
        arr = 255 - arr

    # 3. Strip outer 2% margin to eliminate any outer canvas border / container frame artifacts
    h_orig, w_orig = arr.shape
    margin_y = int(h_orig * 0.02)
    margin_x = int(w_orig * 0.02)

    if margin_y > 0:
        arr[:margin_y, :] = 0
        arr[-margin_y:, :] = 0
    if margin_x > 0:
        arr[:, :margin_x] = 0
        arr[:, -margin_x:] = 0

    # 4. Find stroke bounding box
    mask = arr > 30
    if not mask.any():
        raise ValueError("No drawing detected.")

    rows, cols = np.where(mask)
    min_y, max_y = rows.min(), rows.max()
    min_x, max_x = cols.min(), cols.max()
    h, w = max_y - min_y + 1, max_x - min_x + 1

    # 5. Aspect-ratio preserving square crop with ~14% relative padding
    max_dim = max(h, w)
    pad = max(int(max_dim * 0.14), 4)
    size = max_dim + 2 * pad

    square = np.zeros((size, size), dtype=np.uint8)
    y_off = (size - h) // 2
    x_off = (size - w) // 2
    square[y_off:y_off + h, x_off:x_off + w] = arr[min_y:max_y + 1, min_x:max_x + 1]

    square_img = Image.fromarray(square)

    # 6. Adaptively thicken stroke so line width at 28x28 is ~1.8-2.2 pixels
    filter_size = max(1, int(size * (1.8 / IMAGE_SIZE)))
    if filter_size > 1:
        if filter_size % 2 == 0:
            filter_size += 1
        from PIL import ImageFilter
        square_img = square_img.filter(ImageFilter.MaxFilter(filter_size))

    # 7. Resize to 28x28 Bilinear & Normalize intensity
    proc_img = square_img.resize((IMAGE_SIZE, IMAGE_SIZE), Image.Resampling.BILINEAR)
    proc_arr = np.array(proc_img).astype(np.float32)

    if proc_arr.max() > 0:
        proc_arr = (proc_arr / proc_arr.max()) * 255.0

    tensor = torch.tensor(proc_arr / 255.0, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
    return tensor, proc_img


def predict_image(image: Image.Image):
    image_tensor, processed_image = preprocess_image(image)
    image_tensor = image_tensor.to(DEVICE)

    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.softmax(outputs, dim=1)

        top_probabilities, top_indices = torch.topk(
            probabilities,
            k=min(5, NUM_CLASSES),
            dim=1
        )

    predictions = []

    for probability, index in zip(
        top_probabilities[0],
        top_indices[0]
    ):
        class_index = index.item()

        predictions.append({
            "class": CLASSES[class_index],
            "confidence": round(
                probability.item() * 100,
                2
            )
        })

    return predictions, processed_image