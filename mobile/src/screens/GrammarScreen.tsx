import React, { useEffect, useState } from "react";
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator } from "react-native";
import { useAuthStore } from "@/src/store/authStore";
import { api } from "@/src/services/api";

interface GrammarRule {
  name: string;
  estonian_ending: string;
  finnish_ending: string;
  description: string;
  examples: Array<{ est: string; fi: string; et: string; fi: string }>;
}

export function GrammarScreen({ navigation }: any) {
  const token = useAuthStore((s) => s.token);
  const [rules, setRules] = useState<GrammarRule[]>([]);
  const [selectedRule, setSelectedRule] = useState<GrammarRule | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRules();
  }, []);

  async function loadRules() {
    setLoading(true);
    try {
      const data = await api.getGrammarRules(token!);
      setRules(data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }

  if (loading) {
    return (
      <View style={s.center}>
        <ActivityIndicator size="large" color="#fff" />
        <Text style={s.loadingText}>Loading grammar rules...</Text>
      </View>
    );
  }

  return (
    <View style={s.container}>
      <ScrollView contentContainerStyle={s.content}>
        <Text style={s.title}>📐 Grammar</Text>
        <Text style={s.subtitle}>Estonian → Finnish case transformations</Text>

        {rules.map((rule) => (
          <TouchableOpacity
            key={rule.name}
            style={s.ruleCard}
            onPress={() => setSelectedRule(rule)}
          >
            <Text style={s.ruleName}>{rule.name}</Text>
            <Text style={s.ruleDesc}>{rule.description}</Text>
            <Text style={s.ruleEnding}>{rule.estonian_ending} → {rule.finnish_ending}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#003580" },
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#003580" },
  loadingText: { color: "rgba(255,255,255,0.7)", marginTop: 12 },
  content: { padding: 24, paddingTop: 60 },
  title: { fontSize: 28, fontWeight: "bold", color: "#fff", marginBottom: 8 },
  subtitle: { fontSize: 14, color: "rgba(255,255,255,0.6)", marginBottom: 24 },
  ruleCard: { backgroundColor: "rgba(255,255,255,0.1)", borderRadius: 12, padding: 16, marginBottom: 12 },
  ruleName: { fontSize: 16, fontWeight: "600", color: "#fff", textTransform: "capitalize" },
  ruleDesc: { fontSize: 13, color: "rgba(255,255,255,0.6)", marginTop: 4 },
  ruleEnding: { fontSize: 12, color: "rgba(255,255,255,0.4)", marginTop: 8 },
});
