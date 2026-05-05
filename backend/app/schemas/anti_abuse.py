from datetime import datetime
from pydantic import BaseModel, Field


class AntiAbuseSettingsRead(BaseModel):
    id: int
    enabled: bool
    cooldown_seconds: int
    repeat_threshold: int
    repeat_window_seconds: int
    identical_pattern_threshold: int
    hard_block_on_cooldown: bool
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class AntiAbuseSettingsUpdate(BaseModel):
    enabled: bool | None = None
    cooldown_seconds: int | None = Field(default=None, ge=0, le=3600)
    repeat_threshold: int | None = Field(default=None, ge=1, le=1000)
    repeat_window_seconds: int | None = Field(default=None, ge=1, le=86400)
    identical_pattern_threshold: int | None = Field(default=None, ge=1, le=1000)
    hard_block_on_cooldown: bool | None = None


class AntiAbuseEventRead(BaseModel):
    id: int
    created_at: datetime
    kiosk_code: str | None = None
    event_type: str
    severity: str
    client_ip: str | None = None
    metadata_json: dict | None = None

    model_config = {"from_attributes": True}
