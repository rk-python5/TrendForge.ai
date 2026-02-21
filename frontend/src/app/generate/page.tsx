"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import {
    ArrowLeft,
    Sparkles,
    RefreshCw,
    CheckCircle2,
    XCircle,
    Pencil,
    Copy,
    Check,
} from "lucide-react";
import Link from "next/link";

const POST_TYPES = ["insight", "tip", "story", "question", "achievement", "opinion"];
const TONES = ["professional", "casual", "inspirational", "educational", "thought-provoking"];

type Step = "input" | "generating" | "review";

export default function GeneratePage() {
    const router = useRouter();

    // Form state
    const [topic, setTopic] = useState("");
    const [postType, setPostType] = useState("insight");
    const [tone, setTone] = useState("professional");

    // Generation state
    const [step, setStep] = useState<Step>("input");
    const [result, setResult] = useState<{
        post_id: number | null;
        content: string;
        hashtags: string;
        word_count: number;
        estimated_read_time: number;
    } | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editContent, setEditContent] = useState("");
    const [copied, setCopied] = useState(false);
    const [isRegenerating, setIsRegenerating] = useState(false);
    const [isApproving, setIsApproving] = useState(false);

    const handleGenerate = async () => {
        if (!topic.trim()) return;
        setStep("generating");
        setError(null);

        try {
            const res = await api.generateFromTopic({
                topic: topic.trim(),
                post_type: postType,
                tone,
            });
            setResult(res);
            setEditContent(res.content);
            setStep("review");
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : "Generation failed");
            setStep("input");
        }
    };

    const handleRegenerate = async () => {
        setIsRegenerating(true);
        try {
            const res = await api.generateFromTopic({
                topic: topic.trim(),
                post_type: postType,
                tone,
            });
            if (result?.post_id) {
                await api.deletePost(result.post_id).catch(() => { });
            }
            setResult(res);
            setEditContent(res.content);
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : "Regeneration failed");
        } finally {
            setIsRegenerating(false);
        }
    };

    const handleApprove = async () => {
        if (!result?.post_id) return;
        setIsApproving(true);
        try {
            if (isEditing && editContent !== result.content) {
                await api.updatePost(result.post_id, { content: editContent });
            }
            await api.updatePost(result.post_id, { status: "approved" });
            router.push("/posts");
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : "Approval failed");
        } finally {
            setIsApproving(false);
        }
    };

    const handleDiscard = async () => {
        if (result?.post_id) {
            await api.deletePost(result.post_id).catch(() => { });
        }
        setResult(null);
        setStep("input");
        setTopic("");
        setError(null);
    };

    const handleCopy = () => {
        const text = isEditing ? editContent : (result?.content ?? "");
        const full = result?.hashtags ? `${text}\n\n${result.hashtags}` : text;
        navigator.clipboard.writeText(full);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="max-w-3xl mx-auto animate-fadeIn">
            {/* Header */}
            <div className="flex items-center gap-3 mb-8">
                <Link href="/" className="btn btn-ghost btn-sm">
                    <ArrowLeft className="h-4 w-4" />
                </Link>
                <div>
                    <h1 className="text-xl font-bold text-text">Generate Post</h1>
                    <p className="text-sm text-muted">
                        {step === "input" && "Describe your topic and let AI craft the perfect post"}
                        {step === "generating" && "AI is writing your post..."}
                        {step === "review" && "Review your generated post"}
                    </p>
                </div>
            </div>

            {error && (
                <div className="mb-6 p-4 rounded-xl bg-danger-light text-danger text-sm flex items-center gap-2">
                    <XCircle className="h-4 w-4 shrink-0" />
                    {error}
                </div>
            )}

            {/* ── Step 1: Input ── */}
            {step === "input" && (
                <div className="card p-6 animate-slideUp">
                    <div className="mb-6">
                        <label className="block text-sm font-medium text-text mb-2">
                            What do you want to write about?
                        </label>
                        <textarea
                            className="input textarea"
                            placeholder="e.g., How AI coding assistants are changing the way we build software in 2026..."
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                            rows={3}
                        />
                    </div>

                    <div className="mb-6">
                        <label className="block text-sm font-medium text-text mb-2">
                            Post Type
                        </label>
                        <div className="flex flex-wrap gap-2">
                            {POST_TYPES.map((t) => (
                                <button
                                    key={t}
                                    className={`chip ${postType === t ? "chip-active" : ""}`}
                                    onClick={() => setPostType(t)}
                                >
                                    {t}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="mb-8">
                        <label className="block text-sm font-medium text-text mb-2">
                            Tone
                        </label>
                        <div className="flex flex-wrap gap-2">
                            {TONES.map((t) => (
                                <button
                                    key={t}
                                    className={`chip ${tone === t ? "chip-active" : ""}`}
                                    onClick={() => setTone(t)}
                                >
                                    {t}
                                </button>
                            ))}
                        </div>
                    </div>

                    <button
                        className="btn btn-primary btn-lg w-full"
                        disabled={!topic.trim()}
                        onClick={handleGenerate}
                    >
                        <Sparkles className="h-4 w-4" />
                        Generate Post
                    </button>
                </div>
            )}

            {/* ── Step 2: Generating ── */}
            {step === "generating" && (
                <div className="card p-12 text-center animate-slideUp">
                    <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-light mb-6">
                        <Sparkles className="h-8 w-8 text-primary animate-pulse-slow" />
                    </div>
                    <h2 className="text-lg font-semibold text-text mb-2">
                        Generating your post
                    </h2>
                    <p className="text-sm text-muted mb-6">
                        AI is crafting engaging content about your topic...
                    </p>
                    <div className="max-w-xs mx-auto space-y-2.5">
                        <div className="skeleton h-3 w-full"></div>
                        <div className="skeleton h-3 w-5/6"></div>
                        <div className="skeleton h-3 w-4/6"></div>
                        <div className="skeleton h-3 w-full"></div>
                        <div className="skeleton h-3 w-3/4"></div>
                    </div>
                </div>
            )}

            {/* ── Step 3: Review ── */}
            {step === "review" && result && (
                <div className="space-y-4 animate-slideUp">
                    {/* Post Preview Card */}
                    <div className="card overflow-hidden">
                        {/* LinkedIn-style header */}
                        <div className="flex items-center gap-3 p-4 pb-0">
                            <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center text-sm font-bold text-primary">
                                RK
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-text">Rehaan Khatri</p>
                                <p className="text-xs text-muted">Just now · LinkedIn</p>
                            </div>
                        </div>

                        {/* Content */}
                        <div className="p-4">
                            {isEditing ? (
                                <textarea
                                    className="input textarea min-h-[200px] text-sm leading-relaxed"
                                    value={editContent}
                                    onChange={(e) => setEditContent(e.target.value)}
                                />
                            ) : (
                                <div className="text-sm leading-relaxed text-text whitespace-pre-wrap">
                                    {result.content}
                                </div>
                            )}

                            {result.hashtags && (
                                <p className="text-sm text-primary mt-4">{result.hashtags}</p>
                            )}
                        </div>

                        {/* Metrics Bar */}
                        <div className="flex items-center gap-4 px-4 py-3 border-t border-border-light bg-border-light/30">
                            <span className="text-xs text-muted">
                                📊 {result.word_count} words
                            </span>
                            <span className="text-xs text-muted">
                                ⏱ {Math.ceil((result.estimated_read_time || 30) / 60)}m read
                            </span>
                            <button
                                onClick={handleCopy}
                                className="ml-auto btn btn-ghost btn-sm text-xs"
                            >
                                {copied ? (
                                    <><Check className="h-3 w-3 text-success" /> Copied</>
                                ) : (
                                    <><Copy className="h-3 w-3" /> Copy</>
                                )}
                            </button>
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex flex-wrap gap-3">
                        <button
                            className="btn btn-success flex-1"
                            onClick={handleApprove}
                            disabled={isApproving}
                        >
                            {isApproving ? (
                                <><div className="spinner"></div> Approving...</>
                            ) : (
                                <><CheckCircle2 className="h-4 w-4" /> Approve &amp; Save</>
                            )}
                        </button>

                        <button
                            className="btn btn-secondary"
                            onClick={handleRegenerate}
                            disabled={isRegenerating}
                        >
                            {isRegenerating ? (
                                <><div className="spinner"></div> Regenerating...</>
                            ) : (
                                <><RefreshCw className="h-4 w-4" /> Regenerate</>
                            )}
                        </button>

                        <button
                            className="btn btn-secondary"
                            onClick={() => {
                                if (isEditing) {
                                    setIsEditing(false);
                                    setResult({ ...result, content: editContent });
                                } else {
                                    setIsEditing(true);
                                }
                            }}
                        >
                            <Pencil className="h-4 w-4" />
                            {isEditing ? "Done Editing" : "Edit"}
                        </button>

                        <button className="btn btn-danger" onClick={handleDiscard}>
                            <XCircle className="h-4 w-4" /> Discard
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
