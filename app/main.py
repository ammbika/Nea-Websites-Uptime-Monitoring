import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.base import get_db, AsyncSessionLocal, init_db
from app.api.routes.websites import router as websites_router
from app.api.routes.logs import router as logs_router
from app.services.checker import check_all_websites, check_website
from app.models.website import Website, StatusLog
from app.services.stats import uptime_percent
from app.core.config import settings

scheduler = AsyncIOScheduler()


async def run_check_all():
    async with AsyncSessionLocal() as db:
        await check_all_websites(db)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    asyncio.create_task(run_check_all())

    scheduler.add_job(
        run_check_all,
        "interval",
        seconds=settings.CHECK_INTERVAL_SECONDS,
        id="check_all_websites",
    )
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title=settings.APP_TITLE, lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(websites_router)
app.include_router(logs_router)


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/partials/status-cards", response_class=HTMLResponse)
async def status_cards(request: Request, db: AsyncSession = Depends(get_db)):
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
        statuses.append({
            "website": w,
            "latest_log": log,
            "uptime_percent_24h": uptime,
        })
    return templates.TemplateResponse(
        "partials/status_cards.html",
        {"request": request, "statuses": statuses},
    )


@app.post("/sites/add")
async def add_site(
    name: str = Form(...),
    url: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    site = Website(name=name, url=url)
    db.add(site)
    await db.commit()
    await db.refresh(site)

    # Capture the id before the session closes, open a fresh one for the background task
    site_id = site.id

    async def check_new_site():
        async with AsyncSessionLocal() as new_db:
            fresh_site = await new_db.get(Website, site_id)
            if fresh_site:
                await check_website(new_db, fresh_site)

    asyncio.create_task(check_new_site())

    return RedirectResponse("/", status_code=303)