VENV ?= .venv
PY ?= $(VENV)/bin/python
PIP ?= $(VENV)/bin/pip

.PHONY: venv dev test lint fmt run clean

venv:
	python3 -m venv $(VENV)

dev: venv
	$(PIP) install -U pip wheel
	$(PIP) install -e ".[dev]" || $(PIP) install -e .
	pre-commit install

test:
	PYTHONPATH=src DISABLE_NLP=1 $(PY) -m pytest -q

lint:
	ruff check .
	mypy --ignore-missing-imports .

fmt:
	ruff format .

run:
	$(PY) -m src.qwen_cli_integrator || echo "Define entrypoint in pyproject."

clean:
	rm -rf .venv .pytest_cache dist build *.egg-info
