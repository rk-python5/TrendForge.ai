"use client";

import Link from "next/link";
import { Sparkles, FileText, TrendingUp, Clock, CheckCircle, FileEdit, XCircle, ArrowRight } from "lucide-react";
import { useStats, usePosts } from "@/hooks/use-posts";

function StatCard({ label, value, icon: Icon, color }: { label: string; value: number; icon: React.ComponentType<{ className?: string }>; color: string }) {
  return (
    <div className="card p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-muted">{label}</p>
          <p className="mt-1 text-2xl font-bold text-text">{value}</p>
        </div>
        <div className={`flex h-11 w-11 items-center justify-center rounded-xl ${color}`}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </div>
  );
}

function ActionCard({ href, icon: Icon, title, description, gradient }: { href: string; icon: React.ComponentType<{ className?: string }>; title: string; description: string; gradient: string }) {
  return (
    <Link
      href={href}
      className={`group relative overflow-hidden rounded-2xl p-6 text-white transition-all duration-200 hover:shadow-lg hover:scale-[1.02] ${gradient}`}
    >
      <div className="relative z-10">
        <Icon className="h-8 w-8 mb-3 opacity-90" />
        <h3 className="text-lg font-bold">{title}</h3>
        <p className="mt-1 text-sm opacity-80">{description}</p>
        <div className="mt-4 flex items-center gap-1 text-sm font-medium opacity-90 group-hover:opacity-100">
          Get started <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
        </div>
      </div>
      {/* Decorative circle */}
      <div className="absolute -right-6 -top-6 h-32 w-32 rounded-full bg-white/10" />
    </Link>
  );
}

function PostRow({ topic, status, created_at, word_count, id }: { topic: string; status: string; created_at: string; word_count: number | null; id: number }) {
  const statusStyles: Record<string, string> = {
    draft: "badge-primary",
    approved: "badge-success",
    published: "badge-success",
    rejected: "badge-danger",
    scheduled: "badge-warning",
  };
  return (
    <Link href={`/posts/${id}`} className="flex items-center gap-4 rounded-lg px-4 py-3 transition-colors hover:bg-border-light">
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-text">{topic}</p>
        <p className="text-xs text-muted">{word_count ?? 0} words • {new Date(created_at).toLocaleDateString()}</p>
      </div>
      <span className={`badge ${statusStyles[status] || "badge-muted"}`}>{status}</span>
    </Link>
  );
}

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useStats();
  const { data: postsData, isLoading: postsLoading } = usePosts();

  const greeting = (() => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 17) return "Good afternoon";
    return "Good evening";
  })();

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Greeting */}
      <div>
        <h1 className="text-2xl font-bold text-text">
          {greeting}, Rehaan 👋
        </h1>
        <p className="mt-1 text-muted">
          Here&apos;s an overview of your content engine.
        </p>
      </div>

      {/* Action Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <ActionCard
          href="/generate"
          icon={Sparkles}
          title="Generate Post"
          description="Create AI-powered LinkedIn content"
          gradient="bg-gradient-to-br from-indigo-500 to-purple-600"
        />
        <ActionCard
          href="/posts"
          icon={FileText}
          title="Post Library"
          description="Manage and review your content"
          gradient="bg-gradient-to-br from-emerald-500 to-teal-600"
        />
        <ActionCard
          href="/trends"
          icon={TrendingUp}
          title="Trending Topics"
          description="Discover what's hot in your industry"
          gradient="bg-gradient-to-br from-amber-500 to-orange-600"
        />
      </div>

      {/* Stats Grid */}
      <div>
        <h2 className="mb-4 text-lg font-semibold text-text">Content Overview</h2>
        {statsLoading ? (
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="skeleton h-24 rounded-xl" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <StatCard label="Total Posts" value={stats?.total_posts ?? 0} icon={FileText} color="bg-primary-light text-primary" />
            <StatCard label="Drafts" value={stats?.drafts ?? 0} icon={FileEdit} color="bg-warning-light text-warning" />
            <StatCard label="Approved" value={stats?.approved ?? 0} icon={CheckCircle} color="bg-success-light text-success" />
            <StatCard label="Published" value={stats?.published ?? 0} icon={Clock} color="bg-primary-light text-secondary" />
          </div>
        )}
      </div>

      {/* Recent Posts */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-text">Recent Posts</h2>
          <Link href="/posts" className="text-sm font-medium text-primary hover:text-primary-hover transition-colors">
            View all →
          </Link>
        </div>
        <div className="card divide-y divide-border">
          {postsLoading ? (
            <div className="space-y-2 p-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="skeleton h-14 rounded-lg" />
              ))}
            </div>
          ) : (postsData?.posts?.length ?? 0) === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-light mb-4">
                <Sparkles className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-base font-semibold text-text">No posts yet</h3>
              <p className="mt-1 text-sm text-muted">Generate your first AI-powered LinkedIn post!</p>
              <Link href="/generate" className="btn btn-primary btn-sm mt-4">
                <Sparkles className="h-4 w-4" /> Generate Post
              </Link>
            </div>
          ) : (
            postsData?.posts.slice(0, 5).map((post) => (
              <PostRow key={post.id} {...post} />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
