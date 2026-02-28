export interface PortInfo {
  direction: string;
  name: string;
  width: number;
}

export interface ModuleInfo {
  name: string;
  ports: PortInfo[];
  parameters: string[];
}

export interface CoverageInfo {
  toggle_coverage: Record<string, number>;
  overall_toggle: number;
  fsm_coverage: {
    declared_states: number[];
    visited_states: number[];
    coverage_pct: number;
  } | null;
  total_score: number;
}

export interface GenerateResponse {
  testbench: string;
  description: string;
  module: ModuleInfo;
  sim_success: boolean;
  sim_output: string;
  sim_errors: string[];
  coverage: CoverageInfo | null;
  attempts: number;
}

export interface HealthResponse {
  status: string;
  iverilog: boolean;
  verilator: boolean;
  gemini_configured: boolean;
}

export type PipelineStage = "idle" | "parsing" | "generating" | "simulating" | "analyzing" | "done" | "error";
