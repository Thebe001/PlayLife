"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import VoiceButton from "@/components/voice-button"

const navItems = [
  { href: "/dashboard",              icon: "⚡", label: "Dashboard"    },
  { href: "/dashboard/planning",     icon: "📅", label: "Planning"     },
  { href: "/dashboard/objectives",   icon: "🎯", label: "Objectifs"    },
  { href: "/dashboard/gamification", icon: "🏆", label: "Gamification" },
  { href: "/dashboard/skilltree",    icon: "🌳", label: "Skill Tree"   },
  { href: "/dashboard/journal",      icon: "📓", label: "Journal"      },
  { href: "/dashboard/reviews",      icon: "📊", label: "Reviews"      },
  { href: "/dashboard/stats",        icon: "📈", label: "Stats"        },
  { href: "/dashboard/settings",     icon: "⚙️",  label: "Settings"    },
]

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const [mobileOpen, setMobileOpen] = useState(false)

  const navContent = (
    <>
      <div className="px-3 mb-8">
        <h1 className="text-lg font-bold text-white">⚡ LifeForge</h1>
        <p className="text-xs text-gray-500 mt-0.5">Your Life OS</p>
      </div>
      <nav className="flex flex-col gap-1 flex-1">
        {navItems.map((item) => {
          const active = pathname === item.href
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setMobileOpen(false)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
                active
                  ? "bg-blue-600 text-white font-medium"
                  : "text-gray-400 hover:bg-gray-800 hover:text-white"
              }`}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>
      <div className="px-3 pt-4 border-t border-gray-800">
        <p className="text-xs text-gray-600">Ahmed FRIKHA</p>
        <p className="text-xs text-gray-700">v0.3.0</p>
      </div>
    </>
  )

  return (
    <div className="flex h-screen bg-gray-950 text-white overflow-hidden">
      {/* Desktop sidebar */}
      <aside className="hidden md:flex w-56 bg-gray-900 border-r border-gray-800 flex-col py-6 px-3 shrink-0">
        {navContent}
      </aside>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-40 md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Mobile sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 w-56 bg-gray-900 border-r border-gray-800 flex flex-col py-6 px-3 z-50 transform transition-transform md:hidden ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {navContent}
      </aside>

      <main className="flex-1 overflow-y-auto relative">
        {/* Mobile header */}
        <div className="md:hidden sticky top-0 z-30 bg-gray-950 border-b border-gray-800 px-4 py-3 flex items-center gap-3">
          <button
            onClick={() => setMobileOpen(true)}
            className="text-white text-lg"
            aria-label="Open menu"
          >
            ☰
          </button>
          <span className="text-sm font-semibold text-white">⚡ LifeForge</span>
        </div>
        <div className="page-enter">
          {children}
        </div>
        <VoiceButton />
      </main>
    </div>
  )
}