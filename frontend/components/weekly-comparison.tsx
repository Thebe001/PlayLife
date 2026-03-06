"use client"

import { useEffect, useState } from "react"
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Legend, LineChart, Line,
} from "recharts"

const API = "http://localhost:8000"

interface PillarComparison {
  pillar_id: number
  pillar_name: string
  pillar_color: string
  current: number
  previous: number
  delta: number
  trend: "up" | "down" | "stable"
}

interface WeekData {
  start: string
  end: string
  global: number
  xp: number
  checks: number
}

interface ComparisonData {
  current_week: WeekData
  previous_week: WeekData
  global_delta: number
  global_trend: "up" | "down" | "stable"
  pillars: PillarComparison[]
}

interface DayScore {
  day: string
  date: string
  score: number | null
}

interface BreakdownData {
  current: DayScore[]
  previous: DayScore[]
}

export default function WeeklyComparison() {
  const [comparison, setComparison] = useState<ComparisonData | null>(null)
  const [breakdown, setBreakdown]   = useState<BreakdownData | null>(null)
  const [loading, setLoading]       = useState(true)

  useEffect(() => {
    Promise.all([
      fetch(`${API}/stats/weekly-comparison`).then((r) => r.json()),
      fetch(`${API}/stats/daily-breakdown`).then((r) => r.json()),
    ]).then(([comp, brk]) => {
      setComparison(comp)
      setBreakdown(brk)
      setLoading(false)
    })
  }, [])

  if (loading || !comparison || !breakdown) {
    return (
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
        <div className="animate-pulse h-40 bg-gray-800 rounded-xl" />
      </div>
    )
  }

  const trendIcon  = (t: string) => t === "up" ? "↑" : t === "down" ? "↓" : "→"
  const trendColor = (t: string) => t === "up" ? "#22c55e" : t === "down" ? "#ef4444" : "#6b7280"

  const formatDate = (d: string) =>
    new Date(d).toLocaleDateString("fr-FR", { day: "numeric", month: "short" })

  // Merge les deux semaines pour le BarChart piliers
  const pillarChartData = comparison.pillars.map((p) => ({
    name: p.pillar_name.length > 8 ? p.pillar_name.slice(0, 8) + "…" : p.pillar_name,
    "Cette semaine": p.current,
    "Semaine passée": p.previous,
    color: p.pillar_color,
  }))

  // Merge breakdown pour le LineChart jours
  const dayChartData = breakdown.current.map((d, i) => ({
    day: d.day,
    "Cette semaine": d.score ?? 0,
    "Semaine passée": breakdown.previous[i]?.score ?? 0,
  }))

  return (
    <div className="space-y-4">

      {/* Header KPIs */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
        <h3 className="text-sm font-semibold text-gray-300 mb-4">
          📅 Comparaison Semaine vs Semaine
        </h3>

        <div className="grid grid-cols-3 gap-4 mb-4">
          {[
            {
              label:    "Score global",
              current:  `${comparison.current_week.global}%`,
              previous: `${comparison.previous_week.global}%`,
              delta:    comparison.global_delta,
              trend:    comparison.global_trend,
            },
            {
              label:    "XP gagnés",
              current:  comparison.current_week.xp.toLocaleString(),
              previous: comparison.previous_week.xp.toLocaleString(),
              delta:    comparison.current_week.xp - comparison.previous_week.xp,
              trend:    comparison.current_week.xp >= comparison.previous_week.xp ? "up" : "down",
            },
            {
              label:    "Habitudes cochées",
              current:  comparison.current_week.checks.toString(),
              previous: comparison.previous_week.checks.toString(),
              delta:    comparison.current_week.checks - comparison.previous_week.checks,
              trend:    comparison.current_week.checks >= comparison.previous_week.checks ? "up" : "down",
            },
          ].map((kpi) => (
            <div key={kpi.label} className="bg-gray-800 rounded-xl p-4">
              <p className="text-xs text-gray-500 mb-2">{kpi.label}</p>
              <div className="flex items-end justify-between">
                <div>
                  <p className="text-xl font-bold text-white">{kpi.current}</p>
                  <p className="text-xs text-gray-600 mt-0.5">
                    vs {kpi.previous} semaine passée
                  </p>
                </div>
                <div
                  className="text-lg font-bold"
                  style={{ color: trendColor(kpi.trend) }}
                >
                  {trendIcon(kpi.trend)}
                  <span className="text-sm ml-0.5">
                    {kpi.delta > 0 ? "+" : ""}{kpi.delta}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Dates */}
        <div className="flex justify-between text-xs text-gray-600">
          <span>
            Semaine passée : {formatDate(comparison.previous_week.start)} → {formatDate(comparison.previous_week.end)}
          </span>
          <span>
            Cette semaine : {formatDate(comparison.current_week.start)} → {formatDate(comparison.current_week.end)}
          </span>
        </div>
      </div>

      {/* LineChart — score jour par jour */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
        <h3 className="text-sm font-semibold text-gray-300 mb-4">
          📈 Score jour par jour
        </h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={dayChartData}>
            <XAxis dataKey="day" tick={{ fill: "#6b7280", fontSize: 11 }} />
            <YAxis domain={[0, 100]} tick={{ fill: "#6b7280", fontSize: 11 }} />
            <Tooltip
              contentStyle={{ backgroundColor: "#111827", border: "1px solid #374151", borderRadius: 8 }}
              formatter={(value: unknown) => [
                `${typeof value === "number" ? value : 0}%`,
              ]}
            />
            <Legend wrapperStyle={{ fontSize: 11, color: "#9ca3af" }} />
            <Line
              type="monotone"
              dataKey="Cette semaine"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ fill: "#3b82f6", r: 4 }}
              activeDot={{ r: 6 }}
            />
            <Line
              type="monotone"
              dataKey="Semaine passée"
              stroke="#6b7280"
              strokeWidth={1.5}
              strokeDasharray="4 2"
              dot={{ fill: "#6b7280", r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* BarChart — piliers comparés */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
        <h3 className="text-sm font-semibold text-gray-300 mb-4">
          ⚖️ Piliers — Cette semaine vs Semaine passée
        </h3>
        {pillarChartData.length === 0 ? (
          <p className="text-sm text-gray-600 text-center py-8">Pas encore de données.</p>
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={pillarChartData} barGap={4}>
              <XAxis dataKey="name" tick={{ fill: "#6b7280", fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fill: "#6b7280", fontSize: 11 }} />
              <Tooltip
                contentStyle={{ backgroundColor: "#111827", border: "1px solid #374151", borderRadius: 8 }}
                formatter={(value: unknown) => [
                  `${typeof value === "number" ? value : 0}%`,
                ]}
              />
              <Legend wrapperStyle={{ fontSize: 11, color: "#9ca3af" }} />
              <Bar dataKey="Cette semaine" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Semaine passée" fill="#374151" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}

        {/* Delta par pilier */}
        <div className="mt-4 space-y-2">
          {comparison.pillars.map((p) => (
            <div key={p.pillar_id} className="flex items-center gap-3">
              <div
                className="w-2 h-2 rounded-full shrink-0"
                style={{ backgroundColor: p.pillar_color }}
              />
              <span className="text-xs text-gray-400 flex-1">{p.pillar_name}</span>
              <span className="text-xs text-gray-500">{p.current}%</span>
              <span
                className="text-xs font-semibold w-12 text-right"
                style={{ color: trendColor(p.trend) }}
              >
                {trendIcon(p.trend)} {p.delta > 0 ? "+" : ""}{p.delta}%
              </span>
            </div>
          ))}
        </div>
      </div>

    </div>
  )
}