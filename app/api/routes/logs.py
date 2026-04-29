from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.base import get_db
from app.models.website import StatusLog
from app.schemas.website import StatusLogOut

router = APIRouter(prefix="/api/logs", tags=["logs"])

@router.get("/", response_model=list[StatusLogOut])
async def get_logs(
    website_id: int | None = Query(None),
    from_dt: datetime | None = Query(None, description="ISO 8601 datetime"),
    to_dt: datetime | None = Query(None, description="ISO 8601 datetime"),
    is_up: bool | None = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    """Extract log data for analysis. Filter by site, date range, and status."""
    q = select(StatusLog).order_by(desc(StatusLog.checked_at))
    if website_id is not None:
        q = q.where(StatusLog.website_id == website_id)
    if from_dt:
        q = q.where(StatusLog.checked_at >= from_dt)
    if to_dt:
        q = q.where(StatusLog.checked_at <= to_dt)
    if is_up is not None:
        q = q.where(StatusLog.is_up == is_up)
    q = q.limit(limit).offset(offset)
    result = await db.execute(q)
    return result.scalars().all()
