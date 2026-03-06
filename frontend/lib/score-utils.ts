/**
 * Utilitaires de score — source unique de vérité pour les seuils.
 * Cahier des charges : Bronze ≥ 60% | Argent ≥ 75% | Or ≥ 90% | Diamant ≥ 98%
 */

export type ScoreTier = "Diamant" | "Or" | "Argent" | "Bronze" | "Danger"

export const SCORE_TIERS: { label: ScoreTier; min: number; color: string; emoji: string }[] = [
  { label: "Diamant", min: 98, color: "#b9f2ff", emoji: "💎" },
  { label: "Or",      min: 90, color: "#ffd700", emoji: "🥇" },
  { label: "Argent",  min: 75, color: "#a78bfa", emoji: "🥈" },
  { label: "Bronze",  min: 60, color: "#cd7f32", emoji: "🥉" },
  { label: "Danger",  min: 0,  color: "#ef4444", emoji: "❌" },
]

export function getScoreTier(score: number) {
  return SCORE_TIERS.find((t) => score >= t.min) ?? SCORE_TIERS[SCORE_TIERS.length - 1]
}

export function getScoreColor(score: number): string {
  return getScoreTier(score).color
}

export function getScoreLabel(score: number): string {
  const t = getScoreTier(score)
  return `${t.emoji} ${t.label}`
}