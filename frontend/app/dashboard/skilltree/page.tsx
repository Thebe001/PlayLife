"use client"

import { useEffect, useState } from "react"

const API = "http://localhost:8000"

interface Skill {
  id: string
  label: string
  icon: string
  description: string
  xp_required: number
  checks_required: number
  tier: number
  unlocked: boolean
  position: { x: number; y: number }
  progress: {
    xp_current: number
    xp_required: number
    checks_current: number
    checks_required: number
  }
}

interface PillarTree {
  pillar_id: number
  pillar_name: string
  pillar_color: string
  pillar_icon: string
  xp: number
  total_checks: number
  completed_objectives: number
  skills: Skill[]
}

export default function SkillTree() {
  const [trees, setTrees]           = useState<PillarTree[]>([])
  const [selected, setSelected]     = useState<number>(0)
  const [loading, setLoading]       = useState(true)
  const [hoveredSkill, setHovered]  = useState<Skill | null>(null)

  useEffect(() => {
    fetch(`${API}/skilltree/`)
      .then((r) => r.json())
      .then((data) => {
        setTrees(data)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <div className="p-8 text-gray-500 text-sm animate-pulse">Chargement...</div>
  }

  if (trees.length === 0) {
    return (
      <div className="p-8 text-center">
        <p className="text-gray-500">Aucun pilier actif — configure tes piliers dans Settings.</p>
      </div>
    )
  }

  const tree = trees[selected]
  const color = tree.pillar_color

  // Grouper skills par tier
  const tiers = [1, 2, 3, 4]
  const byTier = (t: number) => tree.skills.filter((s) => s.tier === t)

  const unlockedCount = tree.skills.filter((s) => s.unlocked).length
  const totalCount = tree.skills.length
  const progressPct = Math.round((unlockedCount / totalCount) * 100)

  return (
    <div className="p-8 space-y-6 max-w-4xl">

      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white">🌳 Skill Tree</h2>
        <p className="text-gray-500 text-sm mt-1">Progression par pilier de vie</p>
      </div>

      {/* Pillar selector */}
      <div className="flex gap-3 flex-wrap">
        {trees.map((t, i) => (
          <button
            key={t.pillar_id}
            onClick={() => setSelected(i)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all border ${
              selected === i
                ? "text-white border-transparent"
                : "bg-gray-900 text-gray-400 border-gray-800 hover:text-white"
            }`}
            style={selected === i ? { backgroundColor: t.pillar_color, borderColor: t.pillar_color } : {}}
          >
            <span>{t.pillar_icon}</span>
            <span>{t.pillar_name}</span>
            <span
              className="text-xs px-1.5 py-0.5 rounded-full"
              style={
                selected === i
                  ? { backgroundColor: "rgba(255,255,255,0.2)", color: "white" }
                  : { backgroundColor: "#1f2937", color: "#6b7280" }
              }
            >
              {t.skills.filter((s) => s.unlocked).length}/{t.skills.length}
            </span>
          </button>
        ))}
      </div>

      {/* Stats pilier */}
      <div className="grid grid-cols-4 gap-3">
        {[
          { label: "XP Pilier",      value: tree.xp,                    color },
          { label: "Habitudes",      value: tree.total_checks,           color: "#22c55e" },
          { label: "Objectifs",      value: tree.completed_objectives,   color: "#f59e0b" },
          { label: "Skills",         value: `${unlockedCount}/${totalCount}`, color: "#a78bfa" },
        ].map((s) => (
          <div key={s.label} className="bg-gray-900 rounded-xl border border-gray-800 p-4 text-center">
            <p className="text-xs text-gray-500 mb-1">{s.label}</p>
            <p className="text-xl font-bold" style={{ color: s.color }}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* Progress bar */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
        <div className="flex justify-between text-xs text-gray-500 mb-2">
          <span>Progression du Skill Tree</span>
          <span>{progressPct}%</span>
        </div>
        <div className="w-full bg-gray-800 rounded-full h-2">
          <div
            className="h-2 rounded-full transition-all duration-700"
            style={{ width: `${progressPct}%`, backgroundColor: color }}
          />
        </div>
      </div>

      {/* Skill Tree visuel */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-6 relative">
        <div className="space-y-8">
          {tiers.map((tier) => {
            const tierSkills = byTier(tier)
            if (tierSkills.length === 0) return null

            const tierLabels: Record<number, string> = {
              1: "Débutant",
              2: "Intermédiaire",
              3: "Avancé",
              4: "Maître",
            }

            return (
              <div key={tier}>
                {/* Tier label */}
                <div className="flex items-center gap-3 mb-4">
                  <div className="h-px flex-1 bg-gray-800" />
                  <span className="text-xs text-gray-600 uppercase tracking-widest">
                    Tier {tier} — {tierLabels[tier]}
                  </span>
                  <div className="h-px flex-1 bg-gray-800" />
                </div>

                {/* Skills du tier */}
                <div className="flex justify-center gap-6 flex-wrap">
                  {tierSkills.map((skill) => (
                    <div
                      key={skill.id}
                      className="relative"
                      onMouseEnter={() => setHovered(skill)}
                      onMouseLeave={() => setHovered(null)}
                    >
                      {/* Nœud skill */}
                      <div
                        className={`w-20 h-20 rounded-2xl flex flex-col items-center justify-center gap-1 cursor-pointer transition-all duration-200 border-2 ${
                          skill.unlocked
                            ? "hover:scale-110 hover:shadow-lg"
                            : "opacity-40 grayscale"
                        }`}
                        style={{
                          backgroundColor: skill.unlocked ? `${color}20` : "#1f2937",
                          borderColor: skill.unlocked ? color : "#374151",
                          boxShadow: skill.unlocked ? `0 0 20px ${color}30` : "none",
                        }}
                      >
                        <span className="text-2xl">{skill.icon}</span>
                        <span className="text-xs text-center leading-tight px-1" style={{ color: skill.unlocked ? "white" : "#6b7280" }}>
                          {skill.label}
                        </span>
                        {skill.unlocked && (
                          <div
                            className="absolute -top-1 -right-1 w-4 h-4 rounded-full flex items-center justify-center text-xs"
                            style={{ backgroundColor: color }}
                          >
                            ✓
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>

        {/* Tooltip hover */}
        {hoveredSkill && (
          <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-50 bg-gray-800 border border-gray-700 rounded-xl p-4 w-72 shadow-2xl pointer-events-none">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-2xl">{hoveredSkill.icon}</span>
              <div>
                <p className="text-white font-semibold text-sm">{hoveredSkill.label}</p>
                <p className={`text-xs ${hoveredSkill.unlocked ? "text-green-400" : "text-gray-500"}`}>
                  {hoveredSkill.unlocked ? "✅ Débloqué" : "🔒 Verrouillé"}
                </p>
              </div>
            </div>
            <p className="text-xs text-gray-400 mb-3">{hoveredSkill.description}</p>
            {!hoveredSkill.unlocked && (
              <div className="space-y-1.5">
                <p className="text-xs text-gray-500 uppercase tracking-wider">Requis :</p>
                {hoveredSkill.xp_required > 0 && (
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">XP pilier</span>
                    <span className={hoveredSkill.progress.xp_current >= hoveredSkill.xp_required ? "text-green-400" : "text-red-400"}>
                      {hoveredSkill.progress.xp_current} / {hoveredSkill.xp_required}
                    </span>
                  </div>
                )}
                {hoveredSkill.checks_required > 0 && (
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Habitudes cochées</span>
                    <span className={hoveredSkill.progress.checks_current >= hoveredSkill.checks_required ? "text-green-400" : "text-red-400"}>
                      {hoveredSkill.progress.checks_current} / {hoveredSkill.checks_required}
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

    </div>
  )
}