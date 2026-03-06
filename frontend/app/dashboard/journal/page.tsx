"use client"

import { useEffect, useState } from "react"
import { API } from "@/lib/api"

interface JournalEntry {
  id: number
  date: string
  content: string
  mood: number
  energy: number
  tags: string
  highlight: string
}

const MOOD_LABELS = ["", "😞", "😕", "😐", "🙂", "😄"]
const ENERGY_LABELS = ["", "🔋", "🔋🔋", "🔋🔋🔋", "⚡", "⚡⚡"]
const TAGS_OPTIONS = ["productif", "stressé", "motivé", "fatigué", "focus", "social", "créatif", "calme"]

export default function Journal() {
  const [entries, setEntries] = useState<JournalEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [view, setView] = useState<"write" | "history">("write")

  const today = new Date().toISOString().split("T")[0]

  const [form, setForm] = useState({
    content: "",
    mood: 3,
    energy: 3,
    highlight: "",
    tags: [] as string[],
  })

  const fetchEntries = async () => {
    try {
      const res = await fetch(`${API}/journal/`)
      if (!res.ok) throw new Error(`${res.status}`)
      const data = await res.json()
      setEntries(data)
    } catch {
      setError("Impossible de charger le journal.")
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchEntries()
  }, [])

  const toggleTag = (tag: string) => {
    setForm((prev) => ({
      ...prev,
      tags: prev.tags.includes(tag)
        ? prev.tags.filter((t) => t !== tag)
        : [...prev.tags, tag],
    }))
  }

  const saveEntry = async () => {
    if (!form.content.trim()) return
    try {
      await fetch(`${API}/journal/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          date: today,
          content: form.content,
          mood: form.mood,
          energy: form.energy,
          highlight: form.highlight,
          tags: form.tags.join(","),
        }),
      })
      setForm({ content: "", mood: 3, energy: 3, highlight: "", tags: [] })
      await fetchEntries()
      setView("history")
    } catch {
      setError("Erreur lors de la sauvegarde.")
    }
  }

  const todayEntry = entries.find((e) => e.date === today)

  if (loading) {
    return <div className="p-8 text-gray-500 text-sm animate-pulse">Chargement...</div>
  }

  if (error) {
    return <div className="p-8 text-red-400 text-sm">{error}</div>
  }

  return (
    <div className="p-8 space-y-6 max-w-3xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">📓 Journal</h2>
          <p className="text-gray-500 text-sm mt-1">
            {new Date().toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long" })}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setView("write")}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${
              view === "write" ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-400 hover:text-white"
            }`}
          >
            ✍️ Écrire
          </button>
          <button
            onClick={() => setView("history")}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${
              view === "history" ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-400 hover:text-white"
            }`}
          >
            📚 Historique
          </button>
        </div>
      </div>

      {/* Write View */}
      {view === "write" && (
        <div className="space-y-4">
          {todayEntry && (
            <div className="bg-yellow-900/20 border border-yellow-800/40 rounded-xl px-4 py-3 text-sm text-yellow-400">
              ⚠️ Tu as déjà écrit aujourd'hui. Une nouvelle entrée s'ajoutera à l'historique.
            </div>
          )}

          {/* Mood & Energy */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
              <p className="text-xs text-gray-500 mb-3 uppercase tracking-wider">Humeur</p>
              <div className="flex gap-2 justify-between">
                {[1, 2, 3, 4, 5].map((val) => (
                  <button
                    key={val}
                    onClick={() => setForm({ ...form, mood: val })}
                    className={`text-2xl transition-all ${
                      form.mood === val ? "scale-125" : "opacity-40 hover:opacity-70"
                    }`}
                  >
                    {MOOD_LABELS[val]}
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
              <p className="text-xs text-gray-500 mb-3 uppercase tracking-wider">Énergie</p>
              <div className="flex gap-2 justify-between">
                {[1, 2, 3, 4, 5].map((val) => (
                  <button
                    key={val}
                    onClick={() => setForm({ ...form, energy: val })}
                    className={`text-2xl transition-all ${
                      form.energy === val ? "scale-125" : "opacity-40 hover:opacity-70"
                    }`}
                  >
                    {ENERGY_LABELS[val]}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Tags */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
            <p className="text-xs text-gray-500 mb-3 uppercase tracking-wider">Tags</p>
            <div className="flex flex-wrap gap-2">
              {TAGS_OPTIONS.map((tag) => (
                <button
                  key={tag}
                  onClick={() => toggleTag(tag)}
                  className={`px-3 py-1.5 rounded-full text-xs transition-all ${
                    form.tags.includes(tag)
                      ? "bg-blue-600 text-white"
                      : "bg-gray-800 text-gray-400 hover:bg-gray-700"
                  }`}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>

          {/* Highlight */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
            <p className="text-xs text-gray-500 mb-2 uppercase tracking-wider">✨ Highlight du jour</p>
            <input
              type="text"
              placeholder="La meilleure chose accomplie aujourd'hui..."
              value={form.highlight}
              onChange={(e) => setForm({ ...form, highlight: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Content */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
            <p className="text-xs text-gray-500 mb-2 uppercase tracking-wider">📝 Notes libres</p>
            <textarea
              placeholder="Comment s'est passée ta journée ? Qu'est-ce que tu as appris ? Comment tu te sens ?"
              value={form.content}
              onChange={(e) => setForm({ ...form, content: e.target.value })}
              rows={6}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-blue-500 resize-none"
            />
          </div>

          <button
            onClick={saveEntry}
            disabled={!form.content.trim()}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed rounded-xl text-white text-sm font-medium transition-colors"
          >
            💾 Sauvegarder l'entrée
          </button>
        </div>
      )}

      {/* History View */}
      {view === "history" && (
        <div className="space-y-3">
          {entries.length === 0 ? (
            <div className="bg-gray-900 rounded-xl border border-gray-800 p-10 text-center">
              <p className="text-gray-600 text-sm">Aucune entrée pour l'instant.</p>
            </div>
          ) : (
            [...entries].reverse().map((entry) => (
              <div key={entry.id} className="bg-gray-900 rounded-xl border border-gray-800 p-5 space-y-3">
                {/* Date + mood */}
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">
                    {new Date(entry.date).toLocaleDateString("fr-FR", {
                      weekday: "long", day: "numeric", month: "long"
                    })}
                  </span>
                  <div className="flex items-center gap-3">
                    <span className="text-lg">{MOOD_LABELS[entry.mood]}</span>
                    <span className="text-sm">{ENERGY_LABELS[entry.energy]}</span>
                  </div>
                </div>

                {/* Highlight */}
                {entry.highlight && (
                  <div className="bg-yellow-900/20 border border-yellow-800/30 rounded-lg px-3 py-2">
                    <span className="text-xs text-yellow-400">✨ {entry.highlight}</span>
                  </div>
                )}

                {/* Content */}
                <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">
                  {entry.content}
                </p>

                {/* Tags */}
                {entry.tags && (
                  <div className="flex flex-wrap gap-1.5">
                    {entry.tags.split(",").filter(Boolean).map((tag) => (
                      <span key={tag} className="px-2 py-1 bg-gray-800 rounded-full text-xs text-gray-400">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}