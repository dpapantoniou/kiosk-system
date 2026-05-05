from datetime import datetime
from pydantic import BaseModel, Field


class HeartbeatPayload(BaseModel):
    kiosk_code: str = Field(min_length=1, max_length=50)
    app_version: str | None = None
    device_name: str | None = None
    device_info: dict | None = None


class HeartbeatResponse(BaseModel):
    status: str
    kiosk_code: str
    heartbeat_interval_minutes: int
    received_at: datetime


class KioskStatusRead(BaseModel):
    kiosk_code: str
    name: str | None = None
    location: str | None = None
    is_active: bool | None = None
    last_seen: datetime | None = None
    last_heartbeat: datetime | None = None
    last_submission: datetime | None = None
    app_version: str | None = None
    device_name: str | None = None
    status: str
    minutes_since_seen: float | None = None


class HeartbeatConfigRead(BaseModel):
    heartbeat_interval_minutes: int
    online_threshold_minutes: int
    stale_threshold_minutes: int
    offline_threshold_minutes: int
