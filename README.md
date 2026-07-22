# 🎨 Vision Pictionary

An interactive AI-powered Pictionary game where humans compete against a computer vision model to recognize hand-drawn sketches.

The game works differently from traditional Pictionary:

1. A game organizer secretly gives the player an object to draw.
2. The object is NOT displayed on the screen.
3. The player draws the object on a digital canvas.
4. Human players try to guess the object.
5. At the same time, an AI model analyzes the drawing.
6. The first correct guess wins.

The goal is to explore how computer vision models interpret incomplete, noisy, and highly variable human sketches in real time.

---

## 🚀 Current Status

### Phase 1: Canvas Engine ✅

- [x] Drawing with mouse input
- [x] Stroke data storage
- [x] Canvas redraw from stored stroke data
- [x] Undo functionality
- [x] Replay animation
- [x] Adjustable brush size

### Phase 2: CNN Baseline ✅

A convolutional neural network was trained to classify 20 categories of hand-drawn objects using the Google Quick, Draw! dataset.

| Metric | Result |
|---|---:|
| Classes | 20 |
| Total Images | 20,000 |
| Training Images | 16,000 |
| Validation Images | 2,000 |
| Test Images | 2,000 |
| Best Validation Accuracy | 88.65% |
| Test Top-1 Accuracy | 89.00% |
| Test Top-5 Accuracy | 97.75% |
| Macro F1 Score | 0.8898 |
| Weighted F1 Score | 0.8908 |

The model uses early stopping and saves the best validation checkpoint.

Strongest classes include:

- Banana
- Clock
- Ice Cream
- Chair
- Apple

Most challenging classes include:

- Dog
- Cat
- Key

The largest observed confusion was between cat and dog drawings.

Confusion matrix:

`backend/experiments/confusion_matrix.png`

---

# 🧠 How the System Works

```text
                 GAME ORGANIZER
                       │
                       │ Secret object
                       ▼
                  PLAYER DRAWS
                       │
                       ▼
              React Drawing Canvas
                       │
                       │ Stroke data
                       ▼
              Canvas Preprocessing
                       │
                       │ Image tensor
                       ▼
                CNN Classifier
                       │
                       ▼
               AI Predictions
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
      Human Guessing        AI Guessing
             │                   │
             └─────────┬─────────┘
                       ▼
                 Winner + Score

The AI should progressively update its prediction as the player adds more strokes.

Drawing starts
      ↓
AI: No confident prediction
      ↓
More strokes
      ↓
AI: "Cloud"
      ↓
More strokes
      ↓
AI: "Tree"
      ↓
Human guesses
      ↓
Winner determined
🏗️ Project Architecture
vision-pictionary/
│
├── frontend/
│   └── vision-pictionary/
│       ├── React + TypeScript
│       └── Drawing Canvas
│
├── backend/
│   ├── dataset.py
│   ├── download_dataset.py
│   ├── inspect_dataset.py
│   ├── model.py
│   ├── train.py
│   ├── evaluate.py
│   ├── requirements.txt
│   │
│   ├── experiments/
│   │   └── confusion_matrix.png
│   │
│   ├── data/
│   │   └── quickdraw/
│   │
│   └── models/
│       └── best_model.pth
│
├── README.md
└── .gitignore
📊 Dataset

The model is trained using the Google Quick, Draw! dataset.

The current version uses 20 object categories:

Apple
Banana
Book
Car
Cat
Chair
Clock
Cloud
Cup
Dog
Fish
Flower
Guitar
House
Ice Cream
Key
Light Bulb
Pizza
Star
Tree

The first version intentionally uses 20 classes to establish a strong baseline before expanding the vocabulary.

🤖 CNN Baseline

Training pipeline:

QuickDraw Dataset
       ↓
Dataset Loading
       ↓
Train / Validation / Test Split
       ↓
Image Preprocessing
       ↓
CNN Training
       ↓
Validation
       ↓
Early Stopping
       ↓
Best Model Checkpoint
       ↓
Test Evaluation
       ↓
Confusion Matrix

The model is evaluated using:

Top-1 Accuracy
Top-5 Accuracy
Precision
Recall
F1 Score
Confusion Matrix
🔬 Baseline Results
Test Top-1 Accuracy: 89.00%
Test Top-5 Accuracy: 97.75%
Macro F1 Score: 0.8898
Weighted F1 Score: 0.8908

The baseline CNN provides a strong starting point for integrating real-time drawing recognition into the game.

The next challenge is not simply maximizing offline classification accuracy.

The main challenge is determining whether the AI can recognize a sketch before the human players do.

🛣️ Roadmap
Phase 1: Canvas Engine ✅
 Drawing canvas
 Stroke storage
 Canvas redraw
 Undo
 Replay animation
 Brush size
Phase 2: Dataset + CNN Baseline ✅
 Download QuickDraw dataset
 Select 20 object classes
 Build PyTorch dataset pipeline
 Split dataset
 Build CNN
 Train model
 Add early stopping
 Save best checkpoint
 Evaluate test set
 Generate confusion matrix
 Achieve 89% Top-1 test accuracy
Phase 3: Canvas → CNN Inference Pipeline 🚧
 Convert React canvas drawing into an image
 Match training-time preprocessing
 Normalize drawing input
 Resize input to CNN dimensions
 Build inference-only preprocessing pipeline
 Load trained model for inference
 Run predictions on saved canvas images
 Return Top-1 and Top-5 predictions
 Test predictions on real drawings from the canvas
Phase 4: Real-Time AI Pictionary 🚧
 Build FastAPI inference endpoint
 Connect React frontend to backend
 Send canvas snapshots to backend
 Run predictions during drawing
 Add confidence scores
 Implement prediction updates as strokes are added
 Add confidence threshold
 Prevent premature AI guesses
 Track AI prediction timeline
 Implement human vs AI guessing race
 Add game timer
 Determine winner
 Add scoring system
Phase 5: Model + Game Intelligence
 Analyze real-time prediction failures
 Improve preprocessing
 Experiment with data augmentation
 Reduce cat/dog confusion
 Improve difficult classes
 Compare model architectures
 Evaluate accuracy on partial drawings
 Measure AI guess time
 Measure human guess time
Phase 6: Final Product
 Improve UI/UX
 Add game rounds
 Add scoreboards
 Add visual AI prediction feedback
 Deploy backend
 Deploy frontend
 Add project demo
 Document experiments
 Add technical architecture documentation
🎯 Project Goal

The ultimate goal is to build an interactive computer vision system that doesn't just classify completed drawings.

It should understand a drawing as it is being created.

Can an AI recognize what you're drawing before your friends can?

🧰 Tech Stack
Frontend
React
TypeScript
HTML Canvas
Backend
Python
FastAPI
PyTorch
Machine Learning
Convolutional Neural Network
Google Quick, Draw! Dataset
NumPy
scikit-learn
Matplotlib
Seaborn
Development
Git
GitHub
Python Virtual Environment
📌 Current Milestone

Phase 1 + Phase 2 Complete

The project currently has:

A functional drawing engine
A 20-class QuickDraw dataset
A trained CNN
89% Top-1 test accuracy
97.75% Top-5 test accuracy
Early stopping
Model checkpointing
Classification evaluation
Confusion matrix analysis

The next milestone is connecting the trained computer vision model to the live React drawing canvas.
