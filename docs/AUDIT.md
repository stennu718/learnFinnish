# Auditiraport — learnFinnish

**Kuupäev:** 2026-06-23
**Audiitor:** OWL
**Ulatus:** Backend, Frontend, Mobiil, Testid, CI/CD

---

## 🔴 KRIIILISED (peavad parandama enne productioni)

### 1. SECRET_KEY hardcoded
- **Fail:** `backend/app/core/config.py`
- **Probleem:** `SECRET_KEY: str = "change-me-in-production"` — vaikimisi turvamata väärtus
- **Lahendus:** Genereeri juhuslik võti, kasuta `.env` faili, lisa `SECRET_KEY` kohustuslikuks

### 2. Parooli min-puudub
- **Fail:** `backend/app/api/auth.py`
- **Probleem:** `RegisterRequest.password: str` — ei ole min_length piirang
- **Lahendus:** Lisa `min_length=6` või kasuta `Field(min_length=6)`

### 3. JWT tokeni aegumine liiga pikk
- **Fail:** `backend/app/core/config.py`
- **Probleem:** `ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7` — 7 päeva on liiga pikk
- **Lahendus:** Muuda 60 * 24 (1 päev) või lisa refresh token

### 4. CORS liiga lai
- **Fail:** `backend/app/main.py`
- **Probleem:** `allow_methods=["*"]` ja `allow_headers=["*"]` — liiga lai
- **Lahendus:** Piira kindlate meetodite ja päistega

### 5. `get_db` ei commiti õnnestunud päringuid
- **Fail:** `backend/app/core/database.py`
- **Probleem:** `get_db()` commiti ainult kui ei ole exceptionit, aga `submit_review` kasutab `flush()` mitte `commit()`
- **Lahendus:** Lisa `await db.commit()` pärast `flush()` või kasuta kontekstihaldurit

### 6. Frontend token localStorage'is (mitte turvaline)
- **Fail:** `frontend/src/lib/authStore.ts`
- **Probleem:** Token salvestatakse localStorage'i (XSS rünnetele avatud)
- **Lahendus:** Kasuta httpOnly cookie't või SecureStore (mobiil)

### 7. Mobiil token SecureStore'is (OK)
- **Fail:** `mobile/src/store/authStore.ts`
- **Olek:** ✅ Kasutab `expo-securestore` — turvaline

---

## 🟡 KESKMINE (tuleks parandada)

### 8. Parooli hashimine ilma saltita
- **Fail:** `backend/app/core/auth.py`
- **Probleem:** `CryptContext(schemes=["bcrypt"])` — bcrypt lisab salti automaatselt, OK
- **Olek:** ✅ OK

### 9. Rate limiting puudub
- **Probleem:** API endpointid ei ole rate limiteeritud
- **Lahendus:** Lisa `slowapi` või FastAPI rate limiter

### 10. Input valideerimine SRS review
- **Fail:** `backend/app/api/srs.py`
- **Probleem:** `quality: int` — ei ole piirangut (0-5)
- **Lahendus:** Lisa `Field(ge=0, le=5)`

### 11. Kasutaja is_active kontroll puudub
- **Fail:** `backend/app/core/auth.py`
- **Probleem:** `get_current_user` ei kontrolli `is_active` välja
- **Lahendus:** Lisa kontroll kasutaja aktiivsusele

### 12. E-posti normaliseerimine puudub
- **Fail:** `backend/app/api/auth.py`
- **Probleem:** "Test@test.ee" ja "test@test.ee" on erinevad kasutajad
- **Lahendus:** Normaliseeri email lowercase'iks enne salvestamist

### 13. Parooli väljund response'is
- **Fail:** `backend/app/api/auth.py`
- **Probleem:** `RegisterRequest` ei sisalda `hashed_password` välja, OK
- **Olek:** ✅ OK

### 14. Tokeni blacklisting puudub
- **Probleem:** Välja logitud kasutaja token kehtib ikka
- **Lahendus:** Lisa tokeni blacklisting või lühema aegumisaja

### 15. HTTPS kohustus puudub
- **Probleem:** Arenduskeskkonnas HTTP OK, productioonis kohustuslik
- **Lahendus:** Lisa HTTPS redirect productioonis

---

## 🟢 HEA (korralikult tehtud)

### 16. Bcrypt parooli hashimine
- **Olek:** ✅ Kasutab bcrypt'i, turvaline

### 17. JWT valideerimine
- **Olek:** ✅ Korrektne dekodeerimise ja aegumise kontroll

### 18. SQL injection kaitse
- **Olek:** ✅ SQLAlchemy ORM, parameterized queries

### 19. CORS seadistatud
- **Olek:** ✅ CORS middleware olemas, piiratud originid

### 20. Testid
- **Olek:** ✅ 75/75 testid läbitud, hea katvus

### 21. Andmebaasi mudelid
- **Olek:** ✅ Korrektsed, indeksid olemas

### 22. SRS algoritm
- **Olek:** ✅ SM-2 korrektne implementatsioon

### 23. Seed andmed
- **Olek:** ✅ 329+ sõna, 14 kategooriat, näitelaused

### 24. Frontend/Mobiil
- **Olek:** ✅ Lingvisti stiilis flashcard kogemus

---

## 📊 Kokkuvõte

| Kategooria | Arv | Prioriteet |
|------------|-----|------------|
| 🔴 Kriitiline | 7 | P0 — enne productioni |
| 🟡 Keskmine | 8 | P1 — esimese nädala jooksul |
| 🟢 Hea | 8 | — |

**Soovitused:**
1. Paranda kõik 7 kriilist viga enne productioni
2. Lisada rate limiting
3. Lisada input valideerimine
4. Parandada tokeni turvalisus (httpOnly cookie)
5. Lisada parooli nõuded
6. Lühendada JWT aegumisaega
