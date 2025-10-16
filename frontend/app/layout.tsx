import type { Metadata } from "next";
import "./globals.css";
import { ReactQueryProvider } from "../lib/react-query-provider";

export const metadata: Metadata = {
  title: "Marketing Analytics Agent",
  description: "Chat with an AI agent to explore performance marketing metrics.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background antialiased">
        <ReactQueryProvider>{children}</ReactQueryProvider>
      </body>
    </html>
  );
}
