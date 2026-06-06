.PHONY: help dev dev-backend dev-frontend build test lint format clean seed

help:
	@echo "DevOps Runtime Emotions AI Studio"
	@echo ""
	@echo "Usage:"
	@echo "  make dev            Start full stack (docker-compose)"
	@echo "  make dev-backend    Start backend only"
	@echo "  make dev-frontend   Start frontend only"
	@echo "  make build          Build all docker images"
	@echo "  make test           Run all tests"
	@echo "  make test-backend   Run backend tests only"
	@echo "  make test-frontend  Run frontend tests only"
	@echo "  make lint           Run all linters"
	@echo "  make format         Auto-format code"
	@echo "  make seed           Seed database with sample data"
	@echo "  make clean          Remove build artifacts"

# ─── Dev ──────────────────────────────────────────────────────────────────────
dev:
	docker-compose up --build

dev-backend:
	cd backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

# ─── Build ────────────────────────────────────────────────────────────────────
build:
	docker-compose build

# ─── Tests ────────────────────────────────────────────────────────────────────
test: test-backend test-frontend

test-backend:
	cd backend && poetry run pytest tests/ -v --tb=short

test-frontend:
	cd frontend && npm run test

test-e2e:
	cd frontend && npx playwright test

test-coverage:
	cd backend && poetry run pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

# ─── Lint / Format ────────────────────────────────────────────────────────────
lint: lint-backend lint-frontend

lint-backend:
	cd backend && poetry run ruff check . && poetry run mypy app/

lint-frontend:
	cd frontend && npm run lint && npm run type-check

format:
	cd backend && poetry run ruff format . && poetry run ruff check --fix .
	cd frontend && npm run format

# ─── DB ───────────────────────────────────────────────────────────────────────
seed:
	cd backend && poetry run python scripts/seed_db.py

# ─── Clean ────────────────────────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/.next frontend/out backend/htmlcov backend/.coverage
	@echo "Cleaned."
