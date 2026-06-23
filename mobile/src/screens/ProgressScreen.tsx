import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ActivityIndicator } from "react-native";
import { useAuthStore } from "@/src/store/authStore";
import { api } from "@/src/services/api";

export function ProgressScreen() {
  const token = useAuthStore((s) => s.token);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getProgress(token!).then(setData).finally(() => setLoading(false));
  }, []);

  if (loading) return <View style={s.center}><ActivityIndicator size="large" /></View>;

  return (
    <View style={s.container}>
      <Text style={s.title}>📊 Your Progress</Text>
      <View style={s.statCard}>
        <Text style={s.statLabel}>Level</Text>
        <Text style={s.statValue}>{data?.level || 1}</Text>
      </View>
      <View style={s.statCard}>
        <Text style={s.statLabel}>XP</Text>
        <Text style={s.statValue}>{data?.xp || 0}</Text>
      </View>
      <View style={s.statCard}>
        <Text style={s.statLabel}>Reviews</Text>
        <Text style={s.statValue}>{data?.total_reviews || 0}</Text>
      </View>
      <View style={s.statCard}>
        <Text style={s.statLabel}>Accuracy</Text>
        <Text style={s.statValue}>{data?.accuracy || 0}%</Text>
      </View>
      <View style={s.statCard}>
        <Text style={s.statLabel}>Current Streak</Text>
        <Text style={s.statValue}>🔥 {data?.current_streak || 0}</Text>
      </View>
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, padding: 24, backgroundColor: "#f8f9fa" },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  title: { fontSize: 28, fontWeight: "bold", marginBottom: 24, textAlign: "center" },
  statCard: { backgroundColor: "#fff", borderRadius: 12, padding: 20, marginBottom: 12, flexDirection: "row", justifyContent: "space-between", alignItems: "center", shadowColor: "#000", shadowOpacity: 0.05, shadowRadius: 4, elevation: 2 },
  statLabel: { fontSize: 16, color: "#666" },
  statValue: { fontSize: 24, fontWeight: "bold", color: "#003580" },
});
