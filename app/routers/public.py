"""
Public endpoints – no auth required.
Used by the respondent flow.
"""
import json
import re
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Form, Question, Response, Answer
from ..schemas import ResponseCreate, ResponseOut, FormOut, QuestionOut

router = APIRouter(prefix="/api/public", tags=["public"])


def _validate_answer(question: Question, value: str | None) -> str | None:
    """Server-side validation. Returns error string or None."""
    if question.required and (value is None or str(value).strip() == ""):
        return "This field is required"

    if value is None or str(value).strip() == "":
        return None  # optional + empty = ok

    if question.type == "email":
        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not re.match(pattern, value.strip()):
            return "Please enter a valid email address"

    if question.type == "number":
        try:
            float(value)
        except (ValueError, TypeError):
            return "Please enter a valid number"

    return None


@router.get("/forms/{public_id}", response_model=FormOut)
def get_public_form(public_id: str, db: Session = Depends(get_db)):
    form = db.query(Form).filter(
        Form.public_id == public_id,
        Form.status == "published"
    ).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found or not published")

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


@router.post("/forms/{public_id}/responses", response_model=ResponseOut, status_code=201)
def submit_response(
    public_id: str,
    payload: ResponseCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    form = db.query(Form).filter(
        Form.public_id == public_id,
        Form.status == "published"
    ).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found or not published")

    # Build question lookup
    questions = {q.id: q for q in form.questions}

    # Validate all answers
    errors = {}
    for ans in payload.answers:
        q = questions.get(ans.question_id)
        if not q:
            continue
        val = str(ans.value) if ans.value is not None else None
        err = _validate_answer(q, val)
        if err:
            errors[ans.question_id] = err

    # Also check required questions that weren't answered
    answered_ids = {a.question_id for a in payload.answers}
    for q in form.questions:
        if q.required and q.id not in answered_ids:
            errors[q.id] = "This field is required"

    if errors:
        raise HTTPException(status_code=422, detail={"errors": errors})

    # Persist
    client_ip = request.client.host if request.client else None
    response = Response(form_id=form.id, respondent_ip=client_ip)
    db.add(response)
    db.flush()

    for ans in payload.answers:
        value = json.dumps(ans.value) if isinstance(ans.value, (list, dict)) else str(ans.value) if ans.value is not None else None
        answer = Answer(
            response_id=response.id,
            question_id=ans.question_id,
            value=value,
        )
        db.add(answer)

    db.commit()
    db.refresh(response)
    return ResponseOut(
        id=response.id,
        form_id=response.form_id,
        submitted_at=response.submitted_at,
        answers=[
            {"id": a.id, "question_id": a.question_id, "value": a.value}
            for a in response.answers
        ],
    )
