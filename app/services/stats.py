from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Integer
from app.models.website import StatusLog

async def uptime_percent(db: AsyncSession, website_id: int, hours: int = 24) -> float | None:
    since = datetime.utcnow() - timedelta(hours=hours)
    result = await db.execute(
        select(
            func.count(StatusLog.id).label("total"),
            func.sum(StatusLog.is_up.cast(Integer)).label("up_count"),
        ).where(StatusLog.website_id == website_id, StatusLog.checked_at >= since)
    )
    row = result.first()
    if not row or not row.total:
        return None
    return round((row.up_count / row.total) * 100, 2)
