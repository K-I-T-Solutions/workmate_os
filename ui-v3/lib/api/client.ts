import axios from "axios"
import { saveTokens, clearTokens } from "@/lib/auth/session"
import { refreshTokens } from "@/lib/auth/pkce"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "https://api.workmate.kit-it-koblenz.de"

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
  withCredentials: false,
})

apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token")
    if (token) config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let refreshing: Promise<string | null> | null = null

apiClient.interceptors.response.use(
  res => res,
  async err => {
    const original = err.config
    if (err.response?.status !== 401 || original._retry) {
      return Promise.reject(err)
    }
    original._retry = true

    if (!refreshing) {
      refreshing = (async () => {
        const rt = typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null
        if (!rt) {
          clearTokens()
          if (typeof window !== "undefined") window.location.href = "/login"
          return null
        }
        const fresh = await refreshTokens(rt)
        if (!fresh) {
          clearTokens()
          if (typeof window !== "undefined") window.location.href = "/login"
          return null
        }
        saveTokens(fresh)
        return fresh.access_token
      })().finally(() => { refreshing = null })
    }

    const newToken = await refreshing
    if (!newToken) {
      // Redirect already triggered — let the navigation happen, don't propagate error
      return new Promise(() => {})
    }
    original.headers.Authorization = `Bearer ${newToken}`
    return apiClient(original)
  }
)
