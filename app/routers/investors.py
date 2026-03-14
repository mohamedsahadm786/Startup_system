from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Investor, User
from app.schemas import InvestorCreate, InvestorUpdate, InvestorResponse
from app.auth.dependencies import get_current_user, require_investor

router = APIRouter(prefix="/investors", tags=["Investors"])


# ─────────────────────────────────────────────
# POST /investors
# Only investors can create their profile
# ─────────────────────────────────────────────

@router.post("/", response_model=InvestorResponse, status_code=201)
def create_investor_profile(
    request: InvestorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_investor)  # only investors allowed
):
    # One investor user = one profile only
    existing = db.query(Investor).filter(Investor.user_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Investor profile already exists. Use PUT to update it."
        )

    new_investor = Investor(
        firm_name=request.firm_name,
        focus_areas=request.focus_areas,
        ticket_size=request.ticket_size,
        bio=request.bio,
        user_id=current_user.id
    )
    db.add(new_investor)
    db.commit()
    db.refresh(new_investor)
    return new_investor


# ─────────────────────────────────────────────
# GET /investors
# Anyone logged in can view all investor profiles
# ─────────────────────────────────────────────

@router.get("/", response_model=List[InvestorResponse])
def get_all_investors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    investors = db.query(Investor).all()
    return investors


# ─────────────────────────────────────────────
# GET /investors/{id}
# Anyone logged in can view a single investor profile
# ─────────────────────────────────────────────

@router.get("/{investor_id}", response_model=InvestorResponse)
def get_investor(
    investor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    investor = db.query(Investor).filter(Investor.id == investor_id).first()
    if not investor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investor profile not found"
        )
    return investor


# ─────────────────────────────────────────────
# PUT /investors/{id}
# Only the investor who created it can update it
# ─────────────────────────────────────────────

@router.put("/{investor_id}", response_model=InvestorResponse)
def update_investor_profile(
    investor_id: int,
    request: InvestorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_investor)
):
    investor = db.query(Investor).filter(Investor.id == investor_id).first()

    if not investor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investor profile not found"
        )

    # Make sure this investor owns this profile
    if investor.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own investor profile"
        )

    if request.firm_name is not None:
        investor.firm_name = request.firm_name
    if request.focus_areas is not None:
        investor.focus_areas = request.focus_areas
    if request.ticket_size is not None:
        investor.ticket_size = request.ticket_size
    if request.bio is not None:
        investor.bio = request.bio

    db.commit()
    db.refresh(investor)
    return investor


# ─────────────────────────────────────────────
# DELETE /investors/{id}
# Only the investor who created it can delete it
# ─────────────────────────────────────────────

@router.delete("/{investor_id}", status_code=200)
def delete_investor_profile(
    investor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_investor)
):
    investor = db.query(Investor).filter(Investor.id == investor_id).first()

    if not investor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investor profile not found"
        )

    if investor.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own investor profile"
        )

    db.delete(investor)
    db.commit()
    return {"message": "Investor profile deleted successfully"}