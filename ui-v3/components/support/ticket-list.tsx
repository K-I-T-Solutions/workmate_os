"use client"

import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { supportService } from "@/lib/support/service"
import type { Ticket } from "@/lib/support/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { PlusIcon, MessageSquareIcon, SearchIcon } from "lucide-react"

const STATUS_LABELS: Record<string, string> = {
  open: "Offen", in_progress: "In Bearbeitung", waiting: "Wartend",
  resolved: "Gelöst", closed: "Geschlossen",
}
const STATUS_COLOR: Record<string, string> = {
  open: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  in_progress: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  waiting: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  resolved: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  closed: "bg-muted text-muted-foreground",
}
const PRIORITY_COLOR: Record<string, string> = {
  low: "text-muted-foreground", medium: "text-blue-600",
  high: "text-orange-600", urgent: "text-red-600 font-semibold",
}
const PRIORITY_LABELS: Record<string, string> = {
  low: "Niedrig", medium: "Mittel", high: "Hoch", urgent: "Dringend",
}

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("de-DE")
}

export function TicketList() {
  const router = useRouter()
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [priorityFilter, setPriorityFilter] = useState("all")

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await supportService.list({
        limit: 100,
        status: statusFilter === "all" ? undefined : statusFilter,
        priority: priorityFilter === "all" ? undefined : priorityFilter,
        search: search || undefined,
      })
      setTickets(res.items)
      setTotal(res.total)
    } finally {
      setLoading(false)
    }
  }, [statusFilter, priorityFilter, search])

  useEffect(() => { load() }, [load])

  const openCount = tickets.filter(t => t.status === "open").length
  const urgentCount = tickets.filter(t => t.priority === "urgent").length
  const inProgressCount = tickets.filter(t => t.status === "in_progress").length
  const slaBreachedCount = tickets.filter(t => t.sla_breached).length

  return (
    <div className="space-y-6 px-8 py-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Support</h1>
          <p className="text-sm text-muted-foreground">{total} Tickets gesamt</p>
        </div>
        <Button onClick={() => router.push("/support/new")}>
          <PlusIcon className="mr-2 h-4 w-4" />
          Neu
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          { label: "Offen", value: openCount, color: "text-blue-600" },
          { label: "In Bearbeitung", value: inProgressCount, color: "text-yellow-600" },
          { label: "Dringend", value: urgentCount, color: "text-red-600" },
          { label: "SLA verletzt", value: slaBreachedCount, color: slaBreachedCount > 0 ? "text-red-600 font-bold" : "text-muted-foreground" },
        ].map(s => (
          <div key={s.label} className="rounded-lg border bg-card p-4">
            <p className="text-xs text-muted-foreground">{s.label}</p>
            <p className={`mt-1 text-2xl font-semibold ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        <div className="relative flex-1 min-w-48">
          <SearchIcon className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Suchen…"
            className="pl-8"
          />
        </div>
        <Select value={statusFilter} onValueChange={v => v && setStatusFilter(v)}>
          <SelectTrigger className="w-44"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle Status</SelectItem>
            {Object.entries(STATUS_LABELS).map(([v, l]) => <SelectItem key={v} value={v}>{l}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={priorityFilter} onValueChange={v => v && setPriorityFilter(v)}>
          <SelectTrigger className="w-40"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle Prioritäten</SelectItem>
            {Object.entries(PRIORITY_LABELS).map(([v, l]) => <SelectItem key={v} value={v}>{l}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      {/* List */}
      {loading ? (
        <div className="flex items-center justify-center py-24 text-sm text-muted-foreground">Laden…</div>
      ) : tickets.length === 0 ? (
        <div className="flex flex-col items-center gap-3 py-24 text-muted-foreground">
          <MessageSquareIcon className="h-10 w-10 opacity-30" />
          <p className="text-sm">Keine Tickets gefunden.</p>
        </div>
      ) : (
        <div className="divide-y rounded-lg border overflow-hidden">
          {tickets.map(ticket => (
            <div
              key={ticket.id}
              onClick={() => router.push(`/support/${ticket.id}`)}
              className="flex cursor-pointer items-start gap-4 bg-card px-4 py-3.5 hover:bg-muted/40 transition-colors"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-mono text-xs text-muted-foreground">{ticket.ticket_number}</span>
                  <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLOR[ticket.status] ?? "bg-muted text-muted-foreground"}`}>
                    {STATUS_LABELS[ticket.status] ?? ticket.status}
                  </span>
                  {ticket.sla_breached && (
                    <span className="inline-flex items-center rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900 dark:text-red-200">
                      SLA
                    </span>
                  )}
                </div>
                <p className="mt-1 font-medium leading-snug truncate">{ticket.title}</p>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  {ticket.category} · {fmtDate(ticket.created_at)}
                </p>
              </div>
              <div className="flex items-center gap-3 shrink-0 text-sm">
                <span className={PRIORITY_COLOR[ticket.priority] ?? ""}>
                  {PRIORITY_LABELS[ticket.priority] ?? ticket.priority}
                </span>
                {ticket.comment_count > 0 && (
                  <span className="flex items-center gap-1 text-muted-foreground">
                    <MessageSquareIcon className="h-3.5 w-3.5" />
                    {ticket.comment_count}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
