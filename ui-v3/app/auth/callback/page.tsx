"use client"

import { Suspense, useEffect, useState } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { exchangeCode, popRedirect } from "@/lib/auth/pkce"
import { saveTokens } from "@/lib/auth/session"

function CallbackHandler() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const code = searchParams.get("code")
    const state = searchParams.get("state")
    const errorParam = searchParams.get("error")

    if (errorParam) {
      setError(`Keycloak-Fehler: ${errorParam}`)
      return
    }
    if (!code || !state) {
      setError("Ungültige Callback-Parameter")
      return
    }

    exchangeCode(code, state).then((tokens) => {
      if (!tokens) {
        setError("Token-Austausch fehlgeschlagen")
        return
      }
      saveTokens(tokens)
      window.location.href = popRedirect()
    })
  }, [searchParams, router])

  if (error) {
    return (
      <div className="flex flex-col items-center gap-4">
        <p className="text-sm text-destructive">{error}</p>
        <a href="/login" className="text-sm text-primary hover:underline">Zurück zur Anmeldung</a>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-primary" />
      <p className="text-sm text-muted-foreground">Anmeldung wird verarbeitet…</p>
    </div>
  )
}

export default function CallbackPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <Suspense fallback={
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-primary" />
          <p className="text-sm text-muted-foreground">Laden…</p>
        </div>
      }>
        <CallbackHandler />
      </Suspense>
    </div>
  )
}
