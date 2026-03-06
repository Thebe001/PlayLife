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

// ── Types ──────────────────────────────────────────────

interface Habit {
  id: number
  name: string
  type: "good" | "bad"
  points: number
  frequency: string
  pillar_id: number
  checked: boolean
}

interface Pillar {
  id: number
  name: string
  icon: string
  color: string
}

interface NewHabitForm {
  name: string
  type: "good" | "bad"
  points: number
  frequency: string
  pillar_id: number
}

interface Template {
  id: number
  day_of_week: number
  name: string
}

const DAY_LABELS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

// ── Page ───────────────────────────────────────────────

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

// ── Vue du jour ────────────────────────────────────────

function TodayView() {
  const [habits, setHabits] = useState<Habit[]>([])
  const [pillars, setPillars] = useState<Pillar[]>([])
  const [score, setScore] = useState(0)
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState<NewHabitForm>({
    name: "",
    type: "good",
    points: 20,
    frequency: "daily",
    pillar_id: 1,
  })

  const fetchAll = async () => {
    const [habitsData, pillarsData] = await Promise.all([
      getHabitsToday() as Promise<Habit[]>,
      getPillars() as Promise<Pillar[]>,
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

  const toggleHabit = async (habit: Habit) => {
    // Optimistic update
    setHabits((prev) =>
      prev.map((h) => (h.id === habit.id ? { ...h, checked: !h.checked } : h))
    )
    if (habit.checked) {
      await uncheckHabit(habit.id)
    } else {
      await checkHabit(habit.id)
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

  const goodHabits = habits.filter((h) => h.type === "good")
  const badHabits = habits.filter((h) => h.type === "bad")
  const checkedCount = habits.filter((h) => h.checked).length

  const scoreColor =
    score >= 90 ? "#f59e0b" :
    score >= 75 ? "#a78bfa" :
    score >= 60 ? "#3b82f6" : "#ef4444"

  if (loading) {
    return <div className="text-gray-500 text-sm animate-pulse">Chargement...</div>
  }

  return (
    <div className="space-y-6">

      {/* Header + score */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">📅 Planning</h2>
          <p className="text-gray-500 text-sm mt-1">
            {new Date().toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long" })}
          </p>
        </div>
        <div className="text-right">
          <p className="text-3xl font-bold" style={{ color: scoreColor }}>{score}%</p>
          <p className="text-xs text-gray-500">{checkedCount}/{habits.length} habitudes</p>
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
                <div
                  key={habit.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-gray-800/50 hover:bg-gray-800 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => toggleHabit(habit)}
                      className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
                        habit.checked
                          ? "bg-green-500 border-green-500"
                          : "border-gray-600 hover:border-green-500"
                      }`}
                    >
                      {habit.checked && <span className="text-white text-xs">✓</span>}
                    </button>
                    <div>
                      <p className={`text-sm font-medium ${habit.checked ? "line-through text-gray-500" : "text-white"}`}>
                        {habit.name}
                      </p>
                      <p className="text-xs text-gray-600">
                        {pillar?.icon} {pillar?.name} · +{habit.points} pts
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteHabit(habit.id)}
                    className="text-gray-700 hover:text-red-400 text-xs transition-colors"
                  >
                    ✕
                  </button>
                </div>
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
                <div
                  key={habit.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-gray-800/50 hover:bg-gray-800 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => toggleHabit(habit)}
                      className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
                        habit.checked
                          ? "bg-red-500 border-red-500"
                          : "border-gray-600 hover:border-red-500"
                      }`}
                    >
                      {habit.checked && <span className="text-white text-xs">✗</span>}
                    </button>
                    <div>
                      <p className={`text-sm font-medium ${habit.checked ? "line-through text-gray-500" : "text-white"}`}>
                        {habit.name}
                      </p>
                      <p className="text-xs text-gray-600">
                        {pillar?.icon} {pillar?.name} · -{habit.points} pts
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteHabit(habit.id)}
                    className="text-gray-700 hover:text-red-400 text-xs transition-colors"
                  >
                    ✕
                  </button>
                </div>
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
                min={1}
                max={100}
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

// ── Templates hebdo ────────────────────────────────────

function TemplatesView() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)
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