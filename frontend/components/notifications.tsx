"use client"

import { useEffect, useState, useCallback } from "react"

const API = "http://localhost:8000"

interface Habit {
  id: number
  name: string
  type: string
  checked: boolean
}

interface NotificationSettings {
  enabled: boolean
  reminderHour: number
  reminderMinute: number
  morningEnabled: boolean
  morningHour: number
  eveningEnabled: boolean
  eveningHour: number
}

const DEFAULT_SETTINGS: NotificationSettings = {
  enabled: true,
  reminderHour: 20,
  reminderMinute: 0,
  morningEnabled: true,
  morningHour: 8,
  eveningEnabled: true,
  eveningHour: 20,
}

export default function NotificationManager() {
  const [permission, setPermission]   = useState<NotificationPermission>("default")
  const [settings, setSettings]       = useState<NotificationSettings>(DEFAULT_SETTINGS)
  const [expanded, setExpanded]       = useState(false)
  const [lastCheck, setLastCheck]     = useState<string | null>(null)
  const [notifCount, setNotifCount]   = useState(0)

  // Charger settings depuis localStorage
  useEffect(() => {
    const saved = localStorage.getItem("lifeforge_notif_settings")
    if (saved) {
      try { setSettings(JSON.parse(saved)) } catch {}
    }
    setPermission(Notification.permission)
  }, [])

  const saveSettings = (s: NotificationSettings) => {
    setSettings(s)
    localStorage.setItem("lifeforge_notif_settings", JSON.stringify(s))
  }

  const requestPermission = async () => {
    const result = await Notification.requestPermission()
    setPermission(result)
  }

  const sendNotification = useCallback((title: string, body: string, icon = "⚡") => {
    if (Notification.permission !== "granted") return
    new Notification(`${icon} ${title}`, {
      body,
      icon: "/favicon.ico",
      badge: "/favicon.ico",
      tag: "lifeforge",
    })
    setNotifCount((n) => n + 1)
  }, [])

  const checkAndNotify = useCallback(async () => {
    if (!settings.enabled || Notification.permission !== "granted") return

    const now = new Date()
    const timeKey = `${now.getHours()}:${now.getMinutes()}`

    // Éviter double-notification dans la même minute
    if (lastCheck === timeKey) return
    setLastCheck(timeKey)

    const h = now.getHours()
    const m = now.getMinutes()

    // Notification matin
    if (settings.morningEnabled && h === settings.morningHour && m === 0) {
      sendNotification(
        "Bonne journée !",
        "Tes habitudes t'attendent. Lance une session Pomodoro pour bien commencer.",
        "🌅"
      )
      return
    }

    // Notification soir — check habitudes non cochées
    if (settings.eveningEnabled && h === settings.eveningHour && m === 0) {
      try {
        const res = await fetch(`${API}/habits/today`)
        const habits: Habit[] = await res.json()
        const unchecked = habits.filter((h) => !h.checked && h.type === "good")

        if (unchecked.length === 0) {
          sendNotification(
            "Journée parfaite ! 🏆",
            "Toutes tes habitudes sont cochées. Score maximum aujourd'hui !",
            "🎉"
          )
        } else {
          sendNotification(
            `${unchecked.length} habitude${unchecked.length > 1 ? "s" : ""} restante${unchecked.length > 1 ? "s" : ""}`,
            `Il reste : ${unchecked.slice(0, 3).map((h) => h.name).join(", ")}${unchecked.length > 3 ? "..." : ""}`,
            "🔔"
          )
        }
      } catch {
        sendNotification("Rappel habitudes", "N'oublie pas de cocher tes habitudes du jour !", "🔔")
      }
      return
    }

    // Rappel personnalisé
    if (h === settings.reminderHour && m === settings.reminderMinute) {
      try {
        const res = await fetch(`${API}/score/today`)
        const summary = await res.json()
        const score = summary.global_score ?? 0

        if (score === 0) {
          sendNotification("Tu n'as pas encore commencé", "Lance ton premier Pomodoro et coche tes habitudes !", "⚡")
        } else if (score < 50) {
          sendNotification(`Score : ${score}%`, "Tu peux faire mieux ! Il reste du temps pour progresser.", "📈")
        } else if (score >= 90) {
          sendNotification(`Score : ${score}% 🔥`, "Excellente journée ! Maintiens cette dynamique.", "💎")
        }
      } catch {}
    }
  }, [settings, lastCheck, sendNotification])

  // Vérifier toutes les minutes
  useEffect(() => {
    const interval = setInterval(checkAndNotify, 60 * 1000)
    return () => clearInterval(interval)
  }, [checkAndNotify])

  // Test immédiat au montage si permission déjà accordée
  useEffect(() => {
    if (Notification.permission === "granted" && settings.enabled) {
      // Notification de bienvenue au premier chargement du jour
      const today = new Date().toDateString()
      const lastWelcome = localStorage.getItem("lifeforge_last_welcome")
      if (lastWelcome !== today) {
        setTimeout(() => {
          sendNotification("LifeForge OS actif", "Les notifications sont activées. Bonne journée !", "⚡")
          localStorage.setItem("lifeforge_last_welcome", today)
        }, 2000)
      }
    }
  }, [sendNotification, settings.enabled])

  const permissionColor =
    permission === "granted" ? "text-green-400" :
    permission === "denied"  ? "text-red-400" :
    "text-yellow-400"

  const permissionLabel =
    permission === "granted" ? "✅ Activées" :
    permission === "denied"  ? "❌ Bloquées" :
    "⚠️ Non demandées"

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">

      {/* Header */}
      <button
        onClick={() => setExpanded((e) => !e)}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-gray-800/50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-lg">🔔</span>
          <div className="text-left">
            <p className="text-sm font-semibold text-white">Notifications</p>
            <p className={`text-xs ${permissionColor}`}>{permissionLabel}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {notifCount > 0 && (
            <span className="text-xs px-2 py-0.5 bg-blue-900/40 text-blue-400 rounded-full">
              {notifCount} envoyées
            </span>
          )}
          <span className="text-gray-600 text-sm">{expanded ? "▲" : "▼"}</span>
        </div>
      </button>

      {expanded && (
        <div className="px-5 pb-5 border-t border-gray-800 pt-5 space-y-5">

          {/* Permission */}
          {permission !== "granted" && (
            <div className="bg-yellow-900/20 border border-yellow-800/40 rounded-xl p-4 space-y-3">
              <p className="text-sm text-yellow-300">
                {permission === "denied"
                  ? "Les notifications sont bloquées dans ton navigateur. Modifie les paramètres du site."
                  : "Autorise les notifications pour recevoir des rappels d'habitudes."}
              </p>
              {permission === "default" && (
                <button
                  onClick={requestPermission}
                  className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 rounded-lg text-white text-sm font-medium transition-colors"
                >
                  🔔 Autoriser les notifications
                </button>
              )}
            </div>
          )}

          {/* Toggle global */}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-white">Notifications actives</p>
              <p className="text-xs text-gray-500">Active ou désactive tous les rappels</p>
            </div>
            <button
              onClick={() => saveSettings({ ...settings, enabled: !settings.enabled })}
              className={`w-12 h-6 rounded-full transition-colors relative ${
                settings.enabled ? "bg-blue-600" : "bg-gray-700"
              }`}
            >
              <div
                className={`w-5 h-5 bg-white rounded-full absolute top-0.5 transition-transform ${
                  settings.enabled ? "translate-x-6" : "translate-x-0.5"
                }`}
              />
            </button>
          </div>

          {settings.enabled && (
            <>
              {/* Notification matin */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <p className="text-sm text-white">🌅 Rappel matin</p>
                  <button
                    onClick={() => saveSettings({ ...settings, morningEnabled: !settings.morningEnabled })}
                    className={`w-10 h-5 rounded-full transition-colors relative ${
                      settings.morningEnabled ? "bg-green-600" : "bg-gray-700"
                    }`}
                  >
                    <div
                      className={`w-4 h-4 bg-white rounded-full absolute top-0.5 transition-transform ${
                        settings.morningEnabled ? "translate-x-5" : "translate-x-0.5"
                      }`}
                    />
                  </button>
                </div>
                {settings.morningEnabled && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">Heure :</span>
                    <input
                      type="number"
                      min={0}
                      max={23}
                      value={settings.morningHour}
                      onChange={(e) => saveSettings({ ...settings, morningHour: Number(e.target.value) })}
                      className="w-16 bg-gray-800 border border-gray-700 rounded-lg px-2 py-1 text-white text-sm text-center focus:outline-none focus:border-blue-500"
                    />
                    <span className="text-xs text-gray-500">h00</span>
                  </div>
                )}
              </div>

              {/* Notification soir */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <p className="text-sm text-white">🌙 Rappel soir (habitudes)</p>
                  <button
                    onClick={() => saveSettings({ ...settings, eveningEnabled: !settings.eveningEnabled })}
                    className={`w-10 h-5 rounded-full transition-colors relative ${
                      settings.eveningEnabled ? "bg-purple-600" : "bg-gray-700"
                    }`}
                  >
                    <div
                      className={`w-4 h-4 bg-white rounded-full absolute top-0.5 transition-transform ${
                        settings.eveningEnabled ? "translate-x-5" : "translate-x-0.5"
                      }`}
                    />
                  </button>
                </div>
                {settings.eveningEnabled && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">Heure :</span>
                    <input
                      type="number"
                      min={0}
                      max={23}
                      value={settings.eveningHour}
                      onChange={(e) => saveSettings({ ...settings, eveningHour: Number(e.target.value) })}
                      className="w-16 bg-gray-800 border border-gray-700 rounded-lg px-2 py-1 text-white text-sm text-center focus:outline-none focus:border-blue-500"
                    />
                    <span className="text-xs text-gray-500">h00</span>
                  </div>
                )}
              </div>

              {/* Rappel score personnalisé */}
              <div className="space-y-2">
                <p className="text-sm text-white">📊 Rappel score</p>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500">Heure :</span>
                  <input
                    type="number"
                    min={0}
                    max={23}
                    value={settings.reminderHour}
                    onChange={(e) => saveSettings({ ...settings, reminderHour: Number(e.target.value) })}
                    className="w-16 bg-gray-800 border border-gray-700 rounded-lg px-2 py-1 text-white text-sm text-center focus:outline-none focus:border-blue-500"
                  />
                  <span className="text-xs text-gray-500">:</span>
                  <input
                    type="number"
                    min={0}
                    max={59}
                    value={settings.reminderMinute}
                    onChange={(e) => saveSettings({ ...settings, reminderMinute: Number(e.target.value) })}
                    className="w-16 bg-gray-800 border border-gray-700 rounded-lg px-2 py-1 text-white text-sm text-center focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Bouton test */}
              <button
                onClick={() => sendNotification(
                  "Test LifeForge",
                  "Les notifications fonctionnent correctement 🎉",
                  "✅"
                )}
                disabled={permission !== "granted"}
                className="w-full py-2.5 bg-gray-800 hover:bg-gray-700 disabled:opacity-40 rounded-lg text-gray-300 text-sm transition-colors"
              >
                🧪 Envoyer une notification test
              </button>
            </>
          )}
        </div>
      )}
    </div>
  )
}