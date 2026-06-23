# Kriitiline auditiraport — learnFinnish

**Kuupäev:** 2026-06-24
**Audiitor:** OWL
**Kood:** 74 faili, 7522 rida, 271 testi

---

## 🔴 TÕELISED PROBLEEMID (kood töötab valesti)

### 1. `model_validate(p.__dict__)` — EBATUGINE
- **Fail:** `backend/app/api/words.py:45`
- **Probleem:** `WordPairResponse.model_validate(p.__dict__)` — SQLAlchemy objekt `__dict__` sisab `_sa_instance_state` ja muid sisemisi välju. Pydantic v2 `model_validate` eeldab puhast dict'i.
- **Tulemus:** See töötab juhul kui Pydantic v2 ignoreerib tundmatud välju (mis ta teeb `Extra.ignore` režiimis). Aga see on ohtlane — kui Pydantic konfiguratsioon muutub, hakkab see katki minema.
- **Lahendus:** Kasuta `from_attributes=True` Pydantic konfigs või konverteeri sunduselt:
  ```python
  WordPairResponse(
      id=p.id, estonian=p.estonian, finnish=p.finnish,
      estonian_example=p.estonian_example, finnish_example=p.finnish_example,
      category=p.category, difficulty=p.difficulty,
      is_cognate=p.is_cognate, audio_url=p.audio_url
  )
  ```

### 2. `get_db()` commitib AINULT õnnestunud päringuid
- **Fail:** `backend/app/core/database.py:15-22`
- **Probleem:** `submit_review` kasutab `flush()` mitte `commit()`. Kui `get_db()` rollbackib exceptioni pärast, siis flush'itud andmed kaovad.
- **Tolemus:** Review võib salvestuda pooleliolekuna — SRS kaart uuendatud, aga progress ei uuendu.
- **Lahendus:** Lisa `await db.commit()` pärast `flush()` või kasuta `get_db()` kontekstihalduris commit'i.

### 3. Frontend token localStorage'is — XSS rünne
- **Fail:** `frontend/src/lib/authStore.ts`
- **Probleem:** JWT token salvestatakse ilma persistita. Kui kasutaja sulgeb brauser, token kustub. Aga kui XSS rünne õnnestub, saab ründaja tokeni kätte.
- **Lahendus:** Kasuta `httpOnly` cookie't või vähemalt Zustand persist middleware'it.

### 4. Grammatika mootor on lihtsalt nimekiri
- **Fail:** `backend/app/services/grammar.py`
- **Probleem:** `apply_rule()` kasutab lihtsat `endswith()` — see ei tööda õige soome keele morfoloogiaga. Näiteks `maja` → `talossa` (mitte `majassa`).
- **Tulemus:** Vale tõlgendus, kasutab polnud vale vastust.
- **Lahendus:** Kasuta `omorfi` või `libvoikki` soome keele morfoloogia teeki.

---

## 🟡 KRIITILISED PUUDUSED (kood töötab, aga puudub)

### 5. Rate limiting PUUDUB
- **Probleem:** API endpointid on avatud brute-force rünnetele.
- **Lahendus:** Lisa `slowapi` või custom FastAPI middleware.

### 6. Tokeni blacklisting PUUDUB
- **Probleem:** Logout eiInvalidate'i tokenit. Vana token töötab ikka.
- **Lahendus:** Lisa Redis'is tokeni blacklist või kasuta lühemat JWT aegumist.

### 7. Ainult SQLite
- **Probleem:** SQLite ei sobi production'i jaoks (mitme kasutaja samaaegne ligipääs).
- **Lahendus:** PostgreSQL või Turso (serverless SQLite).

### 8. Frontend ei kasuta API_CIENT
- **Fail:** `frontend/src/app/grammar/page.tsx`
- **Probleem:** Kasutab hardcoded `http://localhost:8000` asemel API klienti.
- **Lahendus:** Kasuta `@/lib/api` klienti.

### 9. Mobiil API klient puudub grammar jaoks
- **Fail:** `mobile/src/services/api.ts`
- **Probleem:** `getGrammarRules` ja `getGrammarExercise` on lisatud, aga `LearnScreen` ei kasuta neid.
- **Lahendus:** Lõpeta Grammatika ekraani integreerimine.

### 10. puuduv .env.example
- **Probleem:** Puudub `.env.example` fail, mis näitab millised keskkonnamuutujad on vajalikud.
- **Lahendus:** Lisa `.env.example` fail.

---

## 🟢 MIS ON KORRAS

### Testid
- 271 testi, 100% läbitud
- Hea katvus: auth, SRS, words, progress, grammar, seed, E2E
- Korrektne pytest_asyncio kasutus

### Turvalisus
- Bcrypt parooli hashimine ✅
- JWT tokenite aegumine ✅
- CORS piiratud ✅
- `is_active` kontroll ✅
- Input valideerimine (parooli pikkus, email formaat) ✅
- SQL injection kaitse (SQLAlchemy ORM) ✅

### Arhitektuur
- FastAPI + SQLAlchemy async ✅
- Zustand state management ✅
- React Native + Expo ✅
- Docker + docker-compose ✅
- GitHub Actions CI/CD ✅

### Funktsionaalsus
- 500+ sõna, 22 kategooriat ✅
- SM-2 SRS algoritm ✅
- Grammatika mootor (12 reeglit) ✅
- Lingvisti stiilis flashcard UI ✅

---

## 📊 Kokkuvõte

| Kategooria | Olek | Prioriteet |
|------------|------|------------|
| **Andmete turbelisus** | 🔴 Oluline | P0 |
| **API turvalisus** | 🟡 Puudub | P1 |
| **Mobiil integratsioon** | 🟡 Poolik | P1 |
| **Testid** | ✅ Hea | — |
| **Arhitektuur** | ✅ Hea | — |

**Soovitused:**
1. Paranda `model_validate` — kasuta konkreetset konverteerimist
2. Paranda `get_db()` commit/rollback loogika
3. Lisa rate limiting
4. Lisa tokeni blacklisting
5. Lõpeta Grammatika ekraani integreerimine mobiilis
6. Lisa .env.example factory
