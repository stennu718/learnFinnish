"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/authStore";
import { api } from "@/lib/api";

interface DueCard {
  card_id: number;
  word_pair_id: number;
  estonian: string;
  finnish: string;
  direction: string;
  category: string;
}

interface Progress {
  xp: number;
  level: number;
  total_reviews: number;
  correct_reviews: number;
}

type CardState = "answering" | "correct" | "incorrect" | "completed";

export default function LearnPage() {
  const token = useAuthStore((s) => s.token);
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);

  const [cards, setCards] = useState<DueCard[]>([]);
  const [current, setCurrent] = useState(0);
  const [answer, setAnswer] = useState("");
  const [hint, setHint] = useState("");
  const [hintLevel, setHintLevel] = useState(0); // 0=none, 1=first letter, 2=first+last, 3=almost
  const [state, setState] = useState<CardState>("answering");
  const [streak, setStreak] = useState(0);
  const [bestStreak, setBestStreak] = useState(0);
  const [totalCorrect, setTotalCorrect] = useState(0);
  const [totalAnswered, setTotalAnswered] = useState(0);
  const [loading, setLoading] = useState(true);
  const [xp, setXp] = useState(0);
  const [showXpPopup, setShowXpPopup] = useState(0);
  const [shake, setShake] = useState(false);

  const card = cards[current];
  const expected = card
    ? card.direction === "et_fi"
      ? card.finnish
      : card.estonian
    : "";
  const question = card
    ? card.direction === "et_fi"
      ? card.estonian
      : card.finnish
    : "";
  const targetLang = card
    ? card.direction === "et_fi"
      ? "finnish"
      : "estonian"
    : "";

  useEffect(() => {
    if (!token) {
      router.push("/login");
      return;
    }
    loadCards();
    loadProgress();
  }, [token]);

  useEffect(() => {
    if (state === "answering" && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [current, state]);

  // Keyboard shortcuts
  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (state === "answering") {
        if (e.key === "Enter" && answer.trim()) {
          e.preventDefault();
          checkAnswer();
        }
        if (e.key === "Tab" && !answer.trim()) {
          e.preventDefault();
          showHint();
        }
      } else if (state === "correct" || state === "incorrect") {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          nextCard();
        }
      }
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  });

  async function loadCards() {
    setLoading(true);
    try {
      await api.initSRS(token!);
      const due = await api.getDueCards(token!);
      setCards(due);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  async function loadProgress() {
    try {
      const p: Progress = await api.getProgress(token!);
      setXp(p.xp || 0);
    } catch {
      // ignore
    }
  }

  function generateHint(word: string, level: number): string {
    if (level === 0) return "";
    if (level === 1) return word[0] + "·".repeat(word.length - 1);
    if (level === 2) return word[0] + "·".repeat(word.length - 2) + word[word.length - 1];
    // level 3: show first half
    const half = Math.ceil(word.length / 2);
    return word.slice(0, half) + "·".repeat(word.length - half);
  }

  function showHint() {
    if (hintLevel >= 3) return;
    const newLevel = hintLevel + 1;
    setHintLevel(newLevel);
    setHint(generateHint(expected, newLevel));
  }

  async function checkAnswer() {
    if (!card || !answer.trim()) return;

    const normalized = answer.trim().toLowerCase().replace(/[,!.?]/g, "");
    const expectedNorm = expected.toLowerCase().replace(/[,!.?]/g, "");

    // Fuzzy match: allow minor typos (1 char difference for words > 3 chars)
    const isCorrect = normalized === expectedNorm || fuzzyMatch(normalized, expectedNorm);

    setState(isCorrect ? "correct" : "incorrect");
    setTotalAnswered((t) => t + 1);

    const quality = isCorrect ? (hintLevel === 0 ? 5 : hintLevel === 1 ? 4 : 3) : 1;

    try {
      const result = await api.reviewCard(token!, card.card_id, quality);
      if (result.xp_earned) {
        setXp((x) => x + result.xp_earned);
        setShowXpPopup(result.xp_earned);
        setTimeout(() => setShowXpPopup(0), 1000);
      }
    } catch {
      // ignore
    }

    if (isCorrect) {
      setTotalCorrect((t) => t + 1);
      setStreak((s) => {
        const newStreak = s + 1;
        setBestStreak((b) => Math.max(b, newStreak));
        return newStreak;
      });
    } else {
      setStreak(0);
    }
  }

  function fuzzyMatch(a: string, b: string): boolean {
    if (Math.abs(a.length - b.length) > 1) return false;
    if (a.length <= 3) return false;
    let diffs = 0;
    const maxLen = Math.max(a.length, b.length);
    for (let i = 0; i < maxLen; i++) {
      if (a[i] !== b[i]) diffs++;
      if (diffs > 1) return false;
    }
    return diffs <= 1;
  }

  function nextCard() {
    if (current + 1 >= cards.length) {
      setState("completed");
      return;
    }
    setCurrent((c) => c + 1);
    setAnswer("");
    setHint("");
    setHintLevel(0);
    setState("answering");
    setShake(false);
  }

  function skipCard() {
    nextCard();
  }

  // Loading
  if (!token) return null;
  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#003580] to-[#0072ce]">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-white/30 border-t-white rounded-full animate-spin mx-auto mb-4" />
          <p className="text-white/80 text-lg">Loading your cards...</p>
        </div>
      </main>
    );
  }

  // Completed
  if (state === "completed" || cards.length === 0) {
    const accuracy = totalAnswered > 0 ? Math.round((totalCorrect / totalAnswered) * 100) : 0;
    return (
      <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#003580] to-[#0072ce] px-4">
        <div className="bg-white rounded-3xl shadow-2xl p-10 text-center max-w-md w-full">
          <div className="text-6xl mb-4">
            {accuracy >= 80 ? "🏆" : accuracy >= 50 ? "💪" : "📚"}
          </div>
          <h1 className="text-3xl font-bold mb-2">Session Complete!</h1>
          <p className="text-gray-500 mb-6">Great work, keep it up!</p>

          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="bg-gray-50 rounded-xl p-4">
              <div className="text-2xl font-bold text-[#003580]">{totalCorrect}/{totalAnswered}</div>
              <div className="text-xs text-gray-400 mt-1">Correct</div>
            </div>
            <div className="bg-gray-50 rounded-xl p-4">
              <div className="text-2xl font-bold text-orange-500">🔥 {bestStreak}</div>
              <div className="text-xs text-gray-400 mt-1">Best Streak</div>
            </div>
            <div className="bg-gray-50 rounded-xl p-4">
              <div className="text-2xl font-bold text-green-500">{accuracy}%</div>
              <div className="text-xs text-gray-400 mt-1">Accuracy</div>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => {
                setCurrent(0);
                setTotalCorrect(0);
                setTotalAnswered(0);
                setStreak(0);
                setBestStreak(0);
                setState("answering");
                loadCards();
              }}
              className="flex-1 bg-[#003580] text-white py-3 rounded-xl font-semibold hover:bg-[#002a66] transition"
            >
              Practice More
            </button>
            <button
              onClick={() => router.push("/")}
              className="flex-1 bg-gray-100 text-gray-700 py-3 rounded-xl font-semibold hover:bg-gray-200 transition"
            >
              Home
            </button>
          </div>
        </div>
      </main>
    );
  }

  const progress = ((current + 1) / cards.length) * 100;

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#003580] to-[#0072ce] flex flex-col">
      {/* Top Bar */}
      <div className="flex items-center justify-between px-4 py-3 text-white">
        <button onClick={() => router.push("/")} className="text-white/70 hover:text-white transition">
          ← Back
        </button>
        <div className="flex items-center gap-4">
          {streak > 0 && (
            <span className="bg-orange-500/20 text-orange-300 px-3 py-1 rounded-full text-sm font-semibold">
              🔥 {streak}
            </span>
          )}
          <span className="bg-white/10 px-3 py-1 rounded-full text-sm">
            ⭐ {xp} XP
          </span>
        </div>
      </div>

      {/* XP Popup */}
      {showXpPopup > 0 && (
        <div className="fixed top-20 left-1/2 -translate-x-1/2 z-50 animate-bounce">
          <div className="bg-green-500 text-white px-4 py-2 rounded-full font-bold shadow-lg">
            +{showXpPopup} XP
          </div>
        </div>
      )}

      {/* Progress Bar */}
      <div className="px-4 mb-2">
        <div className="h-1.5 bg-white/20 rounded-full overflow-hidden">
          <div
            className="h-full bg-white rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="flex justify-between text-white/50 text-xs mt-1">
          <span>{current + 1} / {cards.length}</span>
          <span>{totalCorrect} correct</span>
        </div>
      </div>

      {/* Card Area */}
      <div className="flex-1 flex items-center justify-center px-4 pb-8">
        <div
          className={`bg-white rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden transition-all duration-200 ${
            shake ? "animate-[shake_0.3s_ease-in-out]" : ""
          }`}
        >
          {/* Card Header */}
          <div className="px-6 pt-5 pb-2 flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">
              {card.category}
            </span>
            <span className="text-xs text-gray-400">
              {card.direction === "et_fi" ? "🇪🇪 → 🇫🇮" : "🇫🇮 → 🇪🇪"}
            </span>
          </div>

          {/* Question */}
          <div className="px-6 py-4 text-center">
            <h2 className="text-3xl font-bold text-gray-900">{question}</h2>
          </div>

          {/* Answer Area */}
          <div className="px-6 pb-6">
            {state === "answering" && (
              <>
                {/* Hint */}
                {hint && (
                  <div className="text-center mb-3">
                    <span className="inline-block bg-yellow-50 text-yellow-700 px-4 py-1.5 rounded-lg text-sm font-mono tracking-wider">
                      {hint}
                    </span>
                  </div>
                )}

                {/* Input */}
                <form onSubmit={(e) => { e.preventDefault(); checkAnswer(); }}>
                  <input
                    ref={inputRef}
                    type="text"
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    placeholder={`Type in ${targetLang === "finnish" ? "Finnish" : "Estonian"}...`}
                    className="w-full border-2 border-gray-200 rounded-xl px-4 py-3.5 text-lg text-center focus:border-[#003580] focus:outline-none transition-colors"
                    autoComplete="off"
                    autoCorrect="off"
                    autoCapitalize="off"
                    spellCheck={false}
                  />
                </form>

                {/* Action Buttons */}
                <div className="flex gap-3 mt-4">
                  {hintLevel < 3 && (
                    <button
                      onClick={showHint}
                      className="flex-1 bg-yellow-50 text-yellow-700 py-3 rounded-xl font-semibold hover:bg-yellow-100 transition text-sm"
                    >
                      💡 Hint {hintLevel > 0 ? `(${hintLevel}/3)` : ""}
                    </button>
                  )}
                  <button
                    onClick={skipCard}
                    className="flex-1 bg-gray-50 text-gray-500 py-3 rounded-xl font-semibold hover:bg-gray-100 transition text-sm"
                  >
                    Skip →
                  </button>
                  <button
                    onClick={checkAnswer}
                    disabled={!answer.trim()}
                    className="flex-[2] bg-[#003580] text-white py-3 rounded-xl font-semibold hover:bg-[#002a66] disabled:opacity-40 disabled:cursor-not-allowed transition"
                  >
                    Check ↵
                  </button>
                </div>

                {/* Keyboard hint */}
                <p className="text-center text-xs text-gray-300 mt-3">
                  Press <kbd className="bg-gray-100 px-1.5 py-0.5 rounded text-gray-500 font-mono">Enter</kbd> to check · <kbd className="bg-gray-100 px-1.5 py-0.5 rounded text-gray-500 font-mono">Tab</kbd> for hint
                </p>
              </>
            )}

            {state === "correct" && (
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-3">
                  <span className="text-3xl">✓</span>
                </div>
                <p className="text-green-600 font-bold text-lg mb-1">Correct!</p>
                <p className="text-gray-500 text-sm mb-4">
                  {hintLevel === 0 && "Perfect — no hints needed! 🌟"}
                  {hintLevel === 1 && "Good! You used 1 hint."}
                  {hintLevel === 2 && "Nice! You used 2 hints."}
                  {hintLevel === 3 && "Got it! Keep practicing this one."}
                </p>
                <button
                  onClick={nextCard}
                  className="w-full bg-green-500 text-white py-3.5 rounded-xl font-semibold hover:bg-green-600 transition"
                >
                  Continue →
                </button>
                <p className="text-xs text-gray-300 mt-2">Press Enter or Space</p>
              </div>
            )}

            {state === "incorrect" && (
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-3">
                  <span className="text-3xl">✗</span>
                </div>
                <p className="text-red-500 font-bold text-lg mb-1">Not quite</p>
                <div className="bg-gray-50 rounded-xl p-4 mb-4">
                  <p className="text-sm text-gray-400 mb-1">Correct answer:</p>
                  <p className="text-2xl font-bold text-gray-900">{expected}</p>
                  {answer.trim() && (
                    <p className="text-sm text-gray-400 mt-2">
                      Your answer: <span className="line-through text-red-400">{answer}</span>
                    </p>
                  )}
                </div>
                <button
                  onClick={nextCard}
                  className="w-full bg-[#003580] text-white py-3.5 rounded-xl font-semibold hover:bg-[#002a66] transition"
                >
                  Got it →
                </button>
                <p className="text-xs text-gray-300 mt-2">Press Enter or Space</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
