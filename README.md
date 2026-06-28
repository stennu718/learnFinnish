# learnFinnish

Learn Finnish from Estonian — fast, free, and effective.

526 words, grammar explanations, and smart spaced repetition that helps you remember.

**For**: Estonian speakers who want to learn Finnish for work, travel, or fun.

## Quick Start

```bash
# Clone and run
git clone https://github.com/stennu718/learnFinnish.git
cd learnFinnish/backend
pip install -r requirements.txt
python app/main.py
```

Then open your browser and start learning.

## What you can do

- **Browse 526 words** — each with examples, etymology, and audio pronunciation
- **Practice with quizzes** — multiple choice, text input, and reaction tests to keep you sharp
- **Learn grammar** — clear explanations tailored for Estonian speakers, with interactive exercises
- **Remember with SRS** — spaced repetition figures out what you're about to forget and reviews it before you do
- **Track your progress** — see which words you know, which need work, and how far you've come
- **Use it anywhere** — works on your phone and your computer, so you can study on the bus or at your desk

## Screenshots

| Web | Mobile | Grammar |
|-----|--------|---------|
| ![Web](docs/screenshot-web.png) | ![Mobile](docs/screenshot-mobile.png) | ![Grammar](docs/screenshot-grammar.png) |

## Technical Highlights

- **Backend**: Python 3.11 + FastAPI + async SQLAlchemy
- **Auth**: JWT with refresh tokens, token blacklisting on logout
- **Rate limiting**: Per-endpoint limits (slowapi)
- **Testing**: 271 tests (unit, integration, e2e)
- **Security**: bcrypt password hashing, CORS, security headers, input validation
- **Deployment**: Docker support, GitHub Actions CI/CD

## Architecture

```
backend/
  app/
    api/          # Route handlers (auth, words, srs, progress, grammar)
    core/         # Middleware, auth, config, database, rate limiting
    models/       # SQLAlchemy ORM models
    services/     # Business logic (grammar engine, SRS, seed data)
  main.py         # App entry point, middleware, exception handlers
```

## License

MIT
