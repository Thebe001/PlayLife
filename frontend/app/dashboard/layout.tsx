import Link from "next/link"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen">

      <aside className="w-64 bg-slate-900 text-white p-6 space-y-4">

        <h2 className="text-xl font-bold mb-6">
          LifeForge
        </h2>

        <nav className="space-y-3">

          <Link href="/dashboard" className="block hover:text-blue-400">
            Dashboard
          </Link>

          <Link href="/habits" className="block hover:text-blue-400">
            Habits
          </Link>

          <Link href="/objectives" className="block hover:text-blue-400">
            Objectives
          </Link>

          <Link href="/journal" className="block hover:text-blue-400">
            Journal
          </Link>

          <Link href="/reviews" className="block hover:text-blue-400">
            Reviews
          </Link>

          <Link href="/stats" className="block hover:text-blue-400">
            Stats
          </Link>

        </nav>

      </aside>

      <main className="flex-1 bg-slate-100">
        {children}
      </main>

    </div>
  )
}