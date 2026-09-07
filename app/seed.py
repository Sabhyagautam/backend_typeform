"""
Seed the database with sample forms and responses.
Run once: python -m app.seed
"""
import json
import random
from datetime import datetime, timedelta
from .database import SessionLocal, engine
from .models import Base, Form, Question, Response, Answer


NAMES = ["Rahul Sharma", "Priya Singh", "Aman Gupta", "Neha Joshi", "Vikram Patel",
         "Sunita Rao", "Arjun Mehta", "Pooja Verma", "Siddharth Kumar", "Deepa Nair",
         "Ravi Krishnan", "Ananya Das", "Karan Malhotra", "Meera Iyer", "Suresh Pillai"]

EMAILS = [f"{n.split()[0].lower()}@{'gmail' if i%3==0 else 'yahoo' if i%3==1 else 'outlook'}.com"
          for i, n in enumerate(NAMES)]

LANGUAGES = ["Python", "JavaScript", "Java", "C++"]
LOCATIONS = ["Mumbai", "Bangalore", "Delhi", "Hyderabad", "Chennai", "Pune"]
EXPERIENCE = ["0-1 years", "1-2 years", "2-3 years", "3-5 years", "5+ years"]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear existing data
    db.query(Answer).delete()
    db.query(Response).delete()
    db.query(Question).delete()
    db.query(Form).delete()
    db.commit()

    # ── Form 1: Job Application ───────────────────────────────────────────────
    job_form = Form(
        id="form-job-001",
        title="Job Application Form",
        description="Apply for a position at our company",
        status="published",
        public_id="job-application",
        thank_you_message="Thank you for applying! We'll review your application and get back to you within 5 business days.",
        theme_color="#0445AF",
    )
    db.add(job_form)
    db.flush()

    job_questions = [
        Question(id="jq1", form_id=job_form.id, type="short_text", title="What is your full name?",
                 description="Please enter your first and last name", required=True, order_index=0),
        Question(id="jq2", form_id=job_form.id, type="email", title="What is your email address?",
                 description="We'll use this to contact you", required=True, order_index=1),
        Question(id="jq3", form_id=job_form.id, type="dropdown", title="How many years of experience do you have?",
                 choices=EXPERIENCE, required=True, order_index=2),
        Question(id="jq4", form_id=job_form.id, type="multiple_choice",
                 title="Which programming languages do you know?",
                 choices=LANGUAGES, required=True, order_index=3),
        Question(id="jq5", form_id=job_form.id, type="yes_no",
                 title="Are you willing to relocate?", required=False, order_index=4),
        Question(id="jq6", form_id=job_form.id, type="rating",
                 title="How would you rate your problem-solving skills?",
                 description="1 = beginner, 5 = expert", rating_steps=5, required=False, order_index=5),
        Question(id="jq7", form_id=job_form.id, type="long_text",
                 title="Tell us about yourself",
                 description="Brief introduction (max 300 words)", required=False, order_index=6),
    ]
    for q in job_questions:
        db.add(q)

    # ── Form 2: Developer Survey ───────────────────────────────────────────────
    survey_form = Form(
        id="form-survey-002",
        title="Developer Experience Survey",
        description="Help us understand how developers feel about our tools",
        status="published",
        public_id="dev-survey-2024",
        thank_you_message="Thanks for completing the survey! Your feedback shapes our roadmap.",
        theme_color="#7C3AED",
    )
    db.add(survey_form)
    db.flush()

    survey_questions = [
        Question(id="sq1", form_id=survey_form.id, type="short_text",
                 title="What is your name?", required=True, order_index=0),
        Question(id="sq2", form_id=survey_form.id, type="multiple_choice",
                 title="Which language do you prefer?",
                 choices=LANGUAGES, required=True, order_index=1),
        Question(id="sq3", form_id=survey_form.id, type="number",
                 title="How many hours per week do you code?",
                 description="Enter a number", required=True, order_index=2),
        Question(id="sq4", form_id=survey_form.id, type="dropdown",
                 title="Where are you based?", choices=LOCATIONS, required=False, order_index=3),
        Question(id="sq5", form_id=survey_form.id, type="rating",
                 title="How satisfied are you with your current tools?",
                 rating_steps=5, required=True, order_index=4),
        Question(id="sq6", form_id=survey_form.id, type="yes_no",
                 title="Would you recommend us to a colleague?", required=False, order_index=5),
        Question(id="sq7", form_id=survey_form.id, type="long_text",
                 title="Any suggestions or feedback?", required=False, order_index=6),
    ]
    for q in survey_questions:
        db.add(q)

    # ── Form 3: Event Registration (draft) ────────────────────────────────────
    event_form = Form(
        id="form-event-003",
        title="Tech Conference Registration",
        description="Register for our annual tech conference",
        status="draft",
        public_id="tech-conf-2025",
        theme_color="#059669",
    )
    db.add(event_form)
    db.flush()

    event_questions = [
        Question(form_id=event_form.id, type="short_text", title="Full Name", required=True, order_index=0),
        Question(form_id=event_form.id, type="email", title="Email Address", required=True, order_index=1),
        Question(form_id=event_form.id, type="dropdown", title="T-Shirt Size",
                 choices=["XS", "S", "M", "L", "XL", "XXL"], required=False, order_index=2),
        Question(form_id=event_form.id, type="yes_no", title="Attending the evening networking event?",
                 required=False, order_index=3),
    ]
    for q in event_questions:
        db.add(q)

    db.commit()

    # ── Seed Responses for Job Form ───────────────────────────────────────────
    for i in range(15):
        resp = Response(form_id=job_form.id,
                        submitted_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)))
        db.add(resp)
        db.flush()

        db.add(Answer(response_id=resp.id, question_id="jq1", value=NAMES[i]))
        db.add(Answer(response_id=resp.id, question_id="jq2", value=EMAILS[i]))
        db.add(Answer(response_id=resp.id, question_id="jq3", value=random.choice(EXPERIENCE)))
        db.add(Answer(response_id=resp.id, question_id="jq4", value=random.choice(LANGUAGES)))
        db.add(Answer(response_id=resp.id, question_id="jq5", value=random.choice(["Yes", "No"])))
        db.add(Answer(response_id=resp.id, question_id="jq6", value=str(random.randint(1, 5))))
        db.add(Answer(response_id=resp.id, question_id="jq7",
                      value=f"I am {NAMES[i].split()[0]}, a passionate developer with experience in building scalable systems."))

    # ── Seed Responses for Survey Form ───────────────────────────────────────
    for i in range(24):
        name = NAMES[i % len(NAMES)]
        email = EMAILS[i % len(EMAILS)]
        resp = Response(form_id=survey_form.id,
                        submitted_at=datetime.utcnow() - timedelta(days=random.randint(0, 60)))
        db.add(resp)
        db.flush()

        db.add(Answer(response_id=resp.id, question_id="sq1", value=name))
        db.add(Answer(response_id=resp.id, question_id="sq2", value=random.choice(LANGUAGES)))
        db.add(Answer(response_id=resp.id, question_id="sq3", value=str(random.randint(10, 60))))
        db.add(Answer(response_id=resp.id, question_id="sq4", value=random.choice(LOCATIONS)))
        db.add(Answer(response_id=resp.id, question_id="sq5", value=str(random.randint(1, 5))))
        db.add(Answer(response_id=resp.id, question_id="sq6", value=random.choice(["Yes", "No"])))

    db.commit()
    db.close()
    print("✅ Database seeded successfully!")
    print("  - Job Application Form: 15 responses")
    print("  - Developer Experience Survey: 24 responses")
    print("  - Tech Conference Registration: 0 responses (draft)")


if __name__ == "__main__":
    seed()
