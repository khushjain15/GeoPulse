import os
from fastapi import APIRouter
from sqlalchemy import text
from app.db.session import SessionLocal

router = APIRouter()


@router.get("/health", summary="Liveness and DB connectivity check")
def health_check():
    """Returns service status and database connectivity."""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"

    model_path = os.getenv("MODEL_PATH", "/models/risk_model.pkl")
    model_status = "ok" if os.path.exists(model_path) else "not_loaded"

    return {
        "status": "ok",
        "db": db_status,
        "model": model_status,
        "version": "0.1.0",
    }