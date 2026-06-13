"use client"

import { createContext, useContext, useEffect, useState, useCallback, useRef } from "react"
import { useRouter } from "next/navigation"
import { getAccessToken, getIdToken, getRefreshToken, clearTokens, saveTokens, decodeToken, isTokenExpired, type JwtPayload } from "@/lib/auth/session"
import { buildLogoutUrl, refreshTokens } from "@/lib/auth/pkce"

interface AuthUser {
  sub: string
  name: string
  email: string
  username: string
  initials: string
}

interface AuthCtx {
  user: AuthUser | null
  loading: boolean
  logout: () => void
}

const Context = createContext<AuthCtx>({ user: null, loading: true, logout: () => {} })

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
      if (payload) setUser(buildUser(payload))
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

  return <Context.Provider value={{ user, loading, logout }}>{children}</Context.Provider>
}

export function useAuth() {
  return useContext(Context)
}

function buildUser(p: JwtPayload): AuthUser {
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
  }
}
