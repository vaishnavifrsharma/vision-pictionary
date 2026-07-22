import React, { useEffect, useRef, useState } from "react";

type Point = {
  x: number;
  y: number;
};

type Stroke = {
  points: Point[];
  width: number;
};

type Prediction = {
  class: string;
  confidence: number;
};

export default function DrawingCanvas() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const isDrawing = useRef(false);
  const lastPos = useRef<Point | null>(null);
  const strokes = useRef<Stroke[]>([]);

  const [brushSize, setBrushSize] = useState(4);
  const brushSizeRef = useRef(4);

  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [isPredicting, setIsPredicting] = useState(false);

  const initializeCanvas = (
    ctx: CanvasRenderingContext2D,
    canvas: HTMLCanvasElement
  ) => {
    ctx.clearRect(
      0,
      0,
      canvas.width,
      canvas.height
    );

    ctx.fillStyle = "white";

    ctx.fillRect(
      0,
      0,
      canvas.width,
      canvas.height
    );

    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.strokeStyle = "black";
  };

  const drawLine = (
    ctx: CanvasRenderingContext2D,
    from: Point,
    to: Point
  ) => {
    ctx.beginPath();

    ctx.moveTo(
      from.x,
      from.y
    );

    ctx.lineTo(
      to.x,
      to.y
    );

    ctx.stroke();
  };

  const drawStroke = (
    stroke: Stroke
  ) => {
    if (
      stroke.points.length < 2
    ) {
      return;
    }

    const canvas =
      canvasRef.current;

    if (!canvas) {
      return;
    }

    const ctx =
      canvas.getContext("2d");

    if (!ctx) {
      return;
    }

    ctx.lineWidth =
      stroke.width;

    ctx.beginPath();

    ctx.moveTo(
      stroke.points[0].x,
      stroke.points[0].y
    );

    for (
      let i = 1;
      i < stroke.points.length;
      i += 1
    ) {
      ctx.lineTo(
        stroke.points[i].x,
        stroke.points[i].y
      );
    }

    ctx.stroke();
  };

  const redrawCanvas = () => {
    const canvas =
      canvasRef.current;

    if (!canvas) {
      return;
    }

    const ctx =
      canvas.getContext("2d");

    if (!ctx) {
      return;
    }

    initializeCanvas(
      ctx,
      canvas
    );

    strokes.current.forEach(
      drawStroke
    );
  };

  const sleep = (
    ms: number
  ) =>
    new Promise(
      (resolve) =>
        setTimeout(
          resolve,
          ms
        )
    );

  const undo = () => {
    if (
      strokes.current.length === 0
    ) {
      return;
    }

    strokes.current.pop();

    redrawCanvas();

    setPredictions([]);
  };

  const clearCanvas = () => {
    strokes.current = [];

    const canvas =
      canvasRef.current;

    if (!canvas) {
      return;
    }

    const ctx =
      canvas.getContext("2d");

    if (!ctx) {
      return;
    }

    initializeCanvas(
      ctx,
      canvas
    );

    setPredictions([]);
  };

  const replayCanvas = async () => {
    const canvas =
      canvasRef.current;

    if (!canvas) {
      return;
    }

    const ctx =
      canvas.getContext("2d");

    if (!ctx) {
      return;
    }

    initializeCanvas(
      ctx,
      canvas
    );

    for (
      const stroke of strokes.current
    ) {
      if (
        stroke.points.length < 2
      ) {
        continue;
      }

      ctx.lineWidth =
        stroke.width;

      ctx.beginPath();

      ctx.moveTo(
        stroke.points[0].x,
        stroke.points[0].y
      );

      for (
        let i = 1;
        i < stroke.points.length;
        i += 1
      ) {
        ctx.lineTo(
          stroke.points[i].x,
          stroke.points[i].y
        );

        ctx.stroke();

        await sleep(8);
      }
    }
  };

  const getPos = (
    clientX: number,
    clientY: number
  ): Point => {
    const canvas =
      canvasRef.current!;

    const rect =
      canvas.getBoundingClientRect();

    return {
      x:
        clientX -
        rect.left,

      y:
        clientY -
        rect.top,
    };
  };

  const startDrawing = (
    e: MouseEvent
  ) => {
    const pos =
      getPos(
        e.clientX,
        e.clientY
      );

    isDrawing.current =
      true;

    lastPos.current =
      pos;

    strokes.current.push({
      points: [pos],
      width:
        brushSizeRef.current,
    });
  };

  const draw = (
    e: MouseEvent
  ) => {
    if (
      !isDrawing.current ||
      !lastPos.current
    ) {
      return;
    }

    const canvas =
      canvasRef.current;

    if (!canvas) {
      return;
    }

    const ctx =
      canvas.getContext("2d");

    if (!ctx) {
      return;
    }

    const pos =
      getPos(
        e.clientX,
        e.clientY
      );

    ctx.lineWidth =
      brushSizeRef.current;

    drawLine(
      ctx,
      lastPos.current,
      pos
    );

    lastPos.current =
      pos;

    strokes.current[
      strokes.current.length - 1
    ].points.push(pos);
  };

  const stopDrawing = () => {
    isDrawing.current =
      false;

    lastPos.current =
      null;
  };

  const touchStart = (
    e: TouchEvent
  ) => {
    const t =
      e.touches[0];

    if (!t) {
      return;
    }

    const pos =
      getPos(
        t.clientX,
        t.clientY
      );

    isDrawing.current =
      true;

    lastPos.current =
      pos;

    strokes.current.push({
      points: [pos],
      width:
        brushSizeRef.current,
    });
  };

  const touchMove = (
    e: TouchEvent
  ) => {
    const t =
      e.touches[0];

    if (
      !t ||
      !isDrawing.current ||
      !lastPos.current
    ) {
      return;
    }

    const canvas =
      canvasRef.current;

    if (!canvas) {
      return;
    }

    const ctx =
      canvas.getContext("2d");

    if (!ctx) {
      return;
    }

    const pos =
      getPos(
        t.clientX,
        t.clientY
      );

    ctx.lineWidth =
      brushSizeRef.current;

    drawLine(
      ctx,
      lastPos.current,
      pos
    );

    lastPos.current =
      pos;

    strokes.current[
      strokes.current.length - 1
    ].points.push(pos);

    e.preventDefault();
  };

  const touchEnd = () => {
    stopDrawing();
  };

  const predictDrawing = async () => {
    const canvas =
      canvasRef.current;

    if (!canvas) {
      return;
    }

    if (
      strokes.current.length === 0
    ) {
      return;
    }

    setIsPredicting(true);

    try {
      const blob =
        await new Promise<Blob | null>(
          (resolve) => {
            canvas.toBlob(
              resolve,
              "image/png"
            );
          }
        );

      if (!blob) {
        throw new Error(
          "Could not create canvas image"
        );
      }

      const formData =
        new FormData();

      formData.append(
        "file",
        blob,
        "drawing.png"
      );

      const response =
        await fetch(
          "http://127.0.0.1:8000/predict",
          {
            method: "POST",
            body: formData,
          }
        );

      if (!response.ok) {
        throw new Error(
          `Prediction failed: ${response.status}`
        );
      }

      const data =
        await response.json();

      setPredictions(
        data.predictions
      );

    } catch (error) {
      console.error(
        "Prediction error:",
        error
      );

      setPredictions([]);

    } finally {
      setIsPredicting(false);
    }
  };

  useEffect(() => {
    brushSizeRef.current =
      brushSize;
  }, [brushSize]);

  useEffect(() => {
    const canvas =
      canvasRef.current;

    if (!canvas) {
      return;
    }

    const ctx =
      canvas.getContext("2d");

    if (!ctx) {
      return;
    }

    initializeCanvas(
      ctx,
      canvas
    );

    canvas.addEventListener(
      "mousedown",
      startDrawing
    );

    canvas.addEventListener(
      "mousemove",
      draw
    );

    canvas.addEventListener(
      "mouseup",
      stopDrawing
    );

    canvas.addEventListener(
      "mouseleave",
      stopDrawing
    );

    canvas.addEventListener(
      "touchstart",
      touchStart,
      { passive: false }
    );

    canvas.addEventListener(
      "touchmove",
      touchMove,
      { passive: false }
    );

    canvas.addEventListener(
      "touchend",
      touchEnd
    );

    canvas.addEventListener(
      "touchcancel",
      touchEnd
    );

    return () => {
      canvas.removeEventListener(
        "mousedown",
        startDrawing
      );

      canvas.removeEventListener(
        "mousemove",
        draw
      );

      canvas.removeEventListener(
        "mouseup",
        stopDrawing
      );

      canvas.removeEventListener(
        "mouseleave",
        stopDrawing
      );

      canvas.removeEventListener(
        "touchstart",
        touchStart
      );

      canvas.removeEventListener(
        "touchmove",
        touchMove
      );

      canvas.removeEventListener(
        "touchend",
        touchEnd
      );

      canvas.removeEventListener(
        "touchcancel",
        touchEnd
      );
    };
  }, []);

  const buttonStyle:
    React.CSSProperties = {
    padding:
      "10px 18px",

    fontSize: 16,

    borderRadius: 8,

    border: "none",

    cursor: "pointer",

    minWidth: 120,
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      <canvas
        ref={canvasRef}
        width={800}
        height={500}
        style={{
          border:
            "2px solid black",

          borderRadius: 12,

          touchAction: "none",

          backgroundColor:
            "white",

          cursor:
            "crosshair",
        }}
      />

      <div
        style={{
          display: "flex",
          justifyContent:
            "center",

          alignItems:
            "center",

          gap: 16,

          marginTop: 20,
        }}
      >
        <label>
          Brush Size
        </label>

        <input
          type="range"
          min={1}
          max={10}
          value={brushSize}
          onChange={(e) =>
            setBrushSize(
              Number(
                e.target.value
              )
            )
          }
        />

        <span>
          {brushSize}px
        </span>
      </div>

      <div
        style={{
          display: "flex",
          justifyContent:
            "center",

          gap: 12,

          marginTop: 16,

          flexWrap: "wrap",
        }}
      >
        <button
          onClick={undo}
          style={{
            ...buttonStyle,
            backgroundColor:
              "#007bff",
            color: "white",
          }}
        >
          Undo
        </button>

        <button
          onClick={clearCanvas}
          style={{
            ...buttonStyle,
            backgroundColor:
              "#dc3545",
            color: "white",
          }}
        >
          Clear
        </button>

        <button
          onClick={replayCanvas}
          style={{
            ...buttonStyle,
            backgroundColor:
              "#28ca4b",
            color: "white",
          }}
        >
          Replay
        </button>

        <button
          onClick={predictDrawing}
          disabled={isPredicting}
          style={{
            ...buttonStyle,
            backgroundColor:
              "#6f42c1",
            color: "white",
            opacity:
              isPredicting
                ? 0.7
                : 1,
          }}
        >
          {isPredicting
            ? "Predicting..."
            : "Predict"}
        </button>
      </div>

      {predictions.length > 0 && (
        <div
          style={{
            marginTop: 24,
            width: 400,
            maxWidth: "90%",
          }}
        >
          <h2
            style={{
              textAlign: "center",
              marginBottom: 16,
            }}
          >
            AI Predictions
          </h2>

          {predictions.map(
            (
              prediction,
              index
            ) => (
              <div
                key={
                  prediction.class
                }
                style={{
                  display: "flex",
                  justifyContent:
                    "space-between",
                  padding:
                    "10px 14px",
                  marginBottom: 8,
                  borderRadius: 8,
                  backgroundColor:
                    index === 0
                      ? "#e8dff5"
                      : "#f5f5f5",
                  fontWeight:
                    index === 0
                      ? "bold"
                      : "normal",
                }}
              >
                <span>
                  {index + 1}.{" "}
                  {prediction.class}
                </span>

                <span>
                  {
                    prediction.confidence
                  }%
                </span>
              </div>
            )
          )}
        </div>
      )}
    </div>
  );
}