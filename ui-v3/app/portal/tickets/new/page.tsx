"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { PortalShell } from "@/components/portal/portal-shell"
import { portalService } from "@/lib/portal/service"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { ArrowLeftIcon } from "lucide-react"

function NewTicketForm() {
  const router = useRouter()
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [priority, setPriority] = useState<"low" | "medium" | "high">("medium")
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      const t = await portalService.createTicket({ title: title.trim(), description: description.trim(), priority })
      router.push(`/portal/tickets/${t.id}`)
    } catch {
      setError("Die Anfrage konnte nicht gesendet werden.")
      setSaving(false)
    }
  }

  return (
    <div className="space-y-6">
      <Link href="/portal/tickets" className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeftIcon className="h-4 w-4" /> Zurück
      </Link>
      <h1 className="text-xl font-semibold">Neue Anfrage</h1>
      <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border bg-card p-6">
        <div className="space-y-1.5">
          <Label htmlFor="pt-title">Betreff</Label>
          <Input id="pt-title" value={title} onChange={e => setTitle(e.target.value)} minLength={3} maxLength={300} required placeholder="z.B. Drucker im Empfang druckt nicht" />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="pt-desc">Beschreibung</Label>
          <Textarea id="pt-desc" rows={8} value={description} onChange={e => setDescription(e.target.value)} required
            placeholder="Was ist passiert? Seit wann? Welche Geräte oder Personen sind betroffen?" />
        </div>
        <div className="space-y-1.5">
          <Label>Dringlichkeit</Label>
          <div className="flex gap-1 rounded-lg border bg-muted p-1 w-fit">
            {([["low", "Niedrig"], ["medium", "Normal"], ["high", "Hoch"]] as const).map(([v, l]) => (
              <button key={v} type="button" onClick={() => setPriority(v)}
                className={`rounded-md px-3 py-1 text-xs font-medium transition-colors ${priority === v ? "bg-card text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"}`}>
                {l}
              </button>
            ))}
          </div>
        </div>
        {error && <p className="text-sm text-destructive">{error}</p>}
        <div className="flex justify-end">
          <Button type="submit" disabled={saving || title.trim().length < 3 || !description.trim()}>
            {saving ? "Senden…" : "Anfrage senden"}
          </Button>
        </div>
      </form>
    </div>
  )
}

export default function PortalNewTicketPage() {
  return <PortalShell><NewTicketForm /></PortalShell>
}
