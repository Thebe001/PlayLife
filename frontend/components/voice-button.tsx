"use client"

import { useState, useRef } from "react"

const API = "http://localhost:8000"

interface VoiceResult {
  transcription: string
  action: string
  llm_response: string
  result: Record<string, unknown>
}

export default function VoiceButton() {
  const [state, setState] = useState<"idle" | "recording" | "processing">("idle")
  const [result, setResult] = useState<VoiceResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [showOverlay, setShowOverlay] = useState(false)
  const [textMode, setTextMode] = useState(false)
  const [textInput, setTextInput] = useState("")

  const mediaRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      chunksRef.current = []

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      recorder.onstop = async () => {
        stream.getTracks().forEach(t => t.stop())
        const blob = new Blob(chunksRef.current, { type: "audio/webm" })
        await sendAudio(blob)
      }

      mediaRef.current = recorder
      recorder.start()
      setState("recording")
    } catch {
      setError("Microphone inaccessible. Autorise l'accès au micro.")
    }
  }

  const stopRecording = () => {
    if (mediaRef.current && state === "recording") {
      mediaRef.current.stop()
      setState("processing")
    }
  }

  const sendAudio = async (blob: Blob) => {
  setState("processing")
  const form = new FormData()
  form.append("audio", blob, "recording.webm")

  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 180000) // 3 minutes pour Whisper + Ollama

  try {
    const res = await fetch(`${API}/voice/voice-command`, {
      method: "POST",
      body: form,
      signal: controller.signal,
    })
    clearTimeout(timeout)
    const data = await res.json()
    setResult(data)
    setState("idle")

    if (data.action !== "unknown") {
      setTimeout(() => window.location.reload(), 2000)
    }
  } catch (e: unknown) {
    clearTimeout(timeout)
    if (e instanceof Error && e.name === "AbortError") {
      setError("Timeout — traitement trop long. Réessaie.")
    } else {
      setError("Erreur lors du traitement.")
    }
    setState("idle")
  }
}

  const sendText = async () => {
  if (!textInput.trim()) return
  setState("processing")

  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 120000) // 2 minutes

  try {
    const res = await fetch(`${API}/voice/command`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: textInput }),
      signal: controller.signal,
    })
    clearTimeout(timeout)
    const data = await res.json()
    setResult({
      transcription: textInput,
      action: data.action,
      llm_response: data.llm_response,
      result: data.result,
    })
    setTextInput("")
    setState("idle")

    if (data.action !== "unknown") {
      setTimeout(() => window.location.reload(), 2000)
    }
  } catch (e: unknown) {
    clearTimeout(timeout)
    if (e instanceof Error && e.name === "AbortError") {
      setError("Timeout — Ollama met trop de temps. Réessaie.")
    } else {
      setError("Erreur lors du traitement.")
    }
    setState("idle")
  }
}

  const reset = () => {
    setResult(null)
    setError(null)
    setState("idle")
  }

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => { setShowOverlay(true); reset() }}
        className={`fixed bottom-6 right-6 w-14 h-14 rounded-full shadow-lg flex items-center justify-center text-2xl transition-all z-50 ${
          state === "recording"
            ? "bg-red-500 animate-pulse scale-110"
            : "bg-blue-600 hover:bg-blue-700 hover:scale-105"
        }`}
        title="Assistant vocal"
      >
        🎤
      </button>

      {/* Overlay */}
      {showOverlay && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-end justify-center pb-8">
          <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 w-full max-w-md mx-4 space-y-4">

            {/* Header */}
            <div className="flex items-center justify-between">
              <h3 className="text-white font-semibold">🤖 Assistant LifeForge</h3>
              <button
                onClick={() => setShowOverlay(false)}
                className="text-gray-500 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>

            {/* Mode toggle */}
            <div className="flex gap-2">
              <button
                onClick={() => setTextMode(false)}
                className={`flex-1 py-2 rounded-lg text-sm transition-colors ${
                  !textMode ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-400"
                }`}
              >
                🎤 Vocal
              </button>
              <button
                onClick={() => setTextMode(true)}
                className={`flex-1 py-2 rounded-lg text-sm transition-colors ${
                  textMode ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-400"
                }`}
              >
                ⌨️ Texte
              </button>
            </div>

            {/* Voice mode */}
            {!textMode && (
              <div className="flex flex-col items-center gap-4 py-4">
                {state === "idle" && !result && (
                  <>
                    <button
                      onClick={startRecording}
                      className="w-20 h-20 rounded-full bg-blue-600 hover:bg-blue-700 flex items-center justify-center text-4xl transition-all hover:scale-105"
                    >
                      🎤
                    </button>
                    <p className="text-gray-500 text-sm">Appuie pour parler</p>
                  </>
                )}

                {state === "recording" && (
                  <>
                    <button
                      onClick={stopRecording}
                      className="w-20 h-20 rounded-full bg-red-500 animate-pulse flex items-center justify-center text-4xl"
                    >
                      ⏹️
                    </button>
                    <p className="text-red-400 text-sm animate-pulse">Enregistrement... appuie pour arrêter</p>
                  </>
                )}

                {state === "processing" && (
                  <div className="flex flex-col items-center gap-3">
                    <div className="w-12 h-12 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                    <p className="text-gray-400 text-sm">Analyse en cours...</p>
                  </div>
                )}
              </div>
            )}

            {/* Text mode */}
            {textMode && (
              <div className="space-y-3">
                <input
                  type="text"
                  placeholder='ex: "Marque sport comme fait"'
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && sendText()}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-blue-500"
                  disabled={state === "processing"}
                />
                <button
                  onClick={sendText}
                  disabled={state === "processing" || !textInput.trim()}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg text-white text-sm font-medium transition-colors"
                >
                  {state === "processing" ? "Traitement..." : "Envoyer →"}
                </button>
              </div>
            )}

            {/* Result */}
            {result && (
              <div className="bg-gray-800 rounded-xl p-4 space-y-2">
                {result.transcription && (
                  <p className="text-xs text-gray-500">
                    🎤 <span className="text-gray-300 italic">"{result.transcription}"</span>
                  </p>
                )}
                <p className="text-sm text-white">{result.llm_response}</p>
                {result.action !== "unknown" && (
                  <p className="text-xs text-green-400">✅ Action : {result.action}</p>
                )}
                <button
                  onClick={reset}
                  className="text-xs text-gray-600 hover:text-gray-400 transition-colors"
                >
                  Nouvelle commande
                </button>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="bg-red-900/20 border border-red-800/40 rounded-xl p-3">
                <p className="text-sm text-red-400">{error}</p>
              </div>
            )}

            {/* Examples */}
            {!result && state === "idle" && (
              <div className="space-y-1.5">
                <p className="text-xs text-gray-600 uppercase tracking-wider">Exemples</p>
                {[
                  "Marque sport comme fait",
                  "Quel est mon score aujourd'hui ?",
                  "Crée un objectif finir le projet pilier carrière",
                ].map((ex) => (
                  <button
                    key={ex}
                    onClick={() => { setTextMode(true); setTextInput(ex) }}
                    className="w-full text-left px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-xs text-gray-400 transition-colors"
                  >
                    "{ex}"
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  )
}