"""Verilog RTL parser — regex-based module interface extraction."""

from __future__ import annotations
import re
from .schemas import VerilogModule, VerilogPort


def _strip_comments(source: str) -> str:
    source = re.sub(r"//.*$", "", source, flags=re.MULTILINE)
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    return source


def _parse_width(width_str: str | None) -> int:
    if not width_str:
        return 1
    m = re.match(r"\[(\d+):(\d+)\]", width_str.strip())
    if m:
        return abs(int(m.group(1)) - int(m.group(2))) + 1
    return 1


def _parse_ansi_ports(header: str) -> list[VerilogPort]:
    """Parse ANSI-style ports from module header."""
    ports = []
    pattern = re.compile(
        r"(input|output|inout)\s+(?:(?:wire|reg)\s+)?"
        r"(?:signed\s+)?"
        r"(\[[^\]]+\])?\s*"
        r"(\w+)"
    )
    for m in pattern.finditer(header):
        name = m.group(3)
        if name in ("wire", "reg", "signed"):
            continue
        ports.append(VerilogPort(
            direction=m.group(1),
            name=name,
            width=_parse_width(m.group(2)),
        ))
    return ports


def _parse_body_ports(body: str) -> list[VerilogPort]:
    """Parse non-ANSI-style port declarations from module body."""
    ports = []
    pattern = re.compile(
        r"(input|output|inout)\s+(?:(?:wire|reg)\s+)?"
        r"(?:signed\s+)?"
        r"(\[\d+:\d+\])?\s*"
        r"([^;]+);"
    )
    for m in pattern.finditer(body):
        direction = m.group(1)
        width = _parse_width(m.group(2))
        names = [n.strip() for n in m.group(3).split(",") if n.strip()]
        for name in names:
            clean = re.match(r"(\w+)", name)
            if clean:
                ports.append(VerilogPort(direction=direction, name=clean.group(1), width=width))
    return ports


def _parse_parameters(source: str) -> list[str]:
    params = []
    seen = set()
    # All parameter declarations (both header and body)
    for m in re.finditer(r"\bparameter\s+(?:\[[^\]]+\]\s*)?(\w+)\s*=\s*([^;,\)]+)", source):
        name = m.group(1)
        if name not in seen:
            seen.add(name)
            params.append(f"{name}={m.group(2).strip()}")
    return params


def parse_verilog(source: str) -> VerilogModule:
    """Parse a Verilog source file and extract module interface."""
    clean = _strip_comments(source)

    # Find module declaration
    mod_match = re.search(
        r"module\s+(\w+)\s*(?:#\s*\(.*?\))?\s*\((.*?)\)\s*;",
        clean, re.DOTALL
    )
    if not mod_match:
        raise ValueError("No valid module declaration found")

    name = mod_match.group(1)
    header = mod_match.group(2)

    # Try ANSI-style first (ports declared in header)
    ports = _parse_ansi_ports(header)
    if not ports:
        # Fall back to non-ANSI (ports declared in body)
        body_end = clean.find("endmodule")
        body = clean[mod_match.end():body_end] if body_end != -1 else clean[mod_match.end():]
        ports = _parse_body_ports(body)

    parameters = _parse_parameters(clean)

    return VerilogModule(
        name=name,
        ports=ports,
        parameters=parameters,
        raw_source=source,
    )
