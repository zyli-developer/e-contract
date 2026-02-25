.PHONY: start install dev clean test

start: install
	@echo "Starting API server on http://localhost:8000"
	@uvicorn main:app --reload --port 8000

install:
	@pip install -r requirements.txt

dev: start

test:
	@curl -s http://localhost:8000/health | python -m json.tool

clean:
	@rm -rf __pycache__ .venv *.pyc
