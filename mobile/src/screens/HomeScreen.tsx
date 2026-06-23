import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { useAuthStore } from "@/src/store/authStore";

export function HomeScreen({ navigation }: any) {
  const { logout, token } = useAuthStore();

  return (
    <View style={s.container}>
      <Text style={s.title}>🇪🇪 → 🇫🇮 learnFinnish</Text>
      <Text style={s.subtitle}>The best Estonian-Finnish learning app</Text>

      <TouchableOpacity style={s.btn} onPress={() => navigation.navigate("Learn")}>
        <Text style={s.btnText}>📚 Start Learning</Text>
      </TouchableOpacity>

      <TouchableOpacity style={[s.btn, s.btnSecondary]} onPress={() => navigation.navigate("Progress")}>
        <Text style={s.btnText}>📊 Progress</Text>
      </TouchableOpacity>

      <TouchableOpacity style={[s.btn, s.btnOutline]} onPress={logout}>
        <Text style={[s.btnText, s.btnOutlineText]}>Log Out</Text>
      </TouchableOpacity>
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", alignItems: "center", padding: 24, backgroundColor: "#f8f9fa" },
  title: { fontSize: 28, fontWeight: "bold", marginBottom: 8, textAlign: "center" },
  subtitle: { fontSize: 16, color: "#666", marginBottom: 40, textAlign: "center" },
  btn: { backgroundColor: "#003580", paddingVertical: 16, paddingHorizontal: 40, borderRadius: 12, width: "100%", marginBottom: 12, alignItems: "center" },
  btnText: { color: "#fff", fontSize: 18, fontWeight: "600" },
  btnSecondary: { backgroundColor: "#0072ce" },
  btnOutline: { backgroundColor: "transparent", borderWidth: 2, borderColor: "#ccc" },
  btnOutlineText: { color: "#666" },
});
