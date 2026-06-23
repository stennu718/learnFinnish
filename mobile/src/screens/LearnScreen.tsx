import React, { useEffect, useState, useCallback, useRef } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Animated,
  Dimensions,
  Keyboard,
} from "react-native";
import { useAuthStore } from "@/src/store/authStore";
import { api } from "@/src/services/api";

const { width: SCREEN_WIDTH } = Dimensions.get("window");
const CARD_WIDTH = SCREEN_WIDTH - 32;

interface DueCard {
  card_id: number;
  word_pair_id: number;
  estonian: string;
  finnish: string;
  direction: string;
  category: string;
}

type CardState = "answering" | "correct" | "incorrect" | "completed";

export function LearnScreen({ navigation }: any) {
  const token = useAuthStore((s) => s.token);
  const inputRef = useRef<TextInput>(null);

  const [cards, setCards] = useState<DueCard[]>([]);
  const [current, setCurrent] = useState(0);
  const [answer, setAnswer] = useState("");
  const [hint, setHint] = useState("");
  const [hintLevel, setHintLevel] = useState(0);
  const [state, setState] = useState<CardState>("answering");
  const [streak, setStreak] = useState(0);
  const [bestStreak, setBestStreak] = useState(0);
  const [totalCorrect, setTotalCorrect] = useState(0);
  const [totalAnswered, setTotalAnswered] = useState(0);
  const [loading, setLoading] = useState(true);
  const [xp, setXp] = useState(0);

  // Animations
  const shakeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const xpAnim = useRef(new Animated.Value(0)).current;
  const progressAnim = useRef(new Animated.Value(0)).current;

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
      ? "Finnish"
      : "Estonian"
    : "";

  useEffect(() => {
    loadCards();
    loadProgress();
  }, []);

  useEffect(() => {
    if (state === "answering") {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [current, state]);

  useEffect(() => {
    // Animate progress bar
    const progress = cards.length > 0 ? (current + 1) / cards.length : 0;
    Animated.timing(progressAnim, {
      toValue: progress,
      duration: 300,
      useNativeDriver: false,
    }).start();
  }, [current, cards.length]);

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
      const p = await api.getProgress(token!);
      setXp(p.xp || 0);
    } catch {
      // ignore
    }
  }

  function generateHint(word: string, level: number): string {
    if (level === 0) return "";
    if (level === 1) return word[0] + "•".repeat(word.length - 1);
    if (level === 2) return word[0] + "•".repeat(word.length - 2) + word[word.length - 1];
    const half = Math.ceil(word.length / 2);
    return word.slice(0, half) + "•".repeat(word.length - half);
  }

  function showHint() {
    if (hintLevel >= 3) return;
    const newLevel = hintLevel + 1;
    setHintLevel(newLevel);
    setHint(generateHint(expected, newLevel));
  }

  function shake() {
    Animated.sequence([
      Animated.timing(shakeAnim, { toValue: 10, duration: 50, useNativeDriver: true }),
      Animated.timing(shakeAnim, { toValue: -10, duration: 50, useNativeDriver: true }),
      Animated.timing(shakeAnim, { toValue: 8, duration: 50, useNativeDriver: true }),
      Animated.timing(shakeAnim, { toValue: -8, duration: 50, useNativeDriver: true }),
      Animated.timing(shakeAnim, { toValue: 0, duration: 50, useNativeDriver: true }),
    ]).start();
  }

  function pulseCard() {
    Animated.sequence([
      Animated.timing(scaleAnim, { toValue: 1.02, duration: 100, useNativeDriver: true }),
      Animated.timing(scaleAnim, { toValue: 1, duration: 100, useNativeDriver: true }),
    ]).start();
  }

  function showXpPopup(amount: number) {
    xpAnim.setValue(1);
    Animated.sequence([
      Animated.timing(xpAnim, { toValue: 1.5, duration: 200, useNativeDriver: true }),
      Animated.timing(xpAnim, { toValue: 0, duration: 600, useNativeDriver: true }),
    ]).start();
  }

  async function checkAnswer() {
    if (!card || !answer.trim()) return;
    Keyboard.dismiss();

    const normalized = answer.trim().toLowerCase().replace(/[,!.?]/g, "");
    const expectedNorm = expected.toLowerCase().replace(/[,!.?]/g, "");
    const isCorrect = normalized === expectedNorm || fuzzyMatch(normalized, expectedNorm);

    setState(isCorrect ? "correct" : "incorrect");
    setTotalAnswered((t) => t + 1);

    if (!isCorrect) shake();
    else pulseCard();

    const quality = isCorrect ? (hintLevel === 0 ? 5 : hintLevel === 1 ? 4 : 3) : 1;

    try {
      const result = await api.reviewCard(token!, card.card_id, quality);
      if (result.xp_earned) {
        setXp((x) => x + result.xp_earned);
        showXpPopup(result.xp_earned);
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
  }

  function skipCard() {
    nextCard();
  }

  // Loading
  if (loading) {
    return (
      <View style={s.loadingContainer}>
        <ActivityIndicator size="large" color="#fff" />
        <Text style={s.loadingText}>Loading your cards...</Text>
      </View>
    );
  }

  // Completed
  if (state === "completed" || cards.length === 0) {
    const accuracy = totalAnswered > 0 ? Math.round((totalCorrect / totalAnswered) * 100) : 0;
    return (
      <View style={s.container}>
        <View style={s.completedCard}>
          <Text style={s.completedEmoji}>{accuracy >= 80 ? "🏆" : accuracy >= 50 ? "💪" : "📚"}</Text>
          <Text style={s.completedTitle}>Session Complete!</Text>
          <Text style={s.completedSubtitle}>Great work, keep it up!</Text>

          <View style={s.statsRow}>
            <View style={s.statBox}>
              <Text style={s.statValue}>{totalCorrect}/{totalAnswered}</Text>
              <Text style={s.statLabel}>Correct</Text>
            </View>
            <View style={s.statBox}>
              <Text style={[s.statValue, { color: "#f97316" }]}>🔥 {bestStreak}</Text>
              <Text style={s.statLabel}>Best Streak</Text>
            </View>
            <View style={s.statBox}>
              <Text style={[s.statValue, { color: "#22c55e" }]}>{accuracy}%</Text>
              <Text style={s.statLabel}>Accuracy</Text>
            </View>
          </View>

          <TouchableOpacity
            style={s.primaryBtn}
            onPress={() => {
              setCurrent(0);
              setTotalCorrect(0);
              setTotalAnswered(0);
              setStreak(0);
              setBestStreak(0);
              setState("answering");
              loadCards();
            }}
          >
            <Text style={s.primaryBtnText}>Practice More</Text>
          </TouchableOpacity>
          <TouchableOpacity style={s.secondaryBtn} onPress={() => navigation.goBack()}>
            <Text style={s.secondaryBtnText}>Home</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  const progress = cards.length > 0 ? (current + 1) / cards.length : 0;

  return (
    <View style={s.container}>
      {/* Top Bar */}
      <View style={s.topBar}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={s.backBtn}>← Back</Text>
        </TouchableOpacity>
        <View style={s.topBarRight}>
          {streak > 0 && (
            <View style={s.streakBadge}>
              <Text style={s.streakText}>🔥 {streak}</Text>
            </View>
          )}
          <View style={s.xpBadge}>
            <Text style={s.xpText}>⭐ {xp}</Text>
          </View>
        </View>
      </View>

      {/* XP Popup */}
      <Animated.View
        style={[
          s.xpPopup,
          {
            opacity: xpAnim,
            transform: [{ scale: xpAnim }],
          },
        ]}
        pointerEvents="none"
      >
        <Text style={s.xpPopupText}>+{10} XP</Text>
      </Animated.View>

      {/* Progress Bar */}
      <View style={s.progressContainer}>
        <View style={s.progressBg}>
          <Animated.View
            style={[
              s.progressFill,
              {
                width: progressAnim.interpolate({
                  inputRange: [0, 1],
                  outputRange: ["0%", "100%"],
                }),
              },
            ]}
          />
        </View>
        <View style={s.progressLabels}>
          <Text style={s.progressText}>
            {current + 1} / {cards.length}
          </Text>
          <Text style={s.progressText}>{totalCorrect} correct</Text>
        </View>
      </View>

      {/* Card */}
      <Animated.View
        style={[
          s.card,
          {
            transform: [{ translateX: shakeAnim }, { scale: scaleAnim }],
          },
        ]}
      >
        {/* Card Header */}
        <View style={s.cardHeader}>
          <Text style={s.categoryText}>{card.category}</Text>
          <Text style={s.directionText}>
            {card.direction === "et_fi" ? "🇪🇪 → 🇫🇮" : "🇫🇮 → 🇪🇪"}
          </Text>
        </View>

        {/* Question */}
        <Text style={s.questionText}>{question}</Text>

        {/* Answer Area */}
        {state === "answering" && (
          <>
            {hint && (
              <View style={s.hintContainer}>
                <Text style={s.hintText}>{hint}</Text>
              </View>
            )}

            <TextInput
              ref={inputRef}
              style={s.input}
              value={answer}
              onChangeText={setAnswer}
              placeholder={`Type in ${targetLang}...`}
              placeholderTextColor="#999"
              autoCapitalize="none"
              autoCorrect={false}
              returnKeyType="done"
              onSubmitEditing={answer.trim() ? checkAnswer : undefined}
            />

            <View style={s.actionRow}>
              {hintLevel < 3 && (
                <TouchableOpacity style={s.hintBtn} onPress={showHint}>
                  <Text style={s.hintBtnText}>💡 Hint {hintLevel > 0 ? `(${hintLevel}/3)` : ""}</Text>
                </TouchableOpacity>
              )}
              <TouchableOpacity style={s.skipBtn} onPress={skipCard}>
                <Text style={s.skipBtnText}>Skip →</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[s.checkBtn, !answer.trim() && s.checkBtnDisabled]}
                onPress={checkAnswer}
                disabled={!answer.trim()}
              >
                <Text style={s.checkBtnText}>Check</Text>
              </TouchableOpacity>
            </View>
          </>
        )}

        {state === "correct" && (
          <View style={s.resultContainer}>
            <View style={s.resultIcon}>
              <Text style={s.resultIconText}>✓</Text>
            </View>
            <Text style={s.resultTitle}>Correct!</Text>
            <Text style={s.resultSubtitle}>
              {hintLevel === 0 && "Perfect — no hints needed! 🌟"}
              {hintLevel === 1 && "Good! You used 1 hint."}
              {hintLevel === 2 && "Nice! You used 2 hints."}
              {hintLevel === 3 && "Got it! Keep practicing this one."}
            </Text>
            <TouchableOpacity style={s.continueBtn} onPress={nextCard}>
              <Text style={s.continueBtnText}>Continue →</Text>
            </TouchableOpacity>
          </View>
        )}

        {state === "incorrect" && (
          <View style={s.resultContainer}>
            <View style={[s.resultIcon, s.resultIconWrong]}>
              <Text style={s.resultIconText}>✗</Text>
            </View>
            <Text style={[s.resultTitle, s.resultTitleWrong]}>Not quite</Text>
            <View style={s.answerBox}>
              <Text style={s.answerLabel}>Correct answer:</Text>
              <Text style={s.answerText}>{expected}</Text>
              {answer.trim() && (
                <Text style={styles.wrongAnswer}>
                  Your answer: <Text style={s.strikethrough}>{answer}</Text>
                </Text>
              )}
            </View>
            <TouchableOpacity style={s.continueBtn} onPress={nextCard}>
              <Text style={s.continueBtnText}>Got it →</Text>
            </TouchableOpacity>
          </View>
        )}
      </Animated.View>
    </View>
  );
}

const s = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#003580",
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: "#003580",
    justifyContent: "center",
    alignItems: "center",
  },
  loadingText: {
    color: "rgba(255,255,255,0.7)",
    fontSize: 16,
    marginTop: 16,
  },
  topBar: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingTop: 50,
    paddingBottom: 12,
  },
  backBtn: {
    color: "rgba(255,255,255,0.7)",
    fontSize: 16,
  },
  topBarRight: {
    flexDirection: "row",
    gap: 8,
  },
  streakBadge: {
    backgroundColor: "rgba(249,115,22,0.2)",
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  streakText: {
    color: "#fdba74",
    fontSize: 13,
    fontWeight: "600",
  },
  xpBadge: {
    backgroundColor: "rgba(255,255,255,0.1)",
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  xpText: {
    color: "#fff",
    fontSize: 13,
    fontWeight: "600",
  },
  xpPopup: {
    position: "absolute",
    top: 100,
    alignSelf: "center",
    backgroundColor: "#22c55e",
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    zIndex: 100,
    elevation: 10,
  },
  xpPopupText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 18,
  },
  progressContainer: {
    paddingHorizontal: 16,
    marginBottom: 16,
  },
  progressBg: {
    height: 6,
    backgroundColor: "rgba(255,255,255,0.2)",
    borderRadius: 3,
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    backgroundColor: "#fff",
    borderRadius: 3,
  },
  progressLabels: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 6,
  },
  progressText: {
    color: "rgba(255,255,255,0.5)",
    fontSize: 12,
  },
  card: {
    flex: 1,
    backgroundColor: "#fff",
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingHorizontal: 24,
    paddingTop: 20,
    paddingBottom: 40,
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 16,
  },
  categoryText: {
    fontSize: 12,
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: 1,
    color: "#999",
  },
  directionText: {
    fontSize: 14,
  },
  questionText: {
    fontSize: 32,
    fontWeight: "bold",
    color: "#111",
    textAlign: "center",
    marginBottom: 24,
  },
  hintContainer: {
    alignItems: "center",
    marginBottom: 12,
  },
  hintText: {
    backgroundColor: "#fefce8",
    color: "#a16207",
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    fontSize: 16,
    fontFamily: "monospace",
    letterSpacing: 2,
  },
  input: {
    borderWidth: 2,
    borderColor: "#e5e7eb",
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 18,
    textAlign: "center",
    color: "#111",
    marginBottom: 16,
  },
  actionRow: {
    flexDirection: "row",
    gap: 8,
  },
  hintBtn: {
    flex: 1,
    backgroundColor: "#fefce8",
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
  },
  hintBtnText: {
    color: "#a16207",
    fontWeight: "600",
    fontSize: 14,
  },
  skipBtn: {
    flex: 1,
    backgroundColor: "#f3f4f6",
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
  },
  skipBtnText: {
    color: "#6b7280",
    fontWeight: "600",
    fontSize: 14,
  },
  checkBtn: {
    flex: 2,
    backgroundColor: "#003580",
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
  },
  checkBtnDisabled: {
    opacity: 0.4,
  },
  checkBtnText: {
    color: "#fff",
    fontWeight: "700",
    fontSize: 16,
  },
  resultContainer: {
    alignItems: "center",
    paddingTop: 8,
  },
  resultIcon: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: "#dcfce7",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 12,
  },
  resultIconWrong: {
    backgroundColor: "#fee2e2",
  },
  resultIconText: {
    fontSize: 28,
  },
  resultTitle: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#22c55e",
    marginBottom: 4,
  },
  resultTitleWrong: {
    color: "#ef4444",
  },
  resultSubtitle: {
    fontSize: 14,
    color: "#6b7280",
    textAlign: "center",
    marginBottom: 20,
  },
  answerBox: {
    backgroundColor: "#f9fafb",
    borderRadius: 12,
    padding: 16,
    width: "100%",
    marginBottom: 20,
    alignItems: "center",
  },
  answerLabel: {
    fontSize: 12,
    color: "#9ca3af",
    marginBottom: 4,
  },
  answerText: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#111",
  },
  wrongAnswer: {
    fontSize: 13,
    color: "#9ca3af",
    marginTop: 8,
  },
  strikethrough: {
    textDecorationLine: "line-through",
    color: "#ef4444",
  },
  continueBtn: {
    backgroundColor: "#003580",
    paddingVertical: 16,
    paddingHorizontal: 40,
    borderRadius: 12,
    width: "100%",
    alignItems: "center",
  },
  continueBtnText: {
    color: "#fff",
    fontWeight: "700",
    fontSize: 16,
  },
  // Completed screen
  completedCard: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 32,
  },
  completedEmoji: {
    fontSize: 64,
    marginBottom: 16,
  },
  completedTitle: {
    fontSize: 28,
    fontWeight: "bold",
    color: "#fff",
    marginBottom: 8,
  },
  completedSubtitle: {
    fontSize: 16,
    color: "rgba(255,255,255,0.7)",
    marginBottom: 32,
  },
  statsRow: {
    flexDirection: "row",
    gap: 12,
    marginBottom: 32,
  },
  statBox: {
    backgroundColor: "rgba(255,255,255,0.1)",
    borderRadius: 12,
    padding: 16,
    alignItems: "center",
    minWidth: 90,
  },
  statValue: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#fff",
  },
  statLabel: {
    fontSize: 11,
    color: "rgba(255,255,255,0.5)",
    marginTop: 4,
  },
  primaryBtn: {
    backgroundColor: "#fff",
    paddingVertical: 16,
    paddingHorizontal: 40,
    borderRadius: 12,
    width: "100%",
    alignItems: "center",
    marginBottom: 12,
  },
  primaryBtnText: {
    color: "#003580",
    fontWeight: "700",
    fontSize: 16,
  },
  secondaryBtn: {
    backgroundColor: "rgba(255,255,255,0.1)",
    paddingVertical: 16,
    paddingHorizontal: 40,
    borderRadius: 12,
    width: "100%",
    alignItems: "center",
  },
  secondaryBtnText: {
    color: "#fff",
    fontWeight: "600",
    fontSize: 16,
  },
});
