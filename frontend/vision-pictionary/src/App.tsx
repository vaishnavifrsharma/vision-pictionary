import DrawingCanvas from "./components/DrawingCanvas";

function App() {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        marginTop: "40px",
      }}
    >
      <DrawingCanvas />
    </div>
  );
}

export default App;