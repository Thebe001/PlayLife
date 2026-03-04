const API_URL = "http://localhost:8000"


export async function getPillars() {

  const res = await fetch(`${API_URL}/pillars/`)

  return res.json()

}


export async function getHabits() {

  const res = await fetch(`${API_URL}/habits/`)

  return res.json()

}


export async function getScore() {

  const res = await fetch(`${API_URL}/score/global`)

  return res.json()

}