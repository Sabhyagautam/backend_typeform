from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


# ── Question ──────────────────────────────────────────────────────────────────

class QuestionBase(BaseModel):
    type: str
    title: str
    description: Optional[str] = None
    required: bool = False
    order_index: int = 0
    choices: Optional[List[str]] = None
    rating_steps: Optional[int] = 5


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    required: Optional[bool] = None
    order_index: Optional[int] = None
    choices: Optional[List[str]] = None
    rating_steps: Optional[int] = None


class QuestionOut(QuestionBase):
    id: str
    form_id: str

    class Config:
        from_attributes = True


# ── Form ──────────────────────────────────────────────────────────────────────

class FormBase(BaseModel):
    title: str = "Untitled Form"
    description: Optional[str] = None
    thank_you_message: Optional[str] = "Thank you for your response!"
    theme_color: Optional[str] = "#0445AF"
    button_text: Optional[str] = "Submit"


class FormCreate(FormBase):
    pass


class FormUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    thank_you_message: Optional[str] = None
    theme_color: Optional[str] = None
    button_text: Optional[str] = None


class FormOut(FormBase):
    id: str
    status: str
    public_id: str
    created_at: datetime
    updated_at: datetime
    response_count: int = 0
    questions: List[QuestionOut] = []

    class Config:
        from_attributes = True


class FormListItem(BaseModel):
    id: str
    title: str
    status: str
    public_id: str
    created_at: datetime
    updated_at: datetime
    response_count: int = 0
    question_count: int = 0

    class Config:
        from_attributes = True


# ── Reorder ───────────────────────────────────────────────────────────────────

class ReorderItem(BaseModel):
    id: str
    order_index: int


class ReorderRequest(BaseModel):
    questions: List[ReorderItem]


# ── Answer / Response ─────────────────────────────────────────────────────────

class AnswerIn(BaseModel):
    question_id: str
    value: Any


class ResponseCreate(BaseModel):
    answers: List[AnswerIn]


class AnswerOut(BaseModel):
    id: str
    question_id: str
    value: Optional[str]

    class Config:
        from_attributes = True


class ResponseOut(BaseModel):
    id: str
    form_id: str
    submitted_at: datetime
    answers: List[AnswerOut] = []

    class Config:
        from_attributes = True


# ── Stats ─────────────────────────────────────────────────────────────────────

class ChoiceCount(BaseModel):
    choice: str
    count: int


class QuestionStats(BaseModel):
    question_id: str
    question_title: str
    question_type: str
    total_answers: int
    choice_counts: Optional[List[ChoiceCount]] = None
    average: Optional[float] = None


class FormStats(BaseModel):
    form_id: str
    total_responses: int
    questions: List[QuestionStats]
