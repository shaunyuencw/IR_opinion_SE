import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Home from "./components/Home";

function App() {
  return (
    <>
      <Router>
        <Routes>
          <Route path='/:id' element={<Home />}></Route>
          <Route path="/" element={<Navigate to="/tsla" replace />} />
        </Routes>
      </Router>
    </>
  );
}

export default App
