"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import {
    BarChart3, FileText, Hash, TrendingUp, Clock, PenLine,
} from "lucide-react";
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, Legend,
} from "recharts";

const COLORS = ["#6366F1", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"];

function StatCard({ label, value, icon: Icon, sub }: { label: string; value: number | string; icon: React.ComponentType<{ className?: string }>; sub?: string }) {
    return (
        <div className="card p-5">
            <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary-light">
                    <Icon className="h-5 w-5 text-primary" />
                </div>
                <div>
                    <p className="text-2xl font-bold text-text">{value}</p>
                    <p className="text-xs text-muted">{label}</p>
                    {sub && <p className="text-[10px] text-muted">{sub}</p>}
                </div>
            </div>
        </div>
    );
}

export default function AnalyticsPage() {
    const { data, isLoading } = useQuery({
        queryKey: ["analytics"],
        queryFn: () =>
            fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/analytics`)
                .then((r) => r.json()),
    });

    if (isLoading) {
        return (
            <div className="space-y-6 animate-fadeIn">
                <div className="skeleton h-8 w-48 rounded-lg" />
                <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                    {[...Array(4)].map((_, i) => <div key={i} className="skeleton h-24 rounded-xl" />)}
                </div>
                <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                    <div className="skeleton h-72 rounded-xl" />
                    <div className="skeleton h-72 rounded-xl" />
                </div>
            </div>
        );
    }

    const analytics = data || {};

    return (
        <div className="space-y-8 animate-fadeIn">
            <div>
                <h1 className="text-2xl font-bold text-text flex items-center gap-2">
                    <BarChart3 className="h-6 w-6 text-primary" /> Analytics
                </h1>
                <p className="mt-1 text-muted">Track your content performance and productivity.</p>
            </div>

            {/* Top Stats */}
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                <StatCard label="Total Posts" value={analytics.total_posts || 0} icon={FileText} />
                <StatCard label="Total Words" value={(analytics.total_words || 0).toLocaleString()} icon={PenLine} sub={`~${analytics.avg_word_count || 0} avg/post`} />
                <StatCard label="Trends Discovered" value={analytics.trends_discovered || 0} icon={TrendingUp} />
                <StatCard label="Scheduled" value={analytics.queue_pending || 0} icon={Clock} />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                {/* Posts by Month (Bar Chart) */}
                <div className="card p-6">
                    <h3 className="text-sm font-semibold text-text mb-4">Posts Over Time</h3>
                    {(analytics.monthly_chart || []).length === 0 ? (
                        <div className="flex items-center justify-center h-56 text-sm text-muted">No data yet</div>
                    ) : (
                        <ResponsiveContainer width="100%" height={240}>
                            <BarChart data={analytics.monthly_chart}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                                <XAxis dataKey="month" tick={{ fontSize: 11, fill: "#94A3B8" }} />
                                <YAxis tick={{ fontSize: 11, fill: "#94A3B8" }} allowDecimals={false} />
                                <Tooltip
                                    contentStyle={{ background: "#fff", border: "1px solid #E2E8F0", borderRadius: "8px", fontSize: 12 }}
                                />
                                <Bar dataKey="posts" fill="#6366F1" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    )}
                </div>

                {/* Status Breakdown (Pie Chart) */}
                <div className="card p-6">
                    <h3 className="text-sm font-semibold text-text mb-4">Status Breakdown</h3>
                    {(analytics.status_chart || []).length === 0 ? (
                        <div className="flex items-center justify-center h-56 text-sm text-muted">No data yet</div>
                    ) : (
                        <ResponsiveContainer width="100%" height={240}>
                            <PieChart>
                                <Pie
                                    data={analytics.status_chart}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={55}
                                    outerRadius={90}
                                    paddingAngle={3}
                                    dataKey="value"
                                    nameKey="name"
                                    label={(props: any) => `${props.name || ""} ${((props.percent ?? 0) * 100).toFixed(0)}%`}
                                    labelLine={false}
                                >
                                    {(analytics.status_chart || []).map((_: unknown, i: number) => (
                                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Legend wrapperStyle={{ fontSize: 12 }} />
                                <Tooltip contentStyle={{ background: "#fff", border: "1px solid #E2E8F0", borderRadius: "8px", fontSize: 12 }} />
                            </PieChart>
                        </ResponsiveContainer>
                    )}
                </div>

                {/* Post Type Breakdown */}
                <div className="card p-6">
                    <h3 className="text-sm font-semibold text-text mb-4">Post Types</h3>
                    {(analytics.type_chart || []).length === 0 ? (
                        <div className="flex items-center justify-center h-56 text-sm text-muted">No data yet</div>
                    ) : (
                        <ResponsiveContainer width="100%" height={240}>
                            <BarChart data={analytics.type_chart} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                                <XAxis type="number" tick={{ fontSize: 11, fill: "#94A3B8" }} allowDecimals={false} />
                                <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: "#94A3B8" }} width={80} />
                                <Tooltip contentStyle={{ background: "#fff", border: "1px solid #E2E8F0", borderRadius: "8px", fontSize: 12 }} />
                                <Bar dataKey="value" fill="#10B981" radius={[0, 4, 4, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    )}
                </div>

                {/* Tone Breakdown */}
                <div className="card p-6">
                    <h3 className="text-sm font-semibold text-text mb-4">Tone Distribution</h3>
                    {(analytics.tone_chart || []).length === 0 ? (
                        <div className="flex items-center justify-center h-56 text-sm text-muted">No data yet</div>
                    ) : (
                        <ResponsiveContainer width="100%" height={240}>
                            <PieChart>
                                <Pie
                                    data={analytics.tone_chart}
                                    cx="50%"
                                    cy="50%"
                                    outerRadius={90}
                                    paddingAngle={2}
                                    dataKey="value"
                                    nameKey="name"
                                >
                                    {(analytics.tone_chart || []).map((_: unknown, i: number) => (
                                        <Cell key={i} fill={COLORS[(i + 2) % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Legend wrapperStyle={{ fontSize: 12 }} />
                                <Tooltip contentStyle={{ background: "#fff", border: "1px solid #E2E8F0", borderRadius: "8px", fontSize: 12 }} />
                            </PieChart>
                        </ResponsiveContainer>
                    )}
                </div>
            </div>
        </div>
    );
}
