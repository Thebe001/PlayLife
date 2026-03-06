"use client"

import { useEffect, useState } from "react"
import { API } from "@/lib/api"

interface Review {
  id: number
  type: string
  period_start: string
  period_end: string
  content: string
  edited_content: string | null
  llm_generated: boolean
}

export default function Reviews() {
  const [reviews, setReviews] = useState<Review[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState<string | null>(null)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editContent, setEditContent] = useState("")
  const [error, setError] = useState<string | null>(null)

  const fetchReviews = async () => {
    try {
      const res = await fetch(`${API}/reviews/`)
      if (res.ok) setReviews(await res.json())
    } catch {
      setError("Impossible de charger les reviews.")
    }
    setLoading(false)
  }

  useEffect(() => { fetchReviews() }, [])

  const generate = async (type: "weekly" | "monthly") => {
    setGenerating(type)
    setError(null)
    try {
      const res = await fetch(`${API}/reviews/generate/${type}`, { method: "POST" })
      if (!res.ok) {
        const json = await res.json()
        setError(json.detail ?? "Erreur lors de la génération.")
      } else {
        await fetchReviews()
      }
    } catch {
      setError("Erreur réseau. Le backend est-il lancé ?")
    }
    setGenerating(null)
  }

  const saveEdit = async (review: Review) => {
    await fetch(`${API}/reviews/${review.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        type: review.type,
        period_start: review.period_start,
        period_end: review.period_end,
        content: review.content,
        edited_content: editContent,
      }),
    })
    setEditingId(null)
    await fetchReviews()
  }

  const deleteReview = async (id: number) => {
    await fetch(`${API}/reviews/${id}`, { method: "DELETE" })
    await fetchReviews()
  }

  const typeLabel: Record<string, string> = {
    weekly: "📅 Hebdomadaire",
    monthly: "🗓️ Mensuelle",
    yearly: "🏔️ Annuelle",
  }

  const typeColor: Record<string, string> = {
    weekly: "#3b82f6",
    monthly: "#a78bfa",
    yearly: "#f59e0b",
  }

  if (loading) return (
    <div className="p-8 text-gray-500 text-sm animate-pulse">Chargement...</div>
  )

  return (
    <div className="p-8 space-y-6 max-w-3xl">

      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white">📊 Reviews</h2>
        <p className="text-gray-500 text-sm mt-1">Bilans hebdomadaires et mensuels générés par IA</p>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-900/20 border border-red-800/40 rounded-xl px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Generate buttons */}
      <div className="flex gap-3">
        <button
          onClick={() => generate("weekly")}
          disabled={!!generating}
          className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg text-white text-sm font-medium transition-colors flex items-center gap-2"
        >
          {generating === "weekly" ? (
            <>
              <span className="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin" />
              Génération...
            </>
          ) : "📅 Générer review hebdo"}
        </button>
        <button
          onClick={() => generate("monthly")}
          disabled={!!generating}
          className="px-4 py-2.5 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-lg text-white text-sm font-medium transition-colors flex items-center gap-2"
        >
          {generating === "monthly" ? (
            <>
              <span className="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin" />
              Génération...
            </>
          ) : "🗓️ Générer review mensuelle"}
        </button>
      </div>

      {/* Info Ollama */}
      <p className="text-xs text-gray-600">
        💡 La génération utilise Ollama (Mistral) en local. Si Ollama est off, un bilan statistique est généré automatiquement.
      </p>

      {/* Reviews list */}
      {reviews.length === 0 ? (
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-10 text-center">
          <p className="text-gray-600 text-sm">Aucune review — génères-en une !</p>
        </div>
      ) : (
        <div className="space-y-4">
          {reviews.map((review) => {
            const isEditing = editingId === review.id
            const displayContent = review.edited_content || review.content

            return (
              <div key={review.id} className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">

                {/* Header */}
                <div className="px-5 py-3.5 border-b border-gray-800 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span
                      className="text-xs font-semibold px-2.5 py-1 rounded-full"
                      style={{
                        backgroundColor: `${typeColor[review.type] ?? "#6b7280"}20`,
                        color: typeColor[review.type] ?? "#6b7280",
                      }}
                    >
                      {typeLabel[review.type] ?? review.type}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(review.period_start).toLocaleDateString("fr-FR")}
                      {" → "}
                      {new Date(review.period_end).toLocaleDateString("fr-FR")}
                    </span>
                    {review.llm_generated && (
                      <span className="text-xs text-purple-400">🤖 IA</span>
                    )}
                    {review.edited_content && (
                      <span className="text-xs text-green-500">✏️ Modifiée</span>
                    )}
                  </div>
                  <div className="flex gap-3">
                    {!isEditing && (
                      <button
                        onClick={() => { setEditingId(review.id); setEditContent(displayContent) }}
                        className="text-xs text-gray-500 hover:text-blue-400 transition-colors"
                      >
                        Éditer
                      </button>
                    )}
                    <button
                      onClick={() => deleteReview(review.id)}
                      className="text-xs text-gray-700 hover:text-red-500 transition-colors"
                    >
                      ✕
                    </button>
                  </div>
                </div>

                {/* Content */}
                <div className="px-5 py-4">
                  {isEditing ? (
                    <div className="space-y-3">
                      <textarea
                        value={editContent}
                        onChange={(e) => setEditContent(e.target.value)}
                        rows={14}
                        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm font-mono focus:outline-none focus:border-blue-500 resize-none"
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={() => saveEdit(review)}
                          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white text-sm transition-colors"
                        >
                          💾 Sauvegarder
                        </button>
                        <button
                          onClick={() => setEditingId(null)}
                          className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-gray-400 text-sm transition-colors"
                        >
                          Annuler
                        </button>
                      </div>
                    </div>
                  ) : (
                    <pre className="text-sm text-gray-300 whitespace-pre-wrap font-sans leading-relaxed">
                      {displayContent}
                    </pre>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}