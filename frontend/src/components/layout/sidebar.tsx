"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    LayoutDashboard,
    Sparkles,
    FileText,
    TrendingUp,
    Calendar,
    Settings,
    Zap,
} from "lucide-react";

const NAV = [
    { href: "/", label: "Dashboard", icon: LayoutDashboard },
    { href: "/generate", label: "Generate", icon: Sparkles },
    { href: "/posts", label: "Posts", icon: FileText },
    { href: "/trends", label: "Trends", icon: TrendingUp },
    { href: "/calendar", label: "Calendar", icon: Calendar },
    { href: "/settings", label: "Settings", icon: Settings, badge: "Soon" },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="fixed inset-y-0 left-0 z-30 flex w-64 flex-col border-r border-border bg-card">
            {/* Logo */}
            <div className="flex h-16 items-center gap-2.5 border-b border-border px-6">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
                    <Zap className="h-5 w-5 text-white" />
                </div>
                <div>
                    <h1 className="text-base font-bold text-text">TrendForge</h1>
                    <p className="text-[11px] font-medium text-muted tracking-wide">AI CONTENT ENGINE</p>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 space-y-1 px-3 py-4">
                {NAV.map((item) => {
                    const isActive = pathname === item.href;
                    const Icon = item.icon;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150
                ${isActive
                                    ? "bg-primary-light text-primary"
                                    : "text-muted hover:bg-border-light hover:text-text"
                                }`}
                        >
                            <Icon className="h-[18px] w-[18px]" />
                            <span>{item.label}</span>
                            {item.badge && (
                                <span className="ml-auto rounded-full bg-border-light px-2 py-0.5 text-[10px] font-semibold text-muted">
                                    {item.badge}
                                </span>
                            )}
                        </Link>
                    );
                })}
            </nav>

            {/* Footer */}
            <div className="border-t border-border px-4 py-3">
                <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary">
                        RK
                    </div>
                    <div className="min-w-0">
                        <p className="truncate text-sm font-medium text-text">Rehaan Khatri</p>
                        <p className="text-xs text-muted">Pro Plan</p>
                    </div>
                </div>
            </div>
        </aside>
    );
}
