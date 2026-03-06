"use client"

import { useEffect, useState } from "react"
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"
import { API } from "@/lib/api"
import Link from "next/link"

interface GamificationData {
  total_xp: number
  level: { name: string; min_xp: number; max_xp: number }
  streak: number
  badges: { id: number; name: string; icon: string; description: string; unlocked_at: string }[]
  rewards: { id: number; name: string; level_required: string; reward_type: string; cooldown_days: number }[]
  recent_scores: { date: string; score: number }[]
}

const LEVEL_COLORS: Record<string, string> = {
  Bronze:  "#cd7f32",
  Argent:  "#a8a9ad",
  Or:      "#ffd700",
  Diamant: "#b9f2ff",
  "Maître": "#ff6b9d",
}

export default function Gamification() {
  const [data, setData] = useState<GamificationData | null>(null)
  const [loading, setLoading] = useState(true)
  const [consuming, setConsuming] = useState<number | null>(null)
  const [consumeMsg, setConsumeMsg] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    try {
      await fetch(`${API}/gamification/badges/check`, { method: "POST" })
      const res = await fetch(`${API}/gamification/summary`)
      if (!res.ok) throw new Error(`${res.status}`)
      const json = await res.json()
      setData(json)
    } catch {
      setError("Impossible de charger les données de gamification.")
    }
    setLoading(false)
  }

  useEffect(() => { fetchData() }, [])

  const consumeReward = async (rewardId: number, rewardName: string) => {
    setConsuming(rewardId)
    const res = await fetch(`${API}/rewards/${rewardId}/consume`, { method: "POST" })
    const json = await res.json()
    if (res.ok) {
      setConsumeMsg(`🎉 "${rewardName}" consommée !`)
    } else {
      setConsumeMsg(`⏳ ${json.detail}`)
    }
    setTimeout(() => setConsumeMsg(null), 3000)
    setConsuming(null)
    await fetchData()
  }

  if (loading || !data) {
    return <div className="p-8 text-gray-500 text-sm animate-pulse">Chargement...</div>
  }

  if (error) {
    return <div className="p-8 text-red-400 text-sm">{error}</div>
  }

  const levelColor = LEVEL_COLORS[data.level.name] ?? "#3b82f6"
  const xpRange = data.level.max_xp - data.level.min_xp
  const xpProgress = data.total_xp - data.level.min_xp
  const xpPct = Math.min(100, Math.round((xpProgress / xpRange) * 100))

  return (
    <div className="p-8 space-y-6 max-w-4xl">

      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white">🏆 Gamification</h2>
        <p className="text-gray-500 text-sm mt-1">Ta progression long terme</p>
      </div>

      {/* Toast */}
      {consumeMsg && (
        <div className="bg-green-900/30 border border-green-700/40 rounded-xl px-4 py-3 text-sm text-green-400">
          {consumeMsg}
        </div>
      )}

      {/* XP + Streak */}
      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2 bg-gray-900 rounded-xl border border-gray-800 p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Niveau actuel</p>
              <h3 className="text-2xl font-bold" style={{ color: levelColor }}>
                {data.level.name}
              </h3>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500 mb-1">XP Total</p>
              <p className="text-2xl font-bold text-white">{data.total_xp.toLocaleString()}</p>
            </div>
          </div>
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs text-gray-600">
              <span>{data.level.min_xp} XP</span>
              <span>{xpPct}%</span>
              <span>{data.level.max_xp} XP</span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-3">
              <div
                className="h-3 rounded-full transition-all duration-700"
                style={{ width: `${xpPct}%`, backgroundColor: levelColor }}
              />
            </div>
            <p className="text-xs text-gray-600">
              {Math.max(0, data.level.max_xp - data.total_xp)} XP pour le niveau suivant
            </p>
          </div>
        </div>

        <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 flex flex-col items-center justify-center text-center">
          <div className="text-4xl mb-2">{data.streak > 0 ? "🔥" : "💤"}</div>
          <div className="text-3xl font-bold text-white">{data.streak}</div>
          <p className="text-xs text-gray-500 mt-1">jours de streak</p>
          {data.streak >= 7 && (
            <span className="mt-2 text-xs px-2 py-1 bg-orange-900/30 text-orange-400 rounded-full">
              Streak Warrior 🔥
            </span>
          )}
        </div>
      </div>

      {/* Score History */}
      {data.recent_scores.length > 0 && (
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">📈 Score des 7 derniers jours</h3>
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={data.recent_scores}>
              <XAxis
                dataKey="date"
                tick={{ fill: "#6b7280", fontSize: 11 }}
                tickFormatter={(d) =>
                  new Date(d).toLocaleDateString("fr-FR", { day: "numeric", month: "short" })
                }
              />
              <YAxis domain={[0, 100]} tick={{ fill: "#6b7280", fontSize: 11 }} />
              <Tooltip
                contentStyle={{ backgroundColor: "#111827", border: "1px solid #374151", borderRadius: 8 }}
                labelFormatter={(d) => new Date(d).toLocaleDateString("fr-FR")}
                formatter={(v: unknown) => [`${typeof v === "number" ? v : 0}%`, "Score"]}
              />
              <Line
                type="monotone"
                dataKey="score"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ fill: "#3b82f6", r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Badges */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
        <h3 className="text-sm font-semibold text-gray-300 mb-4">🏅 Badges débloqués</h3>
        {data.badges.length === 0 ? (
          <p className="text-sm text-gray-600">Aucun badge encore — continue à progresser !</p>
        ) : (
          <div className="grid grid-cols-3 gap-3">
            {data.badges.map((badge, index) => (
              <div
                key={`badge-${badge.id}-${index}`}
                className="bg-gray-800 rounded-xl p-4 flex flex-col items-center text-center gap-2"
              >
                <span className="text-3xl">{badge.icon}</span>
                <span className="text-sm font-semibold text-white">{badge.name}</span>
                <span className="text-xs text-gray-500">{badge.description}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Reward Store */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
        <h3 className="text-sm font-semibold text-gray-300 mb-4">🎁 Reward Store</h3>
        {data.rewards.length === 0 ? (
          <p className="text-sm text-gray-600">
            Aucune récompense — ajoutes-en via{" "}
            <Link href="/dashboard/settings" className="text-blue-400 underline">Settings</Link>.
          </p>
        ) : (
          <div className="grid grid-cols-2 gap-3">
            {data.rewards.map((reward, index) => (
              <div
                key={`reward-${reward.id}-${index}`}
                className="bg-gray-800 rounded-xl p-4 flex items-center justify-between gap-3"
              >
                <div>
                  <p className="text-sm text-white font-medium">{reward.name}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs px-2 py-0.5 rounded bg-gray-700 text-gray-400 capitalize">
                      {reward.level_required}
                    </span>
                    {reward.cooldown_days > 0 && (
                      <span className="text-xs text-gray-600">⏳ {reward.cooldown_days}j</span>
                    )}
                    <span className="text-xs text-gray-600 capitalize">{reward.reward_type}</span>
                  </div>
                </div>
                <button
                  onClick={() => consumeReward(reward.id, reward.name)}
                  disabled={consuming === reward.id}
                  className="shrink-0 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg text-xs text-white transition-colors"
                >
                  {consuming === reward.id ? "..." : "Utiliser"}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Seuils */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
        <h3 className="text-sm font-semibold text-gray-300 mb-4">🎖️ Seuils de récompense</h3>
        <div className="grid grid-cols-4 gap-3">
          {[
            { label: "Bronze",  color: "#cd7f32", req: "Score ≥ 60%" },
            { label: "Argent",  color: "#a8a9ad", req: "Score ≥ 75%" },
            { label: "Or",      color: "#ffd700", req: "Score ≥ 90%" },
            { label: "Diamant", color: "#b9f2ff", req: "Score ≥ 98%" },
          ].map((tier) => (
            <div key={`tier-${tier.label}`} className="bg-gray-800 rounded-xl p-3 text-center">
              <div className="text-lg font-bold mb-1" style={{ color: tier.color }}>{tier.label}</div>
              <div className="text-xs text-gray-500">{tier.req}</div>
            </div>
          ))}
        </div>
      </div>

    </div>
  )
}