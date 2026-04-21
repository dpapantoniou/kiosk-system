from pydantic import BaseModel
from datetime import datetime


class ResponseCreate(BaseModel):
    questionnaire_id: int
    kiosk_code: str
    answers: dict


class ResponseRead(ResponseCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
