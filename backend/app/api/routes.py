import csv
import io
import secrets
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, Response as FastAPIResponse, status
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.styles import Font
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.base import Base
from app.db.deps import get_db
from app.db.session import engine
from app.models.admin_user import AdminSession, AdminUser
from app.models.anti_abuse import AntiAbuseEvent
from app.models.kiosk import Kiosk
from app.models.kiosk_monitoring import KioskStatus
from app.models.questionnaire import Question, Questionnaire
from app.models.response import Response
from app.schemas.anti_abuse import (
    AntiAbuseEventRead,
    AntiAbuseSettingsRead,
    AntiAbuseSettingsUpdate,
)
from app.schemas.kiosk import KioskCreate, KioskRead
from app.schemas.kiosk_monitoring import (
    HeartbeatConfigRead,
    HeartbeatPayload,
    HeartbeatResponse,
    KioskStatusRead,
)
from app.schemas.questionnaire import QuestionnaireCreate, QuestionnaireRead
from app.schemas.response import ResponseCreate, ResponseRead
from app.security import verify_password
from app.services.anti_abuse import (
    enforce_before_submission,
    evaluate_after_submission,
    get_or_create_settings,
)
from app.services.kiosk_monitoring import (
    evaluate_status,
    load_heartbeat_config,
    record_kiosk_activity,
)


class BulkAssignRequest(BaseModel):
    questionnaire_id: int
    kiosk_ids: list[int]

class KioskUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    is_active: bool | None = None
    questionnaire_id: int | None = None

class QuestionnaireUpdate(BaseModel):
    code: str
    name: str
    is_active: bool
    questions: list
    
class LoginPayload(BaseModel):
    username: str
    password: str
def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("pt_cxfp_session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session = db.query(AdminSession).filter(
       AdminSession.token == token
    ).first()
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    user = db.get(AdminUser, session.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")

    return user
def require_admin(
    user: AdminUser = Depends(get_current_user)
):

    if user.role not in [
        "pt_admin",
        "eu_admin"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )

    return user
def require_manager_or_admin(
    user: AdminUser = Depends(get_current_user)
):

    if user.role not in [
        "pt_admin",
        "eu_admin",
        "eu_manager"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )

    return user

Base.metadata.create_all(bind=engine)

router = APIRouter()

@router.post("/auth/login")
def login(payload: LoginPayload, response: FastAPIResponse, db: Session = Depends(get_db)):

    user = db.query(AdminUser).filter(
        AdminUser.username == payload.username
    ).first()


    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    ok = verify_password(payload.password, user.password_hash)

    if not ok:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User inactive")

    token = secrets.token_urlsafe(32)

    session = AdminSession(token=token, user_id=user.id)
    db.add(session)
    db.commit()

    response.set_cookie(
        key="pt_cxfp_session",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )


    return {
        "username": user.username,
        "role": user.role,
    }
@router.post("/auth/logout")
def logout(request: Request, response: FastAPIResponse, db: Session = Depends(get_db), user: AdminUser = Depends(require_manager_or_admin)):
    token = request.cookies.get("pt_cxfp_session")

    if token:
        session = db.scalar(select(AdminSession).where(AdminSession.token == token))
        if session:
            db.delete(session)
            db.commit()

    response.delete_cookie("pt_cxfp_session", path="/")
    return {"status": "ok"}

@router.get("/auth/me")
def me(user: AdminUser = Depends(require_manager_or_admin)):
    return {
        "username": user.username,
        "role": user.role,
    }

@router.put("/kiosks/{kiosk_id}", response_model=KioskRead)
def update_kiosk(kiosk_id: int, payload: KioskUpdate, db: Session = Depends(get_db), user: AdminUser = Depends(require_admin)):
    kiosk = db.get(Kiosk, kiosk_id)
    if not kiosk:
        raise HTTPException(status_code=404, detail="Kiosk not found")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(kiosk, key, value)

    db.add(kiosk)
    db.commit()
    db.refresh(kiosk)
    return kiosk

@router.get("/responses", response_model=List[ResponseRead])
def list_responses(db: Session = Depends(get_db), user: AdminUser = Depends(require_manager_or_admin)):
    return db.query(Response).all()


@router.get("/anti-abuse/settings", response_model=AntiAbuseSettingsRead)
def read_anti_abuse_settings(
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_manager_or_admin),
):
    return get_or_create_settings(db)


@router.put("/anti-abuse/settings", response_model=AntiAbuseSettingsRead)
def update_anti_abuse_settings(
    payload: AntiAbuseSettingsUpdate,
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_admin),
):
    settings = get_or_create_settings(db)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(settings, key, value)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


@router.get("/anti-abuse/events", response_model=list[AntiAbuseEventRead])
def list_anti_abuse_events(
    limit: int = 100,
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_manager_or_admin),
):
    safe_limit = max(1, min(limit, 500))
    return (
        db.query(AntiAbuseEvent)
        .order_by(AntiAbuseEvent.created_at.desc())
        .limit(safe_limit)
        .all()
    )


@router.get("/monitoring/config", response_model=HeartbeatConfigRead)
def read_monitoring_config():
    return load_heartbeat_config()


@router.post("/kiosks/heartbeat", response_model=HeartbeatResponse)
def receive_kiosk_heartbeat(
    payload: HeartbeatPayload,
    request: Request,
    db: Session = Depends(get_db),
):
    kiosk = db.query(Kiosk).filter(Kiosk.code == payload.kiosk_code).first()
    if not kiosk:
        raise HTTPException(status_code=404, detail="Kiosk not found")

    client_ip = request.client.host if request.client else None
    status_row = record_kiosk_activity(
        db,
        kiosk_code=payload.kiosk_code,
        activity_type="heartbeat",
        client_ip=client_ip,
        app_version=payload.app_version,
        device_name=payload.device_name,
        device_info=payload.device_info,
    )
    db.commit()
    db.refresh(status_row)

    config = load_heartbeat_config()
    return {
        "status": "ok",
        "kiosk_code": payload.kiosk_code,
        "heartbeat_interval_minutes": config["heartbeat_interval_minutes"],
        "received_at": status_row.last_heartbeat,
    }


@router.get("/kiosks/status", response_model=list[KioskStatusRead])
def list_kiosk_statuses(
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_manager_or_admin),
):
    config = load_heartbeat_config()
    kiosks = db.scalars(select(Kiosk).order_by(Kiosk.id)).all()
    statuses = {
        s.kiosk_code: s
        for s in db.query(KioskStatus).all()
    }

    result = []
    for kiosk in kiosks:
        status_row = statuses.get(kiosk.code)
        last_seen = status_row.last_seen if status_row else None
        state, minutes = evaluate_status(last_seen, config)
        result.append({
            "kiosk_code": kiosk.code,
            "name": kiosk.name,
            "location": kiosk.location,
            "is_active": kiosk.is_active,
            "last_seen": last_seen,
            "last_heartbeat": status_row.last_heartbeat if status_row else None,
            "last_submission": status_row.last_submission if status_row else None,
            "app_version": status_row.app_version if status_row else None,
            "device_name": status_row.device_name if status_row else None,
            "status": state,
            "minutes_since_seen": minutes,
        })
    return result

@router.get("/kiosks", response_model=list[KioskRead])
def list_kiosks(
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_manager_or_admin)
):
    return db.scalars(select(Kiosk).order_by(Kiosk.id)).all()

@router.post("/kiosks", response_model=KioskRead, status_code=status.HTTP_201_CREATED)
def create_kiosk(payload: KioskCreate, db: Session = Depends(get_db), user: AdminUser = Depends(require_admin)):
    existing = db.scalar(select(Kiosk).where(Kiosk.code == payload.code))
    if existing:
        raise HTTPException(status_code=400, detail="Kiosk code already exists")

    kiosk = Kiosk(**payload.model_dump())
    db.add(kiosk)
    db.commit()
    db.refresh(kiosk)
    return kiosk


@router.get("/questionnaires", response_model=list[QuestionnaireRead])
def list_questionnaires(db: Session = Depends(get_db), user: AdminUser = Depends(require_manager_or_admin)):
    stmt = (
        select(Questionnaire)
        .options(selectinload(Questionnaire.questions))
        .order_by(Questionnaire.id)
    )
    return db.scalars(stmt).all()


@router.post("/questionnaires", response_model=QuestionnaireRead, status_code=status.HTTP_201_CREATED)
def create_questionnaire(payload: QuestionnaireCreate, db: Session = Depends(get_db), user: AdminUser = Depends(require_admin)):
    existing = db.scalar(select(Questionnaire).where(Questionnaire.code == payload.code))
    if existing:
        raise HTTPException(status_code=400, detail="Questionnaire code already exists")

    questionnaire = Questionnaire(
        code=payload.code,
        name=payload.name,
        is_active=payload.is_active,
    )

    for q in payload.questions:
        questionnaire.questions.append(
            Question(
                code=q.code,
                order_no=q.order_no,
                question_type=q.question_type,
                text_i18n=q.text_i18n,
                options_i18n=q.options_i18n,
                is_required=q.is_required,
                branching_rule=q.branching_rule,
            )
        )

    db.add(questionnaire)
    db.commit()
    db.refresh(questionnaire)

    return db.scalar(
        select(Questionnaire)
        .options(selectinload(Questionnaire.questions))
        .where(Questionnaire.id == questionnaire.id)
    )
@router.put(
    "/questionnaires/{questionnaire_id}",
    response_model=QuestionnaireRead
)
def update_questionnaire(
    questionnaire_id: int,
    payload: QuestionnaireCreate,
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_admin)
):

    questionnaire = db.get(
        Questionnaire,
        questionnaire_id
    )

    if not questionnaire:
        raise HTTPException(
            status_code=404,
            detail="Questionnaire not found"
        )

    questionnaire.code = payload.code
    questionnaire.name = payload.name
    questionnaire.is_active = payload.is_active

    # remove old questions
    questionnaire.questions.clear()

    db.flush()

    # recreate questions
    for q in payload.questions:

        questionnaire.questions.append(
            Question(
                code=q.code,
                order_no=q.order_no,
                question_type=q.question_type,
                text_i18n=q.text_i18n,
                options_i18n=q.options_i18n,
                is_required=q.is_required,
                branching_rule=q.branching_rule,
            )
        )

    db.add(questionnaire)

    db.commit()

    db.refresh(questionnaire)

    return db.scalar(
        select(Questionnaire)
        .options(
            selectinload(
                Questionnaire.questions
            )
        )
        .where(
            Questionnaire.id
            == questionnaire.id
        )
    )



@router.post("/responses")
def submit_response(
    payload: ResponseCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    client_ip = request.client.host if request.client else None

    settings, _ = enforce_before_submission(
        db,
        kiosk_code=payload.kiosk_code,
        client_ip=client_ip,
    )

    response = Response(
        questionnaire_id=payload.questionnaire_id,
        kiosk_code=payload.kiosk_code,
        answers=payload.answers,
        client_ip=client_ip,
        lang=payload.lang,
    )
    db.add(response)
    db.commit()
    db.refresh(response)

    record_kiosk_activity(
        db,
        kiosk_code=payload.kiosk_code,
        activity_type="submission",
        client_ip=client_ip,
    )

    evaluate_after_submission(
        db,
        response=response,
        settings=settings,
        client_ip=client_ip,
    )
    db.commit()

    return {
        "status": "ok",
        "cooldown_seconds": (
            settings.cooldown_seconds
            if settings.enabled else 0
        ),
        "response": ResponseRead.model_validate(response).model_dump(mode="json"),
    }

from sqlalchemy import select
from sqlalchemy.orm import selectinload

@router.get("/kiosks/{code}/questionnaire")
def get_kiosk_questionnaire(code: str, db: Session = Depends(get_db)):
    kiosk = db.query(Kiosk).filter(Kiosk.code == code).first()
    if not kiosk:
        raise HTTPException(status_code=404, detail="Kiosk not found")
    if not kiosk.questionnaire_id:
        raise HTTPException(status_code=404, detail="No questionnaire assigned")
    questionnaire = db.scalar(
         select(Questionnaire)
         .options(selectinload(Questionnaire.questions))
         .where(Questionnaire.id == kiosk.questionnaire_id)
    )
    if not questionnaire:
        raise HTTPException(status_code=404, detail="Questionnaire not found")

    return {
       "id": questionnaire.id,
       "code": questionnaire.code,
       "name": questionnaire.name,
       "is_active": questionnaire.is_active,
       "questions": [
           {
            "id": q.id,
            "code": q.code,
            "order_no": q.order_no,
            "question_type": q.question_type,
            "text_i18n": q.text_i18n,
            "options_i18n": q.options_i18n,
            "is_required": q.is_required,
            "branching_rule": q.branching_rule,
            }
            for q in questionnaire.questions
        ]
     }
@router.get("/by-code/{code}")
def get_kiosk_by_code(
    code: str,
    db: Session = Depends(get_db)
):
    kiosk = (
        db.query(Kiosk)
        .filter(Kiosk.code == code)
        .first()
    )

    if not kiosk:
        raise HTTPException(
            status_code=404,
            detail="Kiosk not found"
        )

    questionnaire = None

    if kiosk.questionnaire_id:

        questionnaire = db.scalar(
            select(Questionnaire)
            .options(
                selectinload(
                    Questionnaire.questions
                )
            )
            .where(
                Questionnaire.id
                == kiosk.questionnaire_id
            )
        )

    return {
        "id": kiosk.id,
        "code": kiosk.code,
        "name": kiosk.name,
        "location": kiosk.location,
        "is_active": kiosk.is_active,

        "questionnaire": (
            {
                "id": questionnaire.id,
                "code": questionnaire.code,
                "name": questionnaire.name,
                "is_active": questionnaire.is_active,

                "questions": [
                    {
                        "id": q.id,
                        "code": q.code,
                        "order_no": q.order_no,
                        "question_type": q.question_type,
                        "text_i18n": q.text_i18n,
                        "options_i18n": q.options_i18n,
                        "is_required": q.is_required,
                        "branching_rule": q.branching_rule,
                    }
                    for q in questionnaire.questions
                ]
            }
            if questionnaire else None
        )
    }



@router.get("/responses/export.csv")
def export_responses_csv(
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_manager_or_admin),
):
    rows = db.query(Response).order_by(Response.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "id",
        "created_at",
        "kiosk_code",
        "questionnaire_id",
        "lang",
        "client_ip",
        "answers_json",
    ])

    for r in rows:
        writer.writerow([
            r.id,
            r.created_at,
            r.kiosk_code,
            r.questionnaire_id,
            getattr(r, "lang", ""),
            getattr(r, "client_ip", ""),
            r.answers,
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=responses.csv"
        },
    )
@router.get("/responses/export.xlsx")
def export_responses_xlsx(
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_manager_or_admin),
):
    rows = (
        db.query(Response)
        .order_by(Response.created_at.desc())
        .all()
    )
    wb = Workbook()
    ws = wb.active
    ws.title = "Responses"
    headers = [
        "id",
        "created_at",
        "kiosk_code",
        "questionnaire_id",
        "lang",
        "client_ip",
        "answers_json",
    ]
    ws.append(headers)
    # bold header row
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for r in rows:
        ws.append([
            r.id,
            str(r.created_at),
            r.kiosk_code,
            r.questionnaire_id,
            getattr(r, "lang", ""),
            getattr(r, "client_ip", ""),
            str(r.answers),
        ])
    # auto column widths
    for col in ws.columns:
        max_len = 0
        column = col[0].column_letter
        for cell in col:
            try:
                max_len = max(
                    max_len,
                    len(str(cell.value))
                )
            except:
                pass
        adjusted = min(max_len + 2, 60)
        ws.column_dimensions[column].width = adjusted
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=responses.xlsx"
        },
    )
    
@router.get("/analytics/summary")
def analytics_summary(
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_manager_or_admin),
):

    total_responses = (
        db.query(Response).count()
    )

    today = datetime.utcnow().date()

    responses_today = (
        db.query(Response)
        .filter(
            func.date(Response.created_at) == today
        )
        .count()
    )

    # rating averages
    rating_values = []

    rows = db.query(Response).all()

    for r in rows:

        if not r.answers:
            continue

        for v in r.answers.values():

            if isinstance(v, int):
                rating_values.append(v)

    avg_rating = (
        round(
            sum(rating_values) / len(rating_values),
            2
        )
        if rating_values else None
    )

    active_kiosks = (
        db.query(Kiosk)
        .filter(Kiosk.is_active == True)
        .count()
    )

    config = load_heartbeat_config()
    offline_kiosks = 0
    status_rows = {
        s.kiosk_code: s
        for s in db.query(KioskStatus).all()
    }
    for kiosk in db.query(Kiosk).filter(Kiosk.is_active == True).all():
        row = status_rows.get(kiosk.code)
        state, _ = evaluate_status(row.last_seen if row else None, config)
        if state in {"offline", "never_seen"}:
            offline_kiosks += 1

    return {
        "total_responses": total_responses,
        "responses_today": responses_today,
        "avg_rating": avg_rating,
        "active_kiosks": active_kiosks,
        "offline_kiosks": offline_kiosks,
    }
    

@router.post("/kiosks/bulk-assign-questionnaire")
def bulk_assign_questionnaire(
    payload: BulkAssignRequest,
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_admin),
):
    if not payload.kiosk_ids:
        raise HTTPException(
            status_code=400,
            detail="No kiosks selected",
        )

    questionnaire = (
        db.query(Questionnaire)
        .filter(Questionnaire.id == payload.questionnaire_id)
        .first()
    )

    if not questionnaire:
        raise HTTPException(status_code=404, detail="Questionnaire not found")

    kiosks = (
        db.query(Kiosk)
        .filter(Kiosk.id.in_(payload.kiosk_ids))
        .all()
    )

    found_ids = {kiosk.id for kiosk in kiosks}
    missing_ids = sorted(set(payload.kiosk_ids) - found_ids)

    if missing_ids:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "One or more kiosks were not found",
                "missing_kiosk_ids": missing_ids,
            },
        )

    updated = 0

    for kiosk in kiosks:
        kiosk.questionnaire_id = payload.questionnaire_id
        updated += 1

    db.commit()

    return {
        "status": "ok",
        "updated_kiosks": updated,
        "questionnaire_id": payload.questionnaire_id
    }