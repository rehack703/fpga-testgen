import { useState, useEffect } from "react";
import { Editor } from "./components/Editor";
import { Pipeline } from "./components/Pipeline";
import { Results } from "./components/Results";
import { checkHealth, generateTestbench } from "./api";
import type { GenerateResponse, HealthResponse, PipelineStage } from "./types";

export function App() {
  const [rtl, setRtl] = useState("");
  const [stage, setStage] = useState<PipelineStage>("idle");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    checkHealth().then(setHealth).catch(() => {});
  }, []);

  const handleGenerate = async () => {
    if (!rtl.trim()) return;
    setError(null);
    setResult(null);
    setStage("generating");

    try {
      const res = await generateTestbench(rtl);
      setResult(res);
      setStage("done");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Unknown error");
      setStage("error");
    }
  };

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Header */}
      <header style={{ padding: "12px 20px", background: "#161b22", borderBottom: "1px solid #30363d", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ fontSize: 18, fontWeight: 700 }}>FPGA TestGen</span>
          <span style={{ fontSize: 12, color: "#8b949e" }}>LLM-based Testbench Generator</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          {health && (
            <div style={{ display: "flex", gap: 8, fontSize: 11 }}>
              <StatusDot ok={health.gemini_configured} label="Gemini" />
              <StatusDot ok={health.iverilog} label="iverilog" />
              <StatusDot ok={health.verilator} label="verilator" />
            </div>
          )}
          <button
            onClick={handleGenerate}
            disabled={stage === "generating" || !rtl.trim()}
            style={{
              background: stage === "generating" ? "#21262d" : "#238636",
              color: "#fff", border: "none", padding: "8px 20px", borderRadius: 6,
              cursor: stage === "generating" ? "wait" : "pointer",
              fontWeight: 600, fontSize: 14,
            }}
          >
            {stage === "generating" ? "Generating..." : "Generate Testbench"}
          </button>
        </div>
      </header>

      {/* Pipeline status */}
      {stage !== "idle" && <Pipeline stage={stage} error={error} />}

      {/* Main content */}
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        <div style={{ width: "50%", borderRight: "1px solid #30363d" }}>
          <Editor value={rtl} onChange={setRtl} />
        </div>
        <div style={{ width: "50%" }}>
          <Results result={result} />
        </div>
      </div>
    </div>
  );
}

function StatusDot({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
      <span style={{ width: 6, height: 6, borderRadius: "50%", background: ok ? "#3fb950" : "#484f58" }} />
      <span style={{ color: ok ? "#8b949e" : "#484f58" }}>{label}</span>
    </span>
  );
}
