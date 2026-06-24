# Audit & Hindamine — learnFinnish

**Kuupäev:** 2026-06-24
**Audiitor:** OWL
**Projekt:** Eesti-Soome keeleõppe veebi- ja mobiilirakendus

---

## 1. Ülevaade

| Metrik | Väärtus |
|--------|---------|
| Koodiridu | ~19 270 |
| Faile | 85 |
| Testide arv | 271 |
| Testide läbitus | 100% |
| Kategooriad | 22 (sõnad) + grammatika |
| Kepleruhver | 500+ sõna |
| Backend | FastAPI + SQLite |
| Frontend | Next.js 15 + Tailwind |
| Mobiil | React Native + Expo |
| CI/CD | GitHub Actions |
| Dokumentatsioon | STRATEGY.md, TESTPLAN.md, AUDIT.md, CRITICAL_AUDIT.md |

---

## 2. Turvalisus — HINNANG: 7/10

### Tugevused:
| # | Funktsioon | Olek |
|---|-----------|------|
| 1 | Bcrypt parooli hashimine | ✅ |
| 2 | JWT tokenite aegumine (1 päev) | ✅ |
| 3 | Input valideerimine (parooli pikkus, email) | ✅ |
| 4 | CORS piiratud meetodid ja päised | ✅ |
| 5 | is_active kontroll | ✅ |
| 6 | Rate limiting (60 req/min) | ✅ |
| 7 | Token blacklisting (logout) | ✅ |
| 8 | SQL injection kaitse (SQLAlchemy ORM) | ✅ |

### Nõrkused:
| # | Probleem | Prioriteet |
|---|----------|-----------|
| 1 | SECRET_KEY genereeritakse igal käivitamisel — kui protsess taaskäivitub, muutuvad kõik tokenid kehtetuks | 🟡 Keskmine |
| 2 | SQLite ei sobi production'i (mitme kasutaja samaaegne ligipääs) | 🟡 Keskmine |
| 3 | Token blacklisting kasutab SQLite'il (ei pärasta skaleerimist) | 🟡 Keskmine |
| 4 | Rate limiting on in-memory (ei pärasta skaleerimist) | 🟡 Keskmine |
| 5 | HTTPS puudub arenduskeskkonnas | 🟢 Madal |
| 6 | Refresh token puudub | 🟡 Keskmine |

### Soovitused:
- Kasuta PostgreSQL production'i jaoks
- Kasuta Redis rate limiting'u ja token blacklisting'u jaoks
- Lisa refresh token võimalus
- Kasuta keskkonnamuutujat SECRET_KEY'le (mitte auto-genereerimine)

### Turvalisuse hinnang: **7/10**
- Põhilised turvamehhanismid olemas
- Production'i jaoks vaja täiendusi (PostgreSQL, Redis, HTTPS)

---

## 3. Arhitektuur — HINNANG: 8/10

### Tugevused:
| # | Funktsioon | Olek |
|---|-----------|------|
| 1 | Clean separation (backend/frontend/mobile) | ✅ |
| 2 | FastAPI async arhitektuur | ✅ |
| 3 | Zustand state management | ✅ |
| 4 | SQLAlchemy async ORM | ✅ |
| 5 | Docker + docker-compose | ✅ |
| 6 | GitHub Actions CI/CD | ✅ |
| 7 | Rate limiting middleware | ✅ |

### Nõrkused:
| # | Probleem | Prioriteet |
|---|----------|-----------|
| 1 | Monolite deploy (backend + frontend sama Docker) | 🟢 Madal |
| 2 | Puudub eraldi dokumentatsiooni API dokumentatsioon (OpenAPI) | 🟢 Madal |
| 3 | Puudub health check endpoint detailsemalt | 🟢 Madal |
| 4 | Android prebuild tehtud aga Gradle build puudub | 🟡 Keskmine |

### Arhitektuuri hinnang: **8/10**
- Selge, korrastatud arhitektuur
- Modern tehnoloogia
- Kerge kasutada ja laiendada

---

## 4. Koodi kvaliteet — HINNANG: 7/10

### Tugevused:
| # | Funktsioon | Olek |
|---|-----------|------|
| 1 | Pydantic valideerimine kõigis API endpointides | ✅ |
| 2 | Type kinnitused (Python + TypeScript) | ✅ |
| 3 | Korrektne veakäsitlus (HTTPException) | ✅ |
| 4 | Dokumentatsioon (docstring'id) | ✅ |
| 5 | PEP 8 / ESLint konventsioonid | ✅ |

### Nõrkused:
| # | Probleem | Prioriteet |
|---|----------|-----------|
| 1 | Grammatika mootor on lihtsalt heuristic'ist ei tööta keerukate sõnadega | 🔴 Kõrge |
| 2 | Frontend ei kasuta eraldi API klienti (osaliselt duplikaat kood) | 🟡 Keskmine |
| 3 | Mõned API endpointid ei tagasta korrektseid veakoodeid | 🟡 Keskmine |
| 4 | Puudub request logging | 🟢 Madal |
| 5 | Frontend'is on palju korduvat koodi | 🟡 Keskmine |

### Koodi kvaliteedi hinnang: **7/10**
- Hea tehtud, korralik kood
- Vaja: grammatika mootor, API klient, request logging

---

## 5. Funktsionaalsus — HINNANG: 7.5/10

### Tugevused:
| # | Funktsioon | Olek |
|---|-----------|------|
| 1 | Kasutaja registreerimine + autentimine | ✅ |
| 2 | 500+ sõna, 22 kategooriat | ✅ |
| 3 | SM-2 SRS algoritm | ✅ |
| 4 | Spaced repetition (hintadega) | ✅ |
| 5 | Eesti ↔ Soome tõlge mõlemas suunas | ✅ |
| 6 | Progressi jälgimine (XP, level, streaks) | ✅ |
| 7 | Grammatika mootor (12 käänet) | ✅ |
| 8 | API dokumentatsioon | ✅ |

### Nõrkused:
| # | Probleem | Prioriteet |
|---|----------|-----------|
| 1 | Puudub audio tugi (native speaker recordings) | 🔴 Kõrge |
| 2 | Grammatika mootor on lihtsalt nimekiri | 🔴 Kõrge |
| 3 | Puudub valik harjutusi (MCQ, listening) | 🔴 Kõrge |
| 4 | Puudub konvestioon AI-ga | 🔴 Kõrge |
| 5 | Mobiili eluijooksjad pole | 🟡 Keskmine |
| 6 | GPX-formaadis eksport | 🟡 Keskmine |

### Soovitused:
- Lisa audio tugi või integreeri Piper TTS
- Arenda grammatika mootor täielikumaks
- Lisa mitu harjutustüüpi (MCQ, listening)
- Lisa AI konvestioon

### Funktsionaalsuse hinnang: **7.5/10**
- Põhifunktsionaalsus täielik
- Production'i jaoks vaja lisada: audio, valik harjutused, AI tugi

---

## 6. Testimine — HINNANG: 8.5/10

### Tugevused:
| # | Funktsioon | Olek |
|---|-----------|------|
| 1 | 271 testi, 100% läbitud | ✅ |
| 2 | Unit, Integration, E2E testid | ✅ |
| 3 | SM-2 algoritmi detailne testimine | ✅ |
| 4 | OOP testimine | ✅ |
| 5 | UI testimine | ✅ |

### Nõrkused:
| # | Probleem | Prioriteet |
|---|----------|-----------|
| 1 | Frontend testid puuduvad (Jest/Cypress) | 🟡 Keskmine |
| 2 | Mobiil testid puuduvad (Vitest/Playwright) | 🟡 Keskmine |
| 3 | E2E testid lühikesed | 🟢 Madal |
| 4 | OAuth testid puuduvad | 🟡 Keskmine |

### Testimise hinnang: **8.5/10**
- Väga hea testkatvus backend'is
- Vaja: frontend ja mobiil testid

---

## 7. Kasutatavus — HINNANG: 6.5/10

### Tugevused:
| # | Funktsioon | Olek |
|---|-----------|------|
| 1 | Intuitiivne UI (Lingvist stiil) | ✅ |
| 2 | Kiire flashcard-süsteem | ✅ |
| 3 | Progressi jälgimine | ✅ |
| 4 | Veaanimatsioonid | ✅ |

### Nõrkused:
| # | Probleem | Prioriteet |
|---|----------|-----------|
| 1 | Puudub mitmekeelne UI (eesti keel) | 🔴 Kõrge |
| 2 | Puudub fontide valik | 🟡 Keskmine |
| 3 | Mobiil ELUJÄLG erinevatel seadmetel | 🟡 Keskmine |
| 4 | Puudub animatsioonide süsteem | 🟡 Keskmine |

### Soovitused:
- Lisa eestikeelne UI
- Paranda mobiili elujälg
- Lisa animatsioonid

### Kasutatavuse hinnang: **6.5/10**
- Hea põhiosa
- Vaja: mitmekeelsus, interaktiivsus

---

## 8. Järeldus

| Kategooria | Hinnang |
|-----------|---------|
| Turvalisus | 7/10 |
| Arhitektuur | 8/10 |
| Koodi kvaliteet | 7/10 |
| Funktsionaalsus | 7.5/10 |
| Testimine | 8.5/10 |
| Kasutatavus | 6.5/10 |
| **KESKMINE** | **7.5/10** |

### Kokkuvõte:
- **Tugevad pooled:** Selge arhitektuur, 100% testi läbitus, turvalisus, modern tehnoloogia
- **Nõrkused:** Testid frontend/mobiilis puuduvad, mitmekeelsus puudub, grammatika mootor lihtsalt
- **Järgmised sammud:**
  1. Frontend testid (Jest)
  2. API dokumentatsioon (Swagger)
  3. Mitmekeelsus (eesti keel)
  4. Lisa grammatika mootor AI-ga
  5. Audio tugi (TTS)

---

**Audiitor:** OWL
**Kuupäev:** 2026-06-24
