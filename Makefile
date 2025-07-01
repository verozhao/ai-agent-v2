# Makefile
.PHONY: help install test run docker-build docker-run clean

help:
	@echo "Available commands:"
	@echo "  install    Install dependencies"
	@echo "  test       Run tests"
	@echo "  run        Run the agent"
	@echo "  docker     Build and run Docker container"
	@echo "  clean      Clean up generated files"

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v --asyncio-mode=auto

run:
	python main.py

docker-build:
	docker build -t anomaly-agent:latest -f docker/Dockerfile .

docker-run: docker-build
	docker run -it --rm anomaly-agent:latest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf *.egg-info