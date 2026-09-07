from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..models import Form, Question
from ..schemas import (
    FormCreate, FormUpdate, FormOut, FormListItem,
    QuestionCreate, QuestionUpdate, QuestionOut, ReorderRequest
)

router = APIRouter(prefix="/api/forms", tags=["forms"])


def _form_out(form: Form) -> FormOut:
    return FormOut(
        id=form.id,
        title=form.title,
        description=form.description,
        status=form.status,
        public_id=form.public_id,
        created_at=form.created_at,
        updated_at=form.updated_at,
        thank_you_message=form.thank_you_message,
        theme_color=form.theme_color,
        button_text=form.button_text,
        response_count=len(form.responses),
        questions=[
            QuestionOut.model_validate(q)
            for q in sorted(form.questions, key=lambda x: x.order_index)
        ],
    )


# ── Form CRUD ─────────────────────────────────────────────────────────────────

@router.get("", response_model=List[FormListItem])
def list_forms(db: Session = Depends(get_db)):
    forms = db.query(Form).order_by(Form.updated_at.desc()).all()
    return [
        FormListItem(
            id=f.id, title=f.title, status=f.status, public_id=f.public_id,
            created_at=f.created_at, updated_at=f.updated_at,
            response_count=len(f.responses), question_count=len(f.questions),
        )
        for f in forms
    ]


@router.post("", response_model=FormOut, status_code=status.HTTP_201_CREATED)
def create_form(payload: FormCreate, db: Session = Depends(get_db)):
    form = Form(**payload.model_dump())
    db.add(form)
    db.commit()
    db.refresh(form)
    return _form_out(form)


@router.get("/{form_id}", response_model=FormOut)
def get_form(form_id: str, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    return _form_out(form)


@router.patch("/{form_id}", response_model=FormOut)
def update_form(form_id: str, payload: FormUpdate, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(form, k, v)
    form.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(form)
    return _form_out(form)


@router.delete("/{form_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_form(form_id: str, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    db.delete(form)
    db.commit()


@router.post("/{form_id}/duplicate", response_model=FormOut, status_code=status.HTTP_201_CREATED)
def duplicate_form(form_id: str, db: Session = Depends(get_db)):
    original = db.query(Form).filter(Form.id == form_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Form not found")
    new_form = Form(
        title=f"{original.title} (Copy)",
        description=original.description,
        status="draft",
        thank_you_message=original.thank_you_message,
        theme_color=original.theme_color,
        button_text=original.button_text,
    )
    db.add(new_form)
    db.flush()
    for q in sorted(original.questions, key=lambda x: x.order_index):
        db.add(Question(
            form_id=new_form.id, type=q.type, title=q.title,
            description=q.description, required=q.required,
            order_index=q.order_index, choices=q.choices, rating_steps=q.rating_steps,
        ))
    db.commit()
    db.refresh(new_form)
    return _form_out(new_form)


@router.post("/{form_id}/publish", response_model=FormOut)
def publish_form(form_id: str, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    form.status = "published"
    form.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(form)
    return _form_out(form)


@router.post("/{form_id}/unpublish", response_model=FormOut)
def unpublish_form(form_id: str, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    form.status = "draft"
    form.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(form)
    return _form_out(form)


# ── Question CRUD ─────────────────────────────────────────────────────────────

@router.post("/{form_id}/questions", response_model=QuestionOut, status_code=201)
def add_question(form_id: str, payload: QuestionCreate, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    max_order = max((q.order_index for q in form.questions), default=-1)
    data = payload.model_dump()
    data["order_index"] = max_order + 1
    question = Question(form_id=form_id, **data)
    db.add(question)
    form.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(question)
    return QuestionOut.model_validate(question)


@router.patch("/{form_id}/questions/{question_id}", response_model=QuestionOut)
def update_question(form_id: str, question_id: str, payload: QuestionUpdate, db: Session = Depends(get_db)):
    question = db.query(Question).filter(
        Question.id == question_id, Question.form_id == form_id
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(question, k, v)
    form = db.query(Form).filter(Form.id == form_id).first()
    if form:
        form.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(question)
    return QuestionOut.model_validate(question)


@router.delete("/{form_id}/questions/{question_id}", status_code=204)
def delete_question(form_id: str, question_id: str, db: Session = Depends(get_db)):
    question = db.query(Question).filter(
        Question.id == question_id, Question.form_id == form_id
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(question)
    form = db.query(Form).filter(Form.id == form_id).first()
    if form:
        form.updated_at = datetime.utcnow()
    db.commit()


@router.post("/{form_id}/questions/reorder")
def reorder_questions(form_id: str, payload: ReorderRequest, db: Session = Depends(get_db)):
    for item in payload.questions:
        q = db.query(Question).filter(Question.id == item.id, Question.form_id == form_id).first()
        if q:
            q.order_index = item.order_index
    form = db.query(Form).filter(Form.id == form_id).first()
    if form:
        form.updated_at = datetime.utcnow()
    db.commit()
    return {"ok": True}
