# Contributing to learnFinnish

Thank you for your interest in contributing! This is a full-stack language learning app (FastAPI + Next.js + React Native).

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL (or SQLite for local dev)

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Mobile
```bash
cd mobile
npm install
npx expo start
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest tests/ -v` for backend, `npm test` for frontend)
5. Format code (`ruff check --fix .` for Python, `prettier --write .` for JS/TS)
6. Commit with a clear message
7. Open a Pull Request

## Code Style
- Python: PEP 8, ruff linter
- TypeScript: ESLint + Prettier
- Tests: pytest (backend), Vitest (frontend)
- All new features must include tests

## Code of Conduct
Be respectful and constructive. We welcome contributors of all experience levels.
