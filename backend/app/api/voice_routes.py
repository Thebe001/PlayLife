from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db import get_db
from app.services.whisper_service import transcribe_audio
from app.services.llm_service import parse_intent, get_advice
from app.services.action_dispatcher import dispatch
from app.services.scoring_service import get_today_summary

router = APIRouter(prefix="/voice", tags=["Voice & AI"])


class TextCommand(BaseModel):
    text: str


@router.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """Transcrit un fichier audio en texte via Whisper."""
    contents = await audio.read()
    ext = audio.filename.split(".")[-1] if audio.filename else "webm"

    try:
        text = transcribe_audio(contents, ext)
        return {"text": text, "detected_language": "auto"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur Whisper: {str(e)}")


@router.post("/command")
async def process_command(body: TextCommand, db: Session = Depends(get_db)):
    """Parse et exécute une commande textuelle via LLM."""
    intent = await parse_intent(body.text)

    action = intent.get("action", "unknown")
    params = intent.get("params", {})
    llm_response = intent.get("response", "Commande traitée.")

    result = dispatch(action, params, db)

    return {
        "original_text": body.text,
        "action": action,
        "params": params,
        "llm_response": llm_response,
        "result": result,
    }


@router.post("/voice-command")
async def voice_command(audio: UploadFile = File(...), db: Session = Depends(get_db)):
    """Pipeline complet : audio → texte → LLM → action."""
    contents = await audio.read()
    ext = audio.filename.split(".")[-1] if audio.filename else "webm"

    # Step 1: Whisper STT
    try:
        text = transcribe_audio(contents, ext)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur transcription: {str(e)}")

    # Step 2: LLM intent parsing
    intent = await parse_intent(text)
    action = intent.get("action", "unknown")
    params = intent.get("params", {})
    llm_response = intent.get("response", "Commande traitée.")

    # Step 3: Dispatch action
    result = dispatch(action, params, db)

    return {
        "transcription": text,
        "action": action,
        "llm_response": llm_response,
        "result": result,
    }


@router.get("/advice")
async def get_daily_advice(db: Session = Depends(get_db)):
    """Génère un conseil personnalisé basé sur les stats du jour."""
    summary = get_today_summary(db)
    context = f"Score global: {summary['global_score']}%, XP aujourd'hui: {summary['xp_today']}, Piliers: {summary['pillars']}"
    advice = await get_advice(context)
    return {"advice": advice}