"use client";

import { Settings, User, Palette, Bell } from "lucide-react";

export default function SettingsPage() {
    return (
        <div className="space-y-6 animate-fadeIn">
            <div>
                <h1 className="text-2xl font-bold text-text flex items-center gap-2">
                    <Settings className="h-6 w-6 text-primary" /> Settings
                </h1>
                <p className="mt-1 text-muted">Configure your TrendForge experience.</p>
            </div>

            <div className="card flex flex-col items-center justify-center py-20 text-center">
                <div className="mb-6 flex items-center gap-4">
                    <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-100 text-indigo-600">
                        <User className="h-6 w-6" />
                    </div>
                    <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-purple-100 text-purple-600">
                        <Palette className="h-6 w-6" />
                    </div>
                    <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-pink-100 text-pink-600">
                        <Bell className="h-6 w-6" />
                    </div>
                </div>
                <h3 className="text-lg font-semibold text-text">Coming in Phase 5</h3>
                <p className="mt-2 max-w-md text-sm text-muted leading-relaxed">
                    The settings page will include profile configuration, content preferences,
                    notification settings, and API key management.
                </p>
            </div>
        </div>
    );
}
