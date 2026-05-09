from sqlalchemy import (
    Boolean,
    ForeignKey,
    String,
    LargeBinary
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.db.base import Base
class Kiosk(Base):

    __tablename__ = "kiosks"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(200)
    )

    location: Mapped[str] = mapped_column(
        String(200)
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )
    
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    logo_blob: Mapped[bytes | None] = mapped_column(
        LargeBinary,
        nullable=True
    )

    logo_mime: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    questionnaire_id: Mapped[int | None] = mapped_column(
        ForeignKey("questionnaires.id"),
        nullable=True
    )