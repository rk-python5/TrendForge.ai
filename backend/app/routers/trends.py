"""
Trends router — /api/trends/*
"""

from fastapi import APIRouter, Query
from typing import Optional
from app.services.trend_service import trend_service

router = APIRouter()


@router.get("/trends/latest")
async def get_latest_trends(
    source: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = Query(default=25, le=50),
    offset: int = Query(default=0, ge=0),
):
    """Get latest trending topics from database."""
    return await trend_service.get_trends_from_db(
        source=source, category=category, limit=limit, offset=offset
    )


@router.get("/trends/{trend_id}")
async def get_trend(trend_id: int):
    """Get a single trend by ID."""
    from app.supabase_client import supabase
    from fastapi import HTTPException

    result = supabase.table("trending_topics").select("*").eq("id", trend_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Trend not found")
    return result.data


@router.post("/trends/fetch")
async def fetch_trends():
    """Manually trigger trend fetching from all sources."""
    trends = await trend_service.fetch_all_trends(use_cache=False)
    return {"fetched": len(trends), "message": "Trends fetched and scored successfully"}
