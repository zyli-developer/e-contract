# Project Name

A full-stack web application with Next.js frontend and FastAPI backend.

## Quick Start

```bash
make start
```

This will:
1. Install dependencies (Python & Node.js)
2. Start the backend on http://localhost:8000
3. Start the frontend on http://localhost:3000

## Project Structure

```
.
├── frontend/          # Next.js frontend
│   └── app/          # App router pages
├── backend/          # FastAPI backend
│   └── main.py       # API entry point
├── Makefile          # Build commands
└── README.md
```

## API Endpoints

- `GET /health` - Health check
- `GET /api/hello` - Example endpoint

## Development

- Frontend: `make frontend`
- Backend: `make backend`
- Stop all: `make stop`
