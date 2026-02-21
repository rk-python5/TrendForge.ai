"use client";

import { Sidebar } from "@/components/layout/sidebar";
import { type ReactNode } from "react";

export function AppShell({ children }: { children: ReactNode }) {
    return (
        <div className="flex min-h-screen bg-background">
            <Sidebar />
            <main className="ml-64 flex-1 p-6 lg:p-8">
                {children}
            </main>
        </div>
    );
}
