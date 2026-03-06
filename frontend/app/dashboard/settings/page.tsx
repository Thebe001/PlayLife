"use client"

import { useEffect, useState, useRef } from "react"
import { API } from "@/lib/api"

// ── Emoji picker data ──────────────────────────────────────────────────────
const EMOJI_CATEGORIES = [
  {
    label: "Vie & Objectifs",
    emojis: ["🎯","🏆","⚡","🚀","💡","🔥","💎","⭐","🌟","✨","🎖️","🏅","🥇","🎗️","🏁"],
  },
  {
    label: "Santé & Sport",
    emojis: ["💪","🏃","🧘","🥗","😴","❤️","🧠","🦷","👁️","🏋️","⚽","🎾","🚴","🤸","🥊"],
  },
  {
    label: "Travail & Finance",
    emojis: ["💼","💰","📈","💻","🖥️","📊","🏦","💳","📝","🗂️","📋","✅","🔑","🏢","📱"],
  },
  {
    label: "Apprentissage",
    emojis: ["📚","🎓","✏️","🔬","🔭","🎨","🎵","🎸","📖","🗺️","🧪","🖊️","📐","🏫","🧮"],
  },
  {
    label: "Relations & Bien-être",
    emojis: ["👨‍👩‍👧","🤝","❤️‍🔥","🫂","😊","🌿","🌸","☀️","🌙","🎭","🕊️","🌈","🍀","🌻","🧡"],
  },
  {
    label: "Maison & Lifestyle",
    emojis: ["🏠","🍳","🌱","🐕","✈️","🚗","🎮","📸","🛋️","🧹","🍽️","☕","🛁","🌍","🎬"],
  },
]

interface Pillar {
  id: number
  name: string
  icon: string
  color: string
  weight_pct: number
  is_active: boolean
}

interface Reward {
  id: number
  name: string
  level_required: string
  reward_type: string
  cooldown_days: number
  is_active: boolean
}

interface Sanction {
  id: number
  name: string
  description: string
  trigger_threshold: number
  consecutive_days: number
}

type Tab = "pillars" | "rewards" | "sanctions"

// ── Emoji Picker Component ─────────────────────────────────────────────────
function EmojiPicker({
  value,
  onChange,
}: {
  value: string
  onChange: (emoji: string) => void
}) {
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState("")
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener("mousedown", handler)
    return () => document.removeEventListener("mousedown", handler)
  }, [])

  const allEmojis = EMOJI_CATEGORIES.flatMap((c) => c.emojis)
  const filtered = search ? allEmojis.filter((e) => e.includes(search)) : null

  return (
    <div ref={ref} className="relative">
      <label className="text-xs text-gray-500 mb-1 block">Icône</label>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="w-full bg-gray-800 border border-gray-700 hover:border-blue-500 rounded-lg px-3 py-2.5 text-white text-sm flex items-center gap-2 transition-colors focus:outline-none focus:border-blue-500"
      >
        <span className="text-xl">{value}</span>
        <span className="text-gray-500 text-xs flex-1 text-left">Choisir une icône</span>
        <span className="text-gray-600 text-xs">{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div className="absolute z-50 top-full left-0 mt-1 w-72 bg-gray-900 border border-gray-700 rounded-xl shadow-2xl overflow-hidden">
          <div className="p-2 border-b border-gray-800">
            <input
              type="text"
              placeholder="Rechercher un emoji..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-white text-xs placeholder-gray-600 focus:outline-none focus:border-blue-500"
              autoFocus
            />
          </div>
          <div className="overflow-y-auto max-h-64 p-2 space-y-3">
            {filtered ? (
              <div>
                <p className="text-xs text-gray-600 mb-1 px-1">Résultats</p>
                <div className="grid grid-cols-8 gap-1">
                  {filtered.map((emoji) => (
                    <button
                      key={emoji}
                      type="button"
                      onClick={() => { onChange(emoji); setOpen(false); setSearch("") }}
                      className={`text-xl p-1 rounded hover:bg-gray-700 transition-colors ${value === emoji ? "bg-blue-600/30 ring-1 ring-blue-500" : ""}`}
                    >
                      {emoji}
                    </button>
                  ))}
                  {filtered.length === 0 && (
                    <p className="col-span-8 text-xs text-gray-600 text-center py-2">Aucun résultat</p>
                  )}
                </div>
              </div>
            ) : (
              EMOJI_CATEGORIES.map((cat) => (
                <div key={cat.label}>
                  <p className="text-xs text-gray-600 mb-1 px-1">{cat.label}</p>
                  <div className="grid grid-cols-8 gap-1">
                    {cat.emojis.map((emoji) => (
                      <button
                        key={emoji}
                        type="button"
                        onClick={() => { onChange(emoji); setOpen(false) }}
                        className={`text-xl p-1 rounded hover:bg-gray-700 transition-colors ${value === emoji ? "bg-blue-600/30 ring-1 ring-blue-500" : ""}`}
                      >
                        {emoji}
                      </button>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
          <div className="px-3 py-2 border-t border-gray-800 flex items-center gap-2">
            <span className="text-xl">{value}</span>
            <span className="text-xs text-gray-500">Sélectionné</span>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Main Settings Page ─────────────────────────────────────────────────────
export default function Settings() {
  const [tab, setTab]           = useState<Tab>("pillars")
  const [pillars, setPillars]   = useState<Pillar[]>([])
  const [rewards, setRewards]   = useState<Reward[]>([])
  const [sanctions, setSanctions] = useState<Sanction[]>([])
  const [loading, setLoading]   = useState(true)
  const [saved, setSaved]       = useState(false)
  const [apiError, setApiError] = useState<string | null>(null)

  const [pillarForm, setPillarForm] = useState({
    name: "", icon: "⭐", color: "#3b82f6", weight_pct: 20,
  })
  const [rewardForm, setRewardForm] = useState({
    name: "", level_required: "bronze", reward_type: "consumable", cooldown_days: 0,
  })
  const [sanctionForm, setSanctionForm] = useState({
    name: "", description: "", trigger_threshold: 40, consecutive_days: 1,
  })

  const fetchAll = async () => {
    try {
      const [pRes, rRes, sRes] = await Promise.all([
        fetch(`${API}/pillars/`),
        fetch(`${API}/rewards/`),
        fetch(`${API}/rewards/sanctions/`),
      ])
      if (!pRes.ok || !rRes.ok || !sRes.ok) throw new Error("fetch failed")
      setPillars(await pRes.json())
      setRewards(await rRes.json())
      setSanctions(await sRes.json())
    } catch (e) {
      console.error("Settings fetchAll:", e)
    }
    setLoading(false)
  }

  useEffect(() => { fetchAll() }, [])

  const showSaved = () => {
    setSaved(true)
    setApiError(null)
    setTimeout(() => setSaved(false), 2000)
  }

  // ── Piliers ──────────────────────────────────────────────────────────────

  const totalWeight = pillars.filter((p) => p.is_active).reduce((s, p) => s + p.weight_pct, 0)
  const remainingBudget = Math.max(0, 100 - totalWeight)

  const createPillar = async () => {
    if (!pillarForm.name.trim()) return
    setApiError(null)

    // Vérification locale avant d'envoyer
    if (pillarForm.weight_pct > remainingBudget + 0.01) {
      setApiError(`❌ Budget insuffisant — il reste ${remainingBudget.toFixed(1)}% disponible.`)
      return
    }

    const res = await fetch(`${API}/pillars/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(pillarForm),
    })

    if (!res.ok) {
      const err = await res.json()
      setApiError(`❌ ${err.detail}`)
      return
    }

    setPillarForm({ name: "", icon: "⭐", color: "#3b82f6", weight_pct: 20 })
    await fetchAll()
    showSaved()
  }

  const archivePillar = async (id: number) => {
    await fetch(`${API}/pillars/${id}`, { method: "DELETE" })
    await fetchAll()
  }

  // ── Rewards ──────────────────────────────────────────────────────────────

  const createReward = async () => {
    if (!rewardForm.name.trim()) return
    const res = await fetch(`${API}/rewards/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(rewardForm),
    })
    if (!res.ok) {
      const err = await res.json()
      setApiError(`❌ ${err.detail}`)
      return
    }
    setRewardForm({ name: "", level_required: "bronze", reward_type: "consumable", cooldown_days: 0 })
    await fetchAll()
    showSaved()
  }

  const deleteReward = async (id: number) => {
    await fetch(`${API}/rewards/${id}`, { method: "DELETE" })
    await fetchAll()
  }

  // ── Sanctions ─────────────────────────────────────────────────────────────

  const createSanction = async () => {
    if (!sanctionForm.name.trim()) return
    const res = await fetch(`${API}/rewards/sanctions/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(sanctionForm),
    })
    if (!res.ok) {
      const err = await res.json()
      setApiError(`❌ ${err.detail}`)
      return
    }
    setSanctionForm({ name: "", description: "", trigger_threshold: 40, consecutive_days: 1 })
    await fetchAll()
    showSaved()
  }

  const deleteSanction = async (id: number) => {
    await fetch(`${API}/rewards/sanctions/${id}`, { method: "DELETE" })
    await fetchAll()
  }

  if (loading) {
    return <div className="p-8 text-gray-500 text-sm animate-pulse">Chargement...</div>
  }

  return (
    <div className="p-8 space-y-6 max-w-3xl">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">⚙️ Settings</h2>
          <p className="text-gray-500 text-sm mt-1">Configure ton système</p>
        </div>
        {saved && (
          <span className="text-sm text-green-400 bg-green-900/20 border border-green-800/40 px-3 py-1.5 rounded-lg">
            ✅ Sauvegardé
          </span>
        )}
      </div>

      {/* API Error */}
      {apiError && (
        <div className="px-4 py-3 rounded-xl text-sm border bg-red-900/20 border-red-800/40 text-red-400">
          {apiError}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-800 pb-0">
        {(["pillars", "rewards", "sanctions"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => { setTab(t); setApiError(null) }}
            className={`px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px ${
              tab === t
                ? "border-blue-500 text-white"
                : "border-transparent text-gray-500 hover:text-gray-300"
            }`}
          >
            {t === "pillars" ? "🏛️ Piliers" : t === "rewards" ? "🎁 Récompenses" : "⚠️ Sanctions"}
          </button>
        ))}
      </div>

      {/* ── PILIERS ── */}
      {tab === "pillars" && (
        <div className="space-y-4">

          {/* Barre de budget des poids */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-4 space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-400">Budget des poids</span>
              <span className={`text-xs font-semibold ${
                totalWeight === 100 ? "text-green-400" :
                totalWeight > 100   ? "text-red-400"   : "text-yellow-400"
              }`}>
                {totalWeight.toFixed(1)} / 100%
              </span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-300 ${
                  totalWeight > 100   ? "bg-red-500"   :
                  totalWeight === 100 ? "bg-green-500" : "bg-yellow-500"
                }`}
                style={{ width: `${Math.min(totalWeight, 100)}%` }}
              />
            </div>
            <p className={`text-xs ${
              totalWeight === 100 ? "text-green-400" :
              totalWeight > 100   ? "text-red-400"   : "text-yellow-400"
            }`}>
              {totalWeight === 100
                ? "✅ Poids équilibrés — scoring optimal"
                : totalWeight > 100
                ? `❌ Dépassement de ${(totalWeight - 100).toFixed(1)}% — retire ou réduis un pilier`
                : `⚠️ Il reste ${remainingBudget.toFixed(1)}% à allouer`}
            </p>
          </div>

          {/* Piliers actifs */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
            <div className="px-5 py-3 border-b border-gray-800">
              <h3 className="text-sm font-semibold text-gray-300">Piliers actifs</h3>
            </div>
            {pillars.filter((p) => p.is_active).length === 0 ? (
              <p className="px-5 py-4 text-sm text-gray-600">Aucun pilier — crée-en un ci-dessous.</p>
            ) : (
              <div className="divide-y divide-gray-800">
                {pillars.filter((p) => p.is_active).map((pillar) => (
                  <div key={pillar.id} className="flex items-center gap-3 px-5 py-3.5">
                    <div
                      className="w-8 h-8 rounded-lg flex items-center justify-center text-base shrink-0"
                      style={{ backgroundColor: `${pillar.color}20` }}
                    >
                      {pillar.icon}
                    </div>
                    <div className="flex-1">
                      <span className="text-sm text-white">{pillar.name}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-semibold" style={{ color: pillar.color }}>
                        {pillar.weight_pct}%
                      </span>
                      <button
                        onClick={() => archivePillar(pillar.id)}
                        className="text-gray-700 hover:text-red-500 transition-colors text-xs"
                      >
                        Archiver
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Formulaire nouveau pilier */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 space-y-4">
            <h3 className="text-sm font-semibold text-gray-300">Nouveau pilier</h3>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-gray-500 mb-1 block">Nom</label>
                <input
                  type="text"
                  placeholder="ex: Carrière"
                  value={pillarForm.name}
                  onChange={(e) => setPillarForm({ ...pillarForm, name: e.target.value })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-blue-500"
                />
              </div>

              <EmojiPicker
                value={pillarForm.icon}
                onChange={(emoji) => setPillarForm({ ...pillarForm, icon: emoji })}
              />

              <div>
                <label className="text-xs text-gray-500 mb-1 block">Couleur</label>
                <div className="flex gap-2 items-center">
                  <input
                    type="color"
                    value={pillarForm.color}
                    onChange={(e) => setPillarForm({ ...pillarForm, color: e.target.value })}
                    className="w-10 h-10 rounded cursor-pointer bg-transparent border-0"
                  />
                  <span className="text-xs text-gray-500">{pillarForm.color}</span>
                </div>
              </div>

              <div>
                <label className="text-xs text-gray-500 mb-1 block">
                  Poids (%) —{" "}
                  <span className={remainingBudget === 0 ? "text-red-400" : "text-gray-500"}>
                    max {remainingBudget.toFixed(1)}% disponible
                  </span>
                </label>
                <input
                  type="number"
                  min={1}
                  max={remainingBudget}
                  value={pillarForm.weight_pct}
                  onChange={(e) => setPillarForm({ ...pillarForm, weight_pct: Number(e.target.value) })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <button
              onClick={createPillar}
              disabled={totalWeight >= 100}
              className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed rounded-lg text-white text-sm font-medium transition-colors"
            >
              {totalWeight >= 100
                ? "⚠️ Budget poids épuisé (100%)"
                : `+ Ajouter le pilier (${remainingBudget.toFixed(1)}% disponible)`}
            </button>
          </div>
        </div>
      )}

      {/* ── REWARDS ── */}
      {tab === "rewards" && (
        <div className="space-y-4">
          {rewards.length > 0 && (
            <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
              <div className="px-5 py-3 border-b border-gray-800">
                <h3 className="text-sm font-semibold text-gray-300">Récompenses actives</h3>
              </div>
              <div className="divide-y divide-gray-800">
                {rewards.map((reward) => (
                  <div key={reward.id} className="flex items-center gap-3 px-5 py-3.5">
                    <div className="flex-1">
                      <span className="text-sm text-white">{reward.name}</span>
                      <div className="flex gap-2 mt-1">
                        <span className="text-xs text-gray-500 capitalize">{reward.level_required}</span>
                        <span className="text-xs text-gray-600">•</span>
                        <span className="text-xs text-gray-500 capitalize">{reward.reward_type}</span>
                        {reward.cooldown_days > 0 && (
                          <>
                            <span className="text-xs text-gray-600">•</span>
                            <span className="text-xs text-gray-500">{reward.cooldown_days}j cooldown</span>
                          </>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={() => deleteReward(reward.id)}
                      className="text-gray-700 hover:text-red-500 transition-colors text-xs"
                    >
                      Supprimer
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 space-y-4">
            <h3 className="text-sm font-semibold text-gray-300">Nouvelle récompense</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="col-span-2">
                <label className="text-xs text-gray-500 mb-1 block">Nom</label>
                <input
                  type="text"
                  placeholder="ex: Regarder un film"
                  value={rewardForm.name}
                  onChange={(e) => setRewardForm({ ...rewardForm, name: e.target.value })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="text-xs text-gray-500 mb-1 block">Niveau requis</label>
                <select
                  value={rewardForm.level_required}
                  onChange={(e) => setRewardForm({ ...rewardForm, level_required: e.target.value })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500"
                >
                  <option value="bronze">Bronze</option>
                  <option value="silver">Argent</option>
                  <option value="gold">Or</option>
                  <option value="diamond">Diamant</option>
                </select>
              </div>
              <div>
                <label className="text-xs text-gray-500 mb-1 block">Type</label>
                <select
                  value={rewardForm.reward_type}
                  onChange={(e) => setRewardForm({ ...rewardForm, reward_type: e.target.value })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500"
                >
                  <option value="consumable">Consommable</option>
                  <option value="oneshot">One-shot</option>
                </select>
              </div>
              <div className="col-span-2">
                <label className="text-xs text-gray-500 mb-1 block">Cooldown (jours, 0 = illimité)</label>
                <input
                  type="number"
                  min={0}
                  value={rewardForm.cooldown_days}
                  onChange={(e) => setRewardForm({ ...rewardForm, cooldown_days: Number(e.target.value) })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>
            <button
              onClick={createReward}
              className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 rounded-lg text-white text-sm font-medium transition-colors"
            >
              + Ajouter la récompense
            </button>
          </div>
        </div>
      )}

      {/* ── SANCTIONS ── */}
      {tab === "sanctions" && (
        <div className="space-y-4">
          {sanctions.length > 0 && (
            <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
              <div className="px-5 py-3 border-b border-gray-800">
                <h3 className="text-sm font-semibold text-gray-300">Sanctions configurées</h3>
              </div>
              <div className="divide-y divide-gray-800">
                {sanctions.map((sanction) => (
                  <div key={sanction.id} className="flex items-start gap-3 px-5 py-3.5">
                    <div className="flex-1">
                      <span className="text-sm text-white">{sanction.name}</span>
                      {sanction.description && (
                        <p className="text-xs text-gray-500 mt-0.5">{sanction.description}</p>
                      )}
                      <div className="flex gap-2 mt-1">
                        <span className="text-xs text-red-400">Seuil : {sanction.trigger_threshold}%</span>
                        <span className="text-xs text-gray-600">•</span>
                        <span className="text-xs text-gray-500">{sanction.consecutive_days} jour(s) consécutif(s)</span>
                      </div>
                    </div>
                    <button
                      onClick={() => deleteSanction(sanction.id)}
                      className="text-gray-700 hover:text-red-500 transition-colors text-xs mt-0.5"
                    >
                      Supprimer
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 space-y-4">
            <h3 className="text-sm font-semibold text-gray-300">Nouvelle sanction</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="col-span-2">
                <label className="text-xs text-gray-500 mb-1 block">Nom</label>
                <input
                  type="text"
                  placeholder="ex: Pas de réseaux sociaux"
                  value={sanctionForm.name}
                  onChange={(e) => setSanctionForm({ ...sanctionForm, name: e.target.value })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div className="col-span-2">
                <label className="text-xs text-gray-500 mb-1 block">Description</label>
                <input
                  type="text"
                  placeholder="ex: Désactiver Instagram pour 24h"
                  value={sanctionForm.description}
                  onChange={(e) => setSanctionForm({ ...sanctionForm, description: e.target.value })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="text-xs text-gray-500 mb-1 block">Seuil de déclenchement (%)</label>
                <input
                  type="number"
                  min={0}
                  max={100}
                  value={sanctionForm.trigger_threshold}
                  onChange={(e) => setSanctionForm({ ...sanctionForm, trigger_threshold: Number(e.target.value) })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="text-xs text-gray-500 mb-1 block">Jours consécutifs requis</label>
                <input
                  type="number"
                  min={1}
                  value={sanctionForm.consecutive_days}
                  onChange={(e) => setSanctionForm({ ...sanctionForm, consecutive_days: Number(e.target.value) })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>
            <button
              onClick={createSanction}
              className="w-full py-2.5 bg-red-700 hover:bg-red-800 rounded-lg text-white text-sm font-medium transition-colors"
            >
              + Ajouter la sanction
            </button>
          </div>

          {/* Backup Section */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
            <h3 className="text-sm font-semibold text-gray-300 mb-1">💾 Backup & Export</h3>
            <p className="text-xs text-gray-600 mb-4">Exporte toutes tes données en JSON.</p>
            <div className="flex gap-3">
              <a
                href={`${API}/backup/export`}
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2.5 bg-green-700 hover:bg-green-800 rounded-lg text-white text-sm font-medium transition-colors"
              >
                ⬇️ Télécharger backup JSON
              </a>
              <button
                onClick={async () => {
                  const res  = await fetch(`${API}/backup/stats`)
                  const data = await res.json()
                  alert(`📊 Stats DB:\n${Object.entries(data.data ?? data).map(([k, v]) => `${k}: ${v}`).join("\n")}`)
                }}
                className="px-4 py-2.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-gray-300 text-sm transition-colors"
              >
                📊 Stats DB
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}