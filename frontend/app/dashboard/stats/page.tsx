"use client"

import { useEffect, useState } from "react"
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Legend, ScatterChart,
  Scatter, ZAxis, CartesianGrid,
} from "recharts"
import WeeklyComparison from "@/components/weekly-comparison"
import { API } from "@/lib/api"

// ── Types ──────────────────────────────────────────────────────────────────

interface HeatmapDay {
  date:  string
  score: number | null
}

interface Overview {
  avg_7d:               number
  avg_30d:              number
  best_score:           number
  best_score_date:      string | null
  total_habit_checks:   number
  total_xp:             number
  avg_mood:             number
  total_journal_entries: number
}

interface ProgressionData {
  global:  { date: string; score: number }[]
  pillars: Record<string, { color: string; scores: { date: string; score: number }[] }>
}

interface CorrelationPair {
  date:   string
  mood:   number
  energy: number | null
  score:  number
}

interface ByMood {
  avg_score: number
  count:     number
  min_score: number
  max_score: number
}

interface CorrelationData {
  pairs:       CorrelationPair[]
  by_mood:     Record<string, ByMood>
  by_energy:   Record<string, { avg_score: number; count: number }>
  insight:     string | null
  data_points: number
  period_days: number
}

// ── Helpers ────────────────────────────────────────────────────────────────

function scoreToColor(score: number | null): string {
  if (score === null) return "#1f2937"
  if (score >= 90)   return "#f59e0b"
  if (score >= 75)   return "#a78bfa"
  if (score >= 60)   return "#3b82f6"
  if (score >= 40)   return "#22c55e"
  if (score > 0)     return "#ef4444"
  return "#1f2937"
}

const MOOD_LABELS: Record<number, string> = {
  1: "😞 Très bas",
  2: "😕 Bas",
  3: "😐 Neutre",
  4: "😊 Bon",
  5: "😄 Excellent",
}

const MOOD_COLORS: Record<number, string> = {
  1: "#ef4444",
  2: "#f97316",
  3: "#eab308",
  4: "#22c55e",
  5: "#3b82f6",
}

// ── Page principale ────────────────────────────────────────────────────────

export default function Stats() {
  const [heatmap,     setHeatmap]     = useState<HeatmapDay[]>([])
  const [overview,    setOverview]    = useState<Overview | null>(null)
  const [progression, setProgression] = useState<ProgressionData | null>(null)
  const [correlation, setCorrelation] = useState<CorrelationData | null>(null)
  const [period,      setPeriod]      = useState(30)
  const [corrDays,    setCorrDays]    = useState(30)
  const [loading,     setLoading]     = useState(true)
  const [error,       setError]       = useState<string | null>(null)

  const fetchAll = async (days = 30) => {
    try {
      const [hRes, oRes, pRes] = await Promise.all([
        fetch(`${API}/stats/heatmap`),
        fetch(`${API}/stats/overview`),
        fetch(`${API}/stats/progression?days=${days}`),
      ])
      if (!hRes.ok || !oRes.ok || !pRes.ok) throw new Error("fetch failed")
      setHeatmap(await hRes.json())
      setOverview(await oRes.json())
      setProgression(await pRes.json())
    } catch {
      setError("Impossible de charger les statistiques.")
    }
    setLoading(false)
  }

  const fetchCorrelation = async (days: number) => {
    try {
      const res = await fetch(`${API}/stats/correlation?days=${days}`)
      if (!res.ok) throw new Error()
      setCorrelation(await res.json())
    } catch {
      setCorrelation(null)
    }
  }

  useEffect(() => { fetchAll(period) },    [period])
  useEffect(() => { fetchCorrelation(corrDays) }, [corrDays])

  if (loading || !overview || !progression) {
    return <div className="p-8 text-gray-500 text-sm animate-pulse">Chargement...</div>
  }

  if (error) {
    return <div className="p-8 text-red-400 text-sm">{error}</div>
  }

  const mergedProgression = progression.global.map((g) => {
    const row: Record<string, string | number> = { date: g.date, Global: g.score }
    Object.entries(progression.pillars).forEach(([name, data]) => {
      const match = data.scores.find((s) => s.date === g.date)
      if (match) row[name] = match.score
    })
    return row
  })

  const weeks: HeatmapDay[][] = []
  for (let i = 0; i < heatmap.length; i += 7) {
    weeks.push(heatmap.slice(i, i + 7))
  }

  const moodEmoji = (m: number) => {
    if (m >= 4.5) return "😄"
    if (m >= 3.5) return "🙂"
    if (m >= 2.5) return "😐"
    if (m >= 1.5) return "😕"
    return "😞"
  }

  // Données scatter : une entrée par paire mood/score
  const scatterData = correlation?.pairs.map((p) => ({
    mood:  p.mood,
    score: p.score,
    date:  p.date,
  })) ?? []

  // Bar chart humeur : avg score par niveau de mood
  const moodBarData = Object.entries(correlation?.by_mood ?? {}).map(([mood, val]) => ({
    mood:      parseInt(mood),
    label:     MOOD_LABELS[parseInt(mood)] ?? mood,
    avg_score: val.avg_score,
    count:     val.count,
    color:     MOOD_COLORS[parseInt(mood)] ?? "#6b7280",
  }))

  return (
    <div className="p-8 space-y-6 max-w-5xl">

      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white">📈 Stats & Insights</h2>
        <p className="text-gray-500 text-sm mt-1">Vue d&apos;ensemble de ta progression</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Moyenne 7j",    value: `${overview.avg_7d}%`,              color: "#3b82f6" },
          { label: "Moyenne 30j",   value: `${overview.avg_30d}%`,             color: "#a78bfa" },
          { label: "Meilleur jour", value: `${overview.best_score}%`,          color: "#f59e0b" },
          { label: "Total XP",      value: overview.total_xp.toLocaleString(), color: "#22c55e" },
        ].map((kpi) => (
          <div key={kpi.label} className="bg-gray-900 rounded-xl border border-gray-800 p-4">
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">{kpi.label}</p>
            <p className="text-2xl font-bold" style={{ color: kpi.color }}>{kpi.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-4 text-center">
          <p className="text-xs text-gray-500 mb-2">Habitudes cochées</p>
          <p className="text-2xl font-bold text-white">{overview.total_habit_checks}</p>
        </div>
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-4 text-center">
          <p className="text-xs text-gray-500 mb-2">Entrées journal</p>
          <p className="text-2xl font-bold text-white">{overview.total_journal_entries}</p>
        </div>
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-4 text-center">
          <p className="text-xs text-gray-500 mb-2">Humeur moyenne</p>
          <p className="text-2xl font-bold text-white">
            {overview.avg_mood > 0 ? `${moodEmoji(overview.avg_mood)} ${overview.avg_mood}` : "—"}
          </p>
        </div>
      </div>

      {/* Heatmap */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
        <h3 className="text-sm font-semibold text-gray-300 mb-4">🗓️ Heatmap — 365 jours</h3>
        <div className="flex gap-1 overflow-x-auto pb-2">
          {weeks.map((week, wi) => (
            <div key={wi} className="flex flex-col gap-1">
              {week.map((day, di) => (
                <div
                  key={di}
                  className="w-3 h-3 rounded-sm cursor-pointer transition-transform hover:scale-125"
                  style={{ backgroundColor: scoreToColor(day.score) }}
                  title={`${day.date}: ${day.score !== null ? `${day.score}%` : "Pas de données"}`}
                />
              ))}
            </div>
          ))}
        </div>
        <div className="flex items-center gap-3 mt-3">
          <span className="text-xs text-gray-600">Moins</span>
          {[null, 30, 50, 65, 80, 95].map((s, i) => (
            <div key={i} className="w-3 h-3 rounded-sm" style={{ backgroundColor: scoreToColor(s) }} />
          ))}
          <span className="text-xs text-gray-600">Plus</span>
        </div>
      </div>

      {/* Progression Chart */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-gray-300">📊 Progression</h3>
          <div className="flex gap-2">
            {[7, 30, 90].map((d) => (
              <button
                key={d}
                onClick={() => setPeriod(d)}
                className={`px-3 py-1 rounded-lg text-xs transition-colors ${
                  period === d ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-400 hover:text-white"
                }`}
              >
                {d}j
              </button>
            ))}
          </div>
        </div>
        {mergedProgression.length === 0 ? (
          <div className="h-[200px] flex items-center justify-center text-gray-600 text-sm">
            Pas encore assez de données
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={mergedProgression}>
              <XAxis
                dataKey="date"
                tick={{ fill: "#6b7280", fontSize: 10 }}
                tickFormatter={(d) => new Date(d).toLocaleDateString("fr-FR", { day: "numeric", month: "short" })}
              />
              <YAxis domain={[0, 100]} tick={{ fill: "#6b7280", fontSize: 10 }} />
              <Tooltip
                contentStyle={{ backgroundColor: "#111827", border: "1px solid #374151", borderRadius: 8 }}
                labelFormatter={(d) => new Date(d).toLocaleDateString("fr-FR")}
                formatter={(value: unknown, name: unknown) => [`${typeof value === "number" ? value : 0}%`, String(name)]}
              />
              <Legend wrapperStyle={{ fontSize: 11, color: "#9ca3af" }} />
              <Line type="monotone" dataKey="Global" stroke="#3b82f6" strokeWidth={2} dot={false} />
              {Object.entries(progression.pillars).map(([name, data]) => (
                <Line key={name} type="monotone" dataKey={name} stroke={data.color} strokeWidth={1.5} dot={false} strokeDasharray="4 2" />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* ── Corrélation Mood / Score ────────────────────────────────────── */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-gray-300">🧠 Corrélation Humeur / Score</h3>
            <p className="text-xs text-gray-600 mt-0.5">Comment ton humeur influence ta performance</p>
          </div>
          <div className="flex gap-2">
            {[14, 30, 90].map((d) => (
              <button
                key={d}
                onClick={() => setCorrDays(d)}
                className={`px-3 py-1 rounded-lg text-xs transition-colors ${
                  corrDays === d ? "bg-purple-600 text-white" : "bg-gray-800 text-gray-400 hover:text-white"
                }`}
              >
                {d}j
              </button>
            ))}
          </div>
        </div>

        {!correlation || correlation.data_points === 0 ? (
          <div className="h-32 flex items-center justify-center text-gray-600 text-sm">
            Pas encore assez de données — écris dans ton journal avec un mood !
          </div>
        ) : (
          <>
            {/* Insight */}
            {correlation.insight && (
              <div className="bg-purple-900/20 border border-purple-700/30 rounded-xl px-4 py-3">
                <p className="text-sm text-purple-300">💡 {correlation.insight}</p>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              {/* Score moyen par mood — bar chart manuel */}
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">Score moyen par humeur</p>
                <div className="space-y-2">
                  {moodBarData.map((m) => (
                    <div key={m.mood}>
                      <div className="flex justify-between items-center mb-0.5">
                        <span className="text-xs text-gray-400">{m.label}</span>
                        <span className="text-xs font-semibold" style={{ color: m.color }}>
                          {m.avg_score}% <span className="text-gray-600 font-normal">({m.count}j)</span>
                        </span>
                      </div>
                      <div className="w-full bg-gray-800 rounded-full h-1.5">
                        <div
                          className="h-1.5 rounded-full transition-all duration-500"
                          style={{ width: `${m.avg_score}%`, backgroundColor: m.color }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Scatter plot mood vs score */}
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">Nuage de points</p>
                {scatterData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={160}>
                    <ScatterChart>
                      <CartesianGrid stroke="#1f2937" />
                      <XAxis
                        type="number" dataKey="mood" domain={[0.5, 5.5]} name="Humeur"
                        tick={{ fill: "#6b7280", fontSize: 10 }}
                        tickFormatter={(v) => ["", "😞", "😕", "😐", "😊", "😄"][v] ?? v}
                      />
                      <YAxis
                        type="number" dataKey="score" domain={[0, 100]} name="Score"
                        tick={{ fill: "#6b7280", fontSize: 10 }}
                        tickFormatter={(v) => `${v}%`}
                      />
                      <ZAxis range={[30, 30]} />
                      <Tooltip
                        contentStyle={{ backgroundColor: "#111827", border: "1px solid #374151", borderRadius: 8 }}
                        formatter={(value: unknown, name: unknown) => [
                          name === "score" ? `${value}%` : MOOD_LABELS[value as number] ?? value,
                          name === "score" ? "Score" : "Humeur",
                        ]}
                      />
                      <Scatter
                        data={scatterData}
                        fill="#a78bfa"
                        fillOpacity={0.7}
                      />
                    </ScatterChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[160px] flex items-center justify-center text-gray-600 text-sm">
                    Pas de données
                  </div>
                )}
              </div>
            </div>

            <p className="text-xs text-gray-600 text-right">
              Basé sur {correlation.data_points} jour{correlation.data_points > 1 ? "s" : ""} avec journal + score
            </p>
          </>
        )}
      </div>

      {/* Weekly Comparison */}
      <WeeklyComparison />

    </div>
  )
}