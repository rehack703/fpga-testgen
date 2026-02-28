import type { PipelineStage } from "../types";

const STAGES: { key: PipelineStage; label: string }[] = [
  { key: "parsing", label: "Parse RTL" },
  { key: "generating", label: "Generate TB" },
  { key: "simulating", label: "Simulate" },
  { key: "analyzing", label: "Coverage" },
];

interface Props {
  stage: PipelineStage;
  error: string | null;
}

export function Pipeline({ stage, error }: Props) {
  const stageIdx = STAGES.findIndex((s) => s.key === stage);

  return (
    <div style={{ padding: "12px 16px", background: "#161b22", borderBottom: "1px solid #30363d" }}>
      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        {STAGES.map((s, i) => {
          let bg = "#21262d";
          let color = "#484f58";
          if (stage === "done") {
            bg = "#238636";
            color = "#fff";
          } else if (stage === "error" && i <= stageIdx) {
            bg = i === stageIdx ? "#da3633" : "#238636";
            color = "#fff";
          } else if (i < stageIdx) {
            bg = "#238636";
            color = "#fff";
          } else if (i === stageIdx) {
            bg = "#1f6feb";
            color = "#fff";
          }
          return (
            <div key={s.key} style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div style={{ background: bg, color, padding: "4px 12px", borderRadius: 12, fontSize: 12, fontWeight: 500, transition: "all 0.3s" }}>
                {s.label}
              </div>
              {i < STAGES.length - 1 && (
                <div style={{ width: 24, height: 2, background: i < stageIdx || stage === "done" ? "#238636" : "#30363d" }} />
              )}
            </div>
          );
        })}
        {stage === "done" && <span style={{ marginLeft: 8, color: "#3fb950", fontSize: 13 }}>Complete</span>}
      </div>
      {error && <div style={{ marginTop: 8, color: "#f85149", fontSize: 13 }}>{error}</div>}
    </div>
  );
}
