from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Startup, User
from app.schemas import StartupCreate, StartupUpdate, StartupResponse
from app.auth.dependencies import get_current_user, require_founder

router = APIRouter(prefix="/startups", tags=["Startups"])


# ─────────────────────────────────────────────
# POST /startups
# Only founders can create a startup
# ─────────────────────────────────────────────

@router.post("/", response_model=StartupResponse, status_code=201)
def create_startup(
    request: StartupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_founder)   # only founders allowed
):
    new_startup = Startup(
        name=request.name,
        description=request.description,
        industry=request.industry,
        stage=request.stage,
        website=request.website,
        founder_id=current_user.id
    )
    db.add(new_startup)
    db.commit()
    db.refresh(new_startup)
    return new_startup


# ─────────────────────────────────────────────
# GET /startups
# Anyone logged in can view all startups
# ─────────────────────────────────────────────

@router.get("/", response_model=List[StartupResponse])
def get_all_startups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # any logged in user
):
    startups = db.query(Startup).all()
    return startups


# ─────────────────────────────────────────────
# GET /startups/{id}
# Anyone logged in can view a single startup
# ─────────────────────────────────────────────

@router.get("/{startup_id}", response_model=StartupResponse)
def get_startup(
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
    return startup


# ─────────────────────────────────────────────
# PUT /startups/{id}
# Only the founder who created it can update it
# ─────────────────────────────────────────────

@router.put("/{startup_id}", response_model=StartupResponse)
def update_startup(
    startup_id: int,
    request: StartupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_founder)
):
    startup = db.query(Startup).filter(Startup.id == startup_id).first()

    if not startup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup not found"
        )

    # Make sure this founder owns this startup
    if startup.founder_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own startup"
        )

    # Only update fields that were actually sent
    if request.name is not None:
        startup.name = request.name
    if request.description is not None:
        startup.description = request.description
    if request.industry is not None:
        startup.industry = request.industry
    if request.stage is not None:
        startup.stage = request.stage
    if request.website is not None:
        startup.website = request.website

    db.commit()
    db.refresh(startup)
    return startup


# ─────────────────────────────────────────────
# DELETE /startups/{id}
# Only the founder who created it can delete it
# ─────────────────────────────────────────────

@router.delete("/{startup_id}", status_code=200)
def delete_startup(
    startup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_founder)
):
    startup = db.query(Startup).filter(Startup.id == startup_id).first()

    if not startup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup not found"
        )

    # Make sure this founder owns this startup
    if startup.founder_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own startup"
        )

    db.delete(startup)
    db.commit()
    return {"message": "Startup deleted successfully"}