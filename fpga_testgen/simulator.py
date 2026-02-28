"""HDL simulator runner (iverilog / verilator)."""

from __future__ import annotations
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from .config import settings
from .schemas import SimResult


def _parse_errors(stderr: str) -> list[str]:
    errors = []
    for line in stderr.splitlines():
        line = line.strip()
        if line and ("error" in line.lower() or "Error" in line):
            errors.append(line)
    return errors


def _check_test_results(stdout: str) -> list[str]:
    """Check for FAIL messages in simulation output."""
    errors = []
    for line in stdout.splitlines():
        if "FAIL" in line.upper() and "fail_count" not in line:
            errors.append(line.strip())
    return errors


def simulate(
    design_source: str,
    testbench_source: str,
    simulator: str | None = None,
) -> SimResult:
    """Run simulation and return results."""
    sim = simulator or settings.default_simulator

    if sim == "iverilog":
        return _run_iverilog(design_source, testbench_source)
    elif sim == "verilator":
        return _run_verilator(design_source, testbench_source)
    else:
        raise ValueError(f"Unknown simulator: {sim}")


def _run_iverilog(design_source: str, testbench_source: str) -> SimResult:
    if not shutil.which("iverilog"):
        return SimResult(
            success=False, stdout="", stderr="",
            errors=["iverilog not found. Install with: sudo dnf install iverilog"],
        )

    tmpdir = Path(tempfile.mkdtemp(prefix="fpga_testgen_"))
    design_file = tmpdir / "design.v"
    tb_file = tmpdir / "tb.v"
    out_file = tmpdir / "out.vvp"
    vcd_file = tmpdir / "dump.vcd"

    design_file.write_text(design_source)
    tb_file.write_text(testbench_source)

    # Compile
    compile_result = subprocess.run(
        ["iverilog", "-o", str(out_file), str(design_file), str(tb_file)],
        capture_output=True, text=True, timeout=settings.sim_timeout,
        cwd=str(tmpdir),
    )

    if compile_result.returncode != 0:
        errors = _parse_errors(compile_result.stderr)
        if not errors:
            errors = [compile_result.stderr.strip()]
        return SimResult(
            success=False,
            stdout=compile_result.stdout,
            stderr=compile_result.stderr,
            errors=errors,
        )

    # Run simulation
    try:
        sim_result = subprocess.run(
            ["vvp", str(out_file)],
            capture_output=True, text=True, timeout=settings.sim_timeout,
            cwd=str(tmpdir),
        )
    except subprocess.TimeoutExpired:
        return SimResult(
            success=False, stdout="", stderr="",
            errors=["Simulation timed out (possible infinite loop)"],
        )

    test_errors = _check_test_results(sim_result.stdout)
    vcd_path = vcd_file if vcd_file.exists() else None

    return SimResult(
        success=sim_result.returncode == 0 and not test_errors,
        stdout=sim_result.stdout,
        stderr=sim_result.stderr,
        vcd_path=vcd_path,
        errors=test_errors or _parse_errors(sim_result.stderr),
    )


def _run_verilator(design_source: str, testbench_source: str) -> SimResult:
    if not shutil.which("verilator"):
        return SimResult(
            success=False, stdout="", stderr="",
            errors=["verilator not found. Install with: sudo dnf install verilator"],
        )

    tmpdir = Path(tempfile.mkdtemp(prefix="fpga_testgen_"))
    design_file = tmpdir / "design.v"
    tb_file = tmpdir / "tb.v"
    vcd_file = tmpdir / "dump.vcd"

    design_file.write_text(design_source)
    tb_file.write_text(testbench_source)

    # Compile with Verilator
    compile_result = subprocess.run(
        ["verilator", "--binary", "--trace", "-Wno-fatal",
         "-o", "sim", str(design_file), str(tb_file)],
        capture_output=True, text=True, timeout=settings.sim_timeout,
        cwd=str(tmpdir),
    )

    if compile_result.returncode != 0:
        errors = _parse_errors(compile_result.stderr)
        if not errors:
            errors = [compile_result.stderr.strip()]
        return SimResult(
            success=False,
            stdout=compile_result.stdout,
            stderr=compile_result.stderr,
            errors=errors,
        )

    # Find and run the binary
    sim_binary = tmpdir / "obj_dir" / "sim"
    if not sim_binary.exists():
        return SimResult(
            success=False, stdout="", stderr="",
            errors=["Verilator binary not found after compilation"],
        )

    try:
        sim_result = subprocess.run(
            [str(sim_binary)],
            capture_output=True, text=True, timeout=settings.sim_timeout,
            cwd=str(tmpdir),
        )
    except subprocess.TimeoutExpired:
        return SimResult(
            success=False, stdout="", stderr="",
            errors=["Simulation timed out (possible infinite loop)"],
        )

    test_errors = _check_test_results(sim_result.stdout)
    vcd_path = vcd_file if vcd_file.exists() else None

    return SimResult(
        success=sim_result.returncode == 0 and not test_errors,
        stdout=sim_result.stdout,
        stderr=sim_result.stderr,
        vcd_path=vcd_path,
        errors=test_errors or _parse_errors(sim_result.stderr),
    )
