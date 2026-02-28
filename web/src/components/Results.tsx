import { useState } from "react";
import MonacoEditor from "@monaco-editor/react";
import type { GenerateResponse } from "../types";

type Tab = "testbench" | "simulation" | "coverage";

interface Props {
  result: GenerateResponse | null;
}

export function Results({ result }: Props) {
  const [tab, setTab] = useState<Tab>("testbench");

  if (!result) {
    return (
      <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center", color: "#484f58" }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>&#9881;</div>
          <div>Generate a testbench to see results</div>
        </div>
      </div>
    );
  }

  const tabs: { key: Tab; label: string }[] = [
    { key: "testbench", label: "Testbench" },
    { key: "simulation", label: "Simulation" },
    { key: "coverage", label: "Coverage" },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      {/* Tab bar */}
      <div style={{ display: "flex", background: "#161b22", borderBottom: "1px solid #30363d" }}>
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            style={{
              padding: "8px 16px", border: "none", cursor: "pointer", fontSize: 13,
              background: tab === t.key ? "#0d1117" : "transparent",
              color: tab === t.key ? "#c9d1d9" : "#8b949e",
              borderBottom: tab === t.key ? "2px solid #1f6feb" : "2px solid transparent",
            }}
          >
            {t.label}
          </button>
        ))}
        <div style={{ flex: 1 }} />
        <div style={{ padding: "8px 12px", fontSize: 12, color: "#8b949e" }}>
          {result.attempts} attempt{result.attempts > 1 ? "s" : ""} | {result.module.name}
        </div>
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflow: "auto" }}>
        {tab === "testbench" && (
          <div style={{ height: "100%" }}>
            <div style={{ padding: "8px 12px", fontSize: 12, color: "#8b949e", background: "#161b22" }}>
              {result.description}
            </div>
            <MonacoEditor
              height="calc(100% - 36px)"
              defaultLanguage="verilog"
              theme="vs-dark"
              value={result.testbench}
              options={{ readOnly: true, minimap: { enabled: false }, fontSize: 13, scrollBeyondLastLine: false }}
            />
          </div>
        )}

        {tab === "simulation" && (
          <div style={{ padding: 16 }}>
            <div style={{ marginBottom: 12 }}>
              <span style={{
                padding: "4px 8px", borderRadius: 4, fontSize: 12, fontWeight: 600,
                background: result.sim_success ? "#238636" : "#da3633", color: "#fff",
              }}>
                {result.sim_success ? "PASSED" : "FAILED"}
              </span>
            </div>
            {result.sim_errors.length > 0 && (
              <div style={{ marginBottom: 12 }}>
                <div style={{ fontWeight: 600, marginBottom: 4, color: "#f85149" }}>Errors:</div>
                {result.sim_errors.map((e, i) => (
                  <div key={i} style={{ fontFamily: "monospace", fontSize: 12, color: "#f85149", padding: "2px 0" }}>{e}</div>
                ))}
              </div>
            )}
            <pre style={{ fontFamily: "monospace", fontSize: 12, whiteSpace: "pre-wrap", background: "#161b22", padding: 12, borderRadius: 6, border: "1px solid #30363d", maxHeight: 400, overflow: "auto" }}>
              {result.sim_output || "(no output)"}
            </pre>
          </div>
        )}

        {tab === "coverage" && (
          <div style={{ padding: 16 }}>
            {result.coverage ? (
              <>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
                  <ScoreCard label="Total Score" value={result.coverage.total_score} />
                  <ScoreCard label="Toggle Coverage" value={result.coverage.overall_toggle} />
                </div>

                <h3 style={{ fontSize: 14, marginBottom: 8 }}>Signal Toggle Coverage</h3>
                <table style={{ width: "100%", fontSize: 12, borderCollapse: "collapse" }}>
                  <thead>
                    <tr style={{ borderBottom: "1px solid #30363d" }}>
                      <th style={{ textAlign: "left", padding: "6px 8px" }}>Signal</th>
                      <th style={{ textAlign: "left", padding: "6px 8px" }}>Coverage</th>
                      <th style={{ textAlign: "left", padding: "6px 8px", width: "50%" }}></th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(result.coverage.toggle_coverage).sort().map(([sig, cov]) => (
                      <tr key={sig} style={{ borderBottom: "1px solid #21262d" }}>
                        <td style={{ padding: "4px 8px", fontFamily: "monospace" }}>{sig}</td>
                        <td style={{ padding: "4px 8px" }}>{cov.toFixed(1)}%</td>
                        <td style={{ padding: "4px 8px" }}>
                          <div style={{ background: "#21262d", borderRadius: 4, height: 8, overflow: "hidden" }}>
                            <div style={{ width: `${cov}%`, height: "100%", background: cov >= 80 ? "#238636" : cov >= 50 ? "#d29922" : "#da3633", borderRadius: 4 }} />
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {result.coverage.fsm_coverage && (
                  <div style={{ marginTop: 16 }}>
                    <h3 style={{ fontSize: 14, marginBottom: 8 }}>FSM State Coverage</h3>
                    <div style={{ fontSize: 13 }}>
                      <div>Coverage: {result.coverage.fsm_coverage.coverage_pct}%</div>
                      <div>Declared states: [{result.coverage.fsm_coverage.declared_states.join(", ")}]</div>
                      <div>Visited states: [{result.coverage.fsm_coverage.visited_states.join(", ")}]</div>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div style={{ color: "#484f58", textAlign: "center", padding: 40 }}>
                No coverage data available
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function ScoreCard({ label, value }: { label: string; value: number }) {
  const color = value >= 80 ? "#3fb950" : value >= 50 ? "#d29922" : "#f85149";
  return (
    <div style={{ background: "#161b22", border: "1px solid #30363d", borderRadius: 8, padding: 16, textAlign: "center" }}>
      <div style={{ fontSize: 12, color: "#8b949e", marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 700, color }}>{value.toFixed(1)}%</div>
    </div>
  );
}
