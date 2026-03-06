import httpx
import json

from app.config import settings


def parse_intent_rules(text: str) -> dict:
    """Parser basé sur des règles — instantané, sans LLM."""
    text_lower = text.lower()

    if any(w in text_lower for w in ["score", "résultat", "points", "comment je"]):
        return {"action": "get_score", "params": {}, "response": "Je consulte ton score du jour... 📊"}

    if any(w in text_lower for w in ["marque", "coche", "fait", "complété", "terminé"]):
        words = text_lower.split()
        habit_words = []
        skip = {"marque", "coche", "comme", "fait", "complété", "l'habitude", "habitude", "terminé", "la"}
        for w in words:
            if w not in skip:
                habit_words.append(w)
        habit_name = " ".join(habit_words[:3]) if habit_words else "habitude"
        return {
            "action": "check_habit",
            "params": {"habit_name": habit_name},
            "response": f"Je coche '{habit_name}' ✓"
        }

    if any(w in text_lower for w in ["crée", "ajoute", "nouvel", "objectif"]):
        return {
            "action": "create_objective",
            "params": {"title": text, "pillar": "", "horizon": "monthly"},
            "response": "Objectif créé ✓"
        }

    if any(w in text_lower for w in ["objectifs", "liste", "en cours", "retard"]):
        return {"action": "get_objectives", "params": {}, "response": "Voici tes objectifs en cours 🎯"}

    if any(w in text_lower for w in ["journal", "note", "aujourd'hui j"]):
        return {"action": "add_journal", "params": {"content": text}, "response": "Note ajoutée au journal ✓"}

    if any(w in text_lower for w in ["review", "bilan", "semaine"]):
        return {"action": "generate_review", "params": {"type": "weekly"}, "response": "Génération de la review... 📊"}

    return {"action": "unknown", "params": {}, "response": "Commande non reconnue. Essaie : 'score', 'marque X comme fait', 'objectifs'"}


async def parse_intent(text: str) -> dict:
    """Parse l'intention — utilise LLM si disponible, sinon règles."""

    if not settings.USE_LLM:
        return parse_intent_rules(text)

    # Essayer Ollama avec timeout court
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(settings.OLLAMA_URL, json={
                "model": settings.OLLAMA_MODEL,
                "prompt": f"""Tu es l'assistant LifeForge OS. Analyse cette commande et retourne UNIQUEMENT un JSON.

Actions: get_score, check_habit(habit_name), create_objective(title,pillar,horizon), get_objectives, add_journal(content), generate_review(type), unknown

Format: {{"action":"...", "params":{{}}, "response":"message court en français"}}

Commande: "{text}"
JSON:""",
                "stream": False,
            })
            raw = res.json().get("response", "")
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(raw[start:end])
    except Exception as e:
        print(f"⚠️ Ollama timeout/erreur: {e} — fallback règles")

    # Fallback sur les règles
    return parse_intent_rules(text)


async def get_advice(context: str) -> str:
    """Conseil personnalisé — avec fallback."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(settings.OLLAMA_URL, json={
                "model": settings.OLLAMA_MODEL,
                "prompt": f"Donne un conseil motivant en 2 phrases max basé sur: {context}",
                "stream": False,
            })
            return res.json().get("response", "").strip()
    except Exception:
        pass

    # Fallbacks statiques
    import random
    tips = [
        "Continue comme ça ! Chaque habitude cochée te rapproche de tes objectifs. 💪",
        "La régularité bat l'intensité. Un petit effort chaque jour fait la différence. 🔥",
        "Tu construis quelque chose de grand. Reste focus sur tes piliers. ⚡",
        "Les meilleures journées commencent par les premières habitudes cochées. ✅",
    ]
    return random.choice(tips)