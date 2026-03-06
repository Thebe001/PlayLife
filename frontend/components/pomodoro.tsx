"use client"

import { useState, useEffect, useRef, useCallback } from "react"
import { API } from "@/lib/api"

interface Habit {
  id:      number
  name:    string
  type:    string
  points:  number
  checked: boolean
  pillar_id?: number
}

interface PomodoroProps {
  habits:         Habit[]
  onHabitCheck:   (id: number) => void
  activePillarId?: number   // pilier actif pour logger le focus
}

const MODES = {
  focus:       { label: "Focus",        duration: 25 * 60, color: "#3b82f6" },
  short_break: { label: "Pause courte", duration:  5 * 60, color: "#22c55e" },
  long_break:  { label: "Pause longue", duration: 15 * 60, color: "#a78bfa" },
}

type Mode = keyof typeof MODES

// ── Logger une session focus vers le backend ──────────────────────────────────
async function logFocusSession(params: {
  duration_min: number
  pillar_id?:   number | null
  habit_id?:    number | null
  mode:         string
  completed:    boolean
}): Promise<{ xp_earned?: number } | null> {
  try {
    const res = await fetch(`${API}/focus/log`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(params),
    })
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export default function Pomodoro({ habits, onHabitCheck, activePillarId }: PomodoroProps) {
  const [mode,        setMode]        = useState<Mode>("focus")
  const [timeLeft,    setTimeLeft]    = useState(MODES.focus.duration)
  const [running,     setRunning]     = useState(false)
  const [sessions,    setSessions]    = useState(0)
  const [linkedHabit, setLinkedHabit] = useState<number | null>(null)
  const [showDone,    setShowDone]    = useState(false)
  const [expanded,    setExpanded]    = useState(false)
  const [xpToast,     setXpToast]     = useState<number | null>(null)
  const [selectedPillar, setSelectedPillar] = useState<number | null>(activePillarId ?? null)

  const intervalRef   = useRef<NodeJS.Timeout | null>(null)
  const sessionStart  = useRef<Date | null>(null)

  const stop = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current)
    setRunning(false)
  }, [])

  // ── Session terminée ───────────────────────────────────────────────────────
  const onFinish = useCallback(async () => {
    stop()

    if (mode === "focus") {
      const plannedDuration = MODES.focus.duration / 60   // 25 min
      const linkedHabitPillar = linkedHabit
        ? habits.find(h => h.id === linkedHabit)?.pillar_id ?? null
        : null

      // Logger en DB
      const result = await logFocusSession({
        duration_min: plannedDuration,
        pillar_id:    selectedPillar ?? linkedHabitPillar,
        habit_id:     linkedHabit,
        mode:         "pomodoro",
        completed:    true,
      })

      setSessions((s) => s + 1)
      setShowDone(true)

      if (result?.xp_earned && result.xp_earned > 0) {
        setXpToast(result.xp_earned)
        setTimeout(() => setXpToast(null), 3000)
      }

      // Auto-passer en pause
      const next: Mode = sessions > 0 && (sessions + 1) % 4 === 0 ? "long_break" : "short_break"
      setTimeout(() => {
        setMode(next)
        setTimeLeft(MODES[next].duration)
        setShowDone(false)
      }, 4000)
    }
  }, [mode, sessions, stop, linkedHabit, selectedPillar, habits])

  // ── Timer ──────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (running) {
      if (!sessionStart.current) sessionStart.current = new Date()
      intervalRef.current = setInterval(() => {
        setTimeLeft((t) => {
          if (t <= 1) {
            onFinish()
            return 0
          }
          return t - 1
        })
      }, 1000)
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [running, onFinish])

  // ── Interruption : logger quand même si > 5 min ────────────────────────────
  const handleInterrupt = useCallback(async () => {
    if (running && mode === "focus") {
      const elapsed = MODES.focus.duration - timeLeft
      const elapsedMin = Math.floor(elapsed / 60)
      if (elapsedMin >= 5) {
        const linkedHabitPillar = linkedHabit
          ? habits.find(h => h.id === linkedHabit)?.pillar_id ?? null
          : null
        await logFocusSession({
          duration_min: elapsedMin,
          pillar_id:    selectedPillar ?? linkedHabitPillar,
          habit_id:     linkedHabit,
          mode:         "pomodoro",
          completed:    false,
        })
      }
    }
    stop()
  }, [running, mode, timeLeft, stop, linkedHabit, selectedPillar, habits])

  const switchMode = (m: Mode) => {
    if (running) handleInterrupt()
    setMode(m)
    setTimeLeft(MODES[m].duration)
    setShowDone(false)
    sessionStart.current = null
  }

  const reset = () => {
    if (running) handleInterrupt()
    setTimeLeft(MODES[mode].duration)
    setShowDone(false)
    sessionStart.current = null
  }

  const handleCheckLinked = () => {
    if (linkedHabit !== null) {
      onHabitCheck(linkedHabit)
      setShowDone(false)
    }
  }

  const minutes = Math.floor(timeLeft / 60).toString().padStart(2, "0")
  const seconds = (timeLeft % 60).toString().padStart(2, "0")
  const total   = MODES[mode].duration
  const pct     = ((total - timeLeft) / total) * 100
  const color   = MODES[mode].color
  const radius  = 54
  const circ    = 2 * Math.PI * radius
  const dash    = circ - (pct / 100) * circ

  const uncheckedHabits = habits.filter((h) => !h.checked && h.type === "good")

  // Piliers uniques depuis les habitudes
  const pillarOptions = Array.from(
    new Map(
      habits
        .filter(h => h.pillar_id)
        .map(h => [h.pillar_id, h.pillar_id])
    ).values()
  )

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">

      {/* XP Toast */}
      {xpToast !== null && (
        <div className="absolute top-4 right-4 z-50 bg-blue-600 text-white text-sm font-bold px-4 py-2 rounded-xl shadow-lg animate-bounce pointer-events-none">
          +{xpToast} XP 🎯
        </div>
      )}

      {/* Header — toujours visible */}
      <button
        onClick={() => setExpanded((e) => !e)}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-gray-800/50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-lg">⏱️</span>
          <div className="text-left">
            <p className="text-sm font-semibold text-white">Pomodoro</p>
            <p className="text-xs text-gray-500">
              {running
                ? `${minutes}:${seconds} — ${MODES[mode].label}`
                : `${sessions} session${sessions > 1 ? "s" : ""} aujourd'hui`}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {running && (
            <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: color }} />
          )}
          <span className="text-gray-600 text-sm">{expanded ? "▲" : "▼"}</span>
        </div>
      </button>

      {/* Corps expandable */}
      {expanded && (
        <div className="px-5 pb-5 space-y-5 border-t border-gray-800 pt-5">

          {/* Mode tabs */}
          <div className="flex gap-2">
            {(Object.keys(MODES) as Mode[]).map((m) => (
              <button
                key={m}
                onClick={() => switchMode(m)}
                className={`flex-1 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  mode === m ? "text-white" : "bg-gray-800 text-gray-500 hover:text-gray-300"
                }`}
                style={mode === m ? { backgroundColor: color } : {}}
              >
                {MODES[m].label}
              </button>
            ))}
          </div>

          {/* Sélecteur pilier (pour logger le focus) */}
          {mode === "focus" && (
            <div className="space-y-1.5">
              <p className="text-xs text-gray-500 uppercase tracking-wider">Pilier du focus</p>
              <select
                value={selectedPillar ?? ""}
                onChange={(e) => setSelectedPillar(e.target.value ? Number(e.target.value) : null)}
                className="w-full bg-gray-800 rounded-lg px-3 py-2 text-sm text-white border border-gray-700 focus:border-blue-500 outline-none"
              >
                <option value="">Aucun pilier sélectionné</option>
                {habits
                  .filter((h, i, arr) => h.pillar_id && arr.findIndex(x => x.pillar_id === h.pillar_id) === i)
                  .map((h) => (
                    <option key={h.pillar_id} value={h.pillar_id}>Pilier #{h.pillar_id}</option>
                  ))
                }
              </select>
            </div>
          )}

          {/* Timer circulaire */}
          <div className="flex flex-col items-center gap-4">
            <div className="relative w-36 h-36">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r={radius} fill="none" stroke="#1f2937" strokeWidth="8" />
                <circle
                  cx="60" cy="60" r={radius}
                  fill="none"
                  stroke={color}
                  strokeWidth="8"
                  strokeLinecap="round"
                  strokeDasharray={circ}
                  strokeDashoffset={dash}
                  style={{ transition: "stroke-dashoffset 1s linear" }}
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold text-white font-mono">{minutes}:{seconds}</span>
                <span className="text-xs text-gray-500 mt-0.5">{MODES[mode].label}</span>
              </div>
            </div>

            {/* Contrôles */}
            <div className="flex gap-3">
              <button
                onClick={reset}
                className="px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-gray-400 text-sm transition-colors"
              >
                ↺
              </button>
              <button
                onClick={() => {
                  if (running) {
                    handleInterrupt()
                  } else {
                    setRunning(true)
                  }
                }}
                className="px-8 py-2 rounded-lg text-white text-sm font-semibold transition-all hover:scale-105"
                style={{ backgroundColor: color }}
              >
                {running ? "⏸ Pause" : timeLeft === MODES[mode].duration ? "▶ Démarrer" : "▶ Reprendre"}
              </button>
            </div>

            {/* Sessions dots */}
            {sessions > 0 && (
              <div className="flex gap-1.5 items-center">
                {Array.from({ length: Math.min(sessions, 8) }).map((_, i) => (
                  <div
                    key={i}
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: i % 4 === 3 ? "#f59e0b" : "#3b82f6" }}
                  />
                ))}
                <span className="text-xs text-gray-600 ml-1">{sessions * 25} min focus</span>
              </div>
            )}
          </div>

          {/* Lier à une habitude */}
          <div className="space-y-2">
            <p className="text-xs text-gray-500 uppercase tracking-wider">Lier à une habitude</p>
            {uncheckedHabits.length === 0 ? (
              <p className="text-xs text-gray-700">Toutes les habitudes sont cochées 🎉</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {uncheckedHabits.slice(0, 5).map((h) => (
                  <button
                    key={h.id}
                    onClick={() => setLinkedHabit(linkedHabit === h.id ? null : h.id)}
                    className={`px-3 py-1.5 rounded-lg text-xs transition-colors ${
                      linkedHabit === h.id
                        ? "text-white"
                        : "bg-gray-800 text-gray-400 hover:text-white"
                    }`}
                    style={linkedHabit === h.id ? { backgroundColor: color } : {}}
                  >
                    {h.name}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Notification fin de session */}
          {showDone && (
            <div
              className="rounded-xl p-4 space-y-3 border"
              style={{ backgroundColor: `${color}15`, borderColor: `${color}40` }}
            >
              <p className="text-sm font-semibold" style={{ color }}>
                🎉 Session terminée ! +{sessions * 25} XP focus
              </p>
              {linkedHabit !== null ? (
                <button
                  onClick={handleCheckLinked}
                  className="w-full py-2 rounded-lg text-white text-sm font-medium transition-colors"
                  style={{ backgroundColor: color }}
                >
                  ✓ Cocher &quot;{habits.find((h) => h.id === linkedHabit)?.name}&quot;
                </button>
              ) : (
                <p className="text-xs text-gray-500">Lie une habitude pour la cocher automatiquement.</p>
              )}
              <button
                onClick={() => setShowDone(false)}
                className="text-xs text-gray-600 hover:text-gray-400 transition-colors"
              >
                Ignorer
              </button>
            </div>
          )}

        </div>
      )}
    </div>
  )
}