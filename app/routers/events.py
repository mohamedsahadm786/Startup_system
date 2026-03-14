from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Event, User
from app.schemas import EventCreate, EventResponse
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/events", tags=["Events"])


# ─────────────────────────────────────────────
# POST /events
# Any logged in user can create an event
# ─────────────────────────────────────────────

@router.post("/", response_model=EventResponse, status_code=201)
def create_event(
    request: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # any logged in user
):
    new_event = Event(
        title=request.title,
        description=request.description,
        event_date=request.event_date,
        location=request.location,
        created_by=current_user.id
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


# ─────────────────────────────────────────────
# GET /events
# Anyone logged in can view all events
# ─────────────────────────────────────────────

@router.get("/", response_model=List[EventResponse])
def get_all_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    events = db.query(Event).order_by(Event.id.desc()).all()
    return events


# ─────────────────────────────────────────────
# GET /events/{id}
# Anyone logged in can view a single event
# ─────────────────────────────────────────────

@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event


# ─────────────────────────────────────────────
# PUT /events/{id}
# Only the creator can update the event
# ─────────────────────────────────────────────

@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    request: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    # Only the creator can update
    if event.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own events"
        )

    event.title = request.title
    event.description = request.description
    event.event_date = request.event_date
    event.location = request.location

    db.commit()
    db.refresh(event)
    return event


# ─────────────────────────────────────────────
# DELETE /events/{id}
# Only the creator can delete the event
# ─────────────────────────────────────────────

@router.delete("/{event_id}", status_code=200)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    if event.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own events"
        )

    db.delete(event)
    db.commit()
    return {"message": "Event deleted successfully"}