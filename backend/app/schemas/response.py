from pydantic import BaseModel
from datetime import datetime

class ResponseCreate(BaseModel):
    questionnaire_id: int
    kiosk_code: str
    answers: dict
    lang: str | None = None

class ResponseRead(ResponseCreate):
    id: int
    created_at: datetime
    client_ip: str | None = None

    model_config = {"from_attributes": True}
