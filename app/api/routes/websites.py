from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.base import get_db
from app.models.website import Website, StatusLog
from app.schemas.website import WebsiteCreate, WebsiteOut, WebsiteStatus, WebsiteUpdate
from app.services.stats import uptime_percent

router = APIRouter(prefix="/api/websites", tags=["websites"])

@router.get("/", response_model=list[WebsiteOut])
async def list_websites(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Website))
    return result.scalars().all()

@router.post("/", response_model=WebsiteOut, status_code=201)
async def add_website(payload: WebsiteCreate, db: AsyncSession = Depends(get_db)):
    website = Website(name=payload.name, url=payload.url, check_interval=payload.check_interval)
    db.add(website)
    await db.commit()
    await db.refresh(website)
    return website

@router.patch("/{website_id}", response_model=WebsiteOut)
async def update_website(website_id: int, payload: WebsiteUpdate, db: AsyncSession = Depends(get_db)):
    website = await db.get(Website, website_id)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    if payload.name is not None:
        website.name = payload.name
    if payload.url is not None:
        website.url = str(payload.url)
    db.add(website)
    await db.commit()
    await db.refresh(website)
    return website

@router.delete("/{website_id}", status_code=204)
async def remove_website(website_id: int, db: AsyncSession = Depends(get_db)):
    website = await db.get(Website, website_id)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    await db.delete(website)
    await db.commit()

@router.get("/status", response_model=list[WebsiteStatus])
async def all_statuses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Website).where(Website.active == True))
    websites = result.scalars().all()
    statuses = []
    for w in websites:
        latest = await db.execute(
            select(StatusLog)
            .where(StatusLog.website_id == w.id)
            .order_by(desc(StatusLog.checked_at))
            .limit(1)
        )
        log = latest.scalar_one_or_none()
        uptime = await uptime_percent(db, w.id)
        statuses.append(WebsiteStatus(
            website=WebsiteOut.model_validate(w),
            latest_log=log,
            uptime_percent_24h=uptime,
        ))
    return statuses
