import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: {
    default: "EdilEngine - Naviga le leggi dell'edilizia italiana",
    template: "%s | EdilEngine",
  },
  description:
    "Sistema intelligente per navigare le leggi italiane dell'edilizia. Ricerca normativa, incentivi, vincoli territoriali e chatbot RAG con AI.",
  keywords: [
    "edilizia",
    "leggi edilizie",
    "normativa costruzioni",
    "incentivi edilizi",
    "vincoli urbanistici",
    "permessi costruire",
    "guida edilizia",
    "chatbot normativo",
    "RAG",
  ],
  authors: [{ name: "EdilEngine" }],
  openGraph: {
    title: "EdilEngine - Naviga le leggi dell'edilizia italiana",
    description:
      "Sistema intelligente per navigare le leggi italiane dell'edilizia con AI.",
    locale: "it_IT",
    type: "website",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="it" className={inter.variable}>
      <body className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
