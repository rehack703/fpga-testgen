"""VCD-based coverage analysis."""

from __future__ import annotations
import re
from pathlib import Path
from vcdvcd import VCDVCD
from .schemas import CoverageReport, VerilogModule


def _compute_toggle_coverage(vcd: VCDVCD) -> dict[str, float]:
    """Compute toggle coverage: percentage of bits that toggled 0→1 and 1→0."""
    toggle_cov = {}

    for signal_name in vcd.signals:
        # Skip clock and reset signals
        base = signal_name.split(".")[-1]
        if base in ("clk", "clock", "CLK", "rst", "rst_n", "reset"):
            continue

        tv = vcd[signal_name].tv
        if not tv or len(tv) < 2:
            toggle_cov[base] = 0.0
            continue

        # Check if signal toggled
        values = [v for _, v in tv]
        unique_values = set(values)

        if len(unique_values) <= 1:
            toggle_cov[base] = 0.0
        else:
            # For multi-bit signals, check how many unique values appeared
            # Normalize: 2+ unique values = 100% toggle for simplicity
            toggle_cov[base] = 100.0

    return toggle_cov


def _detect_fsm_coverage(
    vcd: VCDVCD, module: VerilogModule
) -> dict | None:
    """Detect FSM state register and compute state coverage."""
    # Find state-like parameters
    state_params = {}
    for param in module.parameters:
        name, _, val = param.partition("=")
        name = name.strip()
        val = val.strip()
        if name.upper() in ("IDLE", "INIT", "DONE", "WAIT", "READ", "WRITE",
                            "GREEN", "YELLOW", "RED", "S0", "S1", "S2", "S3",
                            "STATE_A", "STATE_B", "STATE_C"):
            state_params[name] = val

    if not state_params:
        return None

    # Find state signal in VCD
    state_signal = None
    for sig in vcd.signals:
        base = sig.split(".")[-1]
        if base in ("state", "current_state", "cs", "fsm_state"):
            state_signal = sig
            break

    if not state_signal:
        return None

    tv = vcd[state_signal].tv
    visited_values = set()
    for _, val in tv:
        try:
            visited_values.add(int(val, 2))
        except ValueError:
            visited_values.add(val)

    declared_values = set()
    for val in state_params.values():
        # Parse binary: 2'b00 → 0
        m = re.match(r"\d+'b([01]+)", val)
        if m:
            declared_values.add(int(m.group(1), 2))
        else:
            try:
                declared_values.add(int(val))
            except ValueError:
                pass

    if not declared_values:
        return None

    covered = visited_values & declared_values
    pct = (len(covered) / len(declared_values)) * 100 if declared_values else 0

    return {
        "declared_states": sorted(declared_values),
        "visited_states": sorted(covered),
        "coverage_pct": round(pct, 1),
    }


def analyze_coverage(
    vcd_path: Path, module: VerilogModule
) -> CoverageReport:
    """Analyze VCD file for coverage metrics."""
    vcd = VCDVCD(str(vcd_path))

    toggle = _compute_toggle_coverage(vcd)
    overall = sum(toggle.values()) / len(toggle) if toggle else 0.0
    fsm = _detect_fsm_coverage(vcd, module)

    # Total score: weighted average
    scores = [overall]
    if fsm:
        scores.append(fsm["coverage_pct"])
    total = sum(scores) / len(scores)

    return CoverageReport(
        toggle_coverage=toggle,
        overall_toggle=round(overall, 1),
        fsm_coverage=fsm,
        total_score=round(total, 1),
    )
