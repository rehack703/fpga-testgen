"""Data models for the pipeline."""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class VerilogPort:
    direction: str  # "input" | "output" | "inout"
    name: str
    width: int = 1  # 1 for scalar, N for [N-1:0]

    def __str__(self) -> str:
        w = f"[{self.width - 1}:0] " if self.width > 1 else ""
        return f"{self.direction} {w}{self.name}"


@dataclass
class VerilogModule:
    name: str
    ports: list[VerilogPort]
    parameters: list[str]
    raw_source: str


@dataclass
class SimResult:
    success: bool
    stdout: str
    stderr: str
    vcd_path: Path | None = None
    errors: list[str] = field(default_factory=list)


@dataclass
class CoverageReport:
    toggle_coverage: dict[str, float]
    overall_toggle: float
    fsm_coverage: dict | None = None
    total_score: float = 0.0


@dataclass
class PipelineResult:
    module: VerilogModule
    testbench: str
    description: str
    sim_result: SimResult
    coverage: CoverageReport | None
    attempts: int
