import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Startup, PitchDeck, User
from app.schemas import PitchDeckResponse
from app.auth.dependencies import get_current_user, require_founder
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.pitch_analyzer import analyze_pitch_deck

router = APIRouter(prefix="/startups", tags=["Pitch Decks"])

# Folder where uploaded PDFs will be saved
UPLOAD_DIR = "app/uploads"


# ─────────────────────────────────────────────
# POST /startups/{id}/upload-pitch-deck
# Founder uploads a PDF pitch deck
# ─────────────────────────────────────────────

@router.post("/{startup_id}/upload-pitch-deck", response_model=PitchDeckResponse)
async def upload_pitch_deck(
    startup_id: int,
    file: UploadFile = File(...),      # File(...) means file is required
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

    # Only the founder who owns the startup can upload
    if startup.founder_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload pitch decks for your own startup"
        )

    # Check that uploaded file is a PDF
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    # Read the file bytes
    file_bytes = await file.read()

    # Save the PDF to the uploads folder
    # File name format: startup_1_pitchdeck.pdf
    file_name = f"startup_{startup_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # Extract text from the PDF
    extracted_text = extract_text_from_pdf(file_bytes)

    # Save pitch deck record to DB (analysis is empty for now)
    pitch_deck = PitchDeck(
        startup_id=startup_id,
        file_path=file_path,
        extracted_text=extracted_text,
        analysis=None,
        score=None
    )
    db.add(pitch_deck)
    db.commit()
    db.refresh(pitch_deck)

    return pitch_deck


# ─────────────────────────────────────────────
# POST /startups/{id}/analyze-pitch-deck
# Triggers AI analysis on the uploaded pitch deck
# ─────────────────────────────────────────────

@router.post("/{startup_id}/analyze-pitch-deck", response_model=PitchDeckResponse)
def analyze_pitch(
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

    if startup.founder_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only analyze your own startup's pitch deck"
        )

    # Get the latest uploaded pitch deck for this startup
    pitch_deck = (
        db.query(PitchDeck)
        .filter(PitchDeck.startup_id == startup_id)
        .order_by(PitchDeck.id.desc())
        .first()
    )

    if not pitch_deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pitch deck found. Upload one first."
        )

    if not pitch_deck.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No text could be extracted from this pitch deck."
        )

    # Call OpenAI to analyze the pitch deck
    try:
        result = analyze_pitch_deck(
            extracted_text=pitch_deck.extracted_text,
            startup_name=startup.name
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}"
        )

    # Save analysis results back to the pitch deck record
    pitch_deck.analysis = (
        f"ANALYSIS: {result['analysis']} | "
        f"KEY INSIGHTS: {result['key_insights']} | "
        f"IMPROVEMENTS: {result['improvements']}"
    )
    pitch_deck.score = result["score"]

    db.commit()
    db.refresh(pitch_deck)

    return pitch_deck


# ─────────────────────────────────────────────
# GET /startups/{id}/pitch-deck
# Anyone logged in can view the latest pitch deck result
# ─────────────────────────────────────────────

@router.get("/{startup_id}/pitch-deck", response_model=PitchDeckResponse)
def get_pitch_deck(
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

    pitch_deck = (
        db.query(PitchDeck)
        .filter(PitchDeck.startup_id == startup_id)
        .order_by(PitchDeck.id.desc())
        .first()
    )

    if not pitch_deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pitch deck found for this startup."
        )

    return pitch_deck