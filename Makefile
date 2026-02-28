.PHONY: install dev test lint serve build

install:
	python3 -m venv .venv
	.venv/bin/pip install -e ".[dev]"
	cd web && npm install

dev:
	cd web && npm run dev &
	.venv/bin/uvicorn fpga_testgen.server:app --reload --port 8000

test:
	.venv/bin/pytest tests/ -v

serve:
	cd web && npm run build
	.venv/bin/uvicorn fpga_testgen.server:app --port 8000

lint:
	.venv/bin/ruff check fpga_testgen/
	.venv/bin/ruff format --check fpga_testgen/
