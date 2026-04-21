from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Questionnaire(Base):
    __tablename__ = "questionnaires"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    questions: Mapped[list["Question"]] = relationship(
        back_populates="questionnaire",
        cascade="all, delete-orphan",
        order_by="Question.order_no",
    )


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    questionnaire_id: Mapped[int] = mapped_column(ForeignKey("questionnaires.id"))
    code: Mapped[str] = mapped_column(String(50))
    order_no: Mapped[int] = mapped_column(Integer)
    question_type: Mapped[str] = mapped_column(String(50))
    text_i18n: Mapped[dict] = mapped_column(JSON)
    options_i18n: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False)
    branching_rule: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    questionnaire: Mapped["Questionnaire"] = relationship(back_populates="questions")
