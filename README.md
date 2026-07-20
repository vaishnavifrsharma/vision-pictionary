# 🎨 Vision Pictionary

An AI-powered Pictionary game built from scratch using React, TypeScript, and FastAPI. The goal is to create a real-time sketch recognition system where a computer vision model attempts to recognize a player's drawing as it is being sketched.

> **Current Status:** Canvas Engine Completed 🚧 AI Inference Coming Soon

---

## 📖 Overview

Vision Pictionary aims to combine computer vision with an interactive drawing experience. Instead of recognizing a completed image, the final application will perform continuous inference while the user is still drawing, creating a real-time AI Pictionary experience.

The project is currently focused on building a robust drawing engine that will serve as the foundation for the AI pipeline.

---

## ✨ Current Features

### Drawing Engine

- Freehand drawing canvas
- Mouse and touch support
- Stroke-based drawing storage
- Canvas redraw from stored strokes
- Undo functionality
- Clear canvas
- Replay drawing animation
- Adjustable brush size

---

## 🛠 Tech Stack

### Frontend

- React
- TypeScript
- Vite
- HTML5 Canvas API

### Backend *(Planned)*

- FastAPI
- PyTorch
- OpenCV

### Dataset *(Planned)*

- Google Quick, Draw!

---

## 📂 Project Structure

```
vision-pictionary/
│
├── frontend/
│   └── vision-pictionary/
│       ├── src/
│       │   ├── components/
│       │   │   └── DrawingCanvas.tsx
│       │   └── App.tsx
│       └── ...
│
├── requirements.txt
└── README.md
```

---

## 🚀 Running the Frontend

Clone the repository

```bash
git clone https://github.com/vaishnavifrsharma/vision-pictionary.git
```

Navigate to the frontend

```bash
cd frontend/vision-pictionary
```

Install dependencies

```bash
npm install
```

Start the development server

```bash
npm run dev
```

---

## 🗺 Roadmap

### ✅ Phase 1

- Project setup
- React + Vite
- Canvas rendering

### ✅ Phase 2

- Stroke storage
- Canvas redraw
- Undo
- Clear canvas
- Replay animation
- Brush size control

### 🚧 Phase 3

- Canvas export
- AI preprocessing pipeline
- FastAPI backend
- Sketch classification model
- Real-time prediction
- Confidence visualization
- Gameplay mechanics

---

## 📸 Preview

*(Screenshots and demo GIF will be added as development progresses.)*

---

## 🎯 Project Goal

The long-term vision is to build a real-time AI sketch recognition engine capable of:

- Recognizing drawings while they are still being drawn
- Displaying live prediction confidence
- Powering an interactive AI Pictionary game

---

## 📄 License

This project is licensed under the MIT License.