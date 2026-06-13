"use client"

import { Suspense, useEffect, useState } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { startLogin } from "@/lib/auth/pkce"
import { isLoggedIn } from "@/lib/auth/session"

function LoginForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [loading, setLoading] = useState(false)
  const next = searchParams.get("next") ?? "/dashboard"

  useEffect(() => {
    if (isLoggedIn()) router.replace(next)
  }, [next, router])

  async function handleSSO() {
    setLoading(true)
    await startLogin(next)
  }

  return (
    <div className="rounded-2xl border border-border bg-card p-8">
      <h1 className="font-heading text-lg font-semibold text-foreground">Anmelden</h1>
      <p className="mt-1 text-sm text-muted-foreground">
        Melde dich mit deinem K.I.T.-Konto an.
      </p>

      <button
        onClick={handleSSO}
        disabled={loading}
        className="mt-6 flex w-full items-center justify-center gap-3 rounded-xl bg-primary py-3 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-60 cursor-pointer"
      >
        {loading ? (
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
        ) : (
          <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/>
          </svg>
        )}
        Mit SSO anmelden
      </button>
    </div>
  )
}

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="mb-10 flex flex-col items-center gap-3">
          <div className="relative flex h-14 w-14 items-center justify-center">
            <div className="absolute inset-0 rounded-2xl bg-primary/30 blur-lg" />
            <img src="/workmate-logo.png" alt="WorkmateOS" className="relative h-14 w-14 object-contain" />
          </div>
          <div className="text-center">
            <div className="flex items-baseline justify-center gap-1.5 font-heading">
              <span className="text-2xl font-bold tracking-tight text-foreground">WORKMATE</span>
              <span className="text-2xl font-light text-muted-foreground">|</span>
              <span className="text-2xl font-light text-primary">OS</span>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">K.I.T. Solutions</p>
          </div>
        </div>

        <Suspense fallback={
          <div className="rounded-2xl border border-border bg-card p-8 flex justify-center">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-border border-t-primary" />
          </div>
        }>
          <LoginForm />
        </Suspense>

        <p className="mt-6 text-center text-xs text-muted-foreground">
          WorkmateOS · K.I.T. Solutions GbR
        </p>
      </div>
    </div>
  )
}
