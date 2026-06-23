import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ActivityIndicator, ScrollView, TouchableOpacity } from "react-native";
import { useAuthStore } from "@/src/store/authStore";
import { api } from "@/src/services/api";

export function ProgressScreen({ navigation }: any) {
  const token = useAuthStore((s) => s.token);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getProgress(token!)
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <View style={s.loadingContainer}>
        <ActivityIndicator size="large" color="#fff" />
      </View>
    );
  }

  const accuracy =
    data?.total_reviews > 0
      ? Math.round((data.correct_reviews / data.total_reviews) * 100)
      : 0;

  return (
    <View style={s.container}>
      <ScrollView contentContainerStyle={s.content}>
        <Text style={s.emoji}>📊</Text>
        <Text style={s.title}>Your Progress</Text>

        <View style={s.levelCard}>
          <Text style={s.levelLabel}>Level {data?.level || 1}</Text>
          <View style={s.xpBar}>
            <View
              style={[
                s.xpFill,
                { width: `${((data?.xp || 0) % 100)}%` },
              ]}
            />
          </View>
          <Text style={s.xpText}>{data?.xp || 0} XP total</Text>
        </View>

        <View style={s.statsGrid}>
          <View style={s.statCard}>
            <Text style={s.statIcon}>📝</Text>
            <Text style={s.statValue}>{data?.total_reviews || 0}</Text>
            <Text style={s.statLabel}>Reviews</Text>
          </View>
          <View style={s.statCard}>
            <Text style={s.statIcon}>✅</Text>
            <Text style={s.statValue}>{data?.correct_reviews || 0}</Text>
            <Text style={s.statLabel}>Correct</Text>
          </View>
          <View style={s.statCard}>
            <Text style={s.statIcon}>🎯</Text>
            <Text style={s.statValue}>{accuracy}%</Text>
            <Text style={s.statLabel}>Accuracy</Text>
          </View>
          <View style={s.statCard}>
            <Text style={s.statIcon}>🔥</Text>
            <Text style={s.statValue}>{data?.current_streak || 0}</Text>
            <Text style={s.statLabel}>Streak</Text>
          </View>
        </View>

        <TouchableOpacity
          style={s.primaryBtn}
          onPress={() => navigation.navigate("Learn")}
        >
          <Text style={s.primaryBtnText}>📚 Continue Learning</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
}

import { TouchableOpacity } from "react-native";

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#003580" },
  loadingContainer: { flex: 1, backgroundColor: "#003580", justifyContent: "center", alignItems: "center" },
  content: { padding: 24, paddingTop: 60 },
  emoji: { fontSize: 48, textAlign: "center", marginBottom: 12 },
  title: { fontSize: 28, fontWeight: "bold", color: "#fff", textAlign: "center", marginBottom: 24 },
  levelCard: {
    backgroundColor: "rgba(255,255,255,0.1)",
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
    alignItems: "center",
  },
  levelLabel: { fontSize: 20, fontWeight: "bold", color: "#fff", marginBottom: 12 },
  xpBar: {
    width: "100%",
    height: 8,
    backgroundColor: "rgba(255,255,255,0.2)",
    borderRadius: 4,
    overflow: "hidden",
    marginBottom: 8,
  },
  xpFill: { height: "100%", backgroundColor: "#fff", borderRadius: 4 },
  xpText: { fontSize: 13, color: "rgba(255,255,255,0.6)" },
  statsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 12,
    marginBottom: 24,
  },
  statCard: {
    backgroundColor: "rgba(255,255,255,0.1)",
    borderRadius: 12,
    padding: 16,
    alignItems: "center",
    width: "47%",
  },
  statIcon: { fontSize: 24, marginBottom: 8 },
  statValue: { fontSize: 24, fontWeight: "bold", color: "#fff" },
  statLabel: { fontSize: 12, color: "rgba(255,255,255,0.5)", marginTop: 4 },
  primaryBtn: {
    backgroundColor: "#fff",
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: "center",
  },
  primaryBtnText: { color: "#003580", fontSize: 16, fontWeight: "700" },
});
