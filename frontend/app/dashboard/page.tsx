"use client"

import { useEffect } from "react"
import { useAppStore } from "@/lib/store"
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, Tooltip } from "recharts"
import Link from "next/link"

export default function Dashboard() {
  const { todaySummary, fetchTodaySummary } = useAppStore()

  useEffect(() => {
    fetchTodaySummary()
    const interval = setInterval(fetchTodaySummary, 30000)
    return () => clearInterval(interval)
  }, [fetchTodaySummary])

  const score = todaySummary?.global_score ?? 0
  const xp = todaySummary?.xp_today ?? 0
  const pillars = todaySummary?.pillars ?? []

  const radarData = pillars.map((p) => ({
    pillar: p.pillar_name,
    score: p.score_pct,
  }))

  const scoreColor =
    score >= 90 ? "#f59e0b" :
    score >= 75 ? "#a78bfa" :
    score >= 60 ? "#3b82f6" :
    "#ef4444"

  const scoreLabel =
    score >= 90 ? "💎 Diamant" :
    score >= 75 ? "🥇 Or" :
    score >= 60 ? "🥈 Argent" :
    score >= 40 ? "🥉 Bronze" : "❌ Danger"

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white">Dashboard</h2>
        <p className="text-gray-500 text-sm mt-1">
          {new Date().toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long" })}
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-3 gap-4">
        {/* Score Global */}
        <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
          <p className="text-gray-500 text-xs uppercase tracking-wider mb-2">Score Global</p>
          <div className="flex items-end gap-2">
            <span className="text-4xl font-bold" style={{ color: scoreColor }}>{score}%</span>
          </div>
          <p className="text-xs mt-2" style={{ color: scoreColor }}>{scoreLabel}</p>
        </div>

        {/* XP */}
        <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
          <p className="text-gray-500 text-xs uppercase tracking-wider mb-2">XP Aujourd&apos;hui</p>
          <span className="text-4xl font-bold text-purple-400">+{xp}</span>
          <p className="text-xs text-gray-600 mt-2">points d&apos;expérience</p>
        </div>

        {/* Piliers actifs */}
        <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
          <p className="text-gray-500 text-xs uppercase tracking-wider mb-2">Piliers actifs</p>
          <span className="text-4xl font-bold text-blue-400">{pillars.length}</span>
          <p className="text-xs text-gray-600 mt-2">en cours de suivi</p>
        </div>
      </div>

      {/* Radar + Pillar Scores */}
      <div className="grid grid-cols-2 gap-4">
        {/* Radar Chart */}
        <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">⚖️ Équilibre des Piliers</h3>
          {radarData.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#374151" />
                <PolarAngleAxis dataKey="pillar" tick={{ fill: "#9ca3af", fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#111827", border: "1px solid #374151", borderRadius: 8 }}
                  labelStyle={{ color: "#f3f4f6" }}
                />
                <Radar name="Score" dataKey="score" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
              </RadarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[260px] flex items-center justify-center text-gray-600 text-sm">
              Aucun score aujourd&apos;hui — coche des habitudes !
            </div>
          )}
        </div>

        {/* Pillar breakdown */}
        <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">📊 Scores par Pilier</h3>
          {pillars.length > 0 ? (
            <div className="space-y-4">
              {pillars.map((p) => (
                <div key={p.pillar_id}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-gray-300">{p.pillar_name}</span>
                    <span className="text-sm font-semibold text-white">{p.score_pct}%</span>
                  </div>
                  <div className="w-full bg-gray-800 rounded-full h-2">
                    <div
                      className="h-2 rounded-full transition-all duration-500"
                      style={{
                        width: `${p.score_pct}%`,
                        backgroundColor: p.pillar_color ?? "#3b82f6",
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-gray-600 text-sm">
              Pas encore de données
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <h3 className="text-sm font-semibold text-gray-300 mb-4">⚡ Actions rapides</h3>
        <div className="flex flex-wrap gap-3">
          <Link href="/dashboard/planning" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm text-white transition-colors">
            📅 Voir le planning
          </Link>
          <Link href="/dashboard/objectives" className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm text-white transition-colors">
            🎯 Mes objectifs
          </Link>
          <Link href="/dashboard/journal" className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm text-white transition-colors">
            📓 Écrire dans le journal
          </Link>
        </div>
      </div>
    </div>
  )
}