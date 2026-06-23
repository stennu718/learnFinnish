import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { useAuthStore } from "@/src/store/authStore";
import { HomeScreen } from "@/src/screens/HomeScreen";
import { LearnScreen } from "@/src/screens/LearnScreen";
import { LoginScreen } from "@/src/screens/LoginScreen";
import { RegisterScreen } from "@/src/screens/RegisterScreen";
import { ProgressScreen } from "@/src/screens/ProgressScreen";

const Stack = createNativeStackNavigator();

export default function App() {
  const token = useAuthStore((s) => s.token);

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {token ? (
          <>
            <Stack.Screen name="Home" component={HomeScreen} />
            <Stack.Screen name="Learn" component={LearnScreen} />
            <Stack.Screen name="Progress" component={ProgressScreen} />
          </>
        ) : (
          <>
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="Register" component={RegisterScreen} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
