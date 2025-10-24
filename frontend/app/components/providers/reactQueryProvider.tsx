"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useRef } from "react";

const defaultQueryOptions = {
  queries: {
    staleTime: 60_000,
    gcTime: 300_000,
    retry: 2,
    retryDelay: (attempt: number) => Math.min(1000 * 2 ** attempt, 5000),
    refetchOnWindowFocus: false,
    refetchOnReconnect: true,
  },
  mutations: {
    retry: 0,
  },
};

export function ReactQueryProvider({ children }: { children: React.ReactNode }) {
  const clientRef = useRef<QueryClient>(null);

  clientRef.current ??= new QueryClient({ defaultOptions: defaultQueryOptions });

  return <QueryClientProvider client={clientRef.current}>{children}</QueryClientProvider>;
}
