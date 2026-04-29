from datetime import datetime
from sqlalchemy import String, Boolean, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Website(Base):
    __tablename__ = "websites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False, unique=True)
    check_interval: Mapped[int] = mapped_column(Integer, default=60)  # seconds
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    logs: Mapped[list["StatusLog"]] = relationship(
        "StatusLog", back_populates="website", cascade="all, delete-orphan"
    )

class StatusLog(Base):
    __tablename__ = "status_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    website_id: Mapped[int] = mapped_column(ForeignKey("websites.id"), nullable=False)
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_up: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    website: Mapped["Website"] = relationship("Website", back_populates="logs")
