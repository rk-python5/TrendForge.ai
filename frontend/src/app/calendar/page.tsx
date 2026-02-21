"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, type QueueItem } from "@/lib/api";
import {
    Calendar as CalendarIcon, Clock, Trash2, Loader2, Send, ChevronLeft, ChevronRight, FileText,
} from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

export default function CalendarPage() {
    const now = new Date();
    const [month, setMonth] = useState(now.getMonth() + 1);
    const [year, setYear] = useState(now.getFullYear());
    const qc = useQueryClient();

    const { data: calendarData, isLoading: calLoading } = useQuery({
        queryKey: ["calendar", month, year],
        queryFn: () => api.getCalendar(month, year),
    });

    const { data: queueData, isLoading: queueLoading } = useQuery({
        queryKey: ["queue"],
        queryFn: () => api.getQueue({ limit: 20 }),
    });

    const cancelMutation = useMutation({
        mutationFn: (id: number) => api.cancelSchedule(id),
        onSuccess: () => {
            toast.success("Schedule cancelled");
            qc.invalidateQueries({ queryKey: ["queue"] });
            qc.invalidateQueries({ queryKey: ["calendar"] });
            qc.invalidateQueries({ queryKey: ["posts"] });
        },
        onError: (e) => toast.error(e.message),
    });

    const prevMonth = () => {
        if (month === 1) { setMonth(12); setYear(year - 1); }
        else setMonth(month - 1);
    };
    const nextMonth = () => {
        if (month === 12) { setMonth(1); setYear(year + 1); }
        else setMonth(month + 1);
    };

    // Build calendar grid
    const daysInMonth = new Date(year, month, 0).getDate();
    const firstDay = new Date(year, month - 1, 1).getDay();
    const scheduledByDay: Record<number, QueueItem[]> = {};
    calendarData?.scheduled?.forEach((item) => {
        const d = new Date(item.scheduled_for).getDate();
        if (!scheduledByDay[d]) scheduledByDay[d] = [];
        scheduledByDay[d].push(item);
    });

    const statusBadge: Record<string, string> = {
        pending: "bg-warning-light text-warning",
        publishing: "bg-primary-light text-primary",
        published: "bg-success-light text-success",
        failed: "bg-danger-light text-danger",
        cancelled: "bg-border-light text-muted",
    };

    return (
        <div className="space-y-8 animate-fadeIn">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-text flex items-center gap-2">
                    <CalendarIcon className="h-6 w-6 text-primary" /> Publishing Calendar
                </h1>
                <p className="mt-1 text-muted">Schedule and manage your content publishing.</p>
            </div>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
                {/* Calendar */}
                <div className="lg:col-span-2">
                    <div className="card p-6">
                        {/* Month Nav */}
                        <div className="flex items-center justify-between mb-6">
                            <button onClick={prevMonth} className="btn btn-ghost btn-sm"><ChevronLeft className="h-4 w-4" /></button>
                            <h2 className="text-lg font-semibold text-text">{MONTHS[month - 1]} {year}</h2>
                            <button onClick={nextMonth} className="btn btn-ghost btn-sm"><ChevronRight className="h-4 w-4" /></button>
                        </div>

                        {/* Day Headers */}
                        <div className="grid grid-cols-7 gap-1 mb-2">
                            {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((d) => (
                                <div key={d} className="text-center text-xs font-semibold text-muted py-1">{d}</div>
                            ))}
                        </div>

                        {/* Calendar Grid */}
                        {calLoading ? (
                            <div className="skeleton h-64 rounded-xl" />
                        ) : (
                            <div className="grid grid-cols-7 gap-1">
                                {/* Empty cells for padding */}
                                {Array.from({ length: firstDay }).map((_, i) => (
                                    <div key={`pad-${i}`} className="h-20 rounded-lg bg-border-light/30" />
                                ))}
                                {/* Day cells */}
                                {Array.from({ length: daysInMonth }).map((_, i) => {
                                    const day = i + 1;
                                    const items = scheduledByDay[day] || [];
                                    const isToday = day === now.getDate() && month === now.getMonth() + 1 && year === now.getFullYear();
                                    return (
                                        <div
                                            key={day}
                                            className={`h-20 rounded-lg border p-1.5 text-xs transition-colors ${isToday ? "border-primary bg-primary-light/30" : "border-border-light hover:bg-border-light/50"
                                                }`}
                                        >
                                            <p className={`font-semibold ${isToday ? "text-primary" : "text-text"}`}>{day}</p>
                                            {items.slice(0, 2).map((item) => (
                                                <div key={item.id} className="mt-0.5 truncate rounded bg-primary/10 px-1 py-0.5 text-[10px] font-medium text-primary">
                                                    {item.posts?.topic?.slice(0, 20) || "Post"}
                                                </div>
                                            ))}
                                            {items.length > 2 && (
                                                <p className="mt-0.5 text-[10px] text-muted">+{items.length - 2} more</p>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                </div>

                {/* Queue Sidebar */}
                <div className="space-y-4">
                    <div className="card p-5">
                        <h3 className="text-sm font-semibold text-text mb-4 flex items-center gap-2">
                            <Clock className="h-4 w-4 text-muted" /> Publishing Queue
                        </h3>
                        {queueLoading ? (
                            <div className="space-y-2">
                                {[...Array(3)].map((_, i) => <div key={i} className="skeleton h-16 rounded-lg" />)}
                            </div>
                        ) : (queueData?.queue?.length ?? 0) === 0 ? (
                            <div className="text-center py-8">
                                <Send className="h-8 w-8 text-muted mx-auto mb-2" />
                                <p className="text-sm text-muted">No scheduled posts.</p>
                                <p className="text-xs text-muted mt-1">Approve a post and schedule it!</p>
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {queueData?.queue?.map((item) => (
                                    <div key={item.id} className="rounded-lg border border-border p-3">
                                        <div className="flex items-center justify-between mb-1">
                                            <span className={`inline-flex rounded-full px-2 py-0.5 text-[10px] font-semibold ${statusBadge[item.status] || "badge-muted"}`}>
                                                {item.status}
                                            </span>
                                            {item.status === "pending" && (
                                                <button
                                                    onClick={() => cancelMutation.mutate(item.id)}
                                                    disabled={cancelMutation.isPending}
                                                    className="btn btn-ghost p-1 text-danger hover:bg-danger-light"
                                                >
                                                    <Trash2 className="h-3.5 w-3.5" />
                                                </button>
                                            )}
                                        </div>
                                        <Link href={`/posts/${item.post_id}`} className="text-sm font-medium text-text hover:text-primary transition-colors line-clamp-1">
                                            {item.posts?.topic || `Post #${item.post_id}`}
                                        </Link>
                                        <p className="text-xs text-muted mt-1">
                                            📅 {new Date(item.scheduled_for).toLocaleString()}
                                        </p>
                                        <p className="text-xs text-muted">📱 {item.platform}</p>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Info Card */}
                    <div className="card p-5 bg-gradient-to-br from-indigo-50 to-purple-50">
                        <h3 className="text-sm font-semibold text-text mb-2">💡 How Scheduling Works</h3>
                        <ul className="text-xs text-muted space-y-1.5 leading-relaxed">
                            <li>1. Generate and approve a post</li>
                            <li>2. Open the post and click &quot;Schedule&quot;</li>
                            <li>3. Pick a date and time</li>
                            <li>4. It appears here in the queue</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}
