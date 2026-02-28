"""Pipeline orchestrator: parse → generate → simulate → coverage."""

from __future__ import annotations
from pathlib import Path
from .config import settings
from .parser import parse_verilog
from .generator import generate_testbench
from .simulator import simulate
from .coverage import analyze_coverage
from .schemas import PipelineResult, VerilogModule


def run_pipeline(
    rtl_source: str,
    module_name: str | None = None,
    simulator: str | None = None,
    max_retries: int | None = None,
) -> PipelineResult:
    """Run the full testbench generation pipeline.

    1. Parse RTL to extract module interface
    2. Generate testbench via Gemini API
    3. Simulate with iverilog/verilator
    4. Analyze coverage from VCD
    5. On failure, feed errors back to LLM and retry (up to max_retries)
    """
    retries = max_retries if max_retries is not None else settings.max_retries

    # Stage 1: Parse
    module = parse_verilog(rtl_source)

    errors: list[str] = []
    previous_tb: str | None = None
    testbench = ""
    description = ""
    sim_result = None

    for attempt in range(retries + 1):
        # Stage 2: Generate testbench
        testbench, description = generate_testbench(
            module,
            previous_errors=errors if errors else None,
            previous_tb=previous_tb,
        )

        # Stage 3: Simulate
        sim_result = simulate(module.raw_source, testbench, simulator)

        if sim_result.success:
            # Stage 4: Coverage
            coverage = None
            if sim_result.vcd_path and sim_result.vcd_path.exists():
                try:
                    coverage = analyze_coverage(sim_result.vcd_path, module)
                except Exception:
                    pass  # Coverage analysis is best-effort

            return PipelineResult(
                module=module,
                testbench=testbench,
                description=description,
                sim_result=sim_result,
                coverage=coverage,
                attempts=attempt + 1,
            )

        # Prepare feedback for retry
        errors = sim_result.errors
        previous_tb = testbench

    # All retries exhausted
    return PipelineResult(
        module=module,
        testbench=testbench,
        description=description,
        sim_result=sim_result,
        coverage=None,
        attempts=retries + 1,
    )
