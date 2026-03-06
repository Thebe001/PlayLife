import httpx
from sqlalchemy.orm import Session
from app.models.review import Review
from app.config import settings


async def generate_review_content(stats: dict) -> str:
    """Génère le contenu de la review via Ollama, avec fallback statique."""

    review_type = stats["type"]
    period_label = "semaine" if review_type == "weekly" else "mois"

    pillar_lines = "\n".join(
        f"  - {p['name']}: {p['avg']}% de moyenne"
        for p in stats.get("pillar_avgs", [])
    )
    highlights_lines = "\n".join(
        f"  - {h}" for h in stats.get("highlights", [])
    ) or "  (aucun highlight noté)"

    mood_line = f"{stats['avg_mood']}/5" if stats.get("avg_mood") else "non renseigné"

    prompt = f"""Tu es l'assistant LifeForge OS. Génère une review de {period_label} structurée, motivante et honnête.

DONNÉES DE LA PÉRIODE ({stats['period_start']} → {stats['period_end']}) :
- Score moyen global : {stats['avg_score']}%
- Meilleur jour : {stats['best_score']}%
- Pire jour : {stats['worst_score']}%
- Jours trackés : {stats['total_days']}
- Habitudes cochées : {stats['total_habit_checks']}
- Humeur moyenne : {mood_line}

SCORES PAR PILIER :
{pillar_lines or "  (pas de données par pilier)"}

HIGHLIGHTS DU JOURNAL :
{highlights_lines}

Génère une review en français avec ces sections :
1. 📊 Bilan chiffré (2-3 phrases sur les stats clés)
2. 💪 Points forts (ce qui a bien marché)
3. ⚠️ Points à améliorer (soyons honnêtes)
4. 🎯 Focus de la prochaine {period_label} (1-2 actions concrètes)
5. 💬 Message motivant personnel (1 phrase)

Sois concis, direct, et parle à la première personne (tu/vous). Maximum 300 mots."""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(settings.OLLAMA_URL, json={
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            })
            text = res.json().get("response", "").strip()
            if text:
                return text
    except Exception as e:
        print(f"⚠️ Ollama indisponible pour review: {e} — fallback statique")

    # ── Fallback : review générée sans LLM ─────────────
    return _static_review(stats)


def _static_review(stats: dict) -> str:
    """Review de fallback générée en pur Python si Ollama est down."""
    period_label = "semaine" if stats["type"] == "weekly" else "mois"
    score = stats["avg_score"]
    checks = stats["total_habit_checks"]
    days = stats["total_days"]

    if score >= 90:
        perf = "Semaine exceptionnelle"
        color = "🌟"
    elif score >= 75:
        perf = "Très bonne semaine"
        color = "💪"
    elif score >= 60:
        perf = "Semaine correcte"
        color = "✅"
    else:
        perf = "Semaine difficile"
        color = "⚠️"

    pillar_lines = "\n".join(
        f"  • {p['name']} : {p['avg']}%"
        for p in stats.get("pillar_avgs", [])
    ) or "  • Aucune donnée par pilier"

    mood_line = f"{stats['avg_mood']}/5" if stats.get("avg_mood") else "non renseigné"

    return f"""{color} {perf} — {stats['period_start']} → {stats['period_end']}

📊 BILAN CHIFFRÉ
Score moyen : {score}% | Meilleur jour : {stats['best_score']}% | Pire jour : {stats['worst_score']}%
{days} jour(s) tracké(s), {checks} habitude(s) cochée(s). Humeur moyenne : {mood_line}.

📈 SCORES PAR PILIER
{pillar_lines}

💪 POINTS FORTS
{"Tu as maintenu une belle régularité cette " + period_label + "." if score >= 70 else "Tu as au moins commencé à tracker — c'est l'essentiel."}

⚠️ POINTS À AMÉLIORER
{"Continue sur cette lancée et vise les 90%." if score >= 75 else "Concentre-toi sur 1-2 habitudes clés plutôt que tout faire."}

🎯 FOCUS DE LA PROCHAINE {period_label.upper()}
→ Maintenir le streak et améliorer le pilier le plus faible.
→ Écrire dans le journal chaque soir pour mieux tracker l'humeur.

💬 "{perf} — chaque jour tracké est un jour gagné." """


def get_reviews(db: Session):
    return db.query(Review).order_by(Review.id.desc()).all()


def delete_review(db: Session, review_id: int) -> bool:
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        return False
    db.delete(review)
    db.commit()
    return True