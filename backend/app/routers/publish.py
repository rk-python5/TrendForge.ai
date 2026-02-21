"""
Publish router — /api/publish/*
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.services.publisher_service import publisher_service

router = APIRouter()


class ScheduleRequest(BaseModel):
    post_id: int
    scheduled_for: str
    platform: str = "linkedin"


class PublishNowRequest(BaseModel):
    post_id: int


@router.post("/publish/schedule")
async def schedule_post(body: ScheduleRequest):
    """Schedule a post for future publication."""
    try:
        result = await publisher_service.schedule_post(
            post_id=body.post_id,
            scheduled_for=body.scheduled_for,
            platform=body.platform,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/publish/now")
async def publish_now(body: PublishNowRequest):
    """Publish a post immediately."""
    try:
        return await publisher_service.publish_now(body.post_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/publish/queue")
async def get_queue(
    status: Optional[str] = None,
    limit: int = Query(default=20, le=50),
    offset: int = Query(default=0, ge=0),
):
    """Get the publishing queue."""
    return await publisher_service.get_queue(status=status, limit=limit, offset=offset)


@router.delete("/publish/schedule/{queue_id}")
async def cancel_schedule(queue_id: int):
    """Cancel a scheduled post."""
    try:
        return await publisher_service.cancel_scheduled(queue_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/publish/calendar")
async def get_calendar(
    month: Optional[int] = None,
    year: Optional[int] = None,
):
    """Get calendar view of scheduled and published posts."""
    return await publisher_service.get_calendar(month=month, year=year)
