const ACCESS_KEY = "access_token"
const ID_KEY = "id_token"
const REFRESH_KEY = "refresh_token"
const AUTH_COOKIE = "wm_auth"

export function saveTokens(tokens: { access_token: string; id_token: string; refresh_token?: string }) {
  localStorage.setItem(ACCESS_KEY, tokens.access_token)
  localStorage.setItem(ID_KEY, tokens.id_token)
  if (tokens.refresh_token) localStorage.setItem(REFRESH_KEY, tokens.refresh_token)
  // Set cookie for middleware (30 days, not httpOnly so JS can clear it)
  document.cookie = `${AUTH_COOKIE}=1; path=/; max-age=${60 * 60 * 24 * 30}; SameSite=Lax`
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(ID_KEY)
  localStorage.removeItem(REFRESH_KEY)
  document.cookie = `${AUTH_COOKIE}=; path=/; max-age=0`
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem(ACCESS_KEY)
}

export function getIdToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem(ID_KEY)
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem(REFRESH_KEY)
}

export function isLoggedIn(): boolean {
  return !!getAccessToken()
}

export interface JwtPayload {
  sub: string
  name?: string
  preferred_username?: string
  email?: string
  given_name?: string
  family_name?: string
  realm_access?: { roles: string[] }
  exp: number
}

export function decodeToken(token: string): JwtPayload | null {
  try {
    const payload = token.split(".")[1]
    return JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/")))
  } catch {
    return null
  }
}

export function isTokenExpired(token: string): boolean {
  const payload = decodeToken(token)
  if (!payload) return true
  return Date.now() / 1000 > payload.exp - 30
}
