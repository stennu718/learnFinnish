"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/authStore";
import { api } from "@/lib/api";

interface GrammarRule {
  name: string;
  estonian_ending: string;
  finnish_ending: string;
  description: string;
  examples: Array<{ est: string; fi_word: string; et: string; fi_sentence: string }>;
}

interface GrammarExercise {
  rule_name: string;
  description: string;
  estonian: string;
  finnish: string;
  estonian_sentence: string;
  finnish_sentence: string;
}

export default function GrammarPage() {
  const token = useAuthStore((s) => s.token);
  const router = useRouter();
  const [rules, setRules] = useState<GrammarRule[]>([]);
  const [selectedRule, setSelectedRule] = useState<GrammarRule | null>(null);
  const [exercise, setExercise] = useState<GrammarExercise | null>(null);
  const [answer, setAnswer] = useState("");
  const [showResult, setShowResult] = useState(false);
  const [correct, setCorrect] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) { router.push("/login"); return; }
    loadRules();
  }, [token]);

  async function loadRules() {
    setLoading(true);
    try {
      const resp = await fetch("http://localhost:8000/api/grammar/rules", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (resp.ok) setRules(await resp.json());
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }

  async function loadExercise(ruleName: string) {
    try {
      const resp = await fetch(`http://localhost:8000/api/grammar/exercises/${ruleName}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (resp.ok) {
        const ex = await resp.json();
        setExercise(ex);
        setSelectedRule(rules.find(r => r.name === ruleName) || null);
        setShowResult(false);
        setAnswer("");
      }
    } catch (e) { console.error(e); }
  }

  function checkAnswer() {
    if (!exercise) return;
    const isCorrect = answer.trim().toLowerCase() === exercise.finnish.toLowerCase();
    setCorrect(isCorrect);
    setShowResult(true);
  }

  if (!token) return null;
  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#003580] to-[#0072ce]">
        <div className="text-white text-lg">Loading grammar rules...</div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#003580] to-[#0072ce] p-4">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <button onClick={() => router.push("/")} className="text-white/70 hover:text-white">
            ← Back
          </button>
          <h1 className="text-2xl font-bold text-white">📐 Grammar</h1>
          <div />
        </div>

        {!exercise ? (
          <div className="space-y-3">
            <p className="text-white/70 mb-4">Select a case transformation rule to practice:</p>
            {rules.map((rule) => (
              <button
                key={rule.name}
                onClick={() => loadExercise(rule.name)}
                className="w-full bg-white rounded-xl p-4 text-left hover:shadow-lg transition"
              >
                <div className="font-semibold text-gray-900 capitalize">{rule.name}</div>
                <div className="text-sm text-gray-500 mt-1">{rule.description}</div>
                <div className="text-xs text-gray-400 mt-2">
                  {rule.estonian_ending} → {rule.finnish_ending}
                </div>
              </button>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">
                {selectedRule?.name}
              </span>
              <button onClick={() => setExercise(null)} className="text-sm text-gray-400 hover:text-gray-600">
                ← Back to rules
              </button>
            </div>

            <p className="text-sm text-gray-500 mb-4">{selectedRule?.description}</p>

            <div className="bg-blue-50 rounded-xl p-4 mb-4">
              <p className="text-xs text-blue-400 mb-1">Estonian sentence:</p>
              <p className="text-lg font-semibold text-gray-900">{exercise.estonian_sentence}</p>
            </div>

            {!showResult ? (
              <>
                <p className="text-sm text-gray-500 mb-2">Translate to Finnish:</p>
                <input
                  type="text"
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Type in Finnish..."
                  className="w-full border-2 rounded-xl px-4 py-3 text-lg text-center focus:border-[#003580] focus:outline-none"
                  autoFocus
                  onKeyDown={(e) => { if (e.key === "Enter" && answer.trim()) checkAnswer(); }}
                />
                <button
                  onClick={checkAnswer}
                  disabled={!answer.trim()}
                  className="w-full mt-4 bg-[#003580] text-white py-3 rounded-xl font-semibold disabled:opacity-40"
                >
                  Check
                </button>
              </>
            ) : (
              <div className="text-center">
                <div className={`text-2xl font-bold mb-2 ${correct ? "text-green-600" : "text-red-600"}`}>
                  {correct ? "✅ Correct!" : "❌ Not quite"}
                </div>
                {!correct && (
                  <div className="bg-gray-50 rounded-xl p-4 mb-4">
                    <p className="text-sm text-gray-400">Correct answer:</p>
                    <p className="text-xl font-bold">{exercise.finnish_sentence}</p>
                  </div>
                )}
                <button
                  onClick={() => { setExercise(null); setAnswer(""); setShowResult(false); }}
                  className="w-full bg-[#003580] text-white py-3 rounded-xl font-semibold"
                >
                  Next Exercise
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
