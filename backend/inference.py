import os

import numpy as np
import torch

from PIL import Image
from torchvision import transforms

from model import SketchCNN


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = os.path.join(
    "models",
    "best_model.pth"
)

IMAGE_SIZE = 28

# Padding around drawing after cropping
PADDING = 20

# Pixels darker than this are considered part of drawing
THRESHOLD = 250


DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# LOAD MODEL
# ============================================================

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

model = model.to(
    DEVICE
)

model.eval()


print(
    f"Loaded {NUM_CLASSES} classes:"
)

print(
    CLASSES
)

print(
    "Model loaded successfully!"
)

print(
    f"Device: {DEVICE}"
)


# ============================================================
# PREPROCESS CANVAS
# ============================================================

def preprocess_canvas(
    image: Image.Image
):
    """
    Convert React canvas image into the exact
    format expected by the trained CNN.

    React Canvas:
        White background
        Black drawing

    CNN training data:
        Black background
        White drawing

    Final output:
        1 x 28 x 28 tensor
    """

    # ========================================================
    # 1. Convert image to grayscale
    # ========================================================

    image = image.convert(
        "L"
    )


    # ========================================================
    # 2. Convert PIL image to NumPy array
    # ========================================================

    image_array = np.array(
        image
    )


    # ========================================================
    # 3. Detect drawing pixels
    #
    # Canvas:
    #
    # Background = 255
    # Drawing    = 0
    #
    # Pixels darker than 250 are considered drawing.
    # ========================================================

    drawing_pixels = (
        image_array < THRESHOLD
    )


    # ========================================================
    # 4. Check if canvas is empty
    # ========================================================

    if not drawing_pixels.any():

        raise ValueError(
            "No drawing detected on canvas."
        )


    # ========================================================
    # 5. Find coordinates of drawing pixels
    # ========================================================

    rows, cols = np.where(
        drawing_pixels
    )


    # ========================================================
    # 6. Find bounding box
    # ========================================================

    min_row = rows.min()
    max_row = rows.max()

    min_col = cols.min()
    max_col = cols.max()


    # ========================================================
    # 7. Crop only the drawing
    # ========================================================

    cropped = image_array[
        min_row:max_row + 1,
        min_col:max_col + 1
    ]


    # ========================================================
    # 8. Get crop dimensions
    # ========================================================

    height, width = cropped.shape


    # ========================================================
    # 9. Make the cropped drawing square
    # ========================================================

    size = max(
        height,
        width
    )


    # ========================================================
    # 10. Create white square background
    # ========================================================

    square = np.full(
        (
            size,
            size
        ),
        255,
        dtype=np.uint8
    )


    # ========================================================
    # 11. Calculate center position
    # ========================================================

    y_offset = (
        size - height
    ) // 2

    x_offset = (
        size - width
    ) // 2


    # ========================================================
    # 12. Place drawing in center
    # ========================================================

    square[
        y_offset:
        y_offset + height,

        x_offset:
        x_offset + width
    ] = cropped


    # ========================================================
    # 13. Add padding
    # ========================================================

    padded_size = (
        size
        + 2 * PADDING
    )


    padded = np.full(
        (
            padded_size,
            padded_size
        ),
        255,
        dtype=np.uint8
    )


    # ========================================================
    # 14. Place square drawing inside padded canvas
    # ========================================================

    padded[
        PADDING:
        PADDING + size,

        PADDING:
        PADDING + size
    ] = square


    # ========================================================
    # 15. INVERT IMAGE
    #
    # Before:
    #
    # Background = 255
    # Drawing    = 0
    #
    # After:
    #
    # Background = 0
    # Drawing    = 255
    #
    # This now matches QuickDraw training images.
    # ========================================================

    inverted = (
        255 - padded
    )


    # ========================================================
    # 16. Convert NumPy array to PIL image
    # ========================================================

    processed_image = Image.fromarray(
        inverted
    )


    # ========================================================
    # 17. Resize to 28 × 28
    # ========================================================

    processed_image = processed_image.resize(
        (
            IMAGE_SIZE,
            IMAGE_SIZE
        ),
        Image.Resampling.LANCZOS
    )


    # ========================================================
    # 18. Convert to NumPy
    # ========================================================

    processed_array = np.array(
        processed_image
    )


    # ========================================================
    # 19. Normalize exactly like training
    #
    # Training:
    #
    # image = image / 255.0
    # ========================================================

    processed_array = (
        processed_array
        / 255.0
    )


    # ========================================================
    # 20. Convert to PyTorch tensor
    # ========================================================

    tensor = torch.tensor(
        processed_array,
        dtype=torch.float32
    )


    # ========================================================
    # 21. Add channel dimension
    #
    # [28, 28]
    #
    # becomes:
    #
    # [1, 28, 28]
    # ========================================================

    tensor = tensor.unsqueeze(
        0
    )


    return (
        tensor,
        processed_image
    )


# ============================================================
# PREDICTION
# ============================================================

def predict_image(
    image: Image.Image
):

    # --------------------------------------------------------
    # Preprocess canvas
    # --------------------------------------------------------

    image_tensor, processed_image = (
        preprocess_canvas(
            image
        )
    )


    # --------------------------------------------------------
    # Add batch dimension
    #
    # [1, 28, 28]
    #
    # →
    #
    # [1, 1, 28, 28]
    # --------------------------------------------------------

    image_tensor = image_tensor.unsqueeze(
        0
    )


    # --------------------------------------------------------
    # Move to device
    # --------------------------------------------------------

    image_tensor = image_tensor.to(
        DEVICE
    )


    # --------------------------------------------------------
    # Run CNN
    # --------------------------------------------------------

    with torch.no_grad():

        outputs = model(
            image_tensor
        )


        # Convert logits to probabilities

        probabilities = torch.softmax(
            outputs,
            dim=1
        )


        # Get Top 5

        top_probabilities, top_indices = (
            torch.topk(
                probabilities,
                k=min(
                    5,
                    NUM_CLASSES
                ),
                dim=1
            )
        )


    # --------------------------------------------------------
    # Format predictions
    # --------------------------------------------------------

    predictions = []


    for probability, index in zip(
        top_probabilities[0],
        top_indices[0]
    ):

        class_index = (
            index.item()
        )

        predictions.append(
            {
                "class":
                    CLASSES[
                        class_index
                    ],

                "confidence":
                    round(
                        probability.item()
                        * 100,
                        2
                    )
            }
        )


    return (
        predictions,
        processed_image
    )