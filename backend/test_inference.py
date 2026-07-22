from PIL import Image

from inference import predict_image


# ============================================================
# LOAD TEST CANVAS IMAGE
# ============================================================

image = Image.open(
    "test_drawing.png"
).convert(
    "RGB"
)


# ============================================================
# RUN PREDICTION
# ============================================================

predictions, processed_image = (
    predict_image(
        image
    )
)


# ============================================================
# SAVE PROCESSED IMAGE
# ============================================================

processed_image.resize(
    (
        280,
        280
    )
).save(
    "processed_drawing.png"
)


print(
    "\nProcessed image saved to:"
)

print(
    "processed_drawing.png"
)


# ============================================================
# PRINT PREDICTIONS
# ============================================================

print(
    "\nAI Predictions:"
)

print(
    "--------------------------"
)


for index, prediction in enumerate(
    predictions,
    start=1
):

    print(
        f"{index}. "
        f"{prediction['class']} "
        f"- "
        f"{prediction['confidence']}%"
    )