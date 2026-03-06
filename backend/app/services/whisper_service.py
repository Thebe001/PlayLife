import whisper
import tempfile
import os

_model = None


def get_model():
    """Charge le modèle Whisper à la première utilisation (lazy loading)."""
    global _model
    if _model is None:
        print("🎤 Chargement Whisper small (première utilisation)...")
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
        result = model.transcribe(tmp_path, language=None)
        return result["text"].strip()
    finally:
        os.unlink(tmp_path)