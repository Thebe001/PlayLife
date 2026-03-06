"use client"

import { useEffect, useState } from "react"
import Pomodoro from "@/components/pomodoro"
import { checkHabit } from "@/lib/api"

const API = "http://localhost:8000"

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

export default function Planning() {
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
    const [habitsRes, pillarsRes] = await Promise.all([
      fetch(`${API}/habits/today`),
      fetch(`${API}/pillars/`),
    ])
    const habitsData = await habitsRes.json()
    const pillarsData = await pillarsRes.json()
    setHabits(habitsData)
    setPillars(pillarsData)
    setLoading(false)
  }

  const refreshScore = async () => {
    await fetch(`${API}/score/daily`, { method: "POST" })
    await fetch(`${API}/score/global`, { method: "POST" })
    const res = await fetch(`${API}/score/today`)
    const data = await res.json()
    setScore(data.global_score)
  }

  useEffect(() => {
    fetchAll()
    refreshScore()
  }, [])

  const toggleHabit = async (habit: Habit) => {
    const endpoint = habit.checked
      ? `${API}/habits/uncheck/${habit.id}`
      : `${API}/habits/check/${habit.id}`

    await fetch(endpoint, { method: "POST" })

    // Optimistic update
    setHabits((prev) =>
      prev.map((h) => (h.id === habit.id ? { ...h, checked: !h.checked } : h))
    )

    await refreshScore()
  }

  const createHabit = async () => {
    if (!form.name.trim()) return
    await fetch(`${API}/habits/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    })
    setShowForm(false)
    setForm({ name: "", type: "good", points: 20, frequency: "daily", pillar_id: pillars[0]?.id ?? 1 })
    await fetchAll()
    await refreshScore()
  }

  const goodHabits = habits.filter((h) => h.type === "good")
  const badHabits = habits.filter((h) => h.type === "bad")
  const checkedCount = habits.filter((h) => h.checked).length
  const totalCount = habits.length

  const scoreColor =
    score >= 90 ? "#f59e0b" :
    score >= 75 ? "#a78bfa" :
    score >= 60 ? "#3b82f6" : "#ef4444"

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center h-full">
        <div className="text-gray-500 text-sm animate-pulse">Chargement...</div>
      </div>
    )
  }

  return (
    <div className="p-8 space-y-6 max-w-3xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">📅 Planning du jour</h2>
          <p className="text-gray-500 text-sm mt-1">
            {new Date().toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long" })}
          </p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold" style={{ color: scoreColor }}>{score}%</div>
          <div className="text-xs text-gray-500">{checkedCount}/{totalCount} complétées</div>
        </div>
      </div>
      <Pomodoro
  habits={habits}
  onHabitCheck={checkHabit}
/>

      {/* Progress bar */}
      <div className="w-full bg-gray-800 rounded-full h-2">
        <div
          className="h-2 rounded-full transition-all duration-700"
          style={{
            width: totalCount > 0 ? `${(checkedCount / totalCount) * 100}%` : "0%",
            backgroundColor: scoreColor,
          }}
        />
      </div>

      {/* Good Habits */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
        <div className="px-5 py-3 border-b border-gray-800 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-300">✅ Bonnes habitudes</h3>
          <span className="text-xs text-gray-600">{goodHabits.filter(h => h.checked).length}/{goodHabits.length}</span>
        </div>
        <div className="divide-y divide-gray-800">
          {goodHabits.length === 0 && (
            <p className="px-5 py-4 text-sm text-gray-600">Aucune habitude — ajoutes-en une !</p>
          )}
          {goodHabits.map((habit) => (
            <HabitRow
              key={habit.id}
              habit={habit}
              pillars={pillars}
              onToggle={() => toggleHabit(habit)}
            />
          ))}
        </div>
      </div>

      {/* Bad Habits */}
      {badHabits.length > 0 && (
        <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
          <div className="px-5 py-3 border-b border-gray-800 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-300">⚠️ Mauvaises habitudes</h3>
            <span className="text-xs text-gray-600">{badHabits.filter(h => h.checked).length} avouées</span>
          </div>
          <div className="divide-y divide-gray-800">
            {badHabits.map((habit) => (
              <HabitRow
                key={habit.id}
                habit={habit}
                pillars={pillars}
                onToggle={() => toggleHabit(habit)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Add Habit Button */}
      <button
        onClick={() => setShowForm(!showForm)}
        className="w-full py-3 border border-dashed border-gray-700 rounded-xl text-gray-500 hover:border-blue-500 hover:text-blue-400 transition-colors text-sm"
      >
        + Ajouter une habitude
      </button>

      {/* Add Habit Form */}
      {showForm && (
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 space-y-4">
          <h3 className="text-sm font-semibold text-gray-300">Nouvelle habitude</h3>

          <input
            type="text"
            placeholder="Nom de l'habitude..."
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-blue-500"
          />

          <div className="grid grid-cols-2 gap-3">
            {/* Type */}
            <div>
              <label className="text-xs text-gray-500 mb-1 block">Type</label>
              <select
                value={form.type}
                onChange={(e) => setForm({ ...form, type: e.target.value as "good" | "bad" })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
              >
                <option value="good">✅ Bonne habitude</option>
                <option value="bad">⚠️ Mauvaise habitude</option>
              </select>
            </div>

            {/* Pilier */}
            <div>
              <label className="text-xs text-gray-500 mb-1 block">Pilier</label>
              <select
                value={form.pillar_id}
                onChange={(e) => setForm({ ...form, pillar_id: Number(e.target.value) })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
              >
                {pillars.map((p) => (
                  <option key={p.id} value={p.id}>{p.icon} {p.name}</option>
                ))}
              </select>
            </div>

            {/* Points */}
            <div>
              <label className="text-xs text-gray-500 mb-1 block">Points</label>
              <input
                type="number"
                value={form.points}
                onChange={(e) => setForm({ ...form, points: Number(e.target.value) })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
              />
            </div>

            {/* Fréquence */}
            <div>
              <label className="text-xs text-gray-500 mb-1 block">Fréquence</label>
              <select
                value={form.frequency}
                onChange={(e) => setForm({ ...form, frequency: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
              >
                <option value="daily">Quotidienne</option>
                <option value="weekly">Hebdomadaire</option>
              </select>
            </div>
          </div>

          <div className="flex gap-3 pt-1">
            <button
              onClick={createHabit}
              className="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 rounded-lg text-white text-sm font-medium transition-colors"
            >
              Créer l'habitude
            </button>
            <button
              onClick={() => setShowForm(false)}
              className="px-4 py-2.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-gray-400 text-sm transition-colors"
            >
              Annuler
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Composant HabitRow ─────────────────────────────────

function HabitRow({
  habit,
  pillars,
  onToggle,
}: {
  habit: Habit
  pillars: Pillar[]
  onToggle: () => void
}) {
  const pillar = pillars.find((p) => p.id === habit.pillar_id)
  const isBad = habit.type === "bad"

  return (
    <div
      className={`flex items-center gap-4 px-5 py-3.5 cursor-pointer hover:bg-gray-800/50 transition-colors ${
        habit.checked ? "opacity-60" : ""
      }`}
      onClick={onToggle}
    >
      {/* Checkbox */}
      <div
        className={`w-5 h-5 rounded border-2 flex items-center justify-center shrink-0 transition-all ${
          habit.checked
            ? isBad
              ? "bg-red-500 border-red-500"
              : "bg-blue-500 border-blue-500"
            : "border-gray-600"
        }`}
      >
        {habit.checked && (
          <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        )}
      </div>

      {/* Name */}
      <div className="flex-1">
        <span className={`text-sm ${habit.checked ? "line-through text-gray-500" : "text-white"}`}>
          {habit.name}
        </span>
        {pillar && (
          <span
            className="ml-2 text-xs px-1.5 py-0.5 rounded"
            style={{ backgroundColor: `${pillar.color}20`, color: pillar.color }}
          >
            {pillar.icon} {pillar.name}
          </span>
        )}
      </div>

      {/* Points */}
      <span className={`text-xs font-semibold ${isBad ? "text-red-400" : "text-green-400"}`}>
        {isBad ? "-" : "+"}{habit.points} pts
      </span>
    </div>
  )
}