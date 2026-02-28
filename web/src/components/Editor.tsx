import { useRef } from "react";
import MonacoEditor from "@monaco-editor/react";

const SAMPLE = `module counter #(
    parameter WIDTH = 8
)(
    input wire clk,
    input wire rst_n,
    input wire enable,
    output reg [WIDTH-1:0] count,
    output wire overflow
);

assign overflow = (count == {WIDTH{1'b1}});

always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        count <= {WIDTH{1'b0}};
    else if (enable)
        count <= count + 1'b1;
end

endmodule`;

interface Props {
  value: string;
  onChange: (v: string) => void;
}

export function Editor({ value, onChange }: Props) {
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    file.text().then((text) => onChange(text));
    e.target.value = "";
  };

  const btnStyle = { background: "#21262d", border: "1px solid #30363d", color: "#8b949e", padding: "4px 12px", borderRadius: 6, cursor: "pointer", fontSize: 12 } as const;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div style={{ padding: "8px 12px", background: "#161b22", borderBottom: "1px solid #30363d", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontWeight: 600, fontSize: 14 }}>RTL Source (Verilog)</span>
        <div style={{ display: "flex", gap: 6 }}>
          <input ref={fileRef} type="file" accept=".v,.sv,.vhd,.vhdl" onChange={handleFile} hidden />
          <button onClick={() => fileRef.current?.click()} style={btnStyle}>
            Open File
          </button>
          <button onClick={() => onChange(SAMPLE)} style={btnStyle}>
            Load Sample
          </button>
        </div>
      </div>
      <div style={{ flex: 1 }}>
        <MonacoEditor
          height="100%"
          defaultLanguage="verilog"
          theme="vs-dark"
          value={value}
          onChange={(v) => onChange(v || "")}
          options={{ minimap: { enabled: false }, fontSize: 13, lineNumbers: "on", scrollBeyondLastLine: false }}
        />
      </div>
    </div>
  );
}
