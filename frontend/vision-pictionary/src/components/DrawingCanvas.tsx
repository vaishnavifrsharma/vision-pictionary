import { useEffect, useRef } from "react";

export default function DrawingCanvas() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;

    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    if (!ctx) return;

    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.lineWidth = 8;
    ctx.strokeStyle = "black";
  }, []);

  return (
    <canvas
      ref={canvasRef}
      width={800}
      height={500}
      style={{
        border: "2px solid black",
        borderRadius: "12px",
      }}
    />
  );
}