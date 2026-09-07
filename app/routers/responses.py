"""
Creator-side: view responses & stats for a form.
"""
import json
from typing import List
from collections import Counter
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Form, Response, Answer, Question
from ..schemas import ResponseOut, FormStats, QuestionStats, ChoiceCount, AnswerOut

router = APIRouter(prefix="/api/forms", tags=["responses"])


@router.get("/{form_id}/responses", response_model=List[ResponseOut])
def list_responses(form_id: str, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    responses = (
        db.query(Response)
        .filter(Response.form_id == form_id)
        .order_by(Response.submitted_at.desc())
        .all()
    )
    return [
        ResponseOut(
            id=r.id,
            form_id=r.form_id,
            submitted_at=r.submitted_at,
            answers=[AnswerOut(id=a.id, question_id=a.question_id, value=a.value) for a in r.answers],
        )
        for r in responses
    ]


@router.get("/{form_id}/responses/{response_id}", response_model=ResponseOut)
def get_response(form_id: str, response_id: str, db: Session = Depends(get_db)):
    response = db.query(Response).filter(
        Response.id == response_id, Response.form_id == form_id
    ).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    return ResponseOut(
        id=response.id,
        form_id=response.form_id,
        submitted_at=response.submitted_at,
        answers=[AnswerOut(id=a.id, question_id=a.question_id, value=a.value) for a in response.answers],
    )


@router.get("/{form_id}/stats", response_model=FormStats)
def get_stats(form_id: str, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    total_responses = len(form.responses)
    question_stats = []

    for q in sorted(form.questions, key=lambda x: x.order_index):
        answers = (
            db.query(Answer)
            .filter(Answer.question_id == q.id)
            .all()
        )
        values = [a.value for a in answers if a.value is not None]
        total_answers = len(values)

        choice_counts = None
        average = None

        if q.type in ("multiple_choice", "dropdown", "yes_no"):
            counter = Counter(values)
            choice_counts = [
                ChoiceCount(choice=k, count=v)
                for k, v in sorted(counter.items(), key=lambda x: -x[1])
            ]

        if q.type == "rating":
            try:
                nums = [float(v) for v in values if v]
                average = round(sum(nums) / len(nums), 2) if nums else None
                # Also provide choice counts for bar chart
                counter = Counter(str(int(float(v))) for v in values if v)
                choice_counts = [
                    ChoiceCount(choice=k, count=v)
                    for k, v in sorted(counter.items(), key=lambda x: int(x[0]))
                ]
            except Exception:
                pass

        if q.type == "number":
            try:
                nums = [float(v) for v in values if v]
                average = round(sum(nums) / len(nums), 2) if nums else None
            except Exception:
                pass

        question_stats.append(QuestionStats(
            question_id=q.id,
            question_title=q.title,
            question_type=q.type,
            total_answers=total_answers,
            choice_counts=choice_counts,
            average=average,
        ))

    return FormStats(
        form_id=form_id,
        total_responses=total_responses,
        questions=question_stats,
    )
