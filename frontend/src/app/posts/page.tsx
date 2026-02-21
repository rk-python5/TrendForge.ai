"use client";

import { useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api, type Post } from "@/lib/api";
import { formatDate, truncate, getStatusColor } from "@/lib/utils";
import {
    FileText,
    Search,
    PenLine,
    Trash2,
    Copy,
    Check,
} from "lucide-react";

const STATUS_FILTERS = ["all", "draft", "approved", "published", "rejected"];

export default function PostsPage() {
    const [statusFilter, setStatusFilter] = useState("all");
    const [search, setSearch] = useState("");
    const [copiedId, setCopiedId] = useState<number | null>(null);

    const { data, isLoading, refetch } = useQuery({
        queryKey: ["posts", statusFilter],
        queryFn: () =>
            api.listPosts({
                status: statusFilter === "all" ? undefined : statusFilter,
                limit: 50,
            }),
    });

    const posts = (data?.posts ?? []).filter((p) =>
        search ? p.topic.toLowerCase().includes(search.toLowerCase()) ||
            p.content.toLowerCase().includes(search.toLowerCase()) : true
    );

    const handleDelete = async (id: number) => {
        if (!confirm("Delete this post?")) return;
        await api.deletePost(id);
        refetch();
    };

    const handleCopy = (post: Post) => {
        const text = post.hashtags ? `${post.content}\n\n${post.hashtags}` : post.content;
        navigator.clipboard.writeText(text);
        setCopiedId(post.id);
        setTimeout(() => setCopiedId(null), 2000);
    };

    return (
        <div className="max-w-5xl animate-fadeIn">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-xl font-bold text-text">Posts</h1>
                    <p className="text-sm text-muted">
                        {data?.count ?? 0} posts in your library
                    </p>
                </div>
                <Link href="/generate" className="btn btn-primary btn-sm">
                    <PenLine className="h-3.5 w-3.5" />
                    New Post
                </Link>
            </div>

            {/* Filters */}
            <div className="flex flex-col sm:flex-row gap-3 mb-6">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted" />
                    <input
                        type="text"
                        className="input pl-9"
                        placeholder="Search posts..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>
                <div className="flex gap-1.5">
                    {STATUS_FILTERS.map((s) => (
                        <button
                            key={s}
                            className={`chip text-xs ${statusFilter === s ? "chip-active" : ""}`}
                            onClick={() => setStatusFilter(s)}
                        >
                            {s}
                        </button>
                    ))}
                </div>
            </div>

            {/* Posts list */}
            {isLoading ? (
                <div className="space-y-3">
                    {[1, 2, 3, 4].map((i) => (
                        <div key={i} className="card p-4">
                            <div className="flex gap-4">
                                <div className="flex-1">
                                    <div className="skeleton h-4 w-1/3 mb-2"></div>
                                    <div className="skeleton h-3 w-full mb-1"></div>
                                    <div className="skeleton h-3 w-2/3"></div>
                                </div>
                                <div className="skeleton h-6 w-16 rounded-full"></div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : posts.length === 0 ? (
                <div className="card p-12 text-center">
                    <FileText className="h-10 w-10 text-muted mx-auto mb-3 opacity-40" />
                    <p className="text-sm font-medium text-text mb-1">No posts found</p>
                    <p className="text-xs text-muted mb-4">
                        {statusFilter !== "all"
                            ? `No ${statusFilter} posts. Try a different filter.`
                            : "Generate your first post to see it here."}
                    </p>
                    <Link href="/generate" className="btn btn-primary btn-sm">
                        <PenLine className="h-3.5 w-3.5" />
                        Generate Post
                    </Link>
                </div>
            ) : (
                <div className="space-y-3">
                    {posts.map((post) => (
                        <div key={post.id} className="card p-4 flex gap-4 items-start group">
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                    <Link
                                        href={`/posts/${post.id}`}
                                        className="text-sm font-semibold text-text hover:text-primary transition truncate"
                                    >
                                        {post.topic}
                                    </Link>
                                    <span className={`badge ${getStatusColor(post.status)} shrink-0`}>
                                        {post.status}
                                    </span>
                                </div>
                                <p className="text-xs text-muted line-clamp-2 leading-relaxed mb-2">
                                    {truncate(post.content, 180)}
                                </p>
                                <div className="flex items-center gap-3 text-[10px] text-muted">
                                    <span>{post.post_type}</span>
                                    <span>·</span>
                                    <span>{post.tone}</span>
                                    <span>·</span>
                                    <span>{formatDate(post.created_at)}</span>
                                    {post.word_count && (
                                        <>
                                            <span>·</span>
                                            <span>{post.word_count} words</span>
                                        </>
                                    )}
                                </div>
                            </div>
                            <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition shrink-0">
                                <button
                                    onClick={() => handleCopy(post)}
                                    className="btn btn-ghost btn-sm"
                                    title="Copy"
                                >
                                    {copiedId === post.id ? (
                                        <Check className="h-3.5 w-3.5 text-success" />
                                    ) : (
                                        <Copy className="h-3.5 w-3.5" />
                                    )}
                                </button>
                                <button
                                    onClick={() => handleDelete(post.id)}
                                    className="btn btn-ghost btn-sm text-danger"
                                    title="Delete"
                                >
                                    <Trash2 className="h-3.5 w-3.5" />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
