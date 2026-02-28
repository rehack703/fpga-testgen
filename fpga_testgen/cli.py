"""CLI entry point."""

from __future__ import annotations
import json
from pathlib import Path
import click
from .config import settings


@click.group()
def cli():
    """FPGA TestGen — LLM-based FPGA testbench auto-generation tool."""
    pass


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--module", "-m", default=None, help="Module name (auto-detected if omitted)")
@click.option("--output", "-o", default=None, type=click.Path(path_type=Path), help="Output directory")
@click.option("--retries", "-r", default=None, type=int, help=f"Max retries (default: {settings.max_retries})")
@click.option("--simulator", "-s", default=None, type=click.Choice(["iverilog", "verilator"]))
def generate(file: Path, module: str | None, output: Path | None, retries: int | None, simulator: str | None):
    """Generate a testbench for a Verilog file."""
    from .pipeline import run_pipeline

    rtl_source = file.read_text()
    click.echo(f"Parsing {file.name}...")

    result = run_pipeline(rtl_source, module, simulator, retries)

    click.echo(f"Module: {result.module.name}")
    click.echo(f"Ports: {len(result.module.ports)}")
    click.echo(f"Attempts: {result.attempts}")

    if result.sim_result and result.sim_result.success:
        click.secho("Simulation: PASSED", fg="green")
    else:
        click.secho("Simulation: FAILED", fg="red")
        if result.sim_result:
            for err in result.sim_result.errors:
                click.echo(f"  {err}")

    if result.coverage:
        click.echo(f"\nCoverage Score: {result.coverage.total_score}%")
        click.echo(f"Toggle Coverage: {result.coverage.overall_toggle}%")
        if result.coverage.fsm_coverage:
            fsm = result.coverage.fsm_coverage
            click.echo(f"FSM Coverage: {fsm['coverage_pct']}% "
                        f"({len(fsm['visited_states'])}/{len(fsm['declared_states'])} states)")

    # Save output
    out_dir = output or file.parent
    tb_path = out_dir / f"{result.module.name}_tb.v"
    tb_path.write_text(result.testbench)
    click.echo(f"\nTestbench saved to: {tb_path}")

    if result.sim_result and result.sim_result.stdout:
        log_path = out_dir / f"{result.module.name}_sim.log"
        log_path.write_text(result.sim_result.stdout)
        click.echo(f"Simulation log: {log_path}")


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
def parse(file: Path):
    """Parse a Verilog file and show module info."""
    from .parser import parse_verilog

    module = parse_verilog(file.read_text())
    click.echo(f"Module: {module.name}")
    click.echo("Ports:")
    for p in module.ports:
        click.echo(f"  {p}")
    if module.parameters:
        click.echo("Parameters:")
        for param in module.parameters:
            click.echo(f"  {param}")


@cli.command("simulate")
@click.argument("design", type=click.Path(exists=True, path_type=Path))
@click.argument("testbench", type=click.Path(exists=True, path_type=Path))
@click.option("--simulator", "-s", default=None, type=click.Choice(["iverilog", "verilator"]))
def simulate_cmd(design: Path, testbench: Path, simulator: str | None):
    """Run simulation with existing design and testbench."""
    from .simulator import simulate

    result = simulate(design.read_text(), testbench.read_text(), simulator)
    if result.success:
        click.secho("Simulation PASSED", fg="green")
    else:
        click.secho("Simulation FAILED", fg="red")
        for err in result.errors:
            click.echo(f"  {err}")
    if result.stdout:
        click.echo("\n--- Simulation Output ---")
        click.echo(result.stdout)


@cli.command()
@click.argument("vcd_file", type=click.Path(exists=True, path_type=Path))
@click.argument("design", type=click.Path(exists=True, path_type=Path))
def coverage(vcd_file: Path, design: Path):
    """Analyze coverage from a VCD file."""
    from .parser import parse_verilog
    from .coverage import analyze_coverage

    module = parse_verilog(design.read_text())
    report = analyze_coverage(vcd_file, module)

    click.echo(f"Overall Toggle Coverage: {report.overall_toggle}%")
    click.echo("\nPer-signal toggle:")
    for sig, cov in sorted(report.toggle_coverage.items()):
        bar = "█" * int(cov / 10)
        click.echo(f"  {sig:20s} {cov:5.1f}% {bar}")
    if report.fsm_coverage:
        fsm = report.fsm_coverage
        click.echo(f"\nFSM Coverage: {fsm['coverage_pct']}%")
        click.echo(f"  Declared: {fsm['declared_states']}")
        click.echo(f"  Visited:  {fsm['visited_states']}")
    click.echo(f"\nTotal Score: {report.total_score}%")


@cli.command()
@click.option("--port", "-p", default=8000, type=int, help="Server port")
@click.option("--host", default="0.0.0.0", help="Server host")
def serve(port: int, host: str):
    """Start the web UI server."""
    import uvicorn
    click.echo(f"Starting FPGA TestGen server on {host}:{port}")
    uvicorn.run("fpga_testgen.server:app", host=host, port=port, reload=True)
