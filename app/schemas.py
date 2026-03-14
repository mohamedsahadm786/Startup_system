from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models import UserRole


# ─────────────────────────────────────────────
# AUTH SCHEMAS
# These define what data comes IN and goes OUT
# for signup and login
# ─────────────────────────────────────────────

class SignupRequest(BaseModel):
    """Data the user sends when signing up"""
    name: str
    email: str
    password: str
    role: UserRole                 # must be "founder" or "investor"


class LoginRequest(BaseModel):
    """Data the user sends when logging in"""
    email: str
    password: str


class TokenResponse(BaseModel):
    """What we send back after successful login"""
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    name: str


class UserResponse(BaseModel):
    """Safe user data to return (never return hashed_password)"""
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True        # allows converting SQLAlchemy model to this schema


# ─────────────────────────────────────────────
# STARTUP SCHEMAS
# ─────────────────────────────────────────────

class StartupCreate(BaseModel):
    name: str
    description: str
    industry: str
    stage: str
    website: Optional[str] = None


class StartupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    stage: Optional[str] = None
    website: Optional[str] = None


class StartupResponse(BaseModel):
    id: int
    name: str
    description: str
    industry: str
    stage: str
    website: Optional[str]
    founder_id: int

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# INVESTOR SCHEMAS
# ─────────────────────────────────────────────

class InvestorCreate(BaseModel):
    firm_name: str
    focus_areas: str
    ticket_size: str
    bio: Optional[str] = None


class InvestorUpdate(BaseModel):
    firm_name: Optional[str] = None
    focus_areas: Optional[str] = None
    ticket_size: Optional[str] = None
    bio: Optional[str] = None


class InvestorResponse(BaseModel):
    id: int
    firm_name: str
    focus_areas: str
    ticket_size: str
    bio: Optional[str]
    user_id: int

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# EVALUATION SCHEMAS
# ─────────────────────────────────────────────

class EvaluationResponse(BaseModel):
    id: int
    startup_id: int
    score: float
    strengths: str
    weaknesses: str
    suggestions: str

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# PITCH DECK SCHEMAS
# ─────────────────────────────────────────────

class PitchDeckResponse(BaseModel):
    id: int
    startup_id: int
    file_path: str
    extracted_text: Optional[str]
    analysis: Optional[str]
    score: Optional[float]

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# EVENT SCHEMAS
# ─────────────────────────────────────────────

class EventCreate(BaseModel):
    title: str
    description: str
    event_date: str
    location: str


class EventResponse(BaseModel):
    id: int
    title: str
    description: str
    event_date: str
    location: str
    created_by: int

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# CONNECTION SCHEMAS
# ─────────────────────────────────────────────

class ConnectionCreate(BaseModel):
    receiver_id: int


class ConnectionResponse(BaseModel):
    id: int
    requester_id: int
    receiver_id: int
    status: str

    class Config:
        from_attributes = True