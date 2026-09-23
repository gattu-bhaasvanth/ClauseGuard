import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ClauseGuard — AI-Powered Real-Estate Transaction Intelligence",
  description:
    "Understand your property documents before you sign. Automated cross-document inconsistency detection, risk analysis, and evidence-backed verification for property transactions.",
  keywords: [
    "real estate",
    "transaction intelligence",
    "contract analysis",
    "builder-buyer agreement",
    "cross-document inconsistency",
    "clause intelligence",
    "RERA",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark scroll-smooth">
      <body className="min-h-screen bg-background text-foreground antialiased selection:bg-emerald-500/20 selection:text-emerald-300">
        {children}
      </body>
    </html>
  );
}
