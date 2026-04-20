from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.db.base import Base
from app.db.session import engine
from app.models.kiosk import Kiosk
from app.schemas.kiosk import KioskCreate, KioskRead

Base.metadata.create_all(bind=engine)

router = APIRouter()


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
