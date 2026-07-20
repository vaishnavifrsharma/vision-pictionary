import DrawingCanvas from "./components/DrawingCanvas";

function App() {
  return (
    <div
    style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
    }}
>
    <DrawingCanvas />
</div>
  );
}

export default App;