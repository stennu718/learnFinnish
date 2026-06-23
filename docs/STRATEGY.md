# learnFinnish — Strategy & Architecture

> **Mission:** Build the best Estonia-Finnish language learning app in the world.
> Web + Mobile. Estonian ↔ Finnish. Made for Estonians learning Finnish.

---

## 🎯 Why This Will Win

The existing apps (Duolingo, Memrise, etc.) treat Finnish as just another language. They don't leverage the **massive structural overlap** between Estonian and Finnish — both are Finnic languages sharing ~50% lexical similarity, agglutinative morphology, vowel harmony, and 14+ cases.

**Our unfair advantage:** We build *specifically* for the Estonian→Finnish bridge.

---

## 🧠 Core Learning Philosophy

### 1. Cognate-First Approach
Start with words that are nearly identical (cognates), then gradually introduce divergence patterns:
- Estonian `jää` → Finnish `jää` (ice) ✅ identical
- Estonian `tuba` → Finnish `tupa` (room) ✅ vowel swap pattern
- Estonian `kool` → Finnish `koulu` (school) ✅ common divergence

### 2. Pattern-Based Grammar
Don't teach 14 Finnish cases in isolation. Teach the **Estonian→Finnish transformation rules**:
- Estonian `-s` (inessive)  Finnish `-ssa/-ssä`
- Estonian `-st` (elative)  Finnish `-sta/-stä`
- Estonian `-le` (allative)  Finnish `-lle`
- etc.

### 3. Spaced Repetition (SRS)
SM-2 algorithm adapted for bilingual pairs. Cards track:
- Recognition (Estonian → Finnish)
- Production (Finnish → Estonian)
- Audio comprehension
- Grammar pattern recall

### 4. Contextual Learning
Every word appears in a **real sentence** with audio. No isolated vocabulary.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                   CLIENTS                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Next.js  │  │ React    │  │ PWA (shared) │  │
│  │ Web App  │  │ Native   │  │              │  │
│  └────┬─────┘  └────┬─────┘  └──────┬───────┘  │
│       │              │               │          │
└───────┼──────────────┼───────────────┼──────────┘
        │              │               │
        └──────────────┼───────────────┘
                       │
              ┌────────▼────────┐
              │   FastAPI       │
              │   REST + WS     │
              │   Python 3.11+  │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │   PostgreSQL    │
              │   (prod)        │
              │   SQLite (dev)  │
              └─────────────────┘
```

### Tech Stack
| Layer | Tech | Why |
|-------|------|-----|
| **Backend** | FastAPI + SQLAlchemy | Async, fast, Python ecosystem |
| **DB** | SQLite (dev) / PostgreSQL (prod) | Simple dev, production-ready |
| **Frontend** | Next.js 15 + Tailwind | SSR, great DX, PWA support |
| **Mobile** | React Native (Expo) | Single codebase, native feel |
| **Auth** | JWT + email/password | Simple, no OAuth dependency |
| **Audio** | TTS (Piper) + recorded | Native speaker audio for top 500 words |
| **SRS** | Custom SM-2 | Tailored for bilingual cards |
| **Deploy** | Docker + Railway/Render | Sten prefers Docker |

---

## 📱 Feature Roadmap

### Phase 1 — MVP (Week 1-2)
- [x] Project scaffold
- [ ] User auth (register, login, JWT)
- [ ] 200 core word pairs (cognates first)
- [ ] SRS flashcard system
- [ ] 3 exercise types: multiple choice, type-in, listening
- [ ] Progress dashboard
- [ ] Basic mobile app (Expo)

### Phase 2 — Grammar Engine (Week 3-4)
- [ ] Case transformation trainer (14 cases)
- [ ] Verb conjugation patterns
- [ ] Vowel harmony visualizer
- [ ] "Why is it different?" explanations for each pattern
- [ ] Sentence builder exercises

### Phase 3 — Content Expansion (Week 5-6)
- [ ] 1000+ word pairs
- [ ] Themed vocabulary packs (work, travel, food, nature)
- [ ] Native speaker audio for top 500 words
- [ ] Example sentences with audio
- [ ] Cultural notes (Finnish culture for Estonians)

### Phase 4 — Social & Gamification (Week 7-8)
- [ ] Streaks & XP
- [ ] Leaderboards
- [ ] Daily challenges
- [ ] Study groups
- [ ] Progress sharing

### Phase 5 — AI Features (Week 9-10)
- [ ] AI conversation practice (Finnish chatbot)
- [ ] Pronunciation feedback (Whisper API)
- [ ] Adaptive difficulty
- [ ] Personalized review sessions
- [ ] Mistake pattern analysis

### Phase 6 — Polish & Scale (Week 11-12)
- [ ] Offline mode (mobile)
- [ ] Push notifications
- [ ] Widget (daily word)
- [ ] Apple Watch / Wear OS
- [ ] Performance optimization
- [ ] Accessibility audit

---

## 🔬 Competitive Analysis

| Feature | Duolingo | Memrise | **learnFinnish** |
|---------|----------|---------|-------------------|
| Estonian→Finnish path | ❌ | ❌ | ✅ **Native** |
| Cognate-first approach | ❌ | ❌ | ✅ |
| Pattern-based grammar | ❌ | ❌ | ✅ |
| Native speaker audio | Partial | Partial | ✅ Top 500 |
| Offline mobile | ❌ | ✅ | ✅ |
| AI conversation | ❌ | ❌ | ✅ |
| Cultural context | ❌ | ❌ | ✅ |
| Open source | ❌ | ❌ | ✅ |

---

## 📊 Success Metrics

- **Retention:** D1 > 60%, D7 > 30%, D30 > 15%
- **Learning:** 80% of users can translate 50 basic words after 7 days
- **Engagement:** 15+ min average session, 5+ sessions/week
- **NPS:** > 50

---

## 🌍 Market

- **Primary:** Estonians learning Finnish (~50K active learners)
- **Secondary:** Finnish people learning Estonian
- **Tertiary:** Linguists, language enthusiasts
- **Expansion:** Other Finnic languages (Võro, Karelian, etc.)
