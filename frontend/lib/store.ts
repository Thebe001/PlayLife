import { create } from "zustand"
import { API } from "./api"

// ── Types ──────────────────────────────────────────────

interface PillarScore {
  pillar_id: number
  pillar_name: string
  pillar_color: string
  score_pct: number
  points_earned: number
  points_max: number
}

interface TodaySummary {
  date: string
  global_score: number
  xp_today: number
  pillars: PillarScore[]
}

interface Pillar {
  id: number
  name: string
  icon: string
  color: string
  weight_pct: number
}

interface GamificationSummary {
  total_xp: number
  level: { name: string; min_xp: number; max_xp: number }
  streak: number
  badges: { id: number; name: string; icon: string; description: string; unlocked_at: string }[]
}

interface AppStore {
  // State
  todaySummary: TodaySummary | null
  pillars: Pillar[]
  gamification: GamificationSummary | null
  isRefreshing: boolean

  // Actions
  fetchTodaySummary: () => Promise<void>
  fetchPillars: () => Promise<void>
  fetchGamification: () => Promise<void>
  refreshScores: () => Promise<void>
}

// ── Store ──────────────────────────────────────────────

export const useAppStore = create<AppStore>((set) => ({
  todaySummary: null,
  pillars: [],
  gamification: null,
  isRefreshing: false,

  fetchTodaySummary: async () => {
    try {
      const res = await fetch(`${API}/score/today`)
      if (!res.ok) return
      const data = await res.json()
      set({ todaySummary: data })
    } catch (e) {
      console.error("fetchTodaySummary:", e)
    }
  },

  fetchPillars: async () => {
    try {
      const res = await fetch(`${API}/pillars/`)
      if (!res.ok) return
      const data = await res.json()
      set({ pillars: data })
    } catch (e) {
      console.error("fetchPillars:", e)
    }
  },

  fetchGamification: async () => {
    try {
      const res = await fetch(`${API}/gamification/summary`)
      if (!res.ok) return
      const data = await res.json()
      set({ gamification: data })
    } catch (e) {
      console.error("fetchGamification:", e)
    }
  },

  refreshScores: async () => {
    set({ isRefreshing: true })
    try {
      await fetch(`${API}/score/daily`, { method: "POST" })
      await fetch(`${API}/score/global`, { method: "POST" })
      const res = await fetch(`${API}/score/today`)
      if (res.ok) {
        const data = await res.json()
        set({ todaySummary: data })
      }
    } catch (e) {
      console.error("refreshScores:", e)
    } finally {
      set({ isRefreshing: false })
    }
  },
}))