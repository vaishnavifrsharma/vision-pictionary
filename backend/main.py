import base64
import io
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from inference import predict_image


app = FastAPI(
    title="Vision Pictionary API"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def root():
    return {
        "message": "Vision Pictionary API is running"
    }


@app.post("/predict")
async def predict(request: Request, file: UploadFile = File(None)):
    try:
        image = None

        # Option A: Multipart File Upload
        if file is not None and file.filename:
            contents = await file.read()
            if contents:
                image = Image.open(io.BytesIO(contents))

        # Option B: JSON payload with base64 data URL
        if image is None:
            try:
                body = await request.json()
                image_data = body.get("image") or body.get("file")
                if image_data:
                    if "," in image_data:
                        image_data = image_data.split(",")[1]
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(io.BytesIO(image_bytes))
            except Exception:
                pass

        if image is None:
            raise HTTPException(
                status_code=400,
                detail="No image provided. Send FormData with 'file' or JSON with 'image' (base64 data URL)."
            )

        predictions, processed_image = predict_image(image)

        # Save processed image for debugging/verification
        processed_image.resize((280, 280)).save("processed_drawing.png")

        return {
            "predictions": predictions
        }

    except ValueError as e:
        return {
            "predictions": [],
            "message": str(e)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )