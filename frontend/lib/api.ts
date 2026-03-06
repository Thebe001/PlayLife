const API = "http://localhost:8000"

// ── Helpers ────────────────────────────────────────────

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API}${path}`)
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`)
  return res.json()
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    method: "POST",
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) throw new Error(`POST ${path} failed: ${res.status}`)
  return res.json()
}

async function put<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`PUT ${path} failed: ${res.status}`)
  return res.json()
}

async function del(path: string): Promise<void> {
  const res = await fetch(`${API}${path}`, { method: "DELETE" })
  if (!res.ok) throw new Error(`DELETE ${path} failed: ${res.status}`)
}

// ── Pillars ────────────────────────────────────────────

export const getPillars = () => get("/pillars/")
export const createPillar = (data: unknown) => post("/pillars/", data)
export const deletePillar = (id: number) => del(`/pillars/${id}`)

// ── Habits ─────────────────────────────────────────────

export const getHabits = () => get("/habits/")
export const getHabitsToday = () => get("/habits/today")
export const createHabit = (data: unknown) => post("/habits/", data)
export const checkHabit = (id: number) => post(`/habits/check/${id}`)
export const uncheckHabit = (id: number) => post(`/habits/uncheck/${id}`)
export const deleteHabit = (id: number) => del(`/habits/${id}`)

// ── Score ──────────────────────────────────────────────

export const getTodaySummary = () => get("/score/today")
export const computeDailyScores = () => post("/score/daily")
export const computeGlobalScore = () => post("/score/global")

// ── Objectives ─────────────────────────────────────────

export const getObjectives = () => get("/objectives/")
export const createObjective = (data: unknown) => post("/objectives/", data)
export const deleteObjective = (id: number) => del(`/objectives/${id}`)
export const getTasks = (objectiveId: number) => get(`/objectives/${objectiveId}/tasks`)
export const createTask = (objectiveId: number, data: unknown) =>
  post(`/objectives/${objectiveId}/tasks`, data)
export const checkTask = (taskId: number) => post(`/tasks/${taskId}/check`)

// ── Journal ────────────────────────────────────────────

export const getJournalEntries = () => get("/journal/")
export const createJournalEntry = (data: unknown) => post("/journal/", data)

// ── Reviews ────────────────────────────────────────────

export const getReviews = () => get("/reviews/")
export const generateWeeklyReview = () => post("/reviews/generate/weekly")
export const generateMonthlyReview = () => post("/reviews/generate/monthly")
export const updateReview = (id: number, data: unknown) => put(`/reviews/${id}`, data)
export const deleteReview = (id: number) => del(`/reviews/${id}`)

// ── Gamification ───────────────────────────────────────

export const getGamificationSummary = () => get("/gamification/summary")
export const checkBadges = () => post("/gamification/badges/check")
export const addXP = (amount: number) => post(`/gamification/xp/${amount}`)

// ── Rewards & Sanctions ────────────────────────────────

export const getRewards = () => get("/rewards/")
export const createReward = (data: unknown) => post("/rewards/", data)
export const consumeReward = (id: number) => post(`/rewards/${id}/consume`)
export const deleteReward = (id: number) => del(`/rewards/${id}`)

export const getSanctions = () => get("/rewards/sanctions/")
export const createSanction = (data: unknown) => post("/rewards/sanctions/", data)
export const deleteSanction = (id: number) => del(`/rewards/sanctions/${id}`)
export const getActiveSanctions = () => get("/rewards/sanctions/active")

// ── Stats ──────────────────────────────────────────────

export const getHeatmap = () => get("/stats/heatmap")
export const getProgression = (days: number) => get(`/stats/progression?days=${days}`)
export const getOverview = () => get("/stats/overview")

// ── Voice & AI ─────────────────────────────────────────

export const sendVoiceCommand = (text: string) =>
  post("/voice/command", { text })

export const getDailyAdvice = () => get("/voice/advice")

// ── Backup ─────────────────────────────────────────────

export const getBackupStats = () => get("/backup/stats")
export const getBackupExportUrl = () => `${API}/backup/export`