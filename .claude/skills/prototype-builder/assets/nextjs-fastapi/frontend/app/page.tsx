"use client";

import { useEffect, useState } from "react";

export default function Home() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
    fetch("http://localhost:8000/api/hello")
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch(() => setMessage("Hello World (API not connected)"));
  }, []);

  return (
    <main style={{ padding: "2rem", fontFamily: "system-ui" }}>
      <h1>Prototype Ready!</h1>
      <p>{message}</p>
      <p style={{ color: "#666", marginTop: "1rem" }}>
        Frontend: http://localhost:3000 | Backend: http://localhost:8000
      </p>
    </main>
  );
}
