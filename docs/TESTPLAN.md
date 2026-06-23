# Testplan — learnFinnish

## Ülevaade

| Testitüüp | Failid | Katvus |
|-----------|--------|--------|
| **Unit tests** | `test_unit.py` | SM-2 algoritm, auth utiliidid, mudelid, seed andmed |
| **Integration tests** | `test_integration_auth.py` | Auth endpointid (register, login, me) |
| **Integration tests** | `test_integration_srs.py` | SRS endpointid (init, due, review) |
| **Integration tests** | `test_integration_words.py` | Sõnade ja progressi endpointid |
| **E2E tests** | `test_e2e.py` | Täielik kasutajateekond |
| **Legacy tests** | `test_api.py`, `test_srs.py` | Varasemad testid (säilitatud) |

## Käivitamine

```bash
# Kõik testid
pytest tests/ -v

# Ainult unit testid
pytest tests/test_unit.py -v

# Ainult integratsioonitestid
pytest tests/test_integration_*.py -v

# Ainult E2E testid
pytest tests/test_e2e.py -v

# Koos coverage'iga
pytest tests/ -v --cov=app --cov-report=term-missing
```

## Testid

### Unit Tests (`test_unit.py`)

#### TestSM2Algorithm
- `test_first_review_correct` — esimene õige vastus, interval=1
- `test_first_review_perfect` — perfektne vastus, EF tõuseb
- `test_second_review_correct` — teine õige vastus, interval=6
- `test_third_review_correct` — kolmas õige vastus, interval = prev * EF
- `test_failed_review_resets` — ebaõnnestunud vastus, reset
- `test_ef_minimum` — EF ei lähe alla 1.3
- `test_ef_decreases_on_wrong` — EF langeb valesti vastamisel
- `test_quality_3_borderline` — quality 3 on piir
- `test_quality_0_complete_blackout` — quality 0 on täielik blackout
- `test_long_streak_increases_interval` — pikk järekord suurendab intervali

#### TestAuthUtils
- `test_hash_password` — parooli hashimine
- `test_verify_password_correct` — õige parooli kontroll
- `test_verify_password_incorrect` — vale parooli kontroll
- `test_create_access_token` — tokeni loomine
- `test_token_contains_expiry` — token sisaldab aegumist

#### TestWordPairModel
- `test_create_word_pair` — sõna paari loomine
- `test_cognate_detection` — kognaadi tuvastamine

#### TestSeedData
- `test_seed_json_valid` — JSON seed andmed korrektsed
- `test_seed_food_valid` — toidu seed andmed korrektsed
- `test_seed_transport_valid` — transpordi seed andmed korrektsed
- `test_seed_shopping_valid` — ostlemise seed andmed korrektsed
- `test_seed_health_valid` — tervise seed andmed korrektsed
- `test_seed_home_time_valid` — kodu/aja seed andmed korrektsed
- `test_seed_people_valid` — inimeste seed andmed korrektsed
- `test_seed_clothing_nature_valid` — riietuse/looduse seed andmed korrektsed
- `test_all_categories_present` — kõik kategooriad olemas
- `test_difficulty_range` — raskusaste 1-5

### Integration Tests

#### TestAuthEndpoints (`test_integration_auth.py`)
- `test_health` — health check
- `test_register_success` — edukas registreerimine
- `test_register_duplicate_email` — duplikaat email
- `test_register_missing_email` — puuduv email
- `test_register_short_password` — lühike parool
- `test_login_success` — edukas sisselogimine
- `test_login_wrong_password` — vale parool
- `test_login_nonexistent_user` — olematu kasutaja
- `test_get_me_authenticated` — autenditud profiil
- `test_get_me_unauthenticated` — autendimata profiil
- `test_get_me_invalid_token` — vigane token

#### TestSRSEndpoints (`test_integration_srs.py`)
- `test_init_srs_creates_cards` — SRS kaartide loomine
- `test_init_srs_idempotent` — idempotentsus
- `test_get_due_cards` — ootel kaardid
- `test_review_card_correct` — õige vastus
- `test_review_card_incorrect` — vale vastus
- `test_review_invalid_card` — vigane kaart
- `test_review_missing_quality` — puuduv quality
- `test_due_cards_limit` — limiit
- `test_srs_unauthenticated` — autendimata
- `test_review_updates_progress` — progressi uuendus

#### TestWordEndpoints (`test_integration_words.py`)
- `test_list_words` — sõnade list
- `test_list_words_pagination` — lehekülg
- `test_list_words_by_category` — kategooria järgi
- `test_list_words_cognates_only` — ainult kognaadid
- `test_list_categories` — kategooriad
- `test_words_unauthenticated` — autendimata

#### TestProgressEndpoints (`test_integration_words.py`)
- `test_progress_initial` — algne progress
- `test_progress_after_review` — pärast vaatamist
- `test_progress_unauthenticated` — autendimata

### E2E Tests (`test_e2e.py`)

#### TestE2EUserJourney
- `test_complete_learning_session` — täielik õppimise sessioon
  - Registreerimine → profiil → SRS init → kaartide vaatamine → 3 review'd → progress → sõnad → kategooriad
- `test_multiple_review_sessions` — mitu sessiooni
- `test_error_handling` — vigade käsitlemine

## CI/CD

Testid käivituvat automaatselt GitHub Actions'is:
- Iga `push` ja `PR` puhul
- Python 3.11
- Backend testid + frontend lint + Docker build
