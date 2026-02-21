"""
Analytics router — /api/analytics
"""

from fastapi import APIRouter
from app.supabase_client import supabase

router = APIRouter()


@router.get("/analytics")
async def get_analytics():
    """Get analytics data for the dashboard."""

    # Posts by status
    posts = supabase.table("posts").select("id, status, post_type, tone, created_at, word_count").execute()
    all_posts = posts.data or []

    status_counts = {}
    type_counts = {}
    tone_counts = {}
    total_words = 0
    posts_by_month: dict[str, int] = {}

    for p in all_posts:
        # Status breakdown
        s = p.get("status", "draft")
        status_counts[s] = status_counts.get(s, 0) + 1

        # Post type breakdown
        pt = p.get("post_type", "unknown")
        type_counts[pt] = type_counts.get(pt, 0) + 1

        # Tone breakdown
        t = p.get("tone", "unknown")
        tone_counts[t] = tone_counts.get(t, 0) + 1

        # Word count
        total_words += p.get("word_count") or 0

        # Posts per month
        created = p.get("created_at", "")[:7]  # "YYYY-MM"
        if created:
            posts_by_month[created] = posts_by_month.get(created, 0) + 1

    # Trends count
    trends = supabase.table("trending_topics").select("id", count="exact").execute()
    trends_count = trends.count or 0

    # Queue count
    queue = supabase.table("publishing_queue").select("id, status").execute()
    queue_data = queue.data or []
    queue_pending = sum(1 for q in queue_data if q.get("status") == "pending")

    # Convert dicts to chart-friendly arrays
    status_chart = [{"name": k, "value": v} for k, v in status_counts.items()]
    type_chart = [{"name": k, "value": v} for k, v in type_counts.items()]
    tone_chart = [{"name": k, "value": v} for k, v in tone_counts.items()]
    monthly_chart = sorted(
        [{"month": k, "posts": v} for k, v in posts_by_month.items()],
        key=lambda x: x["month"],
    )

    return {
        "total_posts": len(all_posts),
        "total_words": total_words,
        "avg_word_count": round(total_words / max(len(all_posts), 1)),
        "trends_discovered": trends_count,
        "queue_pending": queue_pending,
        "status_chart": status_chart,
        "type_chart": type_chart,
        "tone_chart": tone_chart,
        "monthly_chart": monthly_chart,
    }
