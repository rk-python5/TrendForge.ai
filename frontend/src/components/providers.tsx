"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";
import { Toaster } from "@/components/ui/sonner";
import { ErrorBoundary } from "@/components/error-boundary";

export function Providers({ children }: { children: ReactNode }) {
    const [queryClient] = useState(
        () =>
            new QueryClient({
                defaultOptions: {
                    queries: { staleTime: 30_000, retry: 1 },
                },
            })
    );

    return (
        <QueryClientProvider client={queryClient}>
            <ErrorBoundary>
                {children}
            </ErrorBoundary>
            <Toaster position="bottom-right" richColors closeButton />
        </QueryClientProvider>
    );
}
