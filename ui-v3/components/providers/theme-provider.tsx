"use client"
import { useEffect } from "react"
import { applyTheme, type ThemeId, THEMES } from "@/lib/theme/use-theme"

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const saved = localStorage.getItem("workmate-theme") as ThemeId | null
    if (saved && THEMES.find(t => t.id === saved)) {
      applyTheme(saved)
    }
  }, [])

  return <>{children}</>
}
