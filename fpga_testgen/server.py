"""FastAPI backend server."""

from __future__ import annotations
import shutil
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .config import settings

app = FastAPI(title="FPGA TestGen", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request/Response models ---

class GenerateRequest(BaseModel):
    rtl: str
    module_name: str | None = None
    max_retries: int = 3
    simulator: str | None = None


class PortInfo(BaseModel):
    direction: str
    name: str
    width: int


class ModuleInfo(BaseModel):
    name: str
    ports: list[PortInfo]
    parameters: list[str]


class CoverageInfo(BaseModel):
    toggle_coverage: dict[str, float]
    overall_toggle: float
    fsm_coverage: dict | None = None
    total_score: float


class GenerateResponse(BaseModel):
    testbench: str
    description: str
    module: ModuleInfo
    sim_success: bool
    sim_output: str
    sim_errors: list[str]
    coverage: CoverageInfo | None = None
    attempts: int


class ParseRequest(BaseModel):
    rtl: str


class ParseResponse(BaseModel):
    module: ModuleInfo


class SimulateRequest(BaseModel):
    design: str
    testbench: str
    simulator: str | None = None


class SimulateResponse(BaseModel):
    success: bool
    stdout: str
    stderr: str
    errors: list[str]


class HealthResponse(BaseModel):
    status: str
    iverilog: bool
    verilator: bool
    gemini_configured: bool


# --- Endpoints ---

@app.get("/api/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        iverilog=settings.has_iverilog,
        verilator=settings.has_verilator,
        gemini_configured=bool(settings.gemini_api_key),
    )


@app.post("/api/parse", response_model=ParseResponse)
def parse_rtl(req: ParseRequest):
    from .parser import parse_verilog

    try:
        module = parse_verilog(req.rtl)
    except ValueError as e:
        raise HTTPException(400, str(e))

    return ParseResponse(
        module=ModuleInfo(
            name=module.name,
            ports=[PortInfo(direction=p.direction, name=p.name, width=p.width) for p in module.ports],
            parameters=module.parameters,
        )
    )


@app.post("/api/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    from .pipeline import run_pipeline

    if not settings.gemini_api_key:
        raise HTTPException(500, "GEMINI_API_KEY not configured")

    try:
        result = run_pipeline(
            req.rtl,
            module_name=req.module_name,
            simulator=req.simulator,
            max_retries=req.max_retries,
        )
    except Exception as e:
        raise HTTPException(500, str(e))

    coverage = None
    if result.coverage:
        coverage = CoverageInfo(
            toggle_coverage=result.coverage.toggle_coverage,
            overall_toggle=result.coverage.overall_toggle,
            fsm_coverage=result.coverage.fsm_coverage,
            total_score=result.coverage.total_score,
        )

    return GenerateResponse(
        testbench=result.testbench,
        description=result.description,
        module=ModuleInfo(
            name=result.module.name,
            ports=[PortInfo(direction=p.direction, name=p.name, width=p.width) for p in result.module.ports],
            parameters=result.module.parameters,
        ),
        sim_success=result.sim_result.success if result.sim_result else False,
        sim_output=result.sim_result.stdout if result.sim_result else "",
        sim_errors=result.sim_result.errors if result.sim_result else [],
        coverage=coverage,
        attempts=result.attempts,
    )


@app.post("/api/simulate", response_model=SimulateResponse)
def simulate_endpoint(req: SimulateRequest):
    from .simulator import simulate

    result = simulate(req.design, req.testbench, req.simulator)
    return SimulateResponse(
        success=result.success,
        stdout=result.stdout,
        stderr=result.stderr,
        errors=result.errors,
    )


# Serve frontend static files (if built)
_web_dist = Path(__file__).parent.parent / "web" / "dist"
if _web_dist.exists():
    app.mount("/", StaticFiles(directory=str(_web_dist), html=True), name="static")
