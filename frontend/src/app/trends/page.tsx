"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, type Trend } from "@/lib/api";
import {
    TrendingUp, RefreshCw, Sparkles, Globe, ExternalLink, Search, Filter, Loader2, Flame,
} from "lucide-react";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

const SOURCES = [
    { value: "", label: "All Sources" },
    { value: "hackernews", label: "🟠 Hacker News" },
    { value: "reddit", label: "🔵 Reddit" },
    { value: "rss", label: "🟢 RSS" },
];

function ScoreBadge({ score }: { score: number | null }) {
    const s = score ?? 0;
    const color = s >= 0.7 ? "bg-success-light text-success" : s >= 0.4 ? "bg-warning-light text-warning" : "bg-border-light text-muted";
    return (
        <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold ${color}`}>
            <Flame className="h-3 w-3" /> {(s * 100).toFixed(0)}%
        </span>
    );
}

function SourceBadge({ source }: { source: string }) {
    const styles: Record<string, string> = {
        hackernews: "bg-orange-100 text-orange-700",
        reddit: "bg-blue-100 text-blue-700",
        rss: "bg-green-100 text-green-700",
    };
    return <span className={`badge ${styles[source] || "badge-muted"}`}>{source}</span>;
}

export default function TrendsPage() {
    const [sourceFilter, setSourceFilter] = useState("");
    const [search, setSearch] = useState("");
    const router = useRouter();
    const qc = useQueryClient();

    const { data, isLoading } = useQuery({
        queryKey: ["trends", sourceFilter],
        queryFn: () => api.listTrends({ source: sourceFilter || undefined, limit: 30 }),
    });

    const fetchMutation = useMutation({
        mutationFn: api.fetchTrends,
        onSuccess: (d) => {
            toast.success(`Fetched ${d.fetched} trends!`);
            qc.invalidateQueries({ queryKey: ["trends"] });
        },
        onError: (e) => toast.error(e.message),
    });

    const generateFromTrend = useMutation({
        mutationFn: (trendId: number) => api.generateFromTrend({ trend_id: trendId }),
        onSuccess: (d) => {
            toast.success("Post generated from trend!");
            if (d.post_id) router.push(`/posts/${d.post_id}`);
        },
        onError: (e) => toast.error(e.message),
    });

    const trends = (data?.trends ?? []).filter((t) =>
        search ? t.title.toLowerCase().includes(search.toLowerCase()) : true
    );

    return (
        <div className="space-y-6 animate-fadeIn">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-text flex items-center gap-2">
                        <TrendingUp className="h-6 w-6 text-primary" /> Trending Topics
                    </h1>
                    <p className="mt-1 text-muted">Discover what&apos;s trending and turn it into content.</p>
                </div>
                <button
                    onClick={() => fetchMutation.mutate()}
                    disabled={fetchMutation.isPending}
                    className="btn btn-primary"
                >
                    {fetchMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                    Fetch Trends
                </button>
            </div>

            {/* Filters */}
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
                    <input className="input pl-10" placeholder="Search trends..." value={search} onChange={(e) => setSearch(e.target.value)} />
                </div>
                <div className="flex items-center gap-1.5">
                    <Filter className="h-4 w-4 text-muted" />
                    {SOURCES.map((s) => (
                        <button key={s.value} onClick={() => setSourceFilter(s.value)} className={`chip ${sourceFilter === s.value ? "chip-active" : ""}`}>
                            {s.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Trends Grid */}
            {isLoading ? (
                <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {[...Array(6)].map((_, i) => <div key={i} className="skeleton h-44 rounded-xl" />)}
                </div>
            ) : trends.length === 0 ? (
                <div className="card flex flex-col items-center justify-center py-16 text-center">
                    <Globe className="h-10 w-10 text-muted mb-4" />
                    <h3 className="text-base font-semibold text-text">No trends yet</h3>
                    <p className="mt-1 text-sm text-muted">Click &quot;Fetch Trends&quot; to pull latest topics from HN, Reddit, and RSS.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {trends.map((t, i) => (
                        <div key={t.id} className="card p-5 flex flex-col animate-slideUp" style={{ animationDelay: `${i * 40}ms` }}>
                            <div className="flex items-center justify-between mb-2">
                                <SourceBadge source={t.source} />
                                <ScoreBadge score={t.relevance_score} />
                            </div>

                            <h3 className="text-sm font-semibold text-text line-clamp-2 flex-1">{t.title}</h3>

                            {t.summary && (
                                <p className="mt-2 text-xs text-muted line-clamp-2">{t.summary}</p>
                            )}

                            <div className="mt-3 flex items-center gap-3 text-xs text-muted border-t border-border pt-3">
                                <span>🔥 {t.engagement_count.toLocaleString()}</span>
                                {t.category && <span>📂 {t.category}</span>}
                                <span>{new Date(t.discovered_at).toLocaleDateString()}</span>
                            </div>

                            <div className="mt-3 flex gap-2">
                                <button
                                    onClick={() => generateFromTrend.mutate(t.id)}
                                    disabled={generateFromTrend.isPending}
                                    className="btn btn-primary btn-sm flex-1"
                                >
                                    <Sparkles className="h-3.5 w-3.5" /> Generate Post
                                </button>
                                {t.source_url && (
                                    <a
                                        href={t.source_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="btn btn-ghost btn-sm"
                                    >
                                        <ExternalLink className="h-3.5 w-3.5" />
                                    </a>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
