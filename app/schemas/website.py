from datetime import datetime
from pydantic import BaseModel, HttpUrl

class WebsiteCreate(BaseModel):
    name: str
    url: HttpUrl
    check_interval: int = 60

class WebsiteUpdate(BaseModel):
    name: str | None = None
    url: str | None = None

class WebsiteOut(BaseModel):
    id: int
    name: str
    url: str
    check_interval: int
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class StatusLogOut(BaseModel):
    id: int
    website_id: int
    checked_at: datetime
    status_code: int | None
    response_time_ms: float | None
    is_up: bool
    error_message: str | None

    model_config = {"from_attributes": True}

class WebsiteStatus(BaseModel):
    website: WebsiteOut
    latest_log: StatusLogOut | None
    uptime_percent_24h: float | None
