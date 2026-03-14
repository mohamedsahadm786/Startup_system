from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Connection, User
from app.schemas import ConnectionCreate, ConnectionResponse, ConnectionAccept
from app.auth.dependencies import get_current_user, require_founder

router = APIRouter(prefix="/connections", tags=["Founder Networking"])


# ─────────────────────────────────────────────
# POST /connections
# Founder sends a connection request to another founder
# ─────────────────────────────────────────────

@router.post("/", response_model=ConnectionResponse, status_code=201)
def send_connection_request(
    request: ConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_founder)   # only founders can connect
):
    # Cannot connect with yourself
    if request.receiver_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot send a connection request to yourself"
        )

    # Check if receiver exists
    receiver = db.query(User).filter(User.id == request.receiver_id).first()
    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if connection already exists in either direction
    existing = db.query(Connection).filter(
        (
            (Connection.requester_id == current_user.id) &
            (Connection.receiver_id == request.receiver_id)
        ) | (
            (Connection.requester_id == request.receiver_id) &
            (Connection.receiver_id == current_user.id)
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connection request already exists between these users"
        )

    # Create the connection request
    new_connection = Connection(
        requester_id=current_user.id,
        receiver_id=request.receiver_id,
        status="pending"
    )
    db.add(new_connection)
    db.commit()
    db.refresh(new_connection)
    return new_connection


# ─────────────────────────────────────────────
# GET /connections/me
# Get all connections for the logged in user
# ─────────────────────────────────────────────

@router.get("/me", response_model=List[ConnectionResponse])
def get_my_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get all connections where this user is either sender or receiver
    connections = db.query(Connection).filter(
        (Connection.requester_id == current_user.id) |
        (Connection.receiver_id == current_user.id)
    ).all()

    return connections


# ─────────────────────────────────────────────
# GET /connections/pending
# Get all pending connection requests received by logged in user
# ─────────────────────────────────────────────

@router.get("/pending", response_model=List[ConnectionResponse])
def get_pending_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only show requests where this user is the RECEIVER
    # and status is still pending
    pending = db.query(Connection).filter(
        Connection.receiver_id == current_user.id,
        Connection.status == "pending"
    ).all()

    return pending


# ─────────────────────────────────────────────
# PUT /connections/{id}/respond
# Accept or reject a connection request
# ─────────────────────────────────────────────

@router.put("/{connection_id}/respond", response_model=ConnectionResponse)
def respond_to_connection(
    connection_id: int,
    request: ConnectionAccept,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    connection = db.query(Connection).filter(
        Connection.id == connection_id
    ).first()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection request not found"
        )

    # Only the receiver can accept or reject
    if connection.receiver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only respond to connection requests sent to you"
        )

    # Only pending connections can be responded to
    if connection.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This connection is already {connection.status}"
        )

    # Validate the status value
    if request.status not in ["accepted", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be either 'accepted' or 'rejected'"
        )

    connection.status = request.status
    db.commit()
    db.refresh(connection)
    return connection


# ─────────────────────────────────────────────
# GET /connections/all
# Get all connections in the platform (for discovery)
# ─────────────────────────────────────────────

@router.get("/all", response_model=List[ConnectionResponse])
def get_all_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    connections = db.query(Connection).filter(
        Connection.status == "accepted"
    ).all()
    return connections


# ─────────────────────────────────────────────
# DELETE /connections/{id}
# Cancel a connection request you sent
# ─────────────────────────────────────────────

@router.delete("/{connection_id}", status_code=200)
def cancel_connection(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    connection = db.query(Connection).filter(
        Connection.id == connection_id
    ).first()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )

    # Only the person who sent the request can cancel it
    if connection.requester_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel connection requests you sent"
        )

    db.delete(connection)
    db.commit()
    return {"message": "Connection request cancelled successfully"}