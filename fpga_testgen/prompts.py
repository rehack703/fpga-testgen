"""Prompt templates for testbench generation."""

from __future__ import annotations
from .schemas import VerilogModule


SYSTEM_PROMPT = """\
You are an expert Verilog verification engineer.
Generate a self-checking Verilog-2001 testbench for the given module.

Requirements:
- Use `timescale 1ns/1ps
- Instantiate the DUT with all ports connected
- Generate clock if the module has a clock input
- Apply reset if the module has a reset input
- Include $dumpfile("dump.vcd") and $dumpvars(0, ...) for waveform capture
- Use if/else with $display for pass/fail checks (not SystemVerilog assert)
- Track pass_count and fail_count integers
- Print final summary: "PASS: N tests passed" or "FAIL: N tests failed"
- End simulation with $finish
- Include a timeout watchdog: $finish after 100000 time units

Output ONLY valid JSON with this exact format:
{"testbench": "<complete verilog testbench code>", "description": "<brief description of test strategy>"}
Do not include markdown formatting, code fences, or any text outside the JSON."""


def build_rtl_context(module: VerilogModule) -> str:
    ports_str = "\n".join(f"  {p}" for p in module.ports)
    params_str = ", ".join(module.parameters) if module.parameters else "None"
    return f"""\
[Module Info]
Name: {module.name}
Ports:
{ports_str}
Parameters: {params_str}

Full source:
{module.raw_source}"""


def build_test_strategy(module: VerilogModule) -> str:
    strategies = ["- Verify reset behavior (if reset signal exists)"]

    has_clk = any(p.name in ("clk", "clock", "CLK") for p in module.ports)
    has_rst = any("rst" in p.name.lower() or "reset" in p.name.lower() for p in module.ports)
    inputs = [p for p in module.ports if p.direction == "input" and p.name not in ("clk", "clock", "CLK")]
    if has_rst:
        inputs = [p for p in inputs if "rst" not in p.name.lower() and "reset" not in p.name.lower()]

    total_input_bits = sum(p.width for p in inputs)

    if total_input_bits <= 8:
        strategies.append("- Exhaustive test: enumerate all input combinations")
    else:
        strategies.append("- Boundary value testing for all inputs (0, max, mid)")
        strategies.append("- Random input sampling (at least 20 random vectors)")

    # FSM detection
    state_params = [p for p in module.parameters if p.split("=")[0] in
                    ("IDLE", "STATE", "S0", "S1", "S2", "S3", "GREEN", "RED", "YELLOW",
                     "INIT", "DONE", "WAIT", "READ", "WRITE")]
    if state_params:
        strategies.append("- FSM: attempt to visit all declared states")
        strategies.append(f"  States: {', '.join(p.split('=')[0] for p in state_params)}")

    if has_clk:
        strategies.append("- Test sequential behavior over multiple clock cycles")
    else:
        strategies.append("- Test combinational logic with various input patterns")

    strategies.append("- Verify all outputs produce expected values")
    return "\n".join(strategies)


def build_prompt(module: VerilogModule) -> str:
    return f"{build_rtl_context(module)}\n\n[Test Strategy]\n{build_test_strategy(module)}"


def build_feedback_prompt(module: VerilogModule, previous_tb: str, errors: list[str]) -> str:
    error_text = "\n".join(errors)
    return f"""{build_rtl_context(module)}

[Previous Testbench That Failed]
{previous_tb}

[Errors]
{error_text}

Fix all errors and regenerate a complete, working testbench.
Do not repeat the same mistakes."""
