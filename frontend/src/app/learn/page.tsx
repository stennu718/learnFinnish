"use client";

import { useEffect, useState } from "react";
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

export default function LearnPage() {
  const token = useAuthStore((s) => s.token);
  const router = useRouter();
  const [cards, setCards] = useState<DueCard[]>([]);
  const [current, setCurrent] = useState(0);
  const [answer, setAnswer] = useState("");
  const [showResult, setShowResult] = useState(false);
  const [correct, setCorrect] = useState(false);
  const [score, setScore] = useState({ correct: 0, total: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      router.push("/login");
      return;
    }
    loadCards();
  }, [token]);

  async function loadCards() {
    setLoading(true);
    try {
      // Init cards if needed
      await api.initSRS(token!);
      const due = await api.getDueCards(token!);
      setCards(due);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!cards[current]) return;

    const card = cards[current];
    const expected = card.direction === "et_fi" ? card.finnish : card.estonian;
    const isCorrect = answer.trim().toLowerCase() === expected.toLowerCase();
    setCorrect(isCorrect);
    setShowResult(true);

    // Submit review
    const quality = isCorrect ? 4 : 1;
    await api.reviewCard(token!, card.card_id, quality);

    setScore((s) => ({ correct: s.correct + (isCorrect ? 1 : 0), total: s.total + 1 }));
  }

  function nextCard() {
    setShowResult(false);
    setAnswer("");
    setCurrent((c) => c + 1);
  }

  if (!token) return null;

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">Loading cards...</p>
      </main>
    );
  }

  if (cards.length === 0 || current >= cards.length) {
    return (
      <main className="min-h-screen flex flex-col items-center justify-center gap-4">
        <h1 className="text-3xl font-bold">🎉 Session Complete!</h1>
        <p className="text-xl">Score: {score.correct}/{score.total}</p>
        <button
          onClick={() => { setCurrent(0); setScore({ correct: 0, total: 0 }); loadCards(); }}
          className="bg-[#003580] text-white px-6 py-2 rounded-lg font-semibold hover:bg-[#002a66] transition"
        >
          Practice More
        </button>
      </main>
    );
  }

  const card = cards[current];
  const question = card.direction === "et_fi" ? card.estonian : card.finnish;
  const answer_lang = card.direction === "et_fi" ? "Finnish" : "Estonian";

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-lg">
        {/* Progress */}
        <div className="flex justify-between text-sm text-gray-500 mb-4">
          <span>Card {current + 1} of {cards.length}</span>
          <span>✅ {score.correct}/{score.total}</span>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-lg border p-8 text-center">
          <p className="text-sm text-gray-400 mb-2 uppercase tracking-wide">{card.category} · Translate to {answer_lang}</p>
          <h2 className="text-4xl font-bold mb-8">{question}</h2>

          {!showResult ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              <input
                type="text"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder={`Type in ${answer_lang}...`}
                className="w-full border-2 rounded-lg px-4 py-3 text-lg text-center focus:ring-2 focus:ring-blue-500 focus:outline-none"
                autoFocus
              />
              <button
                type="submit"
                className="w-full bg-[#003580] text-white py-3 rounded-lg font-semibold hover:bg-[#002a66] transition"
              >
                Check
              </button>
            </form>
          ) : (
            <div className="space-y-4">
              <div className={`text-2xl font-bold ${correct ? "text-green-600" : "text-red-600"}`}>
                {correct ? "✅ Correct!" : "❌ Not quite"}
              </div>
              {!correct && (
                <p className="text-lg">
                  Answer: <span className="font-semibold">{card.direction === "et_fi" ? card.finnish : card.estonian}</span>
                </p>
              )}
              <button
                onClick={nextCard}
                className="w-full bg-gray-800 text-white py-3 rounded-lg font-semibold hover:bg-gray-700 transition"
              >
                Next →
              </button>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
