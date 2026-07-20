import React, { useEffect, useRef } from "react";

export default function DrawingCanvas() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const isDrawing = useRef(false);
  type Point = { x: number; y: number };
  const lastPos = useRef<Point | null>(null);
  type Stroke = Point[];
  const strokes = useRef<Stroke[]>([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // initialize
function initializeCanvas(
    ctx: CanvasRenderingContext2D,
    canvas: HTMLCanvasElement
) {
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.lineWidth = 8;
    ctx.strokeStyle = "black";
}
    initializeCanvas(ctx, canvas);

    const getPos = (clientX: number, clientY: number) => {
      const rect = canvas.getBoundingClientRect();
      return { x: clientX - rect.left, y: clientY - rect.top };
    };

    const startDrawing = (e: MouseEvent) => {
      isDrawing.current = true;
      lastPos.current = getPos(e.clientX, e.clientY);
      strokes.current.push([]);
      strokes.current[strokes.current.length - 1].push(
        lastPos.current
      );
    };

    const draw = (e: MouseEvent) => {
      if (!isDrawing.current || !lastPos.current) return;
      const pos = getPos(e.clientX, e.clientY);
      ctx.beginPath();
      ctx.moveTo(lastPos.current.x, lastPos.current.y);
      ctx.lineTo(pos.x, pos.y);
      ctx.stroke();
      lastPos.current = pos;
      strokes.current[
        strokes.current.length - 1
      ].push(pos);
    };

    const stopDrawing = () => {
      isDrawing.current = false;
      console.log(strokes.current);
      lastPos.current = null;
    };

    // mouse
    canvas.addEventListener("mousedown", startDrawing);
    canvas.addEventListener("mousemove", draw);
    canvas.addEventListener("mouseup", stopDrawing);
    canvas.addEventListener("mouseleave", stopDrawing);

    // touch (basic support)
    const touchStart = (e: TouchEvent) => {
      const t = e.touches[0];
      if (!t) return;
      isDrawing.current = true;
      lastPos.current = getPos(t.clientX, t.clientY);
    };

    const touchMove = (e: TouchEvent) => {
      const t = e.touches[0];
      if (!t || !isDrawing.current || !lastPos.current) return;
      const pos = getPos(t.clientX, t.clientY);
      ctx.beginPath();
      ctx.moveTo(lastPos.current.x, lastPos.current.y);
      ctx.lineTo(pos.x, pos.y);
      ctx.stroke();
      lastPos.current = pos;
      e.preventDefault();
    };

    const touchEnd = () => stopDrawing();

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

  return (
    <canvas
      ref={canvasRef}
      width={800}
      height={500}
      style={{
        border: "2px solid black",
        borderRadius: 12,
        touchAction: "none",
        backgroundColor:"white",
        cursor:"crosshair",
      }}
    />
  );
}