"use client"

import { useEffect, useState } from "react"
import Pomodoro from "@/components/pomodoro"
import NotificationManager from "@/components/notifications"
import {
  API,
  getHabitsToday,
  getPillars,
  checkHabit,
  uncheckHabit,
  createHabit,
  deleteHabit,
  computeDailyScores,
  computeGlobalScore,
  getTodaySummary,
  getTemplates,
  createTemplate,
} from "@/lib/api"
import { getScoreColor, getScoreLabel } from "@/lib/score-utils"

// ── Types ──────────────────────────────────────────────────────────────────

interface Habit {
  id:             number
  name:           string
  type:           "good" | "bad"
  points:         number
  frequency:      string
  pillar_id:      number
  checked:        boolean
  current_streak: number
  best_streak:    number
}

interface Pillar {
  id:    number
  name:  string
  icon:  string
  color: string
}

interface NewHabitForm {
  name:      string
  type:      "good" | "bad"
  points:    number
  frequency: string
  pillar_id: number
}

interface Template {
  id:          number
  day_of_week: number
  name:        string
}

interface XPToast {
  id:     number
  points: number
  streak: number
}

const DAY_LABELS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

// ── Page ───────────────────────────────────────────────────────────────────

export default function Planning() {
  const [tab, setTab] = useState<"today" | "templates">("today")

  return (
    <div className="p-8 space-y-6 max-w-3xl">
      <div className="flex gap-2">
        <button
          onClick={() => setTab("today")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            tab === "today" ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-400 hover:text-white"
          }`}
        >
          📅 Aujourd&apos;hui
        </button>
        <button
          onClick={() => setTab("templates")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            tab === "templates" ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-400 hover:text-white"
          }`}
        >
          🗓️ Templates hebdo
        </button>
      </div>

      {tab === "today" ? <TodayView /> : <TemplatesView />}
    </div>
  )
}

// ── Vue du jour ────────────────────────────────────────────────────────────

function TodayView() {
  const [habits,    setHabits]    = useState<Habit[]>([])
  const [pillars,   setPillars]   = useState<Pillar[]>([])
  const [score,     setScore]     = useState(0)
  const [loading,   setLoading]   = useState(true)
  const [showForm,  setShowForm]  = useState(false)
  const [toasts,    setToasts]    = useState<XPToast[]>([])
  const [form, setForm] = useState<NewHabitForm>({
    name: "", type: "good", points: 20, frequency: "daily", pillar_id: 1,
  })

  // ── Fetch ────────────────────────────────────────────────────────────────

  const fetchAll = async () => {
    const [habitsData, pillarsData] = await Promise.all([
      getHabitsToday() as Promise<Habit[]>,
      getPillars()     as Promise<Pillar[]>,
    ])
    setHabits(habitsData)
    setPillars(pillarsData)
    setLoading(false)
  }

  const refreshScore = async () => {
    await computeDailyScores()
    await computeGlobalScore()
    const data = await getTodaySummary() as { global_score: number }
    setScore(data.global_score)
  }

  useEffect(() => {
    fetchAll()
    refreshScore()
  }, [])

  // ── Toast XP ─────────────────────────────────────────────────────────────

  const showXPToast = (points: number, streak: number) => {
    const id = Date.now()
    setToasts((prev) => [...prev, { id, points, streak }])
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3000)
  }

  // ── Actions ──────────────────────────────────────────────────────────────

  const toggleHabit = async (habit: Habit) => {
    // Optimistic update
    setHabits((prev) =>
      prev.map((h) => (h.id === habit.id ? { ...h, checked: !h.checked } : h))
    )

    if (habit.checked) {
      await uncheckHabit(habit.id)
    } else {
      const res = await checkHabit(habit.id) as {
        points_earned?: number
        streak?: { current_streak: number; best_streak: number }
      }
      if (res?.points_earned && res.points_earned > 0) {
        showXPToast(res.points_earned, res.streak?.current_streak ?? 0)
      }
      // Mettre à jour le streak dans le state local
      if (res?.streak) {
        setHabits((prev) =>
          prev.map((h) =>
            h.id === habit.id
              ? { ...h, current_streak: res.streak!.current_streak, best_streak: res.streak!.best_streak }
              : h
          )
        )
      }
    }

    await refreshScore()
  }

  const handleCreateHabit = async () => {
    if (!form.name.trim()) return
    await createHabit({ ...form, pillar_id: Number(form.pillar_id) })
    setShowForm(false)
    setForm({ name: "", type: "good", points: 20, frequency: "daily", pillar_id: pillars[0]?.id ?? 1 })
    await fetchAll()
    await refreshScore()
  }

  const handleDeleteHabit = async (id: number) => {
    await deleteHabit(id)
    await fetchAll()
  }

  // ── Computed ─────────────────────────────────────────────────────────────

  const goodHabits  = habits.filter((h) => h.type === "good")
  const badHabits   = habits.filter((h) => h.type === "bad")
  const checkedCount = habits.filter((h) => h.checked).length

  if (loading) {
    return <div className="text-gray-500 text-sm animate-pulse">Chargement...</div>
  }

  return (
    <div className="space-y-6">

      {/* XP Toasts */}
      <div className="fixed top-6 right-6 z-50 flex flex-col gap-2 pointer-events-none">
        {toasts.map((t) => (
          <div
            key={t.id}
            className="bg-gray-900 border border-purple-500/50 rounded-xl px-4 py-3 shadow-lg animate-bounce"
          >
            <p className="text-purple-400 font-bold text-sm">+{t.points} XP ⚡</p>
            {t.streak > 1 && (
              <p className="text-orange-400 text-xs mt-0.5">🔥 {t.streak} jours de suite !</p>
            )}
          </div>
        ))}
      </div>

      {/* Header + score */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">📅 Planning</h2>
          <p className="text-gray-500 text-sm mt-1">
            {new Date().toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long" })}
          </p>
        </div>
        <div className="text-right">
          <p className="text-3xl font-bold" style={{ color: getScoreColor(score) }}>{score}%</p>
          <p className="text-xs" style={{ color: getScoreColor(score) }}>{getScoreLabel(score)}</p>
          <p className="text-xs text-gray-500 mt-0.5">{checkedCount}/{habits.length} habitudes</p>
        </div>
      </div>

      {/* Pomodoro */}
      <Pomodoro habits={habits} onHabitCheck={(id) => {
        const habit = habits.find(h => h.id === id)
        if (habit) toggleHabit(habit)
      }} />

      {/* Notifications */}
      <NotificationManager />

      {/* Bonnes habitudes */}
      {goodHabits.length > 0 && (
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">✅ Bonnes habitudes</h3>
          <div className="space-y-2">
            {goodHabits.map((habit) => {
              const pillar = pillars.find((p) => p.id === habit.pillar_id)
              return (
                <HabitRow
                  key={habit.id}
                  habit={habit}
                  pillar={pillar}
                  onToggle={() => toggleHabit(habit)}
                  onDelete={() => handleDeleteHabit(habit.id)}
                />
              )
            })}
          </div>
        </div>
      )}

      {/* Mauvaises habitudes */}
      {badHabits.length > 0 && (
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">⚠️ Habitudes à éviter</h3>
          <div className="space-y-2">
            {badHabits.map((habit) => {
              const pillar = pillars.find((p) => p.id === habit.pillar_id)
              return (
                <HabitRow
                  key={habit.id}
                  habit={habit}
                  pillar={pillar}
                  onToggle={() => toggleHabit(habit)}
                  onDelete={() => handleDeleteHabit(habit.id)}
                />
              )
            })}
          </div>
        </div>
      )}

      {/* Ajouter habitude */}
      <div>
        {!showForm ? (
          <button
            onClick={() => setShowForm(true)}
            className="w-full py-3 rounded-xl border border-dashed border-gray-700 text-gray-500 hover:text-white hover:border-gray-500 text-sm transition-colors"
          >
            + Ajouter une habitude
          </button>
        ) : (
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 space-y-4">
            <h3 className="text-sm font-semibold text-white">Nouvelle habitude</h3>
            <input
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="Nom de l'habitude"
              className="w-full bg-gray-800 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 border border-gray-700 focus:border-blue-500 outline-none"
            />
            <div className="grid grid-cols-2 gap-3">
              <select
                value={form.type}
                onChange={(e) => setForm({ ...form, type: e.target.value as "good" | "bad" })}
                className="bg-gray-800 rounded-lg px-3 py-2 text-sm text-white border border-gray-700"
              >
                <option value="good">✅ Bonne</option>
                <option value="bad">⚠️ À éviter</option>
              </select>
              <select
                value={form.pillar_id}
                onChange={(e) => setForm({ ...form, pillar_id: Number(e.target.value) })}
                className="bg-gray-800 rounded-lg px-3 py-2 text-sm text-white border border-gray-700"
              >
                {pillars.map((p) => (
                  <option key={p.id} value={p.id}>{p.icon} {p.name}</option>
                ))}
              </select>
              <select
                value={form.frequency}
                onChange={(e) => setForm({ ...form, frequency: e.target.value })}
                className="bg-gray-800 rounded-lg px-3 py-2 text-sm text-white border border-gray-700"
              >
                <option value="daily">Quotidien</option>
                <option value="weekly">Hebdomadaire</option>
              </select>
              <input
                type="number"
                value={form.points}
                onChange={(e) => setForm({ ...form, points: Number(e.target.value) })}
                min={1} max={100}
                className="bg-gray-800 rounded-lg px-3 py-2 text-sm text-white border border-gray-700"
                placeholder="Points"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleCreateHabit}
                className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white text-sm font-medium transition-colors"
              >
                Créer
              </button>
              <button
                onClick={() => setShowForm(false)}
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-gray-400 text-sm transition-colors"
              >
                Annuler
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// ── HabitRow ───────────────────────────────────────────────────────────────

interface HabitRowProps {
  habit:    Habit
  pillar:   Pillar | undefined
  onToggle: () => void
  onDelete: () => void
}

function HabitRow({ habit, pillar, onToggle, onDelete }: HabitRowProps) {
  const isGood = habit.type === "good"

  return (
    <div className="flex items-center justify-between p-3 rounded-lg bg-gray-800/50 hover:bg-gray-800 transition-colors">
      <div className="flex items-center gap-3 flex-1 min-w-0">

        {/* Checkbox */}
        <button
          onClick={onToggle}
          className={`shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
            habit.checked
              ? isGood
                ? "bg-green-500 border-green-500"
                : "bg-red-500 border-red-500"
              : isGood
              ? "border-gray-600 hover:border-green-500"
              : "border-gray-600 hover:border-red-500"
          }`}
        >
          {habit.checked && (
            <span className="text-white text-xs">{isGood ? "✓" : "✗"}</span>
          )}
        </button>

        {/* Infos */}
        <div className="min-w-0">
          <p className={`text-sm font-medium truncate ${habit.checked ? "line-through text-gray-500" : "text-white"}`}>
            {habit.name}
          </p>
          <div className="flex items-center gap-2 mt-0.5 flex-wrap">
            <span className="text-xs text-gray-600">
              {pillar?.icon} {pillar?.name} · {isGood ? "+" : "-"}{habit.points} pts
            </span>

            {/* Streak badge */}
            {habit.current_streak > 0 && (
              <span className="inline-flex items-center gap-1 text-xs bg-orange-500/10 text-orange-400 px-1.5 py-0.5 rounded-full">
                🔥 {habit.current_streak}j
                {habit.best_streak > habit.current_streak && (
                  <span className="text-gray-500">/ record {habit.best_streak}j</span>
                )}
              </span>
            )}

            {/* Record égalé */}
            {habit.current_streak > 0 && habit.current_streak === habit.best_streak && (
              <span className="text-xs text-yellow-400">🏆 record</span>
            )}
          </div>
        </div>
      </div>

      {/* Supprimer */}
      <button
        onClick={onDelete}
        className="shrink-0 text-gray-700 hover:text-red-400 text-xs transition-colors ml-2"
      >
        ✕
      </button>
    </div>
  )
}

// ── Templates hebdo ────────────────────────────────────────────────────────

function TemplatesView() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading,   setLoading]   = useState(true)
  const [form, setForm] = useState({ day_of_week: 0, name: "" })

  const fetchTemplates = async () => {
    const data = await getTemplates() as Template[]
    setTemplates(data)
    setLoading(false)
  }

  useEffect(() => { fetchTemplates() }, [])

  const handleCreate = async () => {
    if (!form.name.trim()) return
    await createTemplate(form)
    setForm({ day_of_week: 0, name: "" })
    await fetchTemplates()
  }

  if (loading) return <div className="text-gray-500 text-sm animate-pulse">Chargement...</div>

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-bold text-white">🗓️ Templates hebdo</h2>
        <p className="text-gray-500 text-sm mt-1">Planifie tes journées type</p>
      </div>

      {/* Formulaire */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 flex gap-3">
        <select
          value={form.day_of_week}
          onChange={(e) => setForm({ ...form, day_of_week: Number(e.target.value) })}
          className="bg-gray-800 rounded-lg px-3 py-2 text-sm text-white border border-gray-700"
        >
          {DAY_LABELS.map((d, i) => (
            <option key={i} value={i}>{d}</option>
          ))}
        </select>
        <input
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          placeholder="Nom du template"
          className="flex-1 bg-gray-800 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 border border-gray-700 focus:border-blue-500 outline-none"
        />
        <button
          onClick={handleCreate}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white text-sm font-medium transition-colors"
        >
          Ajouter
        </button>
      </div>

      {/* Liste */}
      {templates.length === 0 ? (
        <p className="text-gray-600 text-sm text-center py-8">Aucun template — crée-en un ci-dessus.</p>
      ) : (
        <div className="space-y-2">
          {templates.map((t) => (
            <div key={t.id} className="bg-gray-900 rounded-xl border border-gray-800 p-4 flex items-center justify-between">
              <div>
                <span className="text-xs text-gray-500 uppercase tracking-wider">{DAY_LABELS[t.day_of_week]}</span>
                <p className="text-sm text-white font-medium mt-0.5">{t.name}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}