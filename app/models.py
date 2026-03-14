from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


# ─────────────────────────────────────────────
# ENUM for user roles
# ─────────────────────────────────────────────

class UserRole(str, enum.Enum):
    founder = "founder"
    investor = "investor"


# ─────────────────────────────────────────────
# TABLE 1: users
# Stores everyone who signs up — founders and investors
# ─────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)  # "founder" or "investor"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships — makes it easy to access related data
    startups = relationship("Startup", back_populates="founder")
    investor_profile = relationship("Investor", back_populates="user", uselist=False)
    events_created = relationship("Event", back_populates="creator")
    connections_sent = relationship("Connection", foreign_keys="Connection.requester_id", back_populates="requester")
    connections_received = relationship("Connection", foreign_keys="Connection.receiver_id", back_populates="receiver")


# ─────────────────────────────────────────────
# TABLE 2: startups
# Stores startup profiles created by founders
# ─────────────────────────────────────────────

class Startup(Base):
    __tablename__ = "startups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    industry = Column(String, nullable=False)
    stage = Column(String, nullable=False)        # e.g. idea, MVP, seed, series A
    website = Column(String, nullable=True)
    founder_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    founder = relationship("User", back_populates="startups")
    evaluations = relationship("Evaluation", back_populates="startup")
    pitch_decks = relationship("PitchDeck", back_populates="startup")


# ─────────────────────────────────────────────
# TABLE 3: investors
# Stores investor profiles created by investors
# ─────────────────────────────────────────────

class Investor(Base):
    __tablename__ = "investors"

    id = Column(Integer, primary_key=True, index=True)
    firm_name = Column(String, nullable=False)
    focus_areas = Column(String, nullable=False)   # e.g. "FinTech, HealthTech"
    ticket_size = Column(String, nullable=False)   # e.g. "$10k - $100k"
    bio = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="investor_profile")


# ─────────────────────────────────────────────
# TABLE 4: evaluations
# Stores AI-generated evaluation results for a startup
# ─────────────────────────────────────────────

class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    startup_id = Column(Integer, ForeignKey("startups.id"), nullable=False)
    score = Column(Float, nullable=False)          # 0 to 100
    strengths = Column(Text, nullable=False)
    weaknesses = Column(Text, nullable=False)
    suggestions = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    startup = relationship("Startup", back_populates="evaluations")


# ─────────────────────────────────────────────
# TABLE 5: pitch_decks
# Stores uploaded pitch deck files and their AI analysis
# ─────────────────────────────────────────────

class PitchDeck(Base):
    __tablename__ = "pitch_decks"

    id = Column(Integer, primary_key=True, index=True)
    startup_id = Column(Integer, ForeignKey("startups.id"), nullable=False)
    file_path = Column(String, nullable=False)     # where the PDF is saved on disk
    extracted_text = Column(Text, nullable=True)   # text pulled out from the PDF
    analysis = Column(Text, nullable=True)         # AI analysis result
    score = Column(Float, nullable=True)           # AI score for the pitch deck
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    startup = relationship("Startup", back_populates="pitch_decks")


# ─────────────────────────────────────────────
# TABLE 6: events
# Stores ecosystem events created by any user
# ─────────────────────────────────────────────

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    event_date = Column(String, nullable=False)    # stored as string e.g. "2026-03-20"
    location = Column(String, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    creator = relationship("User", back_populates="events_created")


# ─────────────────────────────────────────────
# TABLE 7: connections
# Stores founder-to-founder networking connections
# ─────────────────────────────────────────────

class Connection(Base):
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending")     # pending / accepted
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], back_populates="connections_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="connections_received")