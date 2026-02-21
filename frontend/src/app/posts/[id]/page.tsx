"use client";

import { use } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { formatDate, getStatusColor } from "@/lib/utils";
import {
    ArrowLeft,
    Copy,
    Check,
    Trash2,
    CheckCircle2,
} from "lucide-react";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function PostDetailPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = use(params);
    const postId = parseInt(id);
    const router = useRouter();
    const [copied, setCopied] = useState(false);

    const { data: post, isLoading } = useQuery({
        queryKey: ["post", postId],
        queryFn: () => api.getPost(postId),
    });

    const handleCopy = () => {
        if (!post) return;
        const text = post.hashtags ? `${post.content}\n\n${post.hashtags}` : post.content;
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const handleDelete = async () => {
        if (!confirm("Delete this post permanently?")) return;
        await api.deletePost(postId);
        router.push("/posts");
    };

    const handleApprove = async () => {
        await api.updatePost(postId, { status: "approved" });
        router.refresh();
    };

    if (isLoading) {
        return (
            <div className="max-w-3xl mx-auto animate-fadeIn">
                <div className="skeleton h-6 w-32 mb-6"></div>
                <div className="card p-6">
                    <div className="skeleton h-5 w-1/2 mb-4"></div>
                    <div className="skeleton h-3 w-full mb-2"></div>
                    <div className="skeleton h-3 w-full mb-2"></div>
                    <div className="skeleton h-3 w-3/4"></div>
                </div>
            </div>
        );
    }

    if (!post) {
        return (
            <div className="max-w-3xl mx-auto text-center py-20">
                <p className="text-muted">Post not found</p>
                <Link href="/posts" className="btn btn-primary btn-sm mt-4">Back to Posts</Link>
            </div>
        );
    }

    return (
        <div className="max-w-3xl mx-auto animate-fadeIn">
            <div className="flex items-center gap-3 mb-6">
                <Link href="/posts" className="btn btn-ghost btn-sm">
                    <ArrowLeft className="h-4 w-4" />
                </Link>
                <h1 className="text-lg font-bold text-text">Post Detail</h1>
            </div>

            <div className="card overflow-hidden">
                <div className="flex items-center gap-3 p-5 border-b border-border-light">
                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center text-sm font-bold text-primary">
                        RK
                    </div>
                    <div className="flex-1">
                        <p className="text-sm font-semibold text-text">Rehaan Khatri</p>
                        <p className="text-xs text-muted">{formatDate(post.created_at)}</p>
                    </div>
                    <span className={`badge ${getStatusColor(post.status)}`}>{post.status}</span>
                </div>

                <div className="px-5 pt-4 pb-2">
                    <h2 className="text-base font-semibold text-text">{post.topic}</h2>
                </div>

                <div className="px-5 pb-4">
                    <div className="text-sm leading-relaxed text-text whitespace-pre-wrap">
                        {post.content}
                    </div>
                    {post.hashtags && (
                        <p className="text-sm text-primary mt-4">{post.hashtags}</p>
                    )}
                </div>

                <div className="flex items-center gap-4 px-5 py-3 border-t border-border-light bg-border-light/30 text-xs text-muted">
                    <span>{post.post_type}</span>
                    <span>·</span>
                    <span>{post.tone}</span>
                    {post.word_count && (
                        <>
                            <span>·</span>
                            <span>{post.word_count} words</span>
                        </>
                    )}
                </div>
            </div>

            <div className="flex flex-wrap gap-3 mt-4">
                {post.status === "draft" && (
                    <button className="btn btn-success flex-1" onClick={handleApprove}>
                        <CheckCircle2 className="h-4 w-4" /> Approve
                    </button>
                )}
                <button className="btn btn-secondary" onClick={handleCopy}>
                    {copied ? <><Check className="h-4 w-4 text-success" /> Copied</> : <><Copy className="h-4 w-4" /> Copy</>}
                </button>
                <button className="btn btn-danger" onClick={handleDelete}>
                    <Trash2 className="h-4 w-4" /> Delete
                </button>
            </div>
        </div>
    );
}
