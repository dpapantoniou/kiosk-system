from pydantic import BaseModel, Field


class KioskBase(BaseModel):

    code: str = Field(
        min_length=1,
        max_length=50
    )

    name: str = Field(
        min_length=1,
        max_length=200
    )

    location: str = Field(
        min_length=1,
        max_length=200
    )

    is_active: bool = True


class KioskCreate(KioskBase):

    questionnaire_id: int | None = None

    logo_data: str | None = None

    logo_mime: str | None = None


class KioskRead(KioskBase):

    id: int

    questionnaire_id: int | None = None

    logo_data: str | None = None

    logo_mime: str | None = None

    model_config = {
        "from_attributes": True
    }