"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Settings as SettingsIcon, User, Palette, Key, Save, Loader2, CheckCircle } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export default function SettingsPage() {
    const [hfToken, setHfToken] = useState("");
    const [savedHf, setSavedHf] = useState(false);

    const handleSaveHf = () => {
        // In a real app, this would save to the backend
        localStorage.setItem("hf_token", hfToken);
        setSavedHf(true);
        toast.success("Hugging Face token saved locally");
        setTimeout(() => setSavedHf(false), 2000);
    };

    return (
        <div className="space-y-6 animate-fadeIn">
            <div>
                <h1 className="text-2xl font-bold text-text flex items-center gap-2">
                    <SettingsIcon className="h-6 w-6 text-primary" /> Settings
                </h1>
                <p className="mt-1 text-muted">Configure your TrendForge experience.</p>
            </div>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                {/* Profile */}
                <div className="card p-6 space-y-4">
                    <h2 className="text-base font-semibold text-text flex items-center gap-2">
                        <User className="h-4 w-4 text-muted" /> Profile
                    </h2>
                    <div className="space-y-3">
                        <div>
                            <label className="block text-xs font-semibold text-muted mb-1 uppercase tracking-wider">Name</label>
                            <input className="input" defaultValue="Rehaan Khatri" />
                        </div>
                        <div>
                            <label className="block text-xs font-semibold text-muted mb-1 uppercase tracking-wider">Industry</label>
                            <input className="input" defaultValue="Tech / AI / Data Science / ML" />
                        </div>
                        <div>
                            <label className="block text-xs font-semibold text-muted mb-1 uppercase tracking-wider">Expertise</label>
                            <input className="input" defaultValue="Agentic AI, RAG Systems & FinTech Applications" />
                        </div>
                    </div>
                </div>

                {/* Content Preferences */}
                <div className="card p-6 space-y-4">
                    <h2 className="text-base font-semibold text-text flex items-center gap-2">
                        <Palette className="h-4 w-4 text-muted" /> Content Preferences
                    </h2>
                    <div className="space-y-3">
                        <div>
                            <label className="block text-xs font-semibold text-muted mb-1 uppercase tracking-wider">Default Tone</label>
                            <select className="input">
                                <option value="professional">Professional</option>
                                <option value="casual">Casual</option>
                                <option value="inspirational">Inspirational</option>
                                <option value="educational">Educational</option>
                                <option value="thought-provoking">Thought-Provoking</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-xs font-semibold text-muted mb-1 uppercase tracking-wider">Default Post Type</label>
                            <select className="input">
                                <option value="insight">💡 Insight</option>
                                <option value="tip">🎯 Tip</option>
                                <option value="story">📖 Story</option>
                                <option value="question">❓ Question</option>
                                <option value="achievement">🏆 Achievement</option>
                                <option value="opinion">💬 Opinion</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-xs font-semibold text-muted mb-1 uppercase tracking-wider">Max Post Length</label>
                            <input className="input" type="number" defaultValue={3000} />
                        </div>
                    </div>
                </div>

                {/* API Keys */}
                <div className="card p-6 space-y-4">
                    <h2 className="text-base font-semibold text-text flex items-center gap-2">
                        <Key className="h-4 w-4 text-muted" /> API Keys
                    </h2>
                    <div className="space-y-3">
                        <div>
                            <label className="block text-xs font-semibold text-muted mb-1 uppercase tracking-wider">Hugging Face Token</label>
                            <p className="text-xs text-muted mb-2">Required for AI image generation (Stable Diffusion XL)</p>
                            <div className="flex gap-2">
                                <input
                                    className="input flex-1"
                                    type="password"
                                    placeholder="hf_..."
                                    value={hfToken}
                                    onChange={(e) => setHfToken(e.target.value)}
                                />
                                <button onClick={handleSaveHf} className="btn btn-primary btn-sm">
                                    {savedHf ? <CheckCircle className="h-4 w-4" /> : <Save className="h-4 w-4" />}
                                </button>
                            </div>
                        </div>
                        <div>
                            <label className="block text-xs font-semibold text-muted mb-1 uppercase tracking-wider">LinkedIn OAuth</label>
                            <p className="text-xs text-muted mb-2">Connect your LinkedIn account for direct publishing</p>
                            <button className="btn btn-secondary btn-sm" disabled>
                                Connect LinkedIn (Coming Soon)
                            </button>
                        </div>
                    </div>
                </div>

                {/* LLM Config */}
                <div className="card p-6 space-y-4">
                    <h2 className="text-base font-semibold text-text flex items-center gap-2">
                        🤖 LLM Configuration
                    </h2>
                    <div className="space-y-3">
                        <div>
                            <label className="block text-xs font-semibold text-muted mb-1 uppercase tracking-wider">Ollama Base URL</label>
                            <input className="input" defaultValue="http://localhost:11434" />
                        </div>
                        <div>
                            <label className="block text-xs font-semibold text-muted mb-1 uppercase tracking-wider">Model</label>
                            <input className="input" defaultValue="llama3.2:3b" />
                        </div>
                    </div>
                </div>
            </div>

            {/* Save All */}
            <div className="flex justify-end">
                <button className="btn btn-primary" onClick={() => toast.success("Settings saved!")}>
                    <Save className="h-4 w-4" /> Save All Settings
                </button>
            </div>
        </div>
    );
}
