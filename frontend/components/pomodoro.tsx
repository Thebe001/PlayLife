"use client"

import { useState, useEffect, useRef, useCallback } from "react"

interface Habit {
  id: number
  name: string
  type: string
  points: number
  checked: boolean
}

interface PomodoroProps {
  habits: Habit[]
  onHabitCheck: (id: number) => void
}

const MODES = {
  focus:       { label: "Focus",        duration: 25 * 60, color: "#3b82f6" },
  short_break: { label: "Pause courte", duration:  5 * 60, color: "#22c55e" },
  long_break:  { label: "Pause longue", duration: 15 * 60, color: "#a78bfa" },
}

type Mode = keyof typeof MODES

export default function Pomodoro({ habits, onHabitCheck }: PomodoroProps) {
  const [mode, setMode]               = useState<Mode>("focus")
  const [timeLeft, setTimeLeft]       = useState(MODES.focus.duration)
  const [running, setRunning]         = useState(false)
  const [sessions, setSessions]       = useState(0)
  const [linkedHabit, setLinkedHabit] = useState<number | null>(null)
  const [showDone, setShowDone]       = useState(false)
  const [expanded, setExpanded]       = useState(false)
  const intervalRef                   = useRef<NodeJS.Timeout | null>(null)

  const stop = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current)
    setRunning(false)
  }, [])

  const onFinish = useCallback(() => {
    stop()
    if (mode === "focus") {
      setSessions((s) => s + 1)
      setShowDone(true)
    }
    // Auto-passer en pause après focus
    if (mode === "focus") {
      const next: Mode = sessions > 0 && (sessions + 1) % 4 === 0 ? "long_break" : "short_break"
      setTimeout(() => {
        setMode(next)
        setTimeLeft(MODES[next].duration)
        setShowDone(false)
      }, 4000)
    }
  }, [mode, sessions, stop])

  useEffect(() => {
    if (running) {
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

  const switchMode = (m: Mode) => {
    stop()
    setMode(m)
    setTimeLeft(MODES[m].duration)
    setShowDone(false)
  }

  const reset = () => {
    stop()
    setTimeLeft(MODES[mode].duration)
    setShowDone(false)
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

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">

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
              {running ? `${minutes}:${seconds} — ${MODES[mode].label}` : `${sessions} session${sessions > 1 ? "s" : ""} aujourd'hui`}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {running && (
            <span
              className="w-2 h-2 rounded-full animate-pulse"
              style={{ backgroundColor: color }}
            />
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
                <span className="text-3xl font-bold text-white font-mono">
                  {minutes}:{seconds}
                </span>
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
                onClick={() => setRunning((r) => !r)}
                className="px-8 py-2 rounded-lg text-white text-sm font-semibold transition-all hover:scale-105"
                style={{ backgroundColor: color }}
              >
                {running ? "⏸ Pause" : timeLeft === MODES[mode].duration ? "▶ Démarrer" : "▶ Reprendre"}
              </button>
            </div>

            {/* Sessions dots */}
            {sessions > 0 && (
              <div className="flex gap-1.5">
                {Array.from({ length: Math.min(sessions, 8) }).map((_, i) => (
                  <div
                    key={i}
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: i % 4 === 3 ? "#f59e0b" : "#3b82f6" }}
                  />
                ))}
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
              className="rounded-xl p-4 space-y-3 border animate-pulse"
              style={{ backgroundColor: `${color}15`, borderColor: `${color}40` }}
            >
              <p className="text-sm font-semibold" style={{ color }}>
                🎉 Session terminée ! +{sessions * 10} XP
              </p>
              {linkedHabit !== null ? (
                <button
                  onClick={handleCheckLinked}
                  className="w-full py-2 rounded-lg text-white text-sm font-medium transition-colors"
                  style={{ backgroundColor: color }}
                >
                  ✓ Cocher "{habits.find((h) => h.id === linkedHabit)?.name}"
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