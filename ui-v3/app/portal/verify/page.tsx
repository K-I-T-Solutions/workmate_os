"use client"

import { useEffect, useRef, useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { savePortalSession } from "@/lib/portal/client"
import { portalService } from "@/lib/portal/service"

/** Ziel des Magic-Links: /portal/verify#token=… (Fragment → Token landet nicht in Server-Logs) */
export default function PortalVerifyPage() {
  const router = useRouter()
  const [failed, setFailed] = useState(false)
  const started = useRef(false)

  useEffect(() => {
    if (started.current) return  // Token ist einmalig – StrictMode-Doppelaufruf vermeiden
    started.current = true
    const token = new URLSearchParams(window.location.hash.slice(1)).get("token")
    // Token sofort aus der Adresszeile/History entfernen
    window.history.replaceState(null, "", "/portal/verify")
    if (!token) {
      setFailed(true)
      return
    }
    portalService
      .verify(token)
      .then(res => {
        savePortalSession(res.access_token, res.expires_at)
        router.replace("/portal/tickets")
      })
      .catch(() => setFailed(true))
  }, [router])

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-sm rounded-2xl border border-border bg-card p-8 text-center">
        {failed ? (
          <>
            <h1 className="font-heading text-lg font-semibold">Link ungültig</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Der Anmeldelink ist abgelaufen oder wurde bereits verwendet.
            </p>
            <Link href="/portal" className="mt-4 inline-block text-sm text-primary hover:underline">Neuen Link anfordern</Link>
          </>
        ) : (
          <p className="text-sm text-muted-foreground">Anmeldung läuft…</p>
        )}
      </div>
    </div>
  )
}
