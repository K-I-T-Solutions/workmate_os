"use client"
import { useState, useEffect, useCallback } from "react"

export const THEMES = [
  {
    id: "standard",
    name: "Standard",
    description: "Dunkles Theme mit Electric Blue",
    preview: ["#111111", "#1a1a1a"],
    accent: "#0077FF",
    dark: true,
  },
  {
    id: "anthrazit",
    name: "Anthrazit",
    description: "K.I.T Classic — Anthrazit mit Orange",
    preview: ["#232223", "#303030"],
    accent: "#FF9100",
    dark: true,
  },
  {
    id: "midnight",
    name: "Midnight",
    description: "Ultra-dunkel für OLED-Displays",
    preview: ["#000000", "#0a0a0a"],
    accent: "#0077FF",
    dark: true,
  },
  {
    id: "hell",
    name: "Hell",
    description: "Helles, professionelles Theme",
    preview: ["#f8f9fa", "#ffffff"],
    accent: "#0055CC",
    dark: false,
  },
] as const

export type ThemeId = (typeof THEMES)[number]["id"]

const STORAGE_KEY = "workmate-theme"

export function applyTheme(id: ThemeId) {
  const root = document.documentElement
  const theme = THEMES.find(t => t.id === id) ?? THEMES[0]

  if (id === "standard") {
    root.removeAttribute("data-theme")
  } else {
    root.setAttribute("data-theme", id)
  }

  if (theme.dark) {
    root.classList.add("dark")
  } else {
    root.classList.remove("dark")
  }

  localStorage.setItem(STORAGE_KEY, id)
}

export function useTheme() {
  const [theme, setThemeState] = useState<ThemeId>("standard")

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY) as ThemeId | null
    if (saved && THEMES.find(t => t.id === saved)) {
      setThemeState(saved)
    }
  }, [])

  const setTheme = useCallback((id: ThemeId) => {
    setThemeState(id)
    applyTheme(id)
  }, [])

  return { theme, setTheme, themes: THEMES }
}
