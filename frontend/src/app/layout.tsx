import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "learnFinnish — Estonia-Finnish Language Learning",
  description: "The best app for Estonians learning Finnish. Cognate-first approach, spaced repetition, and pattern-based grammar.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="et">
      <body className="bg-gray-50 text-gray-900 antialiased">{children}</body>
    </html>
  );
}
