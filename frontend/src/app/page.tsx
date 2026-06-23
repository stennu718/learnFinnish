"use client";

import Link from "next/link";
import { useAuthStore } from "@/lib/authStore";

export default function HomePage() {
  const token = useAuthStore((s) => s.token);

  return (
    <main className="min-h-screen flex flex-col">
      {/* Hero */}
      <header className="bg-gradient-to-br from-[#003580] to-[#0072ce] text-white">
        <div className="max-w-4xl mx-auto px-6 py-20 text-center">
          <h1 className="text-5xl font-bold mb-4">🇪🇪 → 🇫🇮 learnFinnish</h1>
          <p className="text-xl opacity-90 mb-2">The best Estonian-Finnish language learning app</p>
          <p className="text-sm opacity-70 mb-8">Cognate-first approach · Spaced repetition · Pattern-based grammar</p>
          <div className="flex gap-4 justify-center">
            {token ? (
              <Link href="/learn" className="bg-white text-[#003580] px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition">
                Start Learning →
              </Link>
            ) : (
              <>
                <Link href="/register" className="bg-white text-[#003580] px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition">
                  Get Started Free
                </Link>
                <Link href="/login" className="border border-white/50 px-8 py-3 rounded-lg font-semibold hover:bg-white/10 transition">
                  Log In
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Features */}
      <section className="max-w-4xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">Why learnFinnish?</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            { emoji: "🧠", title: "Cognate-First", desc: "Start with words that are nearly identical between Estonian and Finnish. Build confidence fast." },
            { emoji: "🔄", title: "Spaced Repetition", desc: "SM-2 algorithm ensures you review words at the optimal time for long-term memory." },
            { emoji: "📐", title: "Pattern Grammar", desc: "Learn the transformation rules between Estonian and Finnish cases, not 14 isolated endings." },
            { emoji: "🎧", title: "Native Audio", desc: "Every word and sentence has native speaker audio. Train your ear from day one." },
            { emoji: "📱", title: "Web + Mobile", desc: "Learn on any device. Progress syncs everywhere." },
            { emoji: "🏆", title: "Gamified", desc: "XP, levels, streaks, and leaderboards keep you motivated." },
          ].map((f) => (
            <div key={f.title} className="bg-white rounded-xl p-6 shadow-sm border">
              <div className="text-3xl mb-3">{f.emoji}</div>
              <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
              <p className="text-gray-600 text-sm">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto bg-gray-900 text-gray-400 text-center py-8 text-sm">
        <p>learnFinnish — Open source Estonian-Finnish language learning</p>
        <p className="mt-1">Made with ❤️ in Estonia</p>
      </footer>
    </main>
  );
}
