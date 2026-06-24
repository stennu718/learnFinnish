# Tegevuskava — learnFinnish

**Eesmärk:** Eesti → Soome keeleõppe maailma parim äpp (web + mobile)

**Sihtrühm:** Eesti keelt kõnelevad inkesed, kes õppivad soome keelt

**Periood:** 2026 Q3 (juuni–september)

---

## Sprint 1: MVP (nädalad 1–2) ✅ VALMIS

| # | Ülesanne | Olek | Tegelik |
|---|----------|------|---------|
| 1.1 | GitHub repo loomine | ✅ | stennu718/learnFinnish |
| 1.2 | Backend scaffold (FastAPI + SQLite) | ✅ | 45 faili, 4188 rida |
| 1.3 | Frontend scaffold (Next.js + Tailwind) | ✅ | 13 faili, 2168 rida |
| 1.4 | Mobiil scaffold (React Native + Expo) | ✅ | 12 faili, 1800+ rida |
| 1.5 | JWT autentimine | ✅ | bcrypt + jose |
| 1.6 | 500+ baassõna andmebaasi | ✅ | 22 kategooriat |
| 1.7 | SM-2 SRS algoritm | ✅ | 50+ testi |
| 1.8 | Flashcard UI (Lingvisti stiil) | ✅ | Web + Mobile |
| 1.9 | Grammatika mootor (12 käänet) | ✅ | API + UI |
| 1.10 | Docker + docker-compose | ✅ | Backend + Frontend |
| 1.11 | GitHub Actions CI/CD | ✅ | Tests + Build |
| 1.12 | 271 testi | ✅ | 100% läbitus |

---

## Sprint 2: Turvalisus & Stabiilsus (nädalad 3–4) ✅ VALMIS

| # | Ülesanne | Olek | Tegelik |
|---|----------|------|---------|
| 2.1 | Parooli valideerimine (min 6 tähte) | ✅ | Pydantic Field |
| 2.2 | Email normaliseerimine | ✅ | lowercase + strip |
| 2.3 | CORS piiramine | ✅ | Kindlad meetodid |
| 2.4 | Rate limiting | ✅ | 60 req/min, in-memory |
| 2.5 | Token blacklisting (logout) | ✅ | SQLite |
| 2.6 | is_active kontroll | ✅ | get_current_user |
| 2.7 | SRS input valideerimine | ✅ | Field(ge=0, le=5) |
| 2.8 | Frontend auth turvalisus | ✅ | sessionStorage |
| 2.9 | Kriitiline audit | ✅ | CRITICAL_AUDIT.md |
| 2.10 | Audit & hindamine | ✅ | AUDIT_VALUATION.md |

---

## Sprint 3: Valmisriist & Kvaliteet (nädalad 5–6) 🔄 KÄIB

| # | Ülesanne | Olek | Tegelik |
|---|----------|------|---------|
| 3.1 | E2E testid (3 kasutajateekonda) | ✅ | test_e2e.py |
| 3.2 | API dokumentatsioon (OpenAPI) | ✅ | FastAPI auto-gen |
| 3.3 | .env.example | ✅ | backend/.env.example |
| 3.4 | conftest.py ühtlustamine | ✅ | 271 testi läbitud |
| 3.5 | Android APK build | 🟡 | GitHub Actions, vaja EXPO_TOKEN |
| 3.6 | Frontend lint | ✅ | npm run lint |
| 3.7 | Docker build | ✅ | Backend + Frontend |

---

## Sprint 4: Laiendused (nädalad 7–8) 📋 PLANEERITUD

| # | Ülesanne | Prioriteet | Hinnang |
|---|----------|-----------|---------|
| 4.1 | Mitmekeelsus (eesti keel UI) | 🔴 Kõrge | 2–3 päeva |
| 4.2 | Audio tugi (TTS) | 🔴 Kõrge | 3–5 päeva |
| 4.3 | Valik harjutustüübid (MCQ, listening) | 🔴 Kõrge | 5–7 päeva |
| 4.4 | AI konvestioon | 🟡 Keskmine | 7–10 päeva |
| 4.5 | PostgreSQL migration | 🟡 Keskmine | 2–3 päeva |
| 4.6 | Redis (rate limiting + blacklisting) | 🟡 Keskmine | 1–2 päeva |
| 4.7 | Refresh token | 🟡 Keskmine | 1 päev |
| 4.8 | Frontend testid (Jest) | 🟡 Keskmine | 3–4 päeva |

---

## Sprint 5: Avalik Lansseerimine (nädalad 9–10) 📋 PLANEERITUD

| # | Ülesanne | Prioriteet | Hinnang |
|---|----------|-----------|---------|
| 5.1 | Play Store / App Store avalik lansseerimine | 🔴 Kõrge | 2–3 päeva |
| 5.2 | Kasutajate tagasiside kogumine | 🟡 Keskmine | Jooksev |
| 5.3 | Analytics (Mixpanel/PostHog) | 🟡 Keskmine | 1–2 päeva |
| 5.4 | A/B testimine | 🟢 Madal | 2–3 päeva |

---

## Riskid

| # | Risk | Tõenäosus | Mõju | Lahendus |
|---|------|-----------|------|---------|
| 1 | EAS login ebaõnnestub | 🟡 Keskmine | 🟡 Keskmine | Kasuta GitHub Actions APK build |
| 2 | Grammatika mootor ebatäpne | 🔴 Kõrge | 🟡 Keskmine | Kasuta omorfi/libvoikki |
| 3 | Audio TTS kvaliteet | 🟡 Keskmine | 🟡 Keskmine | Kasuta Piper TTS |
| 4 | PostgreSQL migratsioon | 🟢 Madal | 🟡 Keskmine | Kasuta Alembic |

---

## Mõõdikud (KPIs)

| # | Mõõdik | Praegu | Sprint 4 eesmärk |
|---|--------|--------|-----------------|
| 1 | Testide arv | 271 | 350+ |
| 2 | Testide läbitus | 100% | 100% |
| 3 | Sõnade arv | 500+ | 750+ |
| 4 | API endpointid | 8 | 12+ |
| 5 | CVE-d | 0 | 0 |
| 6 | Dokumentatsioon | 4 faili | 6+ faili |

---

## Meeskond

| Roll | Isik | Vastutus |
|------|------|----------|
| Arendus | Sten | Kõik |
| Audit | OWL | Koodi ülevaatus |
| Testimine | OWL + Sten | Testid |

---

**Viimati uuendatud:** 2026-06-24
**Versioon:** 0.1.0
**Staatus:** MVP valmis, Sprint 3 käib
