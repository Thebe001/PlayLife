"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

const FEATURES = [
  { icon: "🏛️", title: "Piliers de Vie",       desc: "Définis tes sphères fondamentales avec des poids configurables." },
  { icon: "⚡", title: "Scoring Engine",        desc: "Un score global calculé en temps réel à chaque action." },
  { icon: "🏆", title: "Gamification",          desc: "XP, niveaux, badges, streaks — ta vie comme un RPG." },
  { icon: "🎁", title: "Rewards & Sanctions",   desc: "Récompense tes succès. Assume tes échecs." },
  { icon: "🤖", title: "Assistant IA",          desc: "Commandes vocales via Whisper + Ollama en local." },
  { icon: "📓", title: "Journal & Reviews",     desc: "Mood tracking, bilans hebdo et mensuels auto-générés." },
]

const STATS = [
  { value: "6",    label: "Modules"         },
  { value: "100%", label: "Local & Privé"   },
  { value: "∞",    label: "Personnalisable" },
]

export default function Home() {
  const router = useRouter()
  const [mounted, setMounted] = useState(false)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    setMounted(true)
    const t = setTimeout(() => setVisible(true), 100)
    return () => clearTimeout(t)
  }, [])

  if (!mounted) return null

  return (
    <div className="min-h-screen bg-gray-950 text-white overflow-x-hidden">

      {/* Ambient background blobs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div
          className="absolute -top-40 -left-40 w-96 h-96 rounded-full opacity-20"
          style={{
            background: "radial-gradient(circle, #3b82f6 0%, transparent 70%)",
            animation: "float1 8s ease-in-out infinite",
          }}
        />
        <div
          className="absolute top-1/2 -right-40 w-80 h-80 rounded-full opacity-10"
          style={{
            background: "radial-gradient(circle, #a78bfa 0%, transparent 70%)",
            animation: "float2 10s ease-in-out infinite",
          }}
        />
        <div
          className="absolute -bottom-20 left-1/3 w-72 h-72 rounded-full opacity-10"
          style={{
            background: "radial-gradient(circle, #22c55e 0%, transparent 70%)",
            animation: "float1 12s ease-in-out infinite reverse",
          }}
        />
      </div>

      {/* CSS animations */}
      <style>{`
        @keyframes float1 {
          0%, 100% { transform: translateY(0px) scale(1); }
          50% { transform: translateY(-30px) scale(1.05); }
        }
        @keyframes float2 {
          0%, 100% { transform: translateX(0px) scale(1); }
          50% { transform: translateX(-20px) scale(1.08); }
        }
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(30px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeIn {
          from { opacity: 0; }
          to   { opacity: 1; }
        }
        @keyframes pulse-ring {
          0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(59,130,246,0.4); }
          70% { transform: scale(1); box-shadow: 0 0 0 20px rgba(59,130,246,0); }
          100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(59,130,246,0); }
        }
        .fade-up { animation: fadeUp 0.7s ease forwards; }
        .fade-in { animation: fadeIn 0.5s ease forwards; }
        .delay-1 { animation-delay: 0.1s; opacity: 0; }
        .delay-2 { animation-delay: 0.25s; opacity: 0; }
        .delay-3 { animation-delay: 0.4s; opacity: 0; }
        .delay-4 { animation-delay: 0.55s; opacity: 0; }
        .delay-5 { animation-delay: 0.7s; opacity: 0; }
        .pulse-ring { animation: pulse-ring 2s infinite; }
      `}</style>

      {/* Navbar */}
      <nav
        className="relative z-10 flex items-center justify-between px-8 py-5 border-b border-gray-800/50"
        style={{ opacity: visible ? 1 : 0, transition: "opacity 0.5s ease" }}
      >
        <div className="flex items-center gap-2">
          <span className="text-xl">⚡</span>
          <span className="font-bold text-white tracking-tight">LifeForge OS</span>
          <span className="ml-2 text-xs px-2 py-0.5 bg-blue-900/40 text-blue-400 border border-blue-800/40 rounded-full">
            v0.3.0
          </span>
        </div>
        <button
          onClick={() => router.push("/dashboard")}
          className="px-4 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-sm text-gray-300 hover:text-white transition-all"
        >
          Ouvrir l'app →
        </button>
      </nav>

      {/* Hero */}
      <section className="relative z-10 flex flex-col items-center justify-center text-center px-6 pt-24 pb-20">

        {/* Badge */}
        <div className={`fade-up delay-1 mb-6 inline-flex items-center gap-2 px-4 py-2 bg-blue-900/30 border border-blue-700/40 rounded-full text-sm text-blue-300`}>
          <span className="w-2 h-2 bg-blue-400 rounded-full pulse-ring inline-block" />
          Système d'exploitation personnel — 100% local
        </div>

        {/* Title */}
        <h1 className={`fade-up delay-2 text-5xl md:text-7xl font-black tracking-tight leading-tight mb-6`}>
          <span className="text-white">Forge ta</span>
          <br />
          <span
            style={{
              background: "linear-gradient(135deg, #3b82f6 0%, #a78bfa 50%, #22c55e 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            meilleure vie
          </span>
        </h1>

        {/* Subtitle */}
        <p className={`fade-up delay-3 text-lg text-gray-400 max-w-xl leading-relaxed mb-10`}>
          Transforme tes journées en progression mesurable.
          Habitudes, objectifs, scores, récompenses — tout en un seul système cohérent.
        </p>

        {/* CTA */}
        <div className={`fade-up delay-4 flex flex-col sm:flex-row gap-3`}>
          <button
            onClick={() => router.push("/dashboard")}
            className="px-8 py-4 rounded-xl text-white font-semibold text-base transition-all hover:scale-105 hover:shadow-2xl"
            style={{
              background: "linear-gradient(135deg, #2563eb, #7c3aed)",
              boxShadow: "0 0 30px rgba(59,130,246,0.3)",
            }}
          >
            🚀 Lancer LifeForge OS
          </button>
          <button
            onClick={() => document.getElementById("features")?.scrollIntoView({ behavior: "smooth" })}
            className="px-8 py-4 rounded-xl text-gray-300 font-medium text-base bg-gray-800/80 border border-gray-700 hover:bg-gray-700 transition-all"
          >
            Voir les fonctionnalités ↓
          </button>
        </div>

        {/* Stats */}
        <div className={`fade-up delay-5 flex gap-12 mt-16`}>
          {STATS.map((s) => (
            <div key={s.label} className="text-center">
              <div className="text-3xl font-black text-white">{s.value}</div>
              <div className="text-xs text-gray-500 mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Preview card */}
      <section className="relative z-10 flex justify-center px-6 pb-20">
        <div
          className="w-full max-w-2xl rounded-2xl border border-gray-800 overflow-hidden"
          style={{
            background: "linear-gradient(135deg, #111827 0%, #0f172a 100%)",
            boxShadow: "0 0 80px rgba(59,130,246,0.1), 0 25px 50px rgba(0,0,0,0.5)",
          }}
        >
          {/* Fake window bar */}
          <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-800">
            <div className="w-3 h-3 rounded-full bg-red-500/70" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/70" />
            <div className="w-3 h-3 rounded-full bg-green-500/70" />
            <span className="ml-3 text-xs text-gray-600">LifeForge OS — Dashboard</span>
          </div>

          {/* Fake dashboard content */}
          <div className="p-6 space-y-4">
            {/* KPI row */}
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: "Score Global", value: "78%", color: "#3b82f6" },
                { label: "XP Aujourd'hui", value: "+240", color: "#a78bfa" },
                { label: "Streak", value: "12 🔥", color: "#f59e0b" },
              ].map((kpi) => (
                <div key={kpi.label} className="bg-gray-800/60 rounded-xl p-3 border border-gray-700/50">
                  <p className="text-xs text-gray-500 mb-1">{kpi.label}</p>
                  <p className="text-xl font-bold" style={{ color: kpi.color }}>{kpi.value}</p>
                </div>
              ))}
            </div>

            {/* Fake progress bars */}
            <div className="bg-gray-800/60 rounded-xl p-4 border border-gray-700/50 space-y-3">
              <p className="text-xs text-gray-400 font-medium">Piliers du jour</p>
              {[
                { name: "Carrière", pct: 85, color: "#3b82f6" },
                { name: "Santé",    pct: 60, color: "#22c55e" },
                { name: "Finance",  pct: 40, color: "#f59e0b" },
              ].map((p) => (
                <div key={p.name}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-400">{p.name}</span>
                    <span className="text-gray-500">{p.pct}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-1.5">
                    <div
                      className="h-1.5 rounded-full"
                      style={{ width: `${p.pct}%`, backgroundColor: p.color }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Fake habit checklist */}
            <div className="bg-gray-800/60 rounded-xl p-4 border border-gray-700/50 space-y-2">
              <p className="text-xs text-gray-400 font-medium">Habitudes du jour</p>
              {[
                { name: "Deep Work 2h", done: true },
                { name: "Sport 30min",  done: true },
                { name: "Méditation",   done: false },
              ].map((h) => (
                <div key={h.name} className="flex items-center gap-3">
                  <div className={`w-4 h-4 rounded border flex items-center justify-center ${h.done ? "bg-blue-500 border-blue-500" : "border-gray-600"}`}>
                    {h.done && <span className="text-white text-xs">✓</span>}
                  </div>
                  <span className={`text-sm ${h.done ? "line-through text-gray-500" : "text-gray-300"}`}>
                    {h.name}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="relative z-10 px-6 pb-24 max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white mb-3">Tout ce dont tu as besoin</h2>
          <p className="text-gray-500">Un seul système. Zéro friction.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {FEATURES.map((f, i) => (
            <div
              key={f.title}
              className="group p-5 rounded-xl border border-gray-800 hover:border-gray-600 transition-all hover:bg-gray-900/50"
              style={{
                animationDelay: `${i * 0.1}s`,
                background: "linear-gradient(135deg, #111827 0%, #0f172a 100%)",
              }}
            >
              <div className="text-3xl mb-3">{f.icon}</div>
              <h3 className="text-white font-semibold mb-1">{f.title}</h3>
              <p className="text-sm text-gray-500 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA final */}
      <section className="relative z-10 px-6 pb-24 flex flex-col items-center text-center">
        <div
          className="w-full max-w-2xl rounded-2xl p-10 border border-gray-800"
          style={{ background: "linear-gradient(135deg, #1e3a5f 0%, #1e1b4b 100%)" }}
        >
          <h2 className="text-3xl font-bold text-white mb-3">Prêt à forger ta vie ?</h2>
          <p className="text-gray-400 mb-8">Commence dès maintenant. Aucun compte requis. 100% local.</p>
          <button
            onClick={() => router.push("/dashboard")}
            className="px-10 py-4 rounded-xl text-white font-bold text-lg transition-all hover:scale-105"
            style={{
              background: "linear-gradient(135deg, #2563eb, #7c3aed)",
              boxShadow: "0 0 40px rgba(59,130,246,0.4)",
            }}
          >
            🚀 Lancer LifeForge OS
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-gray-800 px-8 py-6 flex items-center justify-between text-xs text-gray-600">
        <span>⚡ LifeForge OS — Built by Ahmed FRIKHA</span>
        <span>Next.js 14 · FastAPI · Ollama · Whisper</span>
      </footer>

    </div>
  )
}