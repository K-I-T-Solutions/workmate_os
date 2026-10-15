"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { getPortalToken } from "@/lib/portal/client"
import { portalService } from "@/lib/portal/service"
import { PortalBrand } from "@/components/portal/portal-shell"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function PortalLoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [sending, setSending] = useState(false)
  const [sent, setSent] = useState(false)
  const [expired, setExpired] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (getPortalToken()) router.replace("/portal/tickets")
    setExpired(new URLSearchParams(window.location.search).has("expired"))
  }, [router])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSending(true)
    setError(null)
    try {
      await portalService.requestLink(email.trim())
      setSent(true)
    } catch {
      setError("Anfrage fehlgeschlagen. Bitte versuchen Sie es später erneut.")
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-sm space-y-8">
        <div className="flex justify-center"><PortalBrand subtitle="K.I.T. Solutions" /></div>
        <div className="rounded-2xl border border-border bg-card p-8">
          {sent ? (
            <div className="space-y-2">
              <h1 className="font-heading text-lg font-semibold">E-Mail unterwegs</h1>
              <p className="text-sm text-muted-foreground">
                Falls für <span className="font-medium text-foreground">{email}</span> ein Portal-Zugang besteht,
                haben wir einen Anmeldelink gesendet. Er ist 15 Minuten gültig.
              </p>
              <button onClick={() => setSent(false)} className="pt-2 text-sm text-primary hover:underline">
                Andere Adresse verwenden
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <h1 className="font-heading text-lg font-semibold">Anmelden</h1>
                <p className="mt-1 text-sm text-muted-foreground">
                  Wir senden Ihnen einen Anmeldelink per E-Mail – ganz ohne Passwort.
                </p>
              </div>
              {expired && <p className="rounded-md bg-muted px-3 py-2 text-sm text-muted-foreground">Ihre Sitzung ist abgelaufen. Bitte melden Sie sich erneut an.</p>}
              <div className="space-y-1.5">
                <Label htmlFor="portal-email">E-Mail-Adresse</Label>
                <Input id="portal-email" type="email" autoComplete="email" value={email} onChange={e => setEmail(e.target.value)} required />
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              <Button type="submit" className="w-full" disabled={sending || !email.trim()}>
                {sending ? "Senden…" : "Anmeldelink anfordern"}
              </Button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
