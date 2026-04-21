from sqlalchemy import ForeignKey, Integer, JSON, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base


class Response(Base):
    __tablename__ = "responses"

    id: Mapped[int] = mapped_column(primary_key=True)
    questionnaire_id: Mapped[int] = mapped_column(ForeignKey("questionnaires.id"))
    kiosk_code: Mapped[str] = mapped_column(String(50))

    answers: Mapped[dict] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # anti-gaming (MVP)
    client_ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
