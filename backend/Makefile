.PHONY: dev lint format test seed

PYTHON ?= python3
MODULES = app tests

dev:
	uvicorn app.main:app --reload

lint:
	$(PYTHON) -m ruff check $(MODULES)
	$(PYTHON) -m black --check $(MODULES)
	$(PYTHON) -m mypy app

format:
	$(PYTHON) -m black $(MODULES)
	$(PYTHON) -m ruff check --fix $(MODULES)

test:
	$(PYTHON) -m pytest

seed:
	docker compose run --rm backend $(PYTHON) -m app.infra.clickhouse.seed_data
