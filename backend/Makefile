.PHONY: lint format

lint:
	python3 -m ruff check app llm_orchestrator.py
	python3 -m black --check app llm_orchestrator.py

format:
	python3 -m black app llm_orchestrator.py
