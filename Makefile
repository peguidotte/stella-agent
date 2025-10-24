.PHONY: help install install-dev clean test lint format run docker-build docker-up docker-down

# Default target
help:
	@echo "Stella Agent - Comandos Disponíveis"
	@echo "===================================="
	@echo ""
	@echo "Setup:"
	@echo "  make install        - Instala dependências de produção"
	@echo "  make install-dev    - Instala todas as dependências (prod + dev)"
	@echo ""
	@echo "Desenvolvimento:"
	@echo "  make run            - Inicia o servidor de desenvolvimento"
	@echo "  make test           - Executa testes"
	@echo "  make test-cov       - Executa testes com cobertura"
	@echo "  make lint           - Verifica código com flake8"
	@echo "  make format         - Formata código com black"
	@echo "  make format-check   - Verifica formatação sem alterar"
	@echo "  make type-check     - Verifica tipos com mypy"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   - Constrói imagem Docker"
	@echo "  make docker-up      - Inicia containers"
	@echo "  make docker-down    - Para containers"
	@echo ""
	@echo "Limpeza:"
	@echo "  make clean          - Remove arquivos temporários"
	@echo "  make clean-all      - Remove tudo (incluindo venv)"
	@echo ""

# Installation
install:
	pip install --upgrade pip
	pip install -r requirements.txt

install-dev:
	pip install --upgrade pip
	pip install -r requirements.txt -r requirements-dev.txt
	pre-commit install

# Run the application
run:
	python main.py

# Testing
test:
	pytest -v

test-cov:
	pytest --cov=stella --cov-report=html --cov-report=term

test-watch:
	pytest-watch

# Linting and Formatting
lint:
	@echo "Running flake8..."
	flake8 stella/ main.py --max-line-length=100
	@echo "Running mypy..."
	mypy stella/ main.py --ignore-missing-imports

format:
	@echo "Formatting with black..."
	black stella/ main.py demo.py --line-length=100
	@echo "Sorting imports with isort..."
	isort stella/ main.py demo.py --profile black

format-check:
	black stella/ main.py demo.py --check --line-length=100
	isort stella/ main.py demo.py --check-only --profile black

type-check:
	mypy stella/ main.py --ignore-missing-imports

# Quality checks (all at once)
check: format-check lint type-check test

# Docker commands
docker-build:
	docker build -t stella-agent:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Cleaning
clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	@echo "Clean complete!"

clean-all: clean
	@echo "Removing virtual environment..."
	rm -rf venv/ .venv/
	@echo "Deep clean complete!"

# Setup environment
setup:
	python -m venv venv
	@echo ""
	@echo "Virtual environment created!"
	@echo "Activate it with: source venv/bin/activate (Linux/Mac) or .\\venv\\Scripts\\activate (Windows)"
	@echo "Then run: make install-dev"

# Generate documentation
docs:
	cd docs && make html
	@echo "Documentation generated in docs/_build/html/index.html"

# Database/Data operations
init-db:
	@echo "Initializing database files..."
	python -c "from stella.data import init_db; init_db()"

backup-data:
	@echo "Backing up data files..."
	mkdir -p backups
	cp -r stella/data/*.json backups/data-$(shell date +%Y%m%d-%H%M%S).json

# Pre-commit
pre-commit:
	pre-commit run --all-files

# Show project info
info:
	@echo "Stella Agent - Project Information"
	@echo "=================================="
	@echo "Python version: $$(python --version)"
	@echo "Pip version: $$(pip --version)"
	@echo "Location: $$(pwd)"
	@echo ""
	@echo "Dependencies:"
	@pip list | grep -E "fastapi|uvicorn|deepface|opencv|gemini" || echo "Run 'make install' first"
