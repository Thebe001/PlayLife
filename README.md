# ⚡ LifeForge OS — Your Personal Life Operating System

> Transform your daily life into a measurable long-term strategy game.

![Version](https://img.shields.io/badge/version-0.3.0-blue)
![Stack](https://img.shields.io/badge/stack-Next.js%2014%20%2B%20FastAPI-blueviolet)
![LLM](https://img.shields.io/badge/LLM-Ollama%20%2B%20Whisper-green)
![License](https://img.shields.io/badge/license-Personal-gray)

---

## 🎯 What is LifeForge OS?

LifeForge OS is a **personal life operating system** — a local web application that turns your daily routine into a long-term strategy game. Define your life pillars, track habits and objectives, earn XP, unlock rewards, and get AI-powered insights — all running **100% locally**, no cloud required.

---

## ✨ Features

| Module | Description |
|--------|-------------|
| 🏛️ **Life Pillars** | Configurable weighted pillars (Career, Health, Finance...) |
| ⚡ **Scoring Engine** | Real-time weighted global score calculation |
| 📅 **Daily Planning** | Habit checklist with good/bad habit tracking |
| 🎯 **Objectives** | Goals with sub-tasks and auto-calculated completion % |
| 🏆 **Gamification** | XP, levels (Bronze→Master), badges, streaks, rewards |
| 🎁 **Reward Store** | Personal rewards with cooldown and one-shot mechanics |
| 🤖 **AI Assistant** | Voice commands via Whisper STT + Ollama LLM (local) |
| 📓 **Journal** | Daily entries with mood, energy, tags, highlights |
| 📊 **Reviews** | Auto-generated weekly/monthly reviews |
| 📈 **Stats** | GitHub-style heatmap, progression charts, KPIs |
| 💾 **Backup** | Full JSON export of all data |

---

## 🛠️ Tech Stack

**Frontend**
- Next.js 14 (App Router)
- Tailwind CSS + shadcn/ui
- Recharts (radar, line charts)
- Zustand (global state)

**Backend**
- FastAPI (Python 3.13)
- SQLAlchemy + SQLite
- Pydantic v2

**AI Layer**
- OpenAI Whisper (local STT)
- Ollama + Mistral-7B (local LLM)
- Rule-based fallback parser

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.com/download)
- ffmpeg

### Installation
```bash
# Clone
git clone https://github.com/ahmedfrikha/lifeforge-os
cd lifeforge-os

# Backend
cd backend
pip install -r requirements.txt
python seed_badges.py
uvicorn main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev

# Ollama (new terminal)
ollama pull mistral
ollama serve
```

Open **http://localhost:3000**

---

## 📁 Project Structure
```
lifeforge-os/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   └── main.py
└── frontend/
    ├── app/
    │   └── dashboard/    # All pages
    └── components/       # Reusable components
```

---

## 🎮 Daily Workflow

1. **Morning** → Open Planning → check today's habits
2. **During day** → Use voice assistant to log actions
3. **Evening** → Write journal entry + check score
4. **Sunday** → Generate weekly review
5. **Anytime** → Track objectives progress

---

## 📊 Scoring System
```
Score Pilier = Points earned / Points max × 100
Score Global = Σ (Score pilier × Poids pilier)

Bronze  ≥ 60% | Argent ≥ 75% | Or ≥ 90% | Diamant ≥ 98%
```

---

## 🤖 AI Voice Commands
```
"Quel est mon score aujourd'hui ?"     → get_score
"Marque sport comme fait"              → check_habit
"Crée un objectif finir le projet"     → create_objective
"Génère ma review de la semaine"       → generate_review
"Liste mes objectifs en cours"         → get_objectives
```

---

## 👤 Author

**Ahmed FRIKHA** — Built for daily personal use + portfolio showcase

> *"Most people use 10 different apps to manage their life. LifeForge OS is one app — your app — built exactly how you want it, running locally, talking to you by voice, and turning your days into measurable progress."*

---

## 📌 Portfolio Stack Line

> Built a full-stack personal productivity OS with **Next.js 14**, **FastAPI**, **SQLAlchemy**, a custom **gamification engine** (XP/levels/badges/skill tree), a weighted **multi-pillar scoring system**, and an **AI voice assistant** powered by local **Whisper STT** and **Ollama LLM** — running entirely offline on localhost with automated LLM-generated weekly reviews.