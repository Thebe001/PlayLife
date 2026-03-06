"use client"

import { useEffect, useState } from "react"
import { API } from "@/lib/api"

interface Task {
  id: number
  title: string
  points: number
  difficulty: string
  status: string
  due_date: string | null
  objective_id: number | null
  pillar_id: number
}

interface Objective {
  id: number
  pillar_id: number
  title: string
  description: string | null
  horizon: string
  deadline: string | null
  completion_pct: number
  status: string
  tasks?: Task[]
}

interface Pillar {
  id: number
  name: string
  icon: string
  color: string
}

interface NewObjForm {
  title: string
  description: string
  pillar_id: number
  horizon: string
  deadline: string
}

interface NewTaskForm {
  title: string
  points: number
  difficulty: string
}

interface XPToast {
  id: number
  message: string
}

export default function Objectives() {
  const [objectives, setObjectives]   = useState<Objective[]>([])
  const [pillars, setPillars]         = useState<Pillar[]>([])
  const [loading, setLoading]         = useState(true)
  const [error, setError]             = useState<string | null>(null)
  const [showForm, setShowForm]       = useState(false)
  const [expandedId, setExpandedId]   = useState<number | null>(null)
  const [taskForms, setTaskForms]     = useState<Record<number, NewTaskForm>>({})
  const [showTaskForm, setShowTaskForm] = useState<number | null>(null)
  const [toasts, setToasts]           = useState<XPToast[]>([])

  const [form, setForm] = useState<NewObjForm>({
    title: "",
    description: "",
    pillar_id: 1,
    horizon: "monthly",
    deadline: "",
  })

  // ── Toast helpers ────────────────────────────────────────────────────────
  const addToast = (message: string) => {
    const id = Date.now()
    setToasts((prev) => [...prev, { id, message }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 3500)
  }

  // ── Data fetching ─────────────────────────────────────────────────────────
  const fetchAll = async () => {
    try {
      const [objRes, pillarRes] = await Promise.all([
        fetch(`${API}/objectives/`),
        fetch(`${API}/pillars/`),
      ])
      if (!objRes.ok || !pillarRes.ok) throw new Error("fetch failed")
      const objs: Objective[]  = await objRes.json()
      const pils: Pillar[]     = await pillarRes.json()

      // Charger les tâches de chaque objectif en parallèle
      const objsWithTasks = await Promise.all(
        objs.map(async (obj) => {
          const res  = await fetch(`${API}/objectives/${obj.id}`)
          const data = await res.json()
          return { ...obj, tasks: data.tasks ?? [] }
        })
      )

      setObjectives(objsWithTasks)
      setPillars(pils)
    } catch {
      setError("Impossible de charger les objectifs.")
    }
    setLoading(false)
  }

  useEffect(() => { fetchAll() }, [])

  // ── Actions ───────────────────────────────────────────────────────────────

  const createObjective = async () => {
    if (!form.title.trim()) return
    const res = await fetch(`${API}/objectives/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...form,
        pillar_id: Number(form.pillar_id),
        deadline: form.deadline || null,
      }),
    })
    if (!res.ok) return
    setShowForm(false)
    setForm({ title: "", description: "", pillar_id: pillars[0]?.id ?? 1, horizon: "monthly", deadline: "" })
    await fetchAll()
  }

  const createTask = async (objId: number) => {
    const tf = taskForms[objId]
    if (!tf?.title?.trim()) return
    await fetch(`${API}/objectives/tasks/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        objective_id: objId,
        pillar_id: objectives.find((o) => o.id === objId)?.pillar_id ?? 1,
        title: tf.title,
        points: tf.points ?? 20,
        difficulty: tf.difficulty ?? "medium",
      }),
    })
    setShowTaskForm(null)
    setTaskForms((prev) => ({ ...prev, [objId]: { title: "", points: 20, difficulty: "medium" } }))
    await fetchAll()
  }

  const completeTask = async (taskId: number, taskTitle: string) => {
    const res  = await fetch(`${API}/objectives/tasks/${taskId}/complete`, { method: "PATCH" })
    const data = await res.json()

    if (res.ok && data.xp_earned > 0) {
      if (data.objective_completed) {
        addToast(`🏆 Objectif complété ! +${data.xp_earned} XP (dont +100 bonus)`)
      } else {
        addToast(`⚡ "${taskTitle}" — +${data.xp_earned} XP`)
      }
    }

    await fetchAll()
  }

  const deleteObjective = async (objId: number) => {
    await fetch(`${API}/objectives/${objId}`, { method: "DELETE" })
    await fetchAll()
  }

  // ── Labels ────────────────────────────────────────────────────────────────

  const horizonLabel: Record<string, string> = {
    weekly:  "📅 Hebdo",
    monthly: "🗓️ Mensuel",
    yearly:  "🏔️ Annuel",
  }

  if (loading) {
    return <div className="p-8 text-gray-500 text-sm animate-pulse">Chargement...</div>
  }

  return (
    <div className="p-8 space-y-6 max-w-3xl">

      {/* XP Toasts */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 pointer-events-none">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className="bg-gray-900 border border-purple-700/50 text-purple-300 px-4 py-3 rounded-xl text-sm shadow-xl animate-pulse"
          >
            {toast.message}
          </div>
        ))}
      </div>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">🎯 Objectifs</h2>
          <p className="text-gray-500 text-sm mt-1">
            {objectives.filter((o) => o.status !== "completed").length} objectif(s) actif(s)
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white text-sm font-medium transition-colors"
        >
          + Nouvel objectif
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="px-4 py-3 rounded-xl text-sm border bg-red-900/20 border-red-800/40 text-red-400">
          {error}
        </div>
      )}

      {/* Create Form */}
      {showForm && (
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 space-y-4">
          <h3 className="text-sm font-semibold text-gray-300">Nouvel objectif</h3>

          <input
            type="text"
            placeholder="Titre de l'objectif..."
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-blue-500"
          />

          <textarea
            placeholder="Description (optionnel)..."
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            rows={2}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-blue-500 resize-none"
          />

          <div className="grid grid-cols-3 gap-3">
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

            <div>
              <label className="text-xs text-gray-500 mb-1 block">Horizon</label>
              <select
                value={form.horizon}
                onChange={(e) => setForm({ ...form, horizon: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
              >
                <option value="weekly">Hebdomadaire</option>
                <option value="monthly">Mensuel</option>
                <option value="yearly">Annuel</option>
              </select>
            </div>

            <div>
              <label className="text-xs text-gray-500 mb-1 block">Deadline</label>
              <input
                type="date"
                value={form.deadline}
                onChange={(e) => setForm({ ...form, deadline: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={createObjective}
              className="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 rounded-lg text-white text-sm font-medium transition-colors"
            >
              Créer
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

      {/* Objectives List */}
      {objectives.length === 0 ? (
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-10 text-center">
          <p className="text-gray-600 text-sm">Aucun objectif pour l&apos;instant.</p>
          <p className="text-gray-700 text-xs mt-1">Crée ton premier objectif !</p>
        </div>
      ) : (
        <div className="space-y-3">
          {objectives.map((obj) => {
            const pillar     = pillars.find((p) => p.id === obj.pillar_id)
            const isExpanded = expandedId === obj.id
            const tasks      = obj.tasks ?? []
            const doneTasks  = tasks.filter((t) => t.status === "done").length
            const tf         = taskForms[obj.id] ?? { title: "", points: 20, difficulty: "medium" }
            const totalXP    = tasks.reduce((sum, t) => sum + (t.points ?? 0), 0)

            return (
              <div
                key={obj.id}
                className={`bg-gray-900 rounded-xl border overflow-hidden transition-colors ${
                  obj.status === "completed"
                    ? "border-green-800/50"
                    : "border-gray-800"
                }`}
              >
                {/* Objective Header */}
                <div
                  className="px-5 py-4 cursor-pointer hover:bg-gray-800/40 transition-colors"
                  onClick={() => setExpandedId(isExpanded ? null : obj.id)}
                >
                  <div className="flex items-start gap-3">

                    {/* Progress ring */}
                    <div className="relative shrink-0 mt-0.5">
                      <svg className="w-10 h-10 -rotate-90" viewBox="0 0 36 36">
                        <circle cx="18" cy="18" r="15" fill="none" stroke="#1f2937" strokeWidth="3" />
                        <circle
                          cx="18" cy="18" r="15"
                          fill="none"
                          stroke={obj.status === "completed" ? "#22c55e" : (pillar?.color ?? "#3b82f6")}
                          strokeWidth="3"
                          strokeDasharray={`${(obj.completion_pct / 100) * 94} 94`}
                          strokeLinecap="round"
                        />
                      </svg>
                      <span className="absolute inset-0 flex items-center justify-center text-xs font-bold text-white">
                        {obj.status === "completed" ? "✓" : `${Math.round(obj.completion_pct)}%`}
                      </span>
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={`font-medium text-sm ${obj.status === "completed" ? "text-green-400" : "text-white"}`}>
                          {obj.title}
                        </span>
                        <span className="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-400">
                          {horizonLabel[obj.horizon]}
                        </span>
                        {pillar && (
                          <span
                            className="text-xs px-2 py-0.5 rounded"
                            style={{ backgroundColor: `${pillar.color}20`, color: pillar.color }}
                          >
                            {pillar.icon} {pillar.name}
                          </span>
                        )}
                        {obj.status === "completed" && (
                          <span className="text-xs px-2 py-0.5 rounded bg-green-900/30 text-green-400">
                            ✅ Complété
                          </span>
                        )}
                      </div>

                      {obj.description && (
                        <p className="text-xs text-gray-500 mt-1 truncate">{obj.description}</p>
                      )}

                      <div className="flex items-center gap-3 mt-1.5">
                        <span className="text-xs text-gray-600">{doneTasks}/{tasks.length} tâches</span>
                        {totalXP > 0 && (
                          <span className="text-xs text-purple-400">⚡ {totalXP} XP potentiel</span>
                        )}
                        {obj.deadline && (
                          <span className="text-xs text-gray-600">
                            📅 {new Date(obj.deadline).toLocaleDateString("fr-FR")}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2 shrink-0">
                      <span className="text-gray-600 text-xs">{isExpanded ? "▲" : "▼"}</span>
                      <button
                        onClick={(e) => { e.stopPropagation(); deleteObjective(obj.id) }}
                        className="text-gray-700 hover:text-red-500 transition-colors text-xs px-2"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                </div>

                {/* Tasks (expanded) */}
                {isExpanded && (
                  <div className="border-t border-gray-800">
                    {tasks.length === 0 && (
                      <p className="px-5 py-3 text-xs text-gray-600">Aucune sous-tâche — ajoutes-en une.</p>
                    )}

                    {tasks.map((task) => (
                      <div
                        key={task.id}
                        className={`flex items-center gap-3 px-5 py-3 border-b border-gray-800/50 ${
                          task.status === "done" ? "opacity-50" : ""
                        }`}
                      >
                        <button
                          onClick={() => task.status !== "done" && completeTask(task.id, task.title)}
                          disabled={task.status === "done"}
                          className={`w-4 h-4 rounded border flex items-center justify-center shrink-0 transition-all ${
                            task.status === "done"
                              ? "bg-green-500 border-green-500 cursor-default"
                              : "border-gray-600 hover:border-green-500 cursor-pointer"
                          }`}
                        >
                          {task.status === "done" && (
                            <svg className="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                            </svg>
                          )}
                        </button>

                        <span className={`text-sm flex-1 ${task.status === "done" ? "line-through text-gray-500" : "text-gray-300"}`}>
                          {task.title}
                        </span>

                        <div className="flex items-center gap-2">
                          <span className="text-xs text-purple-400">⚡ +{task.points} XP</span>
                          <span className="text-xs text-green-400">+{task.points} pts</span>
                        </div>
                      </div>
                    ))}

                    {/* Add task form */}
                    {showTaskForm === obj.id ? (
                      <div className="px-5 py-3 space-y-2">
                        <input
                          type="text"
                          placeholder="Titre de la tâche..."
                          value={tf.title}
                          onChange={(e) =>
                            setTaskForms((prev) => ({ ...prev, [obj.id]: { ...tf, title: e.target.value } }))
                          }
                          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-blue-500"
                        />
                        <div className="flex gap-2">
                          <div className="flex flex-col gap-1">
                            <span className="text-xs text-gray-500">Points / XP</span>
                            <input
                              type="number"
                              min={1}
                              max={200}
                              value={tf.points}
                              onChange={(e) =>
                                setTaskForms((prev) => ({ ...prev, [obj.id]: { ...tf, points: Number(e.target.value) } }))
                              }
                              className="w-24 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
                            />
                          </div>
                          <button
                            onClick={() => createTask(obj.id)}
                            className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white text-sm transition-colors self-end"
                          >
                            Ajouter
                          </button>
                          <button
                            onClick={() => setShowTaskForm(null)}
                            className="px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-gray-400 text-sm transition-colors self-end"
                          >
                            ✕
                          </button>
                        </div>
                        <p className="text-xs text-gray-600">
                          💡 Ces points seront convertis en XP à la complétion de la tâche.
                          Objectif complété = +100 XP bonus supplémentaire.
                        </p>
                      </div>
                    ) : (
                      <button
                        onClick={() => setShowTaskForm(obj.id)}
                        className="w-full px-5 py-3 text-left text-xs text-gray-600 hover:text-blue-400 transition-colors"
                      >
                        + Ajouter une sous-tâche
                      </button>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}