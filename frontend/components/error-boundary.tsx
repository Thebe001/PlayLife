"use client"

import { Component, ReactNode } from "react"

interface Props {
  children: ReactNode
  fallback?: ReactNode
  name?: string // nom de la zone pour le message d'erreur
}

interface State {
  hasError: boolean
  error: Error | null
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error(`[ErrorBoundary:${this.props.name ?? "unknown"}]`, error, info)
  }

  reset = () => this.setState({ hasError: false, error: null })

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback

      return (
        <div className="flex flex-col items-center justify-center min-h-[300px] gap-4 p-8 text-center">
          <div className="text-4xl">⚠️</div>
          <div>
            <p className="text-white font-semibold text-lg">
              {this.props.name ? `Erreur dans "${this.props.name}"` : "Une erreur est survenue"}
            </p>
            <p className="text-gray-400 text-sm mt-1">
              {this.state.error?.message ?? "Erreur inconnue"}
            </p>
          </div>
          <button
            onClick={this.reset}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors"
          >
            Réessayer
          </button>
        </div>
      )
    }

    return this.props.children
  }
}