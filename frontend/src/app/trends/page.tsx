import Link from "next/link";
import { Flame, Clock } from "lucide-react";

export default function TrendsPage() {
    return (
        <div className="max-w-5xl animate-fadeIn">
            <div className="mb-6">
                <h1 className="text-xl font-bold text-text">Trending Topics</h1>
                <p className="text-sm text-muted">
                    Discover what&apos;s hot and generate posts from trending topics
                </p>
            </div>

            <div className="card p-12 text-center">
                <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-orange-50 mb-4">
                    <Flame className="h-8 w-8 text-orange-400" />
                </div>
                <h2 className="text-lg font-semibold text-text mb-2">Coming in Phase 2</h2>
                <p className="text-sm text-muted max-w-md mx-auto mb-1">
                    Trend discovery from Hacker News, Reddit, and RSS feeds is coming soon.
                </p>
                <div className="flex items-center justify-center gap-1 text-xs text-muted mt-3">
                    <Clock className="h-3 w-3" />
                    <span>Auto-fetches every 6 hours with LLM-powered relevance scoring</span>
                </div>
                <Link href="/generate" className="btn btn-primary mt-6">
                    Generate from Custom Topic →
                </Link>
            </div>
        </div>
    );
}
