"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { PortalShell } from "@/components/portal/portal-shell"
import { portalService, PORTAL_STATUS_COLOR, PORTAL_STATUS_LABELS, type PortalTicket } from "@/lib/portal/service"
import { Button } from "@/components/ui/button"

function TicketList() {
  const [filter, setFilter] = useState<"open" | "closed">("open")
  const [tickets, setTickets] = useState<PortalTicket[] | null>(null)

  useEffect(() => {
    setTickets(null)
    portalService.tickets(filter).then(setTickets).catch(() => setTickets([]))
  }, [filter])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Ihre Anfragen</h1>
        <Link href="/portal/tickets/new"><Button>Neue Anfrage</Button></Link>
      </div>

      <div className="flex gap-1 rounded-lg border bg-muted p-1 w-fit">
        {(["open", "closed"] as const).map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`rounded-md px-3 py-1 text-xs font-medium transition-colors ${filter === f ? "bg-card text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"}`}
          >
            {f === "open" ? "Offen" : "Erledigt"}
          </button>
        ))}
      </div>

      {tickets === null ? (
        <p className="text-sm text-muted-foreground">Laden…</p>
      ) : tickets.length === 0 ? (
        <p className="rounded-lg border bg-card py-12 text-center text-sm text-muted-foreground">
          {filter === "open" ? "Keine offenen Anfragen." : "Keine erledigten Anfragen."}
        </p>
      ) : (
        <div className="divide-y overflow-hidden rounded-lg border bg-card">
          {tickets.map(t => (
            <Link key={t.id} href={`/portal/tickets/${t.id}`} className="flex items-center gap-3 px-5 py-4 hover:bg-muted/30">
              <span className="w-24 shrink-0 font-mono text-xs text-muted-foreground">{t.ticket_number}</span>
              <span className="flex-1 truncate text-sm font-medium">{t.title}</span>
              <span className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${PORTAL_STATUS_COLOR[t.status] ?? "bg-muted"}`}>
                {PORTAL_STATUS_LABELS[t.status] ?? t.status}
              </span>
              <span className="hidden w-24 shrink-0 text-right text-xs text-muted-foreground sm:block">
                {new Date(t.updated_at ?? t.created_at).toLocaleDateString("de-DE")}
              </span>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

export default function PortalTicketsPage() {
  return <PortalShell><TicketList /></PortalShell>
}
