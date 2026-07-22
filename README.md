# 🎯 AI Pictionary Classifier (V2 - 50 Classes)

An end-to-end Computer Vision application that transforms hand-drawn sketches into real-time predictions using a custom PyTorch Convolutional Neural Network trained on 50 Google QuickDraw dataset categories.

Users can draw directly on an interactive canvas with QuickDraw-style continuous live predictions, view single top-1 estimates while drawing, and inspect full top-3 confidence rankings alongside model preprocessing visual pipelines on demand.

---

## ✨ Features

- 🖌️ **Interactive Drawing Canvas**: Built with React + TypeScript, featuring continuous live stroke capture, customizable stroke sizes, undo, clear, and replay.
- ⏱️ **Calm Live Predictions**: Smooth 1500ms throttled real-time inference while drawing with non-intrusive Top-1 guess badges and threshold-gated confidence (`≥60%`).
- 🧠 **PyTorch SketchCNN V2**: Enhanced deep convolutional network with Batch Normalization and 8° rotational data augmentation trained across 50 categories with **87.36% Top-1** and **96.36% Top-5 test accuracy**.
- 📐 **2-Column Side-by-Side Layout**: Modern workspace with canvas on the left and live prediction sidebar on the right.
- ⚡ **FastAPI Backend**: Low-latency REST API accepting base64 image data and multipart file uploads with sub-50ms CPU inference.
- 🔍 **Model Vision Pipeline ("What The Model Sees")**: Real-time visual explanation displaying the exact $28\times 28$ preprocessed tensor fed into the CNN.
- 🎨 **Custom Color Palette UI**: Styled with a warm, nature-inspired palette (Beige `#F7F4D5`, Dark Green `#0A3323`, Midnight Green `#105666`, Moss Green `#839958`, and Rosy Brown `#D3968C`).

---

## 🚀 How To Run

### 1. Clone Repository

```bash
git clone https://github.com/vaishnavifrsharma/vision-pictionary.git
cd vision-pictionary
```

---

### 2. Backend Setup

```bash
cd backend

python3 -m venv venv
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

pip install -r requirements.txt
```

Start FastAPI server (pre-trained 50-class model `models/best_model.pth` is included out of the box):

```bash
uvicorn main:app --reload --port 8000
```

Backend runs on: `http://127.0.0.1:8000`

---

### 3. Frontend Setup

Open a new terminal:

```bash
cd frontend/vision-pictionary

npm install
npm run dev
```

Frontend runs on: `http://localhost:5173`

---

### 4. Start Drawing

1. Open `http://localhost:5173` in your browser.
2. Draw any sketch from the 50 supported categories (e.g., house, guitar, pizza, airplane, eyeglasses, rainbow, dragon, etc.).
3. Watch continuous top-1 live predictions update dynamically while drawing.
4. Click **Predict** to reveal runner-up predictions and the preprocessed model vision tensor.

---

## 📚 Supported QuickDraw Categories (50 Classes)

`airplane`, `apple`, `banana`, `bicycle`, `book`, `bridge`, `bus`, `camera`, `candle`, `car`, `cat`, `chair`, `clock`, `cloud`, `cookie`, `cup`, `diamond`, `dog`, `door`, `drums`, `envelope`, `eye`, `eyeglasses`, `fish`, `flower`, `guitar`, `hammer`, `hat`, `headphones`, `house`, `ice cream`, `key`, `ladder`, `light bulb`, `lightning`, `moon`, `mountain`, `mushroom`, `pants`, `pencil`, `pizza`, `rainbow`, `scissors`, `shoe`, `skull`, `snake`, `snowflake`, `spider`, `star`, `tree`

---

## 🏗️ System Architecture

```text
React Drawing Canvas (Left)         Prediction Sidebar (Right)
         │                                      │
         ├── Throttled (1500ms) Live Strokes ────┤
         │                                      │
         ▼                                      ▼
    PNG Base64                         Single Top-1 Badge
         │                            ("Keep Drawing..." if <60%)
         ▼                                      │
  FastAPI Backend                               │ (On Predict Click)
         │                                      ▼
Image Preprocessing Pipeline ──────> Top-3 Confidence Bars &
(Crop -> Pad -> Thickening -> 28x28) 28x28 Model Vision Tensor
         │
         ▼
PyTorch SketchCNN V2 (50 Classes)
```

---

## 🤖 Model V2 Architecture & Performance

Custom Convolutional Neural Network (`SketchCNN_v2`):

```text
Input (1 × 28 × 28)
  │
  ├── Conv2d(1 → 32, k=3, p=1)  → BatchNorm2d(32)  → ReLU → MaxPool2d(2) ──> (32 × 14 × 14)
  ├── Conv2d(32 → 64, k=3, p=1) → BatchNorm2d(64)  → ReLU → MaxPool2d(2) ──> (64 × 7 × 7)
  ├── Conv2d(64 → 128, k=3, p=1)→ BatchNorm2d(128) → ReLU → MaxPool2d(2) ──> (128 × 3 × 3)
  ├── Flatten (1152) → Linear(1152 → 256) → BatchNorm1d(256) → ReLU → Dropout(0.4)
  └── Linear(256 → 50) → Softmax Output
```

- **Training Dataset**: 75,000 QuickDraw sketches across 50 categories (1,500 samples/class).
- **Data Augmentation**: `RandomRotation(degrees=8)` during PyTorch training.
- **Top-1 Test Accuracy**: **87.36%**
- **Top-5 Test Accuracy**: **96.36%**
- **Confusion Matrix**: Saved at `backend/experiments/confusion_matrix.png`.
- **Model Checkpoint**: Included at `backend/models/best_model.pth` (1.6 MB).

---

## 🛠️ Tech Stack

- **Frontend**: React 18, TypeScript, HTML5 Canvas, Vanilla CSS3
- **Backend**: FastAPI, Uvicorn, Python 3.10+, PIL (Pillow)
- **Machine Learning**: PyTorch, Torchvision, NumPy, Scikit-Learn, Matplotlib
- **Dataset**: Google QuickDraw (50 Classes)

---

## 👩‍💻 Author

**Vaishnavi Sharma**  
Computer Vision • Machine Learning • Full Stack AI Applications