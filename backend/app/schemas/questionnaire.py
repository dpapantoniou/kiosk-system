from pydantic import BaseModel, Field

class QuestionRead(BaseModel):
    id: int
    code: str
    order_no: int
    question_type: str
    text_i18n: dict

    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    order_no: int
    question_type: str = Field(min_length=1, max_length=50)
    text_i18n: dict
    options_i18n: dict | None = None
    is_required: bool = False
    branching_rule: dict | None = None


class QuestionCreate(QuestionBase):
    pass


class QuestionRead(QuestionBase):
    id: int

    model_config = {"from_attributes": True}

class QuestionnaireRead(BaseModel):
    id: int
    code: str
    name: str
    is_active: bool
    questions: list[QuestionRead]

    class Config:
        from_attributes = True


class QuestionnaireBase(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=200)
    is_active: bool = True


class QuestionnaireCreate(QuestionnaireBase):
    questions: list[QuestionCreate] = []


class QuestionnaireRead(QuestionnaireBase):
    id: int
    questions: list[QuestionRead] = []

    model_config = {"from_attributes": True}
