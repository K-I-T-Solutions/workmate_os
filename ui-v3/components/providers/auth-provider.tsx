"use client"

import { createContext, useContext, useEffect, useState, useCallback, useRef } from "react"
import { useRouter } from "next/navigation"
import { getAccessToken, getIdToken, getRefreshToken, clearTokens, saveTokens, decodeToken, isTokenExpired, type JwtPayload } from "@/lib/auth/session"
import { buildLogoutUrl, refreshTokens } from "@/lib/auth/pkce"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "https://api.workmate.kit-it-koblenz.de"

async function fetchPermissions(token: string): Promise<string[]> {
  try {
    const res = await fetch(`${API_BASE}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) return []
    const data = await res.json()
    return Array.isArray(data.permissions) ? data.permissions : []
  } catch {
    return []
  }
}

interface AuthUser {
  sub: string
  name: string
  email: string
  username: string
  initials: string
  permissions: string[]
}

interface AuthCtx {
  user: AuthUser | null
  loading: boolean
  logout: () => void
  hasPermission: (perm: string) => boolean
}

const Context = createContext<AuthCtx>({ user: null, loading: true, logout: () => {}, hasPermission: () => false })

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const routerRef = useRef(router)
  routerRef.current = router
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function init() {
      let token = getAccessToken()

      if (!token) {
        // No token at all → send to login
        setLoading(false)
        routerRef.current.push("/login")
        return
      }

      if (isTokenExpired(token)) {
        // Try silent refresh; on failure keep user=null — apiClient interceptor handles 401
        const rt = getRefreshToken()
        if (rt) {
          const fresh = await refreshTokens(rt)
          if (fresh) {
            saveTokens(fresh)
            token = fresh.access_token
          }
        }
      }

      const payload = decodeToken(token)
      if (payload) {
        const permissions = await fetchPermissions(token)
        setUser(buildUser(payload, permissions))
      }
      setLoading(false)
    }
    init()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const logout = useCallback(() => {
    const idToken = getIdToken()
    clearTokens()
    if (idToken) {
      window.location.href = buildLogoutUrl(idToken)
    } else {
      router.push("/login")
    }
  }, [router])

  const hasPermission = useCallback((required: string): boolean => {
    const perms = user?.permissions ?? []
    if (perms.includes("*")) return true
    if (perms.includes(required)) return true
    return perms.some(p => p.endsWith(".*") && required.startsWith(p.slice(0, -1)))
  }, [user])

  return <Context.Provider value={{ user, loading, logout, hasPermission }}>{children}</Context.Provider>
}

export function useAuth() {
  return useContext(Context)
}

function buildUser(p: JwtPayload, permissions: string[] = []): AuthUser {
  const name = p.name ?? p.preferred_username ?? "Nutzer"
  const parts = name.split(" ")
  const initials = parts.length >= 2
    ? `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
    : name.slice(0, 2).toUpperCase()
  return {
    sub: p.sub,
    name,
    email: p.email ?? "",
    username: p.preferred_username ?? "",
    initials,
    permissions,
  }
}
