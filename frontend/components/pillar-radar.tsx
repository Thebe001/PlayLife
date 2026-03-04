"use client"

import { useEffect, useState } from "react"
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  ResponsiveContainer
} from "recharts"

type Pillar = {
  id: number
  name: string
  weight_pct: number
}

export default function PillarRadar() {

  const [data, setData] = useState<any[]>([])

  useEffect(() => {

    fetch("http://localhost:8000/pillars")
      .then(res => res.json())
      .then(pillars => {

        const chartData = pillars.map((p: Pillar) => ({
          pillar: p.name,
          score: p.weight_pct
        }))

        setData(chartData)

      })

  }, [])

  return (

    <div className="h-[300px] w-full">

      <ResponsiveContainer>

        <RadarChart data={data}>

          <PolarGrid />

          <PolarAngleAxis dataKey="pillar" />

          <Radar
            name="Score"
            dataKey="score"
            stroke="#2563eb"
            fill="#3b82f6"
            fillOpacity={0.6}
          />

        </RadarChart>

      </ResponsiveContainer>

    </div>

  )
}