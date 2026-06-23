const API_URL = process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000";

export const api = {
  async register(email: string, password: string, display_name: string = "") {
    const res = await fetch(`${API_URL}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, display_name }),
    });
    if (!res.ok) throw new Error("Registration failed");
    return res.json();
  },

  async login(email: string, password: string) {
    const res = await fetch(`${API_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error("Login failed");
    return res.json();
  },

  async getDueCards(token: string) {
    const res = await fetch(`${API_URL}/api/srs/due`, {
      headers: { Authorization: "Bearer " + token },
    });
    if (!res.ok) throw new Error("Failed to fetch cards");
    return res.json();
  },

  async reviewCard(token: string, cardId: number, quality: number) {
    const res = await fetch(`${API_URL}/api/srs/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: "Bearer " + token },
      body: JSON.stringify({ card_id: cardId, quality }),
    });
    if (!res.ok) throw new Error("Review failed");
    return res.json();
  },

  async initSRS(token: string) {
    const res = await fetch(`${API_URL}/api/srs/init`, {
      method: "POST",
      headers: { Authorization: "Bearer " + token },
    });
    if (!res.ok) throw new Error("Init failed");
    return res.json();
  },

  async getProgress(token: string) {
    const res = await fetch(`${API_URL}/api/progress`, {
      headers: { Authorization: "Bearer " + token },
    });
    if (!res.ok) throw new Error("Failed to fetch progress");
    return res.json();
  },
};
