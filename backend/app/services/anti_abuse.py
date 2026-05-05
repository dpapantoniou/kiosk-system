from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.anti_abuse import AntiAbuseEvent, AntiAbuseSettings, KioskCooldown
from app.models.response import Response


def get_or_create_settings(db: Session) -> AntiAbuseSettings:
    settings = db.query(AntiAbuseSettings).order_by(AntiAbuseSettings.id.asc()).first()
    if settings:
        return settings

    settings = AntiAbuseSettings()
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def log_event(
    db: Session,
    *,
    kiosk_code: str | None,
    event_type: str,
    severity: str = "info",
    client_ip: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AntiAbuseEvent:
    event = AntiAbuseEvent(
        kiosk_code=kiosk_code,
        event_type=event_type,
        severity=severity,
        client_ip=client_ip,
        metadata_json=metadata or {},
    )
    db.add(event)
    return event


def get_remaining_cooldown_seconds(db: Session, kiosk_code: str, now: datetime | None = None) -> int:
    now = now or datetime.utcnow()
    row = db.get(KioskCooldown, kiosk_code)
    if not row or row.cooldown_until <= now:
        return 0
    return max(0, int((row.cooldown_until - now).total_seconds()))


def enforce_before_submission(
    db: Session,
    *,
    kiosk_code: str,
    client_ip: str | None,
) -> tuple[AntiAbuseSettings, int]:
    settings = get_or_create_settings(db)
    if not settings.enabled:
        return settings, 0

    remaining = get_remaining_cooldown_seconds(db, kiosk_code)
    if remaining > 0:
        log_event(
            db,
            kiosk_code=kiosk_code,
            event_type="cooldown_violation_attempt",
            severity="warning",
            client_ip=client_ip,
            metadata={
                "remaining_seconds": remaining,
                "hard_block": settings.hard_block_on_cooldown,
            },
        )
        db.commit()

        if settings.hard_block_on_cooldown:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "status": "cooldown_active",
                    "remaining_seconds": remaining,
                },
            )

    return settings, remaining


def evaluate_after_submission(
    db: Session,
    *,
    response: Response,
    settings: AntiAbuseSettings,
    client_ip: str | None,
) -> None:
    if not settings.enabled:
        return

    now = datetime.utcnow()

    cooldown_until = now + timedelta(seconds=settings.cooldown_seconds)
    cooldown = db.get(KioskCooldown, response.kiosk_code)
    if cooldown:
        cooldown.cooldown_until = cooldown_until
        cooldown.updated_at = now
    else:
        db.add(
            KioskCooldown(
                kiosk_code=response.kiosk_code,
                cooldown_until=cooldown_until,
                updated_at=now,
            )
        )

    log_event(
        db,
        kiosk_code=response.kiosk_code,
        event_type="cooldown_started",
        severity="info",
        client_ip=client_ip,
        metadata={
            "response_id": response.id,
            "cooldown_seconds": settings.cooldown_seconds,
            "cooldown_until": cooldown_until.isoformat(),
        },
    )

    window_start = now - timedelta(seconds=settings.repeat_window_seconds)
    recent_count = (
        db.query(Response)
        .filter(Response.kiosk_code == response.kiosk_code)
        .filter(Response.created_at >= window_start)
        .count()
    )

    if recent_count >= settings.repeat_threshold:
        log_event(
            db,
            kiosk_code=response.kiosk_code,
            event_type="rapid_repeat_detected",
            severity="warning",
            client_ip=client_ip,
            metadata={
                "response_id": response.id,
                "recent_count": recent_count,
                "window_seconds": settings.repeat_window_seconds,
                "threshold": settings.repeat_threshold,
            },
        )

    identical_count = (
        db.query(Response)
        .filter(Response.kiosk_code == response.kiosk_code)
        .filter(Response.questionnaire_id == response.questionnaire_id)
        .filter(Response.answers == response.answers)
        .filter(Response.created_at >= window_start)
        .count()
    )

    if identical_count >= settings.identical_pattern_threshold:
        log_event(
            db,
            kiosk_code=response.kiosk_code,
            event_type="identical_pattern_detected",
            severity="warning",
            client_ip=client_ip,
            metadata={
                "response_id": response.id,
                "identical_count": identical_count,
                "window_seconds": settings.repeat_window_seconds,
                "threshold": settings.identical_pattern_threshold,
            },
        )
