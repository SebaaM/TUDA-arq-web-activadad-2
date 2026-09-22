import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "@source/App";
import "@source/index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
