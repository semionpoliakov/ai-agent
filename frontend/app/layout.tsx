import type { Metadata } from "next";
import "./globals.css";
import { Inter } from "next/font/google";
import { ReactQueryProvider } from "@/components/providers/react-query-provider";

const inter = Inter({ subsets: ["latin"], display: "swap" });

export const metadata: Metadata = {
  title: "Marketing Analytics Agent",
  description: "Chat with an AI agent to explore performance marketing metrics.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} min-h-screen bg-background antialiased`}>
        <ReactQueryProvider>{children}</ReactQueryProvider>
      </body>
    </html>
  );
}
