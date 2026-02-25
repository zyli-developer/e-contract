.PHONY: start install dev clean test

start: install
	@python main.py

install:
	@pip install -r requirements.txt 2>/dev/null || true

dev: start

test:
	@python main.py --help

clean:
	@rm -rf __pycache__ .venv *.pyc dist/ build/ *.egg-info/
