.PHONY: help install start test test-cov clean

help: ## Zeige alle verfügbaren Befehle
	@echo "Verfügbare Befehle:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf " \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Installiere das Paket
	pip install -e ".[web]"
	pip install pytest

start: ## Starte die Web-GUI
	python -m uvicorn heizlast.web.app:app --reload --host 0.0.0.0 --port 8000

test: ## Führe alle Tests aus
	pytest tests/ -v

test-cov: ## Tests mit Coverage
	pytest tests/ -v --cov=heizlast --cov-report=html

clean: ## Aufräumen
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage
