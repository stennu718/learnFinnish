import React, { useEffect, useState } from "react";
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator } from "react-native";
import { useAuthStore } from "@/src/store/authStore";
import { api } from "@/src/services/api";

interface DueCard {
  card_id: number;
  word_pair_id: number;
  estonian: string;
  finnish: string;
  direction: string;
  category: string;
}

export function LearnScreen() {
  const token = useAuthStore((s) => s.token);
  const [cards, setCards] = useState<DueCard[]>([]);
  const [current, setCurrent] = useState(0);
  const [answer, setAnswer] = useState("");
  const [showResult, setShowResult] = useState(false);
  const [correct, setCorrect] = useState(false);
  const [score, setScore] = useState({ correct: 0, total: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCards();
  }, []);

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

  async function handleSubmit() {
    if (!cards[current]) return;
    const card = cards[current];
    const expected = card.direction === "et_fi" ? card.finnish : card.estonian;
    const isCorrect = answer.trim().toLowerCase() === expected.toLowerCase();
    setCorrect(isCorrect);
    setShowResult(true);
    await api.reviewCard(token!, card.card_id, isCorrect ? 4 : 1);
    setScore((s) => ({ correct: s.correct + (isCorrect ? 1 : 0), total: s.total + 1 }));
  }

  function nextCard() {
    setShowResult(false);
    setAnswer("");
    setCurrent((c) => c + 1);
  }

  if (loading) return <View style={s.center}><ActivityIndicator size="large" /><Text>Loading...</Text></View>;
  if (cards.length === 0 || current >= cards.length) return (
    <View style={s.center}>
      <Text style={s.big}>🎉 Done!</Text>
      <Text style={s.score}>Score: {score.correct}/{score.total}</Text>
      <TouchableOpacity style={s.btn} onPress={() => { setCurrent(0); setScore({ correct: 0, total: 0 }); loadCards(); }}>
        <Text style={s.btnText}>Practice More</Text>
      </TouchableOpacity>
    </View>
  );

  const card = cards[current];
  const question = card.direction === "et_fi" ? card.estonian : card.finnish;
  const answerLang = card.direction === "et_fi" ? "Finnish" : "Estonian";

  return (
    <View style={s.container}>
      <View style={s.header}>
        <Text style={s.progress}>{current + 1}/{cards.length}</Text>
        <Text style={s.scoreText}>✅ {score.correct}/{score.total}</Text>
      </View>

      <View style={s.card}>
        <Text style={s.category}>{card.category} · To {answerLang}</Text>
        <Text style={s.question}>{question}</Text>

        {!showResult ? (
          <>
            <TextInput
              style={s.input}
              value={answer}
              onChangeText={setAnswer}
              placeholder={`Type in ${answerLang}...`}
              autoFocus
            />
            <TouchableOpacity style={s.btn} onPress={handleSubmit}>
              <Text style={s.btnText}>Check</Text>
            </TouchableOpacity>
          </>
        ) : (
          <>
            <Text style={[s.result, correct ? s.correct : s.wrong]}>
              {correct ? "✅ Correct!" : "❌ Not quite"}
            </Text>
            {!correct && <Text style={s.answer}>Answer: {card.direction === "et_fi" ? card.finnish : card.estonian}</Text>}
            <TouchableOpacity style={s.btn} onPress={nextCard}>
              <Text style={s.btnText}>Next →</Text>
            </TouchableOpacity>
          </>
        )}
      </View>
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, padding: 24, backgroundColor: "#f8f9fa", justifyContent: "center" },
  center: { flex: 1, justifyContent: "center", alignItems: "center", padding: 24 },
  header: { flexDirection: "row", justifyContent: "space-between", marginBottom: 20 },
  progress: { color: "#666", fontSize: 14 },
  scoreText: { color: "#666", fontSize: 14 },
  card: { backgroundColor: "#fff", borderRadius: 16, padding: 24, shadowColor: "#000", shadowOpacity: 0.1, shadowRadius: 8, elevation: 3 },
  category: { color: "#999", fontSize: 12, textTransform: "uppercase", marginBottom: 8 },
  question: { fontSize: 32, fontWeight: "bold", textAlign: "center", marginBottom: 24 },
  input: { borderWidth: 2, borderColor: "#e5e7eb", borderRadius: 12, padding: 16, fontSize: 18, textAlign: "center", marginBottom: 16 },
  btn: { backgroundColor: "#003580", padding: 16, borderRadius: 12, alignItems: "center" },
  btnText: { color: "#fff", fontSize: 18, fontWeight: "600" },
  result: { fontSize: 24, fontWeight: "bold", textAlign: "center", marginBottom: 12 },
  correct: { color: "#16a34a" },
  wrong: { color: "#dc2626" },
  answer: { fontSize: 18, textAlign: "center", marginBottom: 16 },
  big: { fontSize: 32, fontWeight: "bold", marginBottom: 8 },
  score: { fontSize: 20, color: "#666", marginBottom: 24 },
});
