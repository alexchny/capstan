PY=uv run python
LINT_RUFF=uv run ruff check
LINT_MYPY=uv run mypy

.PHONY: lint test sim shadow prod bench fmt hooks

hooks:
	pre-commit install

lint:
	$(LINT_RUFF) src tests
	$(LINT_MYPY) --config-file mypy.ini src

test:
	PYTHONPATH=src uv run pytest

sim:
	$(PY) -m scripts.run_sim configs/config.yaml

shadow:
	$(PY) -m scripts.run_shadow configs/config.yaml

prod:
	$(PY) -m scripts.run_prod configs/config.yaml

bench:
	$(PY) -m scripts.run_sim --benchmark configs/config.yaml 