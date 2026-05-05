from datetime import datetime
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class KioskStatus(Base):
    __tablename__ = "kiosk_status"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    kiosk_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_heartbeat: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_submission: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    app_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    device_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    client_ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    device_info_json: Mapped[str | None] = mapped_column(Text, nullable=True)
