import React from "react";
import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from "react-native";
import { useAuthStore } from "@/src/store/authStore";

export function HomeScreen({ navigation }: any) {
  const { logout } = useAuthStore();

  return (
    <View style={s.container}>
      <ScrollView contentContainerStyle={s.content}>
        {/* Hero */}
        <View style={s.hero}>
          <Text style={s.emoji}>🇪🇪 → 🇫🇮</Text>
          <Text style={s.title}>learnFinnish</Text>
          <Text style={s.subtitle}>The best Estonian-Finnish language learning app</Text>
          <Text style={s.tagline}>Cognate-first · Spaced repetition · Pattern grammar</Text>
        </View>

        {/* Start Learning Button */}
        <TouchableOpacity style={s.primaryBtn} onPress={() => navigation.navigate("Learn")}>
          <Text style={s.primaryBtnText}>📚 Start Learning</Text>
        </TouchableOpacity>

        {/* Secondary Actions */}
        <View style={s.secondaryRow}>
          <TouchableOpacity style={s.secondaryBtn} onPress={() => navigation.navigate("Progress")}>
            <Text style={s.secondaryBtnText}>📊 Progress</Text>
          </TouchableOpacity>
          <TouchableOpacity style={s.secondaryBtn} onPress={logout}>
            <Text style={s.secondaryBtnText}>Log Out</Text>
          </TouchableOpacity>
        </View>

        {/* Features */}
        <View style={s.features}>
          {[
            { emoji: "🧠", title: "Cognate-First", desc: "Start with words nearly identical in Estonian & Finnish" },
            { emoji: "💡", title: "Smart Hints", desc: "3-level hint system when you're stuck" },
            { emoji: "🔄", title: "Spaced Repetition", desc: "SM-2 algorithm for long-term memory" },
            { emoji: "🔥", title: "Streaks", desc: "Build your daily learning streak" },
          ].map((f) => (
            <View key={f.title} style={s.featureCard}>
              <Text style={s.featureEmoji}>{f.emoji}</Text>
              <Text style={s.featureTitle}>{f.title}</Text>
              <Text style={s.featureDesc}>{f.desc}</Text>
            </View>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#003580" },
  content: { padding: 24, paddingTop: 60 },
  hero: { alignItems: "center", marginBottom: 32 },
  emoji: { fontSize: 48, marginBottom: 12 },
  title: { fontSize: 36, fontWeight: "bold", color: "#fff", marginBottom: 8 },
  subtitle: { fontSize: 16, color: "rgba(255,255,255,0.8)", textAlign: "center", marginBottom: 4 },
  tagline: { fontSize: 12, color: "rgba(255,255,255,0.5)", textAlign: "center" },
  primaryBtn: {
    backgroundColor: "#fff",
    paddingVertical: 18,
    borderRadius: 16,
    alignItems: "center",
    marginBottom: 12,
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  primaryBtnText: { color: "#003580", fontSize: 18, fontWeight: "700" },
  secondaryRow: { flexDirection: "row", gap: 12, marginBottom: 32 },
  secondaryBtn: {
    flex: 1,
    backgroundColor: "rgba(255,255,255,0.1)",
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
  },
  secondaryBtnText: { color: "#fff", fontSize: 14, fontWeight: "600" },
  features: { gap: 12 },
  featureCard: {
    backgroundColor: "rgba(255,255,255,0.08)",
    borderRadius: 12,
    padding: 16,
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  featureEmoji: { fontSize: 28 },
  featureTitle: { fontSize: 14, fontWeight: "600", color: "#fff", flex: 1 },
  featureDesc: { fontSize: 12, color: "rgba(255,255,255,0.6)", flex: 2 },
});
