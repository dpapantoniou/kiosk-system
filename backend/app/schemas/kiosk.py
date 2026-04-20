from pydantic import BaseModel, Field


class KioskBase(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=200)
    location: str = Field(min_length=1, max_length=200)
    is_active: bool = True


class KioskCreate(KioskBase):
    pass


class KioskRead(KioskBase):
    id: int

    model_config = {"from_attributes": True}
