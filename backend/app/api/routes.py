from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from fastapi import Request
from app.db.deps import get_db
from app.models.kiosk import Kiosk
from app.models.questionnaire import Questionnaire

from typing import List  
from app.models.response import Response
from app.schemas.response import ResponseCreate, ResponseRead

from app.db.deps import get_db
from app.db.base import Base
from app.db.session import engine
from app.models.kiosk import Kiosk
from app.models.questionnaire import Questionnaire, Question
from app.schemas.kiosk import KioskCreate, KioskRead
from app.schemas.questionnaire import QuestionnaireCreate, QuestionnaireRead
from pydantic import BaseModel

import csv
import io
import secrets
from fastapi import Response as FastAPIResponse
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.models.admin_user import AdminUser, AdminSession
from app.security import verify_password

class KioskUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    is_active: bool | None = None
    questionnaire_id: int | None = None
    
class LoginPayload(BaseModel):
    username: str
    password: str
def require_admin(request: Request, db: Session = Depends(get_db)):
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
def logout(request: Request, response: FastAPIResponse, db: Session = Depends(get_db), user: AdminUser = Depends(require_admin)):
    token = request.cookies.get("pt_cxfp_session")

    if token:
        session = db.scalar(select(AdminSession).where(AdminSession.token == token))
        if session:
            db.delete(session)
            db.commit()

    response.delete_cookie("pt_cxfp_session", path="/")
    return {"status": "ok"}

@router.get("/auth/me")
def me(user: AdminUser = Depends(require_admin)):
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
def list_responses(db: Session = Depends(get_db), user: AdminUser = Depends(require_admin)):
    return db.query(Response).all()

@router.get("/kiosks", response_model=list[KioskRead])
def list_kiosks(
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_admin)
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
def list_questionnaires(db: Session = Depends(get_db), user: AdminUser = Depends(require_admin)):
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

@router.post("/responses", response_model=ResponseRead)
def submit_response(
    payload: ResponseCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    client_ip = request.client.host
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
    return response

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

@router.get("/responses/export.csv")
def export_responses_csv(
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_admin),
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
