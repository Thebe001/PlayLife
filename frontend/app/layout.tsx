import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import "./globals.css"
import ErrorBoundary from "@/components/error-boundary"

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
})

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
})

export const metadata: Metadata = {
  title: {
    default:  "LifeForge OS",
    template: "%s · LifeForge OS",
  },
  description:
    "Ton système d'exploitation personnel — habitudes, objectifs, scoring, gamification et assistant IA, 100% local.",
  keywords: ["productivité", "habitudes", "gamification", "life os", "objectifs"],
  authors: [{ name: "Ahmed FRIKHA" }],
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fr">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <ErrorBoundary name="App">
          {children}
        </ErrorBoundary>
      </body>
    </html>
  )
}