"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, type Post } from "@/lib/api";

export function usePosts(status?: string) {
    return useQuery({
        queryKey: ["posts", status],
        queryFn: () => api.listPosts({ status: status || undefined, limit: 50 }),
    });
}

export function usePost(id: number) {
    return useQuery({
        queryKey: ["posts", id],
        queryFn: () => api.getPost(id),
        enabled: !!id,
    });
}

export function useStats() {
    return useQuery({
        queryKey: ["stats"],
        queryFn: api.getStats,
    });
}

export function useUpdatePost() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: ({ id, data }: { id: number; data: Partial<Pick<Post, "content" | "status" | "hashtags" | "post_type" | "tone">> }) =>
            api.updatePost(id, data),
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["posts"] });
            qc.invalidateQueries({ queryKey: ["stats"] });
        },
    });
}

export function useDeletePost() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (id: number) => api.deletePost(id),
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["posts"] });
            qc.invalidateQueries({ queryKey: ["stats"] });
        },
    });
}

export function useGeneratePost() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (data: { topic: string; post_type?: string; tone?: string; generate_hashtags?: boolean }) =>
            api.generateFromTopic(data),
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["posts"] });
            qc.invalidateQueries({ queryKey: ["stats"] });
        },
    });
}

export function useGenerateIdeas() {
    return useMutation({
        mutationFn: (data: { theme: string; count?: number }) => api.generateIdeas(data),
    });
}

export function useReviewPost() {
    return useMutation({
        mutationFn: (content: string) => api.reviewPost(content),
    });
}
