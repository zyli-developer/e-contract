.PHONY: start stop install dev backend frontend clean

# Default target
start: install
	@echo "Starting services..."
	@make -j2 backend frontend

install:
	@echo "Installing dependencies..."
	@cd backend && pip install -r requirements.txt
	@cd frontend && npm install

backend:
	@echo "Starting backend on http://localhost:8000"
	@cd backend && uvicorn main:app --reload --port 8000

frontend:
	@echo "Starting frontend on http://localhost:3000"
	@cd frontend && npm run dev

stop:
	@echo "Stopping services..."
	@pkill -f "uvicorn main:app" || true
	@pkill -f "next dev" || true

clean:
	@rm -rf backend/__pycache__ backend/.venv
	@rm -rf frontend/node_modules frontend/.next

dev: start
