"""
Generation router — AI content generation endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.content_service import content_service

router = APIRouter()


# --- Schemas ---

class GenerateFromTopicRequest(BaseModel):
    topic: str
    post_type: str = "insight"
    tone: str = "professional"
    generate_hashtags: bool = True


class GenerateFromTrendRequest(BaseModel):
    trend_id: int
    post_type: str = "insight"
    tone: str = "professional"


class GenerateIdeasRequest(BaseModel):
    theme: str
    count: int = 5


class ReviewRequest(BaseModel):
    content: str


class ImproveRequest(BaseModel):
    post_id: int
    feedback: str


# --- Endpoints ---

@router.post("/generate/from-topic")
async def generate_from_topic(body: GenerateFromTopicRequest):
    """Generate a LinkedIn post from a custom topic."""
    try:
        result = await content_service.generate_post(
            topic=body.topic,
            post_type=body.post_type,
            tone=body.tone,
            generate_hashtags=body.generate_hashtags,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/from-trend")
async def generate_from_trend(body: GenerateFromTrendRequest):
    """Generate a LinkedIn post from a trending topic."""
    from app.supabase_client import supabase

    # Fetch the trend
    trend_result = (
        supabase.table("trending_topics")
        .select("*")
        .eq("id", body.trend_id)
        .single()
        .execute()
    )
    if not trend_result.data:
        raise HTTPException(status_code=404, detail="Trend not found")

    trend = trend_result.data
    topic = f"{trend['title']}"
    if trend.get("summary"):
        topic += f" — {trend['summary']}"

    try:
        result = await content_service.generate_post(
            topic=topic,
            post_type=body.post_type,
            tone=body.tone,
            source_trend_id=body.trend_id,
        )
        # Mark trend as used
        supabase.table("trending_topics").update({"used": True}).eq("id", body.trend_id).execute()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/ideas")
async def generate_ideas(body: GenerateIdeasRequest):
    """Generate post topic ideas from a theme."""
    try:
        ideas = await content_service.generate_ideas(body.theme, body.count)
        return {"ideas": ideas, "theme": body.theme}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/review")
async def review_post(body: ReviewRequest):
    """Review post content for quality."""
    try:
        review = await content_service.review_post(body.content)
        return review
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/improve")
async def improve_post(body: ImproveRequest):
    """Improve an existing post based on feedback."""
    try:
        result = await content_service.improve_post(body.post_id, body.feedback)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class GenerateImageRequest(BaseModel):
    post_id: int


@router.post("/generate/image")
async def generate_image(body: GenerateImageRequest):
    """Generate an AI image for a post."""
    from app.services.image_service import image_service

    try:
        result = await image_service.generate_for_post(body.post_id)
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
