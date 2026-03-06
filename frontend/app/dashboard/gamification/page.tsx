"use client"

import { useEffect, useState, useCallback } from "react"
import { useAppStore } from "@/lib/store"
import { checkBadges, getRewards, consumeReward, getActiveSanctions } from "@/lib/api"
import { getScoreTier } from "@/lib/score-utils"
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from "recharts"

// ── Types ──────────────────────────────────────────────────────────────────

interface Badge {
  id: number
  name: string
  icon: string
  description: string
  unlocked_at: string
}

interface RewardItem {
  id: number
  name: string
  level_required: string
  reward_type: string
  cooldown_days: number
}

interface ActiveSanction {
  id: number
  name: string
  description: string
  trigger_threshold: number
  consecutive_days: number
}

// ── Component ─────────────────────────────────────────────────────────────

export default function Gamification() {
  const { gamification, fetchGamification } = useAppStore()
  const [rewards, setRewards] = useState<RewardItem[]>([])
  const [sanctions, setSanctions] = useState<ActiveSanction[]>([])
  const [checkingBadges, setCheckingBadges] = useState(false)
  const [newBadges, setNewBadges] = useState<string[]>([])
  const [consumeMsg, setConsumeMsg] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const loadAll = useCallback(async () => {
    try {
      await fetchGamification()
      const [rw, sn] = await Promise.all([
        getRewards().catch(() => []),
        getActiveSanctions().catch(() => []),
      ])
      setRewards(rw as RewardItem[])
      setSanctions(sn as ActiveSanction[])
    } catch {
      // ignore
    }
    setLoading(false)
  }, [fetchGamification])

  useEffect(() => { loadAll() }, [loadAll])

  const handleCheckBadges = async () => {
    setCheckingBadges(true)
    try {
      const result = await checkBadges() as { unlocked: string[]; count: number }
      setNewBadges(result.unlocked)
      if (result.count > 0) await fetchGamification()
    } catch { /* ignore */ }
    setCheckingBadges(false)
  }

  const handleConsumeReward = async (id: number, name: string) => {
    try {
      await consumeReward(id)
      setConsumeMsg(`🎉 "${name}" consommée !`)
      setTimeout(() => setConsumeMsg(null), 3000)
    } catch {
      setConsumeMsg(`⏳ Récompense en cooldown`)
      setTimeout(() => setConsumeMsg(null), 3000)
    }
  }

  if (loading || !gamification) {
    return <div className="p-8 text-gray-500 text-sm animate-pulse">Chargement...</div>
  }

  const { total_xp, level, streak, badges, recent_scores } = gamification as {
    total_xp: number
    level: { name: string; min_xp: number; max_xp: number }
    streak: number
    badges: Badge[]
    recent_scores?: { date: string; score: number }[]
  }

  const xpInLevel = total_xp - level.min_xp
  const xpRange = level.max_xp - level.min_xp
  const levelProgress = xpRange > 0 ? Math.min(100, (xpInLevel / xpRange) * 100) : 100

  const tierInfo = getScoreTier(recent_scores?.[0]?.score ?? 0)

  // Score sparkline for chart
  const chartData = [...(recent_scores ?? [])].reverse()

  return (
    <div className="p-8 space-y-6 max-w-5xl">

      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white">🏆 Gamification</h2>
        <p className="text-gray-500 text-sm mt-1">XP, niveau, badges, récompenses & sanctions</p>
      </div>

      {/* Toast */}
      {consumeMsg && (
        <div className="fixed top-4 right-4 z-50 bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white shadow-lg">
          {consumeMsg}
        </div>
      )}

      {/* KPI Row */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">XP Total</p>
          <p className="text-2xl font-bold text-blue-400">{total_xp.toLocaleString()}</p>
        </div>
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Niveau</p>
          <p className="text-2xl font-bold text-purple-400">{level.name}</p>
        </div>
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Streak</p>
          <p className="text-2xl font-bold text-amber-400">🔥 {streak}j</p>
        </div>
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Rang actuel</p>
          <p className="text-2xl font-bold" style={{ color: tierInfo.color }}>
            {tierInfo.emoji} {tierInfo.label}
          </p>
        </div>
      </div>

      {/* XP Progress Bar */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-gray-300">⬆️ Progression vers le niveau suivant</h3>
          <span className="text-xs text-gray-500">{xpInLevel} / {xpRange} XP</span>
        </div>
        <div className="w-full bg-gray-800 rounded-full h-4 overflow-hidden">
          <div
            className="h-4 rounded-full transition-all duration-700 bg-gradient-to-r from-blue-600 to-purple-500"
            style={{ width: `${levelProgress}%` }}
          />
        </div>
        <div className="flex justify-between mt-2 text-xs text-gray-600">
          <span>{level.min_xp} XP</span>
          <span>{level.max_xp} XP</span>
        </div>
      </div>

      {/* Score Trend (mini chart) */}
      {chartData.length > 0 && (
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">📈 Score global — 30 derniers jours</h3>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis
                dataKey="date"
                tick={{ fill: "#6b7280", fontSize: 10 }}
                tickFormatter={(d) => new Date(d).toLocaleDateString("fr-FR", { day: "numeric", month: "short" })}
              />
              <YAxis domain={[0, 100]} tick={{ fill: "#6b7280", fontSize: 10 }} />
              <Tooltip
                contentStyle={{ backgroundColor: "#111827", border: "1px solid #374151", borderRadius: 8 }}
                labelFormatter={(d) => new Date(d as string).toLocaleDateString("fr-FR")}
                formatter={(value: unknown) => [`${typeof value === "number" ? value : 0}%`, "Score"]}
              />
              <Line type="monotone" dataKey="score" stroke="#3b82f6" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Badges */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-gray-300">🎖️ Badges débloqués ({badges.length})</h3>
            {newBadges.length > 0 && (
              <p className="text-xs text-green-400 mt-1">
                ✨ Nouveau{newBadges.length > 1 ? "x" : ""} : {newBadges.join(", ")}
              </p>
            )}
          </div>
          <button
            onClick={handleCheckBadges}
            disabled={checkingBadges}
            className="px-3 py-1.5 rounded-lg text-xs bg-purple-600 hover:bg-purple-700 text-white transition-colors disabled:opacity-50"
          >
            {checkingBadges ? "Vérification..." : "Vérifier les badges"}
          </button>
        </div>

        {badges.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-600 text-sm">Aucun badge débloqué pour l&apos;instant</p>
            <p className="text-gray-700 text-xs mt-1">Continue ta routine pour les débloquer !</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {badges.map((badge) => (
              <div
                key={badge.id}
                className="bg-gray-800/50 rounded-xl border border-gray-700/50 p-4 text-center hover:border-purple-600/40 transition-colors group"
              >
                <div className="text-3xl mb-2 group-hover:scale-110 transition-transform">
                  {badge.icon || "🏅"}
                </div>
                <p className="text-sm font-medium text-white truncate">{badge.name}</p>
                <p className="text-xs text-gray-500 mt-1 line-clamp-2">{badge.description}</p>
                <p className="text-[10px] text-gray-600 mt-2">
                  {new Date(badge.unlocked_at).toLocaleDateString("fr-FR")}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Rewards */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
        <h3 className="text-sm font-semibold text-gray-300 mb-4">🎁 Récompenses disponibles</h3>
        {rewards.length === 0 ? (
          <p className="text-gray-600 text-sm text-center py-4">
            Aucune récompense configurée — ajoute-les dans les Paramètres
          </p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {rewards.map((r) => (
              <div
                key={r.id}
                className="flex items-center justify-between bg-gray-800/40 rounded-xl border border-gray-700/50 p-4"
              >
                <div>
                  <p className="text-sm font-medium text-white">{r.name}</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    Niveau requis : {r.level_required} • Cooldown : {r.cooldown_days}j
                  </p>
                </div>
                <button
                  onClick={() => handleConsumeReward(r.id, r.name)}
                  className="px-3 py-1.5 rounded-lg text-xs bg-green-600 hover:bg-green-700 text-white transition-colors shrink-0"
                >
                  Consommer
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Active Sanctions */}
      {sanctions.length > 0 && (
        <div className="bg-red-950/30 rounded-xl border border-red-800/40 p-5">
          <h3 className="text-sm font-semibold text-red-400 mb-4">⚠️ Sanctions actives</h3>
          <div className="space-y-3">
            {sanctions.map((s) => (
              <div
                key={s.id}
                className="flex items-center gap-3 bg-red-900/20 rounded-xl border border-red-800/30 p-4"
              >
                <span className="text-xl">🚫</span>
                <div>
                  <p className="text-sm font-medium text-red-300">{s.name}</p>
                  <p className="text-xs text-red-400/70 mt-0.5">
                    {s.description} • Seuil : {s.trigger_threshold}% • {s.consecutive_days}j consécutifs
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Streak detail */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
        <h3 className="text-sm font-semibold text-gray-300 mb-4">🔥 Détail du streak</h3>
        <div className="flex items-center gap-6">
          <div className="text-center">
            <div className="text-5xl font-bold text-amber-400">{streak}</div>
            <p className="text-xs text-gray-500 mt-1">jours consécutifs</p>
          </div>
          <div className="flex-1 space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500 w-16">7 jours</span>
              <div className="flex-1 bg-gray-800 rounded-full h-2">
                <div
                  className="h-2 rounded-full bg-amber-500 transition-all"
                  style={{ width: `${Math.min(100, (streak / 7) * 100)}%` }}
                />
              </div>
              <span className={`text-xs ${streak >= 7 ? "text-green-400" : "text-gray-600"}`}>
                {streak >= 7 ? "✓" : `${7 - streak}j restants`}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500 w-16">30 jours</span>
              <div className="flex-1 bg-gray-800 rounded-full h-2">
                <div
                  className="h-2 rounded-full bg-purple-500 transition-all"
                  style={{ width: `${Math.min(100, (streak / 30) * 100)}%` }}
                />
              </div>
              <span className={`text-xs ${streak >= 30 ? "text-green-400" : "text-gray-600"}`}>
                {streak >= 30 ? "✓" : `${30 - streak}j restants`}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500 w-16">100 jours</span>
              <div className="flex-1 bg-gray-800 rounded-full h-2">
                <div
                  className="h-2 rounded-full bg-blue-500 transition-all"
                  style={{ width: `${Math.min(100, (streak / 100) * 100)}%` }}
                />
              </div>
              <span className={`text-xs ${streak >= 100 ? "text-green-400" : "text-gray-600"}`}>
                {streak >= 100 ? "✓" : `${100 - streak}j restants`}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}1