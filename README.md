# FPGA TestGen

Gemini API를 활용한 FPGA 테스트벤치 자동 생성 도구.

Verilog RTL 코드를 입력하면 테스트벤치 생성 → 시뮬레이션 → 커버리지 분석까지 자동으로 수행합니다.

## Setup

```bash
# 의존성 설치
make install

# 환경변수 설정
cp .env.example .env
# .env 파일에 GEMINI_API_KEY 입력

# iverilog 설치 (Fedora)
sudo dnf install iverilog
```

## Usage

### CLI

```bash
# 테스트벤치 생성 (전체 파이프라인)
fpga-testgen generate design.v

# 모듈 파싱만
fpga-testgen parse design.v

# 시뮬레이션만
fpga-testgen simulate design.v testbench.v

# 커버리지 분석
fpga-testgen coverage dump.vcd design.v
```

### Web UI

```bash
make dev    # http://localhost:5173
```

## Tech Stack

- **Backend**: Python, FastAPI, Google Gemini API
- **Frontend**: React, Monaco Editor, Vite
- **Simulation**: Icarus Verilog / Verilator
- **Coverage**: VCD 파일 기반 toggle / FSM 커버리지 분석
