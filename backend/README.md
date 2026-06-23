# Backend — FastAPI

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API

- `POST /api/auth/register` — Create account
- `POST /api/auth/login` — Login, get JWT
- `GET  /api/words` — List word pairs
- `GET /api/srs/due` — Get due cards
- `POST /api/srs/review` — Submit review
- `GET /api/progress` — User progress stats
