from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from fastapi import Request
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
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

Base.metadata.create_all(bind=engine)

router = APIRouter()


@router.get("/responses", response_model=List[ResponseRead])
def list_responses(db: Session = Depends(get_db)):
    return db.query(Response).all()

@router.get("/kiosks", response_model=list[KioskRead])
def list_kiosks(db: Session = Depends(get_db)):
    return db.scalars(select(Kiosk).order_by(Kiosk.id)).all()


@router.post("/kiosks", response_model=KioskRead, status_code=status.HTTP_201_CREATED)
def create_kiosk(payload: KioskCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(Kiosk).where(Kiosk.code == payload.code))
    if existing:
        raise HTTPException(status_code=400, detail="Kiosk code already exists")

    kiosk = Kiosk(**payload.model_dump())
    db.add(kiosk)
    db.commit()
    db.refresh(kiosk)
    return kiosk


@router.get("/questionnaires", response_model=list[QuestionnaireRead])
def list_questionnaires(db: Session = Depends(get_db)):
    stmt = (
        select(Questionnaire)
        .options(selectinload(Questionnaire.questions))
        .order_by(Questionnaire.id)
    )
    return db.scalars(stmt).all()


@router.post("/questionnaires", response_model=QuestionnaireRead, status_code=status.HTTP_201_CREATED)
def create_questionnaire(payload: QuestionnaireCreate, db: Session = Depends(get_db)):
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
