/**
 * API client for FastAPI backend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`, {
        headers: { "Content-Type": "application/json", ...options?.headers },
        ...options,
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || "API Error");
    }
    if (res.status === 204) return null as T;
    return res.json();
}

/* ── Types ── */

export interface Post {
    id: number;
    topic: string;
    content: string;
    status: "draft" | "approved" | "published" | "rejected" | "scheduled";
    post_type: string;
    tone: string;
    hashtags: string | null;
    image_url: string | null;
    source_trend_id: number | null;
    word_count: number | null;
    estimated_read_time: number | null;
    created_at: string;
    approved_at: string | null;
    published_at: string | null;
    scheduled_for: string | null;
    updated_at: string;
}

export interface Stats {
    total_posts: number;
    drafts: number;
    approved: number;
    published: number;
    rejected: number;
    scheduled: number;
}

export interface GenerateResult {
    post_id: number | null;
    topic: string;
    content: string;
    hashtags: string;
    post_type: string;
    tone: string;
    word_count: number;
    estimated_read_time: number;
}

export interface ReviewResult {
    review: string;
    score: number;
    content: string;
}

export interface Trend {
    id: number;
    title: string;
    source: string;
    source_url: string | null;
    summary: string | null;
    relevance_score: number | null;
    engagement_count: number;
    category: string | null;
    discovered_at: string;
    used: boolean;
    metadata: Record<string, unknown>;
}

export interface QueueItem {
    id: number;
    post_id: number;
    scheduled_for: string;
    platform: string;
    status: string;
    error_message: string | null;
    published_at: string | null;
    posts?: Post;
}

/* ── Posts ── */

export const api = {
    // Posts
    listPosts: (params?: { status?: string; limit?: number; offset?: number }) => {
        const q = new URLSearchParams();
        if (params?.status) q.set("status", params.status);
        if (params?.limit) q.set("limit", String(params.limit));
        if (params?.offset) q.set("offset", String(params.offset));
        const qs = q.toString();
        return request<{ posts: Post[]; count: number }>(`/api/posts${qs ? `?${qs}` : ""}`);
    },

    getPost: (id: number) => request<Post>(`/api/posts/${id}`),

    createPost: (data: { topic: string; content: string; post_type?: string; tone?: string; hashtags?: string }) =>
        request<Post>("/api/posts", { method: "POST", body: JSON.stringify(data) }),

    updatePost: (id: number, data: Partial<Pick<Post, "content" | "status" | "hashtags" | "post_type" | "tone">>) =>
        request<Post>(`/api/posts/${id}`, { method: "PATCH", body: JSON.stringify(data) }),

    deletePost: (id: number) => request<null>(`/api/posts/${id}`, { method: "DELETE" }),

    // Stats
    getStats: () => request<Stats>("/api/stats"),

    // Generation
    generateFromTopic: (data: { topic: string; post_type?: string; tone?: string; generate_hashtags?: boolean }) =>
        request<GenerateResult>("/api/generate/from-topic", { method: "POST", body: JSON.stringify(data) }),

    generateIdeas: (data: { theme: string; count?: number }) =>
        request<{ ideas: string[]; theme: string }>("/api/generate/ideas", { method: "POST", body: JSON.stringify(data) }),

    reviewPost: (content: string) =>
        request<ReviewResult>("/api/generate/review", { method: "POST", body: JSON.stringify({ content }) }),

    improvePost: (postId: number, feedback: string) =>
        request<{ post_id: number; content: string; status: string }>("/api/generate/improve", {
            method: "POST",
            body: JSON.stringify({ post_id: postId, feedback }),
        }),

    // Image Generation (Phase 3)
    generateImage: (postId: number) =>
        request<{ image_url: string | null; prompt: string; post_id: number }>("/api/generate/image", {
            method: "POST",
            body: JSON.stringify({ post_id: postId }),
        }),

    // Trends (Phase 2)
    listTrends: (params?: { source?: string; category?: string; limit?: number; offset?: number }) => {
        const q = new URLSearchParams();
        if (params?.source) q.set("source", params.source);
        if (params?.category) q.set("category", params.category);
        if (params?.limit) q.set("limit", String(params.limit));
        if (params?.offset) q.set("offset", String(params.offset));
        const qs = q.toString();
        return request<{ trends: Trend[]; count: number }>(`/api/trends/latest${qs ? `?${qs}` : ""}`);
    },

    getTrend: (id: number) => request<Trend>(`/api/trends/${id}`),

    fetchTrends: () =>
        request<{ fetched: number; message: string }>("/api/trends/fetch", { method: "POST" }),

    generateFromTrend: (data: { trend_id: number; post_type?: string; tone?: string }) =>
        request<GenerateResult>("/api/generate/from-trend", { method: "POST", body: JSON.stringify(data) }),

    // Publishing (Phase 4)
    schedulePost: (data: { post_id: number; scheduled_for: string; platform?: string }) =>
        request<QueueItem>("/api/publish/schedule", { method: "POST", body: JSON.stringify(data) }),

    publishNow: (postId: number) =>
        request<{ message: string; post_id: number }>("/api/publish/now", {
            method: "POST",
            body: JSON.stringify({ post_id: postId }),
        }),

    getQueue: (params?: { status?: string; limit?: number }) => {
        const q = new URLSearchParams();
        if (params?.status) q.set("status", params.status);
        if (params?.limit) q.set("limit", String(params.limit));
        const qs = q.toString();
        return request<{ queue: QueueItem[]; count: number }>(`/api/publish/queue${qs ? `?${qs}` : ""}`);
    },

    cancelSchedule: (queueId: number) =>
        request<{ message: string }>(`/api/publish/schedule/${queueId}`, { method: "DELETE" }),

    getCalendar: (month?: number, year?: number) => {
        const q = new URLSearchParams();
        if (month) q.set("month", String(month));
        if (year) q.set("year", String(year));
        const qs = q.toString();
        return request<{ month: number; year: number; scheduled: QueueItem[]; published: Post[] }>(
            `/api/publish/calendar${qs ? `?${qs}` : ""}`
        );
    },

    // Health
    health: () => request<{ status: string; service: string }>("/api/health"),
};
