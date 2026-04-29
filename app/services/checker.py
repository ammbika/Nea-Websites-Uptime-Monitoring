import time
import httpx
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.website import Website, StatusLog
from app.core.config import settings

async def check_website(db: AsyncSession, website: Website) -> StatusLog:
    """Ping a website and persist the result."""
    is_up = False
    status_code = None
    response_time_ms = None
    error_message = None

    start = time.monotonic()
    try:
        headers = {
    "User-Agent": "Mozilla/5.0"
}
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS, headers=headers) as client:
            response = await client.get(str(website.url), follow_redirects=True)
        elapsed = (time.monotonic() - start) * 1000
        status_code = response.status_code
        print(f"Checked {website.url} - Status: {status_code}, Time: {elapsed:.2f}ms")
        response_time_ms = round(elapsed, 2)
        is_up = response.status_code < 500
    except httpx.TimeoutException:
        error_message = "Request timed out"
    except httpx.RequestError as e:
        error_message = str(e)

    log = StatusLog(
        website_id=website.id,
        checked_at=datetime.utcnow(),
        status_code=status_code,
        response_time_ms=response_time_ms,
        is_up=is_up,
        error_message=error_message,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


async def check_all_websites(db: AsyncSession) -> None:
    """Called by the scheduler to check every active website."""
    print("Starting scheduled check of all websites...")
    result = await db.execute(select(Website).where(Website.active == True))
    websites = result.scalars().all()
    for website in websites:
        await check_website(db, website)
