"use client"

import { use, useEffect, useState } from "react"
import Link from "next/link"
import { PortalShell } from "@/components/portal/portal-shell"
import { portalService, PORTAL_STATUS_COLOR, PORTAL_STATUS_LABELS, type PortalTicketDetail } from "@/lib/portal/service"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { ArrowLeftIcon, SendIcon } from "lucide-react"

function fmt(d: string) {
  return new Date(d).toLocaleString("de-DE", { dateStyle: "short", timeStyle: "short" })
}

function TicketView({ id }: { id: string }) {
  const [ticket, setTicket] = useState<PortalTicketDetail | null>(null)
  const [notFound, setNotFound] = useState(false)
  const [reply, setReply] = useState("")
  const [sending, setSending] = useState(false)

  useEffect(() => {
    portalService.ticket(id).then(setTicket).catch(() => setNotFound(true))
  }, [id])

  async function handleReply(e: React.FormEvent) {
    e.preventDefault()
    if (!reply.trim()) return
    setSending(true)
    try {
      setTicket(await portalService.reply(id, reply.trim()))
      setReply("")
    } finally {
      setSending(false)
    }
  }

  if (notFound) return <p className="text-sm text-destructive">Anfrage nicht gefunden.</p>
  if (!ticket) return <p className="text-sm text-muted-foreground">Laden…</p>

  const done = ticket.status === "resolved" || ticket.status === "closed"

  return (
    <div className="space-y-6">
      <Link href="/portal/tickets" className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeftIcon className="h-4 w-4" /> Alle Anfragen
      </Link>

      <div>
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-mono text-xs text-muted-foreground">{ticket.ticket_number}</span>
          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${PORTAL_STATUS_COLOR[ticket.status] ?? "bg-muted"}`}>
            {PORTAL_STATUS_LABELS[ticket.status] ?? ticket.status}
          </span>
        </div>
        <h1 className="mt-1 text-xl font-semibold">{ticket.title}</h1>
        <p className="text-xs text-muted-foreground">Erstellt am {fmt(ticket.created_at)}</p>
      </div>

      {ticket.description && (
        <div className="whitespace-pre-wrap rounded-lg border bg-card p-4 text-sm">{ticket.description}</div>
      )}

      <div className="space-y-3">
        {ticket.comments.map(c => (
          <div key={c.id} className={`flex ${c.from_customer ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[85%] rounded-lg border p-4 ${c.from_customer ? "bg-primary/10 border-primary/30" : "bg-card"}`}>
              <p className="mb-1 text-xs text-muted-foreground">
                {c.from_customer ? "Sie" : "K.I.T. Support"} · {fmt(c.created_at)}
              </p>
              <p className="whitespace-pre-wrap text-sm">{c.content}</p>
            </div>
          </div>
        ))}
      </div>

      <form onSubmit={handleReply} className="space-y-3 rounded-lg border bg-card p-4">
        {done && <p className="text-xs text-muted-foreground">Diese Anfrage ist erledigt. Mit einer Antwort wird sie wieder geöffnet.</p>}
        <Textarea rows={4} value={reply} onChange={e => setReply(e.target.value)} placeholder="Ihre Nachricht…" />
        <div className="flex justify-end">
          <Button type="submit" size="sm" disabled={sending || !reply.trim()}>
            <SendIcon className="mr-2 h-3.5 w-3.5" /> {sending ? "Senden…" : "Antworten"}
          </Button>
        </div>
      </form>
    </div>
  )
}

export default function PortalTicketPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  return <PortalShell><TicketView id={id} /></PortalShell>
}
