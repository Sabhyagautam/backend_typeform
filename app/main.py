import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine
from .models import Base
from .routers import forms, public, responses

# Create all tables on startup (safe to call repeatedly — no-ops if tables exist)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Typeform Clone API", version="1.0.0")

# ---------------------------------------------------------------------------
# CORS
# In production set ALLOWED_ORIGINS to your Vercel URL, e.g.:
#   ALLOWED_ORIGINS=https://your-app.vercel.app
# Multiple origins can be separated by commas.
# Falls back to allowing all origins if the var is not set (safe for dev/demo).
# ---------------------------------------------------------------------------
_raw = os.environ.get("ALLOWED_ORIGINS", "*")
if _raw == "*":
    allow_origins = ["*"]
else:
    allow_origins = [o.strip() for o in _raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=_raw != "*",   # credentials only work with explicit origins
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(forms.router)
app.include_router(public.router)
app.include_router(responses.router)


@app.get("/")
def root():
    """Health-check endpoint."""
    return {"status": "ok", "message": "Typeform Clone API", "docs": "/docs"}
