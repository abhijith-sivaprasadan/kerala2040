.PHONY: install test lint smoke

install:
	python -m pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check src tests scripts

smoke:
	python scripts/run_baseline.py
