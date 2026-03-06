import { create } from "zustand"

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

interface AppStore {
  todaySummary: TodaySummary | null
  pillars: Pillar[]
  fetchTodaySummary: () => Promise<void>
  fetchPillars: () => Promise<void>
}

const API = "http://localhost:8000"

export const useAppStore = create<AppStore>((set) => ({
  todaySummary: null,
  pillars: [],

  fetchTodaySummary: async () => {
    const res = await fetch(`${API}/score/today`)
    const data = await res.json()
    set({ todaySummary: data })
  },

  fetchPillars: async () => {
    const res = await fetch(`${API}/pillars/`)
    const data = await res.json()
    set({ pillars: data })
  },
}))