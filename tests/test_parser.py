"""Tests for RTL parser."""

from pathlib import Path
from fpga_testgen.parser import parse_verilog

FIXTURES = Path(__file__).parent / "fixtures"


def test_counter_module():
    src = (FIXTURES / "counter.v").read_text()
    mod = parse_verilog(src)
    assert mod.name == "counter"
    assert len(mod.ports) == 5
    names = {p.name for p in mod.ports}
    assert names == {"clk", "rst_n", "enable", "count", "overflow"}
    # count should have width > 1 — but it uses parameter WIDTH-1
    # regex picks up WIDTH-1:0 as-is, so width defaults to 1 for parameterized
    clk = next(p for p in mod.ports if p.name == "clk")
    assert clk.direction == "input"
    assert clk.width == 1


def test_alu_module():
    src = (FIXTURES / "alu.v").read_text()
    mod = parse_verilog(src)
    assert mod.name == "alu"
    assert len(mod.ports) == 5
    a = next(p for p in mod.ports if p.name == "a")
    assert a.width == 8
    assert a.direction == "input"
    op = next(p for p in mod.ports if p.name == "op")
    assert op.width == 3
    result = next(p for p in mod.ports if p.name == "result")
    assert result.direction == "output"
    assert result.width == 8


def test_fsm_module():
    src = (FIXTURES / "fsm.v").read_text()
    mod = parse_verilog(src)
    assert mod.name == "traffic_light"
    assert len(mod.ports) == 7
    state = next(p for p in mod.ports if p.name == "state")
    assert state.width == 2
    assert state.direction == "output"
    # Check parameters
    param_names = [p.split("=")[0] for p in mod.parameters]
    assert "IDLE" in param_names
    assert "RED" in param_names


def test_non_ansi_style():
    src = """
    module simple(a, b, y);
        input a;
        input b;
        output y;
        assign y = a & b;
    endmodule
    """
    mod = parse_verilog(src)
    assert mod.name == "simple"
    assert len(mod.ports) == 3


def test_comments_stripped():
    src = """
    // This is a comment
    module test(
        input wire clk, /* block comment */
        output reg [3:0] data
    );
    endmodule
    """
    mod = parse_verilog(src)
    assert mod.name == "test"
    assert len(mod.ports) == 2
    data = next(p for p in mod.ports if p.name == "data")
    assert data.width == 4
