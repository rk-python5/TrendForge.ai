"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    LayoutDashboard, Sparkles, FileText, TrendingUp, Calendar,
    Settings, Zap, Menu, X, BarChart3,
} from "lucide-react";

const NAV = [
    { href: "/", label: "Dashboard", icon: LayoutDashboard },
    { href: "/generate", label: "Generate", icon: Sparkles },
    { href: "/posts", label: "Posts", icon: FileText },
    { href: "/trends", label: "Trends", icon: TrendingUp },
    { href: "/calendar", label: "Calendar", icon: Calendar },
    { href: "/analytics", label: "Analytics", icon: BarChart3 },
    { href: "/settings", label: "Settings", icon: Settings },
];

function NavLinks({ onClick }: { onClick?: () => void }) {
    const pathname = usePathname();
    return (
        <>
            {NAV.map((item) => {
                const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
                const Icon = item.icon;
                return (
                    <Link
                        key={item.href}
                        href={item.href}
                        onClick={onClick}
                        className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150
              ${isActive ? "bg-primary-light text-primary" : "text-muted hover:bg-border-light hover:text-text"}`}
                    >
                        <Icon className="h-[18px] w-[18px]" />
                        <span>{item.label}</span>
                    </Link>
                );
            })}
        </>
    );
}

export function Sidebar() {
    const [mobileOpen, setMobileOpen] = useState(false);
    const pathname = usePathname();

    // Close on route change
    useEffect(() => { setMobileOpen(false); }, [pathname]);

    return (
        <>
            {/* Mobile hamburger */}
            <button
                onClick={() => setMobileOpen(true)}
                className="fixed left-4 top-4 z-50 flex h-10 w-10 items-center justify-center rounded-lg bg-card border border-border shadow-sm lg:hidden"
                aria-label="Open menu"
            >
                <Menu className="h-5 w-5 text-text" />
            </button>

            {/* Mobile Overlay */}
            {mobileOpen && (
                <div className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm lg:hidden" onClick={() => setMobileOpen(false)} />
            )}

            {/* Mobile Drawer */}
            <aside
                className={`fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-border bg-card transition-transform duration-300 lg:hidden
          ${mobileOpen ? "translate-x-0" : "-translate-x-full"}`}
            >
                <div className="flex h-16 items-center justify-between border-b border-border px-6">
                    <div className="flex items-center gap-2.5">
                        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
                            <Zap className="h-5 w-5 text-white" />
                        </div>
                        <div>
                            <h1 className="text-base font-bold text-text">TrendForge</h1>
                            <p className="text-[11px] font-medium text-muted tracking-wide">AI CONTENT ENGINE</p>
                        </div>
                    </div>
                    <button onClick={() => setMobileOpen(false)} className="btn btn-ghost p-1.5">
                        <X className="h-5 w-5" />
                    </button>
                </div>
                <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
                    <NavLinks onClick={() => setMobileOpen(false)} />
                </nav>
                <SidebarFooter />
            </aside>

            {/* Desktop Sidebar */}
            <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col border-r border-border bg-card lg:flex">
                <div className="flex h-16 items-center gap-2.5 border-b border-border px-6">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
                        <Zap className="h-5 w-5 text-white" />
                    </div>
                    <div>
                        <h1 className="text-base font-bold text-text">TrendForge</h1>
                        <p className="text-[11px] font-medium text-muted tracking-wide">AI CONTENT ENGINE</p>
                    </div>
                </div>
                <nav className="flex-1 space-y-1 px-3 py-4">
                    <NavLinks />
                </nav>
                <SidebarFooter />
            </aside>
        </>
    );
}

function SidebarFooter() {
    return (
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
    );
}
