# Changelog

All notable changes to the learnFinnish project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Cross-worker rate limiter with Redis and file-based fallback for multi-worker uvicorn deployments
- CHANGELOG.md following Keep a Changelog format
- `screenshots/` directory with capture guidelines

## [0.1.0] - 2025-06-28

### Added
- Initial release: Estonia-Finnish language learning application
- FastAPI backend with auth, words, SRS, progress, and grammar endpoints
- Lingvist-style flashcard UI with hints, streaks, XP, keyboard navigation, and fuzzy matching
- Mobile app rewrite with flashcard experience
- 329+ conversational word pairs across 14 categories
- Grammar engine: 12 Estonian-Finnish case transformation rules
- SM-2 spaced repetition algorithm
- Token blacklisting and rate limiting middleware
- Comprehensive test suite (271+ tests covering auth, SRS, words, grammar, E2E)
- Security features: password validation, email normalization, CORS, input validation
- CI/CD pipeline with static export and GitHub Pages deploy for frontend
- Android CI/CD support
- MIT License
- Contributing guidelines and project documentation

### Fixed
- Grammar engine illative case transformation
- Model validation, database commit, and API client issues
- Logout URL, model defaults, and UI typos
- Token blacklist enforcement on `get_current_user`
- SECRET_KEY requirement enforcement

[Unreleased]: https://github.com/lan/learnFinnish/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/lan/learnFinnish/releases/tag/v0.1.0
