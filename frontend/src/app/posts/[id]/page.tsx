"use client";

import { use, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import {
    ArrowLeft, CheckCircle, XCircle, Edit3, Trash2, Copy, Check,
    Star, Hash, Loader2, Clock, Image, CalendarPlus, Send,
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

export default function PostDetailPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = use(params);
    const postId = Number(id);
    const router = useRouter();
    const qc = useQueryClient();

    const { data: post, isLoading } = useQuery({
        queryKey: ["posts", postId],
        queryFn: () => api.getPost(postId),
        enabled: !!postId,
    });

    const [editing, setEditing] = useState(false);
    const [editContent, setEditContent] = useState("");
    const [copied, setCopied] = useState(false);
    const [showSchedule, setShowSchedule] = useState(false);
    const [scheduleDate, setScheduleDate] = useState("");

    const updatePost = useMutation({
        mutationFn: ({ data }: { data: Record<string, string> }) => api.updatePost(postId, data),
        onSuccess: () => { qc.invalidateQueries({ queryKey: ["posts"] }); qc.invalidateQueries({ queryKey: ["stats"] }); },
    });

    const deletePost = useMutation({
        mutationFn: () => api.deletePost(postId),
        onSuccess: () => { toast.success("Post deleted"); router.push("/posts"); },
    });

    const reviewPost = useMutation({ mutationFn: (content: string) => api.reviewPost(content) });

    const generateImage = useMutation({
        mutationFn: () => api.generateImage(postId),
        onSuccess: () => {
            toast.success("Image generated!");
            qc.invalidateQueries({ queryKey: ["posts", postId] });
        },
        onError: (e) => toast.error(e.message),
    });

    const publishNow = useMutation({
        mutationFn: () => api.publishNow(postId),
        onSuccess: () => {
            toast.success("Post published!");
            qc.invalidateQueries({ queryKey: ["posts"] });
        },
        onError: (e) => toast.error(e.message),
    });

    const schedulePost = useMutation({
        mutationFn: () => api.schedulePost({ post_id: postId, scheduled_for: new Date(scheduleDate).toISOString() }),
        onSuccess: () => {
            toast.success("Post scheduled!");
            setShowSchedule(false);
            qc.invalidateQueries({ queryKey: ["posts"] });
            qc.invalidateQueries({ queryKey: ["queue"] });
            qc.invalidateQueries({ queryKey: ["calendar"] });
        },
        onError: (e) => toast.error(e.message),
    });

    if (isLoading) {
        return (
            <div className="space-y-6 animate-fadeIn">
                <div className="skeleton h-8 w-48 rounded-lg" />
                <div className="skeleton h-96 rounded-xl" />
            </div>
        );
    }

    if (!post) {
        return (
            <div className="card flex flex-col items-center justify-center py-20 text-center">
                <h2 className="text-lg font-semibold text-text">Post not found</h2>
                <Link href="/posts" className="btn btn-primary btn-sm mt-4"><ArrowLeft className="h-4 w-4" /> Back</Link>
            </div>
        );
    }

    const statusStyles: Record<string, string> = {
        draft: "badge-primary", approved: "badge-success", published: "badge-success",
        rejected: "badge-danger", scheduled: "badge-warning",
    };

    const handleStatusChange = (status: string) => {
        updatePost.mutate({ data: { status } }, { onSuccess: () => toast.success(`Post ${status}`) });
    };

    const handleSaveEdit = () => {
        updatePost.mutate({ data: { content: editContent } }, {
            onSuccess: () => { toast.success("Updated"); setEditing(false); },
        });
    };

    const handleCopy = () => {
        const full = `${post.content}\n\n${post.hashtags || ""}`.trim();
        navigator.clipboard.writeText(full);
        setCopied(true); toast.success("Copied!");
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="space-y-6 animate-fadeIn">
            {/* Header */}
            <div className="flex items-center gap-4">
                <Link href="/posts" className="btn btn-ghost btn-sm"><ArrowLeft className="h-4 w-4" /> Back</Link>
                <div className="min-w-0 flex-1">
                    <h1 className="truncate text-xl font-bold text-text">{post.topic}</h1>
                    <div className="mt-1 flex items-center gap-3 text-sm text-muted">
                        <span className={`badge ${statusStyles[post.status] || "badge-muted"}`}>{post.status}</span>
                        <span>{post.post_type}</span><span>•</span><span>{post.tone}</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
                {/* Content */}
                <div className="lg:col-span-2 space-y-4">
                    {/* Image Preview */}
                    {post.image_url && (
                        <div className="card overflow-hidden">
                            <img src={post.image_url} alt="Post banner" className="w-full h-auto rounded-t-xl" />
                        </div>
                    )}

                    <div className="card p-6">
                        <div className="mb-4 flex items-center justify-between">
                            <h2 className="text-sm font-semibold text-text uppercase tracking-wider">Content</h2>
                            <div className="flex items-center gap-2">
                                <button onClick={handleCopy} className="btn btn-ghost btn-sm">
                                    {copied ? <Check className="h-4 w-4 text-success" /> : <Copy className="h-4 w-4" />}
                                    {copied ? "Copied" : "Copy"}
                                </button>
                                {!editing && (
                                    <button onClick={() => { setEditContent(post.content); setEditing(true); }} className="btn btn-ghost btn-sm">
                                        <Edit3 className="h-4 w-4" /> Edit
                                    </button>
                                )}
                            </div>
                        </div>

                        {editing ? (
                            <div className="space-y-3">
                                <textarea className="input textarea min-h-[250px]" value={editContent} onChange={(e) => setEditContent(e.target.value)} />
                                <div className="flex gap-2 justify-end">
                                    <button onClick={() => setEditing(false)} className="btn btn-secondary btn-sm">Cancel</button>
                                    <button onClick={handleSaveEdit} disabled={updatePost.isPending} className="btn btn-primary btn-sm">
                                        {updatePost.isPending && <Loader2 className="h-4 w-4 animate-spin" />} Save
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <div className="whitespace-pre-wrap text-sm leading-relaxed text-text">{post.content}</div>
                        )}

                        {post.hashtags && (
                            <div className="mt-4 flex items-center gap-1 text-sm text-primary border-t border-border pt-4">
                                <Hash className="h-3.5 w-3.5" /> {post.hashtags}
                            </div>
                        )}
                    </div>

                    {/* AI Review */}
                    {reviewPost.data && (
                        <div className="card p-6 animate-slideUp">
                            <h2 className="mb-3 text-sm font-semibold text-text uppercase tracking-wider flex items-center gap-2">
                                <Star className="h-4 w-4 text-warning" /> AI Review
                            </h2>
                            <div className="mb-3 flex items-center gap-2">
                                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-warning-light text-lg font-bold text-warning">
                                    {reviewPost.data.score}
                                </div>
                                <span className="text-sm text-muted">/ 10</span>
                            </div>
                            <div className="whitespace-pre-wrap text-sm text-muted leading-relaxed">{reviewPost.data.review}</div>
                        </div>
                    )}
                </div>

                {/* Actions Sidebar */}
                <div className="space-y-4">
                    <div className="card p-5 space-y-3">
                        <h3 className="text-sm font-semibold text-text">Metrics</h3>
                        <div className="grid grid-cols-2 gap-3 text-center">
                            <div className="rounded-lg bg-border-light p-3">
                                <p className="text-lg font-bold text-text">{post.word_count ?? 0}</p>
                                <p className="text-xs text-muted">Words</p>
                            </div>
                            <div className="rounded-lg bg-border-light p-3">
                                <p className="text-lg font-bold text-text">{post.estimated_read_time ?? 0}s</p>
                                <p className="text-xs text-muted">Read Time</p>
                            </div>
                        </div>
                    </div>

                    <div className="card p-5 space-y-2">
                        <h3 className="text-sm font-semibold text-text mb-1">Actions</h3>
                        {post.status === "draft" && (
                            <>
                                <button onClick={() => handleStatusChange("approved")} disabled={updatePost.isPending} className="btn btn-success w-full">
                                    <CheckCircle className="h-4 w-4" /> Approve
                                </button>
                                <button onClick={() => handleStatusChange("rejected")} disabled={updatePost.isPending} className="btn btn-danger w-full">
                                    <XCircle className="h-4 w-4" /> Reject
                                </button>
                            </>
                        )}
                        {post.status === "approved" && (
                            <>
                                <button onClick={() => publishNow.mutate()} disabled={publishNow.isPending} className="btn btn-primary w-full">
                                    {publishNow.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />} Publish Now
                                </button>
                                <button onClick={() => setShowSchedule(!showSchedule)} className="btn btn-secondary w-full">
                                    <CalendarPlus className="h-4 w-4" /> Schedule
                                </button>
                            </>
                        )}

                        {/* Schedule Form */}
                        {showSchedule && (
                            <div className="rounded-lg border border-border p-3 space-y-2 animate-slideUp">
                                <input
                                    type="datetime-local"
                                    className="input text-sm"
                                    value={scheduleDate}
                                    onChange={(e) => setScheduleDate(e.target.value)}
                                />
                                <button
                                    onClick={() => schedulePost.mutate()}
                                    disabled={!scheduleDate || schedulePost.isPending}
                                    className="btn btn-primary btn-sm w-full"
                                >
                                    {schedulePost.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Clock className="h-4 w-4" />}
                                    Confirm Schedule
                                </button>
                            </div>
                        )}

                        {/* Image Generation */}
                        <button
                            onClick={() => generateImage.mutate()}
                            disabled={generateImage.isPending}
                            className="btn btn-secondary w-full"
                        >
                            {generateImage.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Image className="h-4 w-4" />}
                            Generate Image
                        </button>

                        <button onClick={() => reviewPost.mutate(post.content)} disabled={reviewPost.isPending} className="btn btn-secondary w-full">
                            {reviewPost.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Star className="h-4 w-4" />} AI Review
                        </button>

                        <button onClick={() => { if (confirm("Delete?")) deletePost.mutate(); }} className="btn btn-ghost w-full text-danger hover:bg-danger-light">
                            <Trash2 className="h-4 w-4" /> Delete
                        </button>
                    </div>

                    <div className="card p-5 space-y-2">
                        <h3 className="text-sm font-semibold text-text">Timeline</h3>
                        <div className="text-xs text-muted space-y-1.5">
                            <p>Created: {new Date(post.created_at).toLocaleString()}</p>
                            {post.approved_at && <p>Approved: {new Date(post.approved_at).toLocaleString()}</p>}
                            {post.scheduled_for && <p>Scheduled: {new Date(post.scheduled_for).toLocaleString()}</p>}
                            {post.published_at && <p>Published: {new Date(post.published_at).toLocaleString()}</p>}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
