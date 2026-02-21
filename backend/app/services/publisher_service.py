"""
Publisher Service — scheduling, queue management, LinkedIn publishing.
"""

import json
from datetime import datetime, timezone
from typing import Optional
from app.supabase_client import supabase
from app.config import settings


class PublisherService:
    """Manages post scheduling, queue, and publishing."""

    # ── Queue Management ─────────────────────────────────

    async def schedule_post(
        self,
        post_id: int,
        scheduled_for: str,
        platform: str = "linkedin",
    ) -> dict:
        """Schedule a post for future publication."""
        # Validate the post exists
        post = supabase.table("posts").select("id, status").eq("id", post_id).single().execute()
        if not post.data:
            raise ValueError(f"Post {post_id} not found")

        # Insert into publishing queue
        result = supabase.table("publishing_queue").insert({
            "post_id": post_id,
            "scheduled_for": scheduled_for,
            "platform": platform,
            "status": "pending",
        }).execute()

        # Update post status
        supabase.table("posts").update({
            "status": "scheduled",
            "scheduled_for": scheduled_for,
        }).eq("id", post_id).execute()

        return result.data[0] if result.data else {}

    async def get_queue(
        self,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        """Get scheduled posts queue."""
        query = (
            supabase.table("publishing_queue")
            .select("*, posts(id, topic, content, post_type, hashtags)")
            .order("scheduled_for", desc=False)
        )
        if status:
            query = query.eq("status", status)
        query = query.range(offset, offset + limit - 1)
        result = query.execute()
        return {"queue": result.data, "count": len(result.data)}

    async def cancel_scheduled(self, queue_id: int) -> dict:
        """Cancel a scheduled post."""
        # Get the queue item to find the post_id
        item = supabase.table("publishing_queue").select("post_id").eq("id", queue_id).single().execute()
        if not item.data:
            raise ValueError("Queue item not found")

        # Update queue status
        supabase.table("publishing_queue").update({"status": "cancelled"}).eq("id", queue_id).execute()

        # Revert post status to approved
        supabase.table("posts").update({
            "status": "approved",
            "scheduled_for": None,
        }).eq("id", item.data["post_id"]).execute()

        return {"message": "Schedule cancelled", "queue_id": queue_id}

    async def publish_now(self, post_id: int) -> dict:
        """Mark a post as published immediately.
        In a full implementation, this would call the LinkedIn API."""

        post = supabase.table("posts").select("*").eq("id", post_id).single().execute()
        if not post.data:
            raise ValueError("Post not found")

        # For now, just mark as published (LinkedIn OAuth would go here)
        supabase.table("posts").update({
            "status": "published",
            "published_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", post_id).execute()

        return {
            "message": "Post marked as published",
            "post_id": post_id,
            "note": "LinkedIn OAuth integration required for actual publishing.",
        }

    async def get_calendar(self, month: Optional[int] = None, year: Optional[int] = None) -> dict:
        """Get posts organized by date for calendar view."""
        now = datetime.now(timezone.utc)
        m = month or now.month
        y = year or now.year

        # Get scheduled posts for the month
        start = f"{y}-{m:02d}-01T00:00:00Z"
        if m == 12:
            end = f"{y+1}-01-01T00:00:00Z"
        else:
            end = f"{y}-{m+1:02d}-01T00:00:00Z"

        scheduled = (
            supabase.table("publishing_queue")
            .select("*, posts(id, topic, content, post_type, status)")
            .gte("scheduled_for", start)
            .lt("scheduled_for", end)
            .order("scheduled_for", desc=False)
            .execute()
        )

        published = (
            supabase.table("posts")
            .select("id, topic, status, published_at")
            .eq("status", "published")
            .not_.is_("published_at", "null")
            .gte("published_at", start)
            .lt("published_at", end)
            .execute()
        )

        return {
            "month": m,
            "year": y,
            "scheduled": scheduled.data,
            "published": published.data,
        }


publisher_service = PublisherService()
