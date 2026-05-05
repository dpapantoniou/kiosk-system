from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.models.kiosk_monitoring import KioskStatus

DEFAULT_HEARTBEAT_CONFIG = {
    "heartbeat_interval_minutes": 30,
    "online_threshold_minutes": 45,
    "stale_threshold_minutes": 90,
    "offline_threshold_minutes": 90,
}


def _config_path() -> Path:
    # backend/app/services -> backend/config/heartbeat_config.json
    return Path(__file__).resolve().parents[2] / "config" / "heartbeat_config.json"


def load_heartbeat_config() -> dict[str, int]:
    config = dict(DEFAULT_HEARTBEAT_CONFIG)
    path = _config_path()

    try:
        if path.exists():
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                for key in config:
                    value = loaded.get(key)
                    if isinstance(value, int) and value > 0:
                        config[key] = value
    except Exception:
        # Keep safe defaults if the file is missing or malformed.
        pass

    # Keep thresholds internally consistent even if edited manually.
    if config["online_threshold_minutes"] > config["stale_threshold_minutes"]:
        config["stale_threshold_minutes"] = config["online_threshold_minutes"]
    if config["offline_threshold_minutes"] < config["stale_threshold_minutes"]:
        config["offline_threshold_minutes"] = config["stale_threshold_minutes"]

    return config


def get_or_create_kiosk_status(db: Session, kiosk_code: str) -> KioskStatus:
    status = (
        db.query(KioskStatus)
        .filter(KioskStatus.kiosk_code == kiosk_code)
        .first()
    )
    if status:
        return status

    status = KioskStatus(kiosk_code=kiosk_code)
    db.add(status)
    db.flush()
    return status


def record_kiosk_activity(
    db: Session,
    *,
    kiosk_code: str,
    activity_type: str,
    client_ip: str | None = None,
    app_version: str | None = None,
    device_name: str | None = None,
    device_info: dict[str, Any] | None = None,
) -> KioskStatus:
    now = datetime.utcnow()
    status = get_or_create_kiosk_status(db, kiosk_code)

    status.last_seen = now
    status.client_ip = client_ip

    if activity_type == "heartbeat":
        status.last_heartbeat = now
        if app_version is not None:
            status.app_version = app_version
        if device_name is not None:
            status.device_name = device_name
        if device_info is not None:
            status.device_info_json = json.dumps(device_info, ensure_ascii=False)

    elif activity_type == "submission":
        status.last_submission = now

    db.add(status)
    return status


def evaluate_status(last_seen: datetime | None, config: dict[str, int]) -> tuple[str, float | None]:
    if not last_seen:
        return "never_seen", None

    minutes = (datetime.utcnow() - last_seen).total_seconds() / 60

    if minutes <= config["online_threshold_minutes"]:
        return "online", round(minutes, 1)
    if minutes <= config["stale_threshold_minutes"]:
        return "stale", round(minutes, 1)
    return "offline", round(minutes, 1)
