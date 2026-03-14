from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Startup, Evaluation, User
from app.schemas import EvaluationResponse
from app.auth.dependencies import get_current_user, require_founder
from app.services.ai_evaluator import evaluate_startup

router = APIRouter(prefix="/startups", tags=["AI Evaluation"])


# ─────────────────────────────────────────────
# POST /startups/{id}/evaluate
# Founder triggers AI evaluation for their startup
# ─────────────────────────────────────────────

@router.post("/{startup_id}/evaluate", response_model=EvaluationResponse)
def trigger_evaluation(
    startup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_founder)
):
    # Check startup exists
    startup = db.query(Startup).filter(Startup.id == startup_id).first()
    if not startup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup not found"
        )

    # Only the founder who owns the startup can evaluate it
    if startup.founder_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only evaluate your own startup"
        )

    # Call OpenAI and get the evaluation result
    try:
        result = evaluate_startup(
            name=startup.name,
            description=startup.description,
            industry=startup.industry,
            stage=startup.stage
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI evaluation failed: {str(e)}"
        )

    # Save evaluation to database
    evaluation = Evaluation(
        startup_id=startup.id,
        score=result["score"],
        strengths=result["strengths"],
        weaknesses=result["weaknesses"],
        suggestions=result["suggestions"]
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    return evaluation


# ─────────────────────────────────────────────
# GET /startups/{id}/evaluation
# Anyone logged in can view the latest evaluation
# ─────────────────────────────────────────────

@router.get("/{startup_id}/evaluation", response_model=EvaluationResponse)
def get_evaluation(
    startup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check startup exists
    startup = db.query(Startup).filter(Startup.id == startup_id).first()
    if not startup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup not found"
        )

    # Get the latest evaluation for this startup
    evaluation = (
        db.query(Evaluation)
        .filter(Evaluation.startup_id == startup_id)
        .order_by(Evaluation.id.desc())
        .first()
    )

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No evaluation found for this startup. Trigger one first."
        )

    return evaluation


# ─────────────────────────────────────────────
# GET /startups/{id}/evaluations
# Get all evaluations history for a startup
# ─────────────────────────────────────────────

@router.get("/{startup_id}/evaluations", response_model=List[EvaluationResponse])
def get_all_evaluations(
    startup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    startup = db.query(Startup).filter(Startup.id == startup_id).first()
    if not startup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup not found"
        )

    evaluations = (
        db.query(Evaluation)
        .filter(Evaluation.startup_id == startup_id)
        .order_by(Evaluation.id.desc())
        .all()
    )

    return evaluations