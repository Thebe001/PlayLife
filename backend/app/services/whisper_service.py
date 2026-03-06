import whisper
import tempfile
import os

# Charge le modèle une seule fois au démarrage (small = bon compromis vitesse/précision)
_model = None


def get_model():
    global _model
    if _model is None:
        print("🎤 Chargement du modèle Whisper small...")
        _model = whisper.load_model("small")
        print("✅ Whisper prêt.")
    return _model


def transcribe_audio(audio_bytes: bytes, extension: str = "webm") -> str:
    """Transcrit un fichier audio en texte."""
    model = get_model()

    with tempfile.NamedTemporaryFile(suffix=f".{extension}", delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name

    try:
        result = model.transcribe(tmp_path, language=None)  # auto-detect fr/en
        return result["text"].strip()
    finally:
        os.unlink(tmp_path)