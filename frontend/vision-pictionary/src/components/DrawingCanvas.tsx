import React, { useEffect, useRef, useState } from "react";

export default function DrawingCanvas() {
  type Point = { x: number; y: number };
  type Stroke = { points: Point[]; width: number };

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const isDrawing = useRef(false);
  const lastPos = useRef<Point | null>(null);
  const strokes = useRef<Stroke[]>([]);
  const [brushSize, setBrushSize] = useState(8);
  const brushSizeRef = useRef(8);

  const initializeCanvas = (ctx: CanvasRenderingContext2D, canvas: HTMLCanvasElement) => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.strokeStyle = "black";
  };

  const drawLine = (ctx: CanvasRenderingContext2D, from: Point, to: Point) => {
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

  const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

  const undo = () => {
    if (strokes.current.length === 0) return;
    strokes.current.pop();
    redrawCanvas();
  };

  const clearCanvas = () => {
    strokes.current = [];
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    initializeCanvas(ctx, canvas);
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
    return { x: clientX - rect.left, y: clientY - rect.top };
  };

  const startDrawing = (e: MouseEvent) => {
    const pos = getPos(e.clientX, e.clientY);
    isDrawing.current = true;
    lastPos.current = pos;
    strokes.current.push({ points: [pos], width: brushSizeRef.current });
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
    strokes.current.push({ points: [pos], width: brushSizeRef.current });
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

  const touchEnd = () => stopDrawing();

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

  const buttonStyle: React.CSSProperties = {
    padding: "10px 18px",
    fontSize: 16,
    borderRadius: 8,
    border: "none",
    cursor: "pointer",
    minWidth: 120,
  };

  return (
    <>
      <canvas
        ref={canvasRef}
        width={800}
        height={500}
        style={{
          border: "2px solid black",
          borderRadius: 12,
          touchAction: "none",
          backgroundColor: "white",
          cursor: "crosshair",
        }}
      />

      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          gap: 16,
          marginTop: 20,
        }}
      >
        <label>Brush Size</label>
        <input
          type="range"
          min={2}
          max={30}
          value={brushSize}
          onChange={(e) => setBrushSize(Number(e.target.value))}
        />
        <span>{brushSize}px</span>
      </div>

      <div style={{ display: "flex", justifyContent: "center", gap: 12, marginTop: 16 }}>
        <button onClick={undo} style={{ ...buttonStyle, backgroundColor: "#007bff", color: "white" }}>
          Undo
        </button>
        <button onClick={clearCanvas} style={{ ...buttonStyle, backgroundColor: "#dc3545", color: "white" }}>
          Clear
        </button>
        <button onClick={replayCanvas} style={{ ...buttonStyle, backgroundColor: "#28ca4b", color: "white" }}>
          Replay
        </button>
      </div>
    </>
  );
}
