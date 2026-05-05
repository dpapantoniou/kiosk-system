from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AntiAbuseSettings(Base):
    __tablename__ = "anti_abuse_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    cooldown_seconds: Mapped[int] = mapped_column(Integer, default=45, nullable=False)
    repeat_threshold: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    repeat_window_seconds: Mapped[int] = mapped_column(Integer, default=120, nullable=False)
    identical_pattern_threshold: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    hard_block_on_cooldown: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class KioskCooldown(Base):
    __tablename__ = "kiosk_cooldowns"

    kiosk_code: Mapped[str] = mapped_column(String(50), primary_key=True)
    cooldown_until: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AntiAbuseEvent(Base):
    __tablename__ = "anti_abuse_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    kiosk_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="info", nullable=False)
    client_ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
