import axios from "axios"

/**
 * Kundenportal – eigener API-Client mit eigener Session.
 * Bewusst getrennt vom Mitarbeiter-apiClient (kein Keycloak, kein Refresh).
 */
const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "https://api.workmate.kit-it-koblenz.de"

const TOKEN_KEY = "wm_portal_token"
const EXPIRES_KEY = "wm_portal_expires"

export function getPortalToken(): string | null {
  if (typeof window === "undefined") return null
  try {
    const token = localStorage.getItem(TOKEN_KEY)
    const expires = localStorage.getItem(EXPIRES_KEY)
    if (!token || !expires || new Date(expires) <= new Date()) return null
    return token
  } catch {
    return null
  }
}

export function savePortalSession(token: string, expiresAt: string) {
  try {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(EXPIRES_KEY, expiresAt)
  } catch {
    // Privater Modus o.ä. – Session gilt dann nur bis zum Reload
  }
}

export function clearPortalSession() {
  try {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(EXPIRES_KEY)
  } catch {}
}

export const portalClient = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
})

portalClient.interceptors.request.use(config => {
  const token = getPortalToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

portalClient.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401 && typeof window !== "undefined" && !err.config?.url?.includes("/auth/")) {
      clearPortalSession()
      window.location.href = "/portal?expired=1"
    }
    return Promise.reject(err)
  },
)
