import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClientProvider } from "@tanstack/react-query";

import { App } from "./App";
import { createWorkspaceQueryClient } from "./query-client";
import "../index.css";

const container = document.getElementById("root");
const queryClient = createWorkspaceQueryClient();

if (container === null) {
  throw new Error("Root container #root was not found.");
}

createRoot(container).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>
);
