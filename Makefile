.PHONY: help install dev test build run clean docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install     Install all dependencies"
	@echo "  make dev         Start development environment"
	@echo "  make test        Run tests"
	@echo "  make build       Build production images"
	@echo "  make run         Run production environment"
	@echo "  make clean       Clean temporary files"
	@echo "  make docker-up   Start Docker environment"
	@echo "  make docker-down Stop Docker environment"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev:
	@echo "Starting development environment..."
	@cd backend && uvicorn app.main:app --reload --port 8000 &
	@cd frontend && npm start &
	@wait

test:
	cd backend && pytest
	cd frontend && npm test

build:
	docker-compose build

run:
	docker-compose up

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf frontend/node_modules
	rm -rf frontend/build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down
