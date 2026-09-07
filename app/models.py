import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Form(Base):
    __tablename__ = "forms"

    id = Column(String, primary_key=True, default=gen_uuid)
    title = Column(String, nullable=False, default="Untitled Form")
    description = Column(Text, nullable=True)
    status = Column(String, default="draft")          # draft | published
    public_id = Column(String, unique=True, default=gen_uuid)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    thank_you_message = Column(Text, default="Thank you for your response!")
    theme_color = Column(String, default="#0445AF")
    button_text = Column(String, default="Submit")

    questions = relationship(
        "Question", back_populates="form",
        cascade="all, delete-orphan",
        order_by="Question.order_index"
    )
    responses = relationship(
        "Response", back_populates="form",
        cascade="all, delete-orphan"
    )


class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, default=gen_uuid)
    form_id = Column(String, ForeignKey("forms.id"), nullable=False)
    # short_text | long_text | multiple_choice | dropdown | email | number | yes_no | rating
    type = Column(String, nullable=False)
    title = Column(Text, nullable=False, default="Untitled Question")
    description = Column(Text, nullable=True)
    required = Column(Boolean, default=False)
    order_index = Column(Integer, nullable=False, default=0)
    choices = Column(JSON, nullable=True)   # list[str] for mc/dropdown
    rating_steps = Column(Integer, default=5)

    form = relationship("Form", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")


class Response(Base):
    __tablename__ = "responses"

    id = Column(String, primary_key=True, default=gen_uuid)
    form_id = Column(String, ForeignKey("forms.id"), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    respondent_ip = Column(String, nullable=True)

    form = relationship("Form", back_populates="responses")
    answers = relationship("Answer", back_populates="response", cascade="all, delete-orphan")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(String, primary_key=True, default=gen_uuid)
    response_id = Column(String, ForeignKey("responses.id"), nullable=False)
    question_id = Column(String, ForeignKey("questions.id"), nullable=False)
    value = Column(Text, nullable=True)

    response = relationship("Response", back_populates="answers")
    question = relationship("Question", back_populates="answers")
