import { create } from "zustand"
import {
  getTodaySummary,
  computeDailyScores,
  computeGlobalScore,
  getPillars,
  getGamificationSummary,
} from "./api"

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
  todaySummary: TodaySummary | null
  pillars: Pillar[]
  gamification: GamificationSummary | null
  isRefreshing: boolean

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
      const data = await getTodaySummary()
      set({ todaySummary: data as TodaySummary })
    } catch (e) {
      console.error("fetchTodaySummary:", e)
    }
  },

  fetchPillars: async () => {
    try {
      const data = await getPillars()
      set({ pillars: data as Pillar[] })
    } catch (e) {
      console.error("fetchPillars:", e)
    }
  },

  fetchGamification: async () => {
    try {
      const data = await getGamificationSummary()
      set({ gamification: data as GamificationSummary })
    } catch (e) {
      console.error("fetchGamification:", e)
    }
  },

  refreshScores: async () => {
    set({ isRefreshing: true })
    try {
      await computeDailyScores()
      await computeGlobalScore()
      const data = await getTodaySummary()
      set({ todaySummary: data as TodaySummary })
    } catch (e) {
      console.error("refreshScores:", e)
    } finally {
      set({ isRefreshing: false })
    }
  },
}))