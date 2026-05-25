.PHONY: help install lint format test coverage airflow-up airflow-down run-nba run-football train evaluate dashboard clean

BLUE  := \033[34m
RESET := \033[0m

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "$(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install -r requirements.txt

lint: ## Run flake8 + isort check + black check
	flake8 ingestion/ transformation/ models/ tests/ --max-line-length=100
	isort --check-only ingestion/ transformation/ models/ tests/
	black --check ingestion/ transformation/ models/ tests/

format: ## Auto-format code
	isort ingestion/ transformation/ models/ tests/
	black ingestion/ transformation/ models/ tests/

test: ## Run unit tests
	pytest tests/ -v

coverage: ## Run tests with coverage
	pytest tests/ --cov=ingestion --cov=transformation --cov=models \
		--cov-report=term-missing --cov-report=html

airflow-up: ## Start Airflow (Docker)
	docker-compose up -d
	@echo "$(BLUE)Airflow → http://localhost:8080 (admin/admin)$(RESET)"

airflow-down: ## Stop Airflow
	docker-compose down

run-nba: ## Run NBA pipeline manually
	python scripts/run_nba_pipeline.py

run-football: ## Run football pipeline manually
	python scripts/run_football_pipeline.py

train: ## Train recommendation model
	python models/train.py

evaluate: ## Evaluate recommendation model
	python models/evaluate.py

dashboard: ## Launch Streamlit dashboard
	streamlit run dashboard/app.py --server.port 8501

clean: ## Remove cache files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage
