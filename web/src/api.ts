import type { GenerateResponse, HealthResponse } from "./types";

const BASE = "/api";

export async function checkHealth(): Promise<HealthResponse> {
  const res = await fetch(`${BASE}/health`);
  return res.json();
}

export async function generateTestbench(rtl: string): Promise<GenerateResponse> {
  const res = await fetch(`${BASE}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rtl, max_retries: 3 }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Generation failed");
  }
  return res.json();
}
