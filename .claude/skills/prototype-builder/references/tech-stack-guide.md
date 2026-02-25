# Tech Stack Selection Guide

## Default Recommendations by Project Type

| Project Type | Recommended Stack | Why |
|--------------|-------------------|-----|
| Web App (full-stack) | Next.js + FastAPI | Type-safe frontend, fast Python backend, great AI library support |
| API Service | FastAPI | Fast, auto-docs, async support, excellent for AI integration |
| CLI Tool | Python + argparse/click | Simple, readable, rich ecosystem |
| Frontend Only | Next.js | React-based, great DX, easy deployment |
| Data/ML Project | FastAPI + Python | Native ML library support |

## Stack Compatibility Matrix

### Frontend + Backend Combinations

| Frontend | Backend | Compatibility | Notes |
|----------|---------|---------------|-------|
| Next.js | FastAPI | Excellent | Recommended default |
| Next.js | Node.js/Express | Good | All-JS stack |
| Vue | FastAPI | Good | Alternative to React |
| React (CRA) | FastAPI | Good | Simpler than Next.js |

### Warning Signs (Suggest Alternatives)

| User Request | Issue | Suggestion |
|--------------|-------|------------|
| PHP + React | Unusual combo | Suggest Node.js or FastAPI backend |
| Java + Vue for prototype | Overhead too high | Suggest FastAPI for faster iteration |
| Multiple databases | Complexity | Start with one, add later |
| Microservices for MVP | Over-engineering | Start monolithic |

## Technology Notes

### FastAPI (Python)
- Pros: Auto OpenAPI docs, async, type hints, AI library ecosystem
- Cons: GIL for CPU-bound tasks
- Best for: APIs, AI/ML backends, rapid prototyping

### Next.js
- Pros: SSR/SSG, file-based routing, React ecosystem
- Cons: Learning curve for non-React devs
- Best for: Full-stack web apps, SEO-important sites

### Python CLI
- Pros: Quick to write, readable, cross-platform
- Cons: Requires Python installed
- Best for: Dev tools, automation scripts, data processing
