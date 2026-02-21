"""
Posts router — CRUD and stats.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.supabase_client import supabase

router = APIRouter()


# --- Schemas ---

class PostCreate(BaseModel):
    topic: str
    content: str
    post_type: str = "insight"
    tone: str = "professional"
    hashtags: Optional[str] = None


class PostUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None
    hashtags: Optional[str] = None
    post_type: Optional[str] = None
    tone: Optional[str] = None


# --- Endpoints ---

@router.get("/posts")
async def list_posts(
    status: Optional[str] = None,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
):
    """List posts, optionally filtered by status."""
    query = supabase.table("posts").select("*").order("created_at", desc=True)
    if status:
        query = query.eq("status", status)
    query = query.range(offset, offset + limit - 1)
    result = query.execute()
    return {"posts": result.data, "count": len(result.data)}


@router.get("/posts/{post_id}")
async def get_post(post_id: int):
    """Get a single post by ID."""
    result = supabase.table("posts").select("*").eq("id", post_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Post not found")
    return result.data


@router.post("/posts", status_code=201)
async def create_post(body: PostCreate):
    """Create a post manually."""
    word_count = len(body.content.split())
    result = supabase.table("posts").insert({
        "topic": body.topic,
        "content": body.content,
        "post_type": body.post_type,
        "tone": body.tone,
        "hashtags": body.hashtags,
        "word_count": word_count,
        "estimated_read_time": int(word_count * 0.5),
        "status": "draft",
    }).execute()
    return result.data[0]


@router.patch("/posts/{post_id}")
async def update_post(post_id: int, body: PostUpdate):
    """Update a post's content, status, etc."""
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Recalculate metrics if content changed
    if "content" in updates:
        wc = len(updates["content"].split())
        updates["word_count"] = wc
        updates["estimated_read_time"] = int(wc * 0.5)

    # Auto-set timestamps based on status
    if updates.get("status") == "approved":
        updates["approved_at"] = "now()"
    elif updates.get("status") == "published":
        updates["published_at"] = "now()"

    result = (
        supabase.table("posts")
        .update(updates)
        .eq("id", post_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Post not found")
    return result.data[0]


@router.delete("/posts/{post_id}", status_code=204)
async def delete_post(post_id: int):
    """Delete a post."""
    supabase.table("posts").delete().eq("id", post_id).execute()
    return None


@router.get("/stats")
async def get_stats():
    """Get dashboard statistics."""
    all_posts = supabase.table("posts").select("status").execute()
    posts = all_posts.data or []

    total = len(posts)
    by_status = {}
    for p in posts:
        s = p["status"]
        by_status[s] = by_status.get(s, 0) + 1

    return {
        "total_posts": total,
        "drafts": by_status.get("draft", 0),
        "approved": by_status.get("approved", 0),
        "published": by_status.get("published", 0),
        "rejected": by_status.get("rejected", 0),
        "scheduled": by_status.get("scheduled", 0),
    }
