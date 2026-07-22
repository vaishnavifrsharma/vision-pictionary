import { useEffect, useRef, useState } from "react";

type Point = {
  x: number;
  y: number;
};

type Stroke = {
  points: Point[];
  width: number;
};

type Prediction = {
  label: string;
  class?: string;
  confidence: number;
};

export default function DrawingCanvas() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const isDrawing = useRef(false);
  const lastPos = useRef<Point | null>(null);
  const strokes = useRef<Stroke[]>([]);

  const [brushSize, setBrushSize] = useState(6);
  const brushSizeRef = useRef(6);

  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [processedImage, setProcessedImage] = useState<string | null>(null);
  const [isPredicting, setIsPredicting] = useState(false);

  const initializeCanvas = (
    ctx: CanvasRenderingContext2D,
    canvas: HTMLCanvasElement
  ) => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#F7F4D5";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.strokeStyle = "#0A3323";
  };

  const drawLine = (
    ctx: CanvasRenderingContext2D,
    from: Point,
    to: Point
  ) => {
    ctx.beginPath();
    ctx.moveTo(from.x, from.y);
    ctx.lineTo(to.x, to.y);
    ctx.stroke();
  };

  const drawStroke = (stroke: Stroke) => {
    if (stroke.points.length < 2) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.lineWidth = stroke.width;
    ctx.beginPath();
    ctx.moveTo(stroke.points[0].x, stroke.points[0].y);
    for (let i = 1; i < stroke.points.length; i += 1) {
      ctx.lineTo(stroke.points[i].x, stroke.points[i].y);
    }
    ctx.stroke();
  };

  const redrawCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    initializeCanvas(ctx, canvas);
    strokes.current.forEach(drawStroke);
  };

  const sleep = (ms: number) =>
    new Promise((resolve) => setTimeout(resolve, ms));

  const undo = () => {
    if (strokes.current.length === 0) return;
    strokes.current.pop();
    redrawCanvas();
    setPredictions([]);
    setProcessedImage(null);
  };

  const clearCanvas = () => {
    strokes.current = [];
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    initializeCanvas(ctx, canvas);
    setPredictions([]);
    setProcessedImage(null);
  };

  const replayCanvas = async () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    initializeCanvas(ctx, canvas);

    for (const stroke of strokes.current) {
      if (stroke.points.length < 2) continue;
      ctx.lineWidth = stroke.width;
      ctx.beginPath();
      ctx.moveTo(stroke.points[0].x, stroke.points[0].y);
      for (let i = 1; i < stroke.points.length; i += 1) {
        ctx.lineTo(stroke.points[i].x, stroke.points[i].y);
        ctx.stroke();
        await sleep(8);
      }
    }
  };

  const getPos = (clientX: number, clientY: number): Point => {
    const canvas = canvasRef.current!;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    return {
      x: (clientX - rect.left) * scaleX,
      y: (clientY - rect.top) * scaleY,
    };
  };

  const startDrawing = (e: MouseEvent) => {
    const pos = getPos(e.clientX, e.clientY);
    isDrawing.current = true;
    lastPos.current = pos;
    strokes.current.push({
      points: [pos],
      width: brushSizeRef.current,
    });
  };

  const draw = (e: MouseEvent) => {
    if (!isDrawing.current || !lastPos.current) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const pos = getPos(e.clientX, e.clientY);
    ctx.lineWidth = brushSizeRef.current;
    drawLine(ctx, lastPos.current, pos);
    lastPos.current = pos;
    strokes.current[strokes.current.length - 1].points.push(pos);
  };

  const stopDrawing = () => {
    isDrawing.current = false;
    lastPos.current = null;
  };

  const touchStart = (e: TouchEvent) => {
    const t = e.touches[0];
    if (!t) return;
    const pos = getPos(t.clientX, t.clientY);
    isDrawing.current = true;
    lastPos.current = pos;
    strokes.current.push({
      points: [pos],
      width: brushSizeRef.current,
    });
  };

  const touchMove = (e: TouchEvent) => {
    const t = e.touches[0];
    if (!t || !isDrawing.current || !lastPos.current) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const pos = getPos(t.clientX, t.clientY);
    ctx.lineWidth = brushSizeRef.current;
    drawLine(ctx, lastPos.current, pos);
    lastPos.current = pos;
    strokes.current[strokes.current.length - 1].points.push(pos);
    e.preventDefault();
  };

  const touchEnd = () => {
    stopDrawing();
  };

  const predictDrawing = async () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    if (strokes.current.length === 0) return;

    setIsPredicting(true);

    try {
      const blob = await new Promise<Blob | null>((resolve) => {
        canvas.toBlob(resolve, "image/png");
      });

      if (!blob) {
        throw new Error("Could not create canvas image");
      }

      const formData = new FormData();
      formData.append("file", blob, "drawing.png");

      const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Prediction failed: ${response.status}`);
      }

      const data = await response.json();
      setPredictions(data.predictions || []);
      if (data.processed_image) {
        setProcessedImage(data.processed_image);
      }
    } catch (error) {
      console.error("Prediction error:", error);
      setPredictions([]);
      setProcessedImage(null);
    } finally {
      setIsPredicting(false);
    }
  };

  useEffect(() => {
    brushSizeRef.current = brushSize;
  }, [brushSize]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    initializeCanvas(ctx, canvas);

    canvas.addEventListener("mousedown", startDrawing);
    canvas.addEventListener("mousemove", draw);
    canvas.addEventListener("mouseup", stopDrawing);
    canvas.addEventListener("mouseleave", stopDrawing);

    canvas.addEventListener("touchstart", touchStart, { passive: false });
    canvas.addEventListener("touchmove", touchMove, { passive: false });
    canvas.addEventListener("touchend", touchEnd);
    canvas.addEventListener("touchcancel", touchEnd);

    return () => {
      canvas.removeEventListener("mousedown", startDrawing);
      canvas.removeEventListener("mousemove", draw);
      canvas.removeEventListener("mouseup", stopDrawing);
      canvas.removeEventListener("mouseleave", stopDrawing);

      canvas.removeEventListener("touchstart", touchStart);
      canvas.removeEventListener("touchmove", touchMove);
      canvas.removeEventListener("touchend", touchEnd);
      canvas.removeEventListener("touchcancel", touchEnd);
    };
  }, []);

  const topPrediction = predictions.length > 0 ? predictions[0] : null;
  const otherPredictions = predictions.slice(1);

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <h1 className="app-title">🎯 AI Pictionary Classifier</h1>
        <p className="app-subtitle">
          Draw a sketch on the canvas below and watch PyTorch CNN predict it in real-time
        </p>
      </header>

      {/* Main Drawing Canvas Card */}
      <div className="canvas-card">
        <canvas ref={canvasRef} width={800} height={500} />

        {/* Controls Bar */}
        <div className="controls-bar">
          <div className="brush-control">
            <label htmlFor="brush-size">Brush Size</label>
            <input
              id="brush-size"
              type="range"
              min={2}
              max={16}
              value={brushSize}
              onChange={(e) => setBrushSize(Number(e.target.value))}
            />
            <span className="brush-size-val">{brushSize}px</span>
          </div>

          <div className="action-buttons">
            <button className="btn btn-secondary" onClick={undo}>
              Undo
            </button>
            <button className="btn btn-danger" onClick={clearCanvas}>
              Clear
            </button>
            <button className="btn btn-emerald" onClick={replayCanvas}>
              Replay
            </button>

            {predictions.length > 0 ? (
              <button
                className="btn btn-emerald"
                onClick={() => {
                  clearCanvas();
                }}
              >
                Draw Again
              </button>
            ) : null}

            <button
              className="btn btn-primary"
              onClick={predictDrawing}
              disabled={isPredicting}
            >
              {isPredicting ? "Predicting..." : "Predict"}
            </button>
          </div>
        </div>

        {/* Loading State */}
        {isPredicting && (
          <div className="loading-container">
            <div className="spinner"></div>
            <span>⚡ Analyzing drawing with PyTorch CNN...</span>
          </div>
        )}
      </div>

      {/* Results Section */}
      {predictions.length > 0 && (
        <div className="results-wrapper">
          {/* Top Prediction & Runner-Ups Card */}
          <div className="prediction-card">
            <div className="prediction-header">
              <span>🎯 Prediction Results</span>
            </div>

            {/* Top Prediction Pick */}
            {topPrediction && (
              <div className="top-pick-box">
                <div className="top-pick-info">
                  <span className="top-pick-title">Top Match</span>
                  <span className="top-pick-label">
                    {topPrediction.label || topPrediction.class}
                  </span>
                </div>
                <span className="top-pick-score">
                  {topPrediction.confidence}%
                </span>
              </div>
            )}

            {/* Other Guesses */}
            {otherPredictions.length > 0 && (
              <div>
                <div className="other-guesses-title">Other guesses:</div>
                {otherPredictions.map((pred) => {
                  const labelName = pred.label || pred.class || "";
                  return (
                    <div key={labelName} className="prediction-item">
                      <span className="label">{labelName}</span>
                      <div className="bar">
                        <div
                          className="fill"
                          style={{ width: `${pred.confidence}%` }}
                        />
                      </div>
                      <span className="percent">{pred.confidence}%</span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Phase 4: Model Vision Pipeline Visualizer ("What The Model Sees") */}
          {processedImage && (
            <div className="pipeline-card">
              <div className="pipeline-title">
                🔍 Model Vision Pipeline (What The Model Sees)
              </div>
              <div className="pipeline-flow">
                <div className="pipeline-step">
                  <span className="pipeline-step-label">1. Your Canvas Sketch</span>
                  <span style={{ fontSize: "2rem" }}>🎨</span>
                </div>
                <div className="pipeline-arrow">↓</div>
                <div className="pipeline-step">
                  <span className="pipeline-step-label">2. Preprocessed Tensor (28×28)</span>
                  <img
                    src={processedImage}
                    alt="Preprocessed 28x28 grayscale tensor"
                    className="processed-preview"
                  />
                </div>
                <div className="pipeline-arrow">↓</div>
                <div className="pipeline-step">
                  <span className="pipeline-step-label">3. CNN Softmax Predictions</span>
                  <span style={{ fontSize: "2rem" }}>🤖</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}