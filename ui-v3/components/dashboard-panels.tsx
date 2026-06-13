"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import {
  Users, FileText, FolderKanban, Wallet, Clock, ArrowRight,
  KanbanSquare, Headphones, UserCog, BookOpen, Settings,
} from "lucide-react"
import { apiClient } from "@/lib/api/client"
import { supportService } from "@/lib/support/service"
import type { Ticket } from "@/lib/support/types"

interface InvoiceStats {
  outstanding_amount: string
  overdue_count: number
  total_revenue: string
}

interface Activity {
  id: string
  type: string
  description: string
  created_at: string
  occurred_at?: string
  customer_name?: string
}

export function FinanzenCard({ invoiceStats }: { invoiceStats: InvoiceStats | null }) {
  const fmt = (val: string | undefined) =>
    val ? parseFloat(val).toLocaleString("de-DE", { style: "currency", currency: "EUR" }) : "–"

  const rows = [
    { label: "Offen", value: fmt(invoiceStats?.outstanding_amount), color: "text-chart-2" },
    { label: "Überfällig", value: invoiceStats ? String(invoiceStats.overdue_count) : "–", color: invoiceStats?.overdue_count ? "text-destructive" : "text-foreground" },
    { label: "Umsatz", value: fmt(invoiceStats?.total_revenue), color: "text-chart-3" },
  ]

  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <div className="flex items-center justify-between">
        <h3 className="font-heading text-sm font-bold text-foreground">Finanzen</h3>
        <Link href="/invoices" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
          Alle →
        </Link>
      </div>
      <div className="mt-4 grid grid-cols-3 divide-x divide-border">
        {rows.map((r) => (
          <div key={r.label} className="px-3 first:pl-0">
            <p className="text-xs text-muted-foreground">{r.label}</p>
            <p className={`mt-1.5 text-lg font-semibold ${r.color}`}>{r.value}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

const activityLabels: Record<string, string> = {
  call: "Anruf",
  email: "E-Mail",
  meeting: "Meeting",
  note: "Notiz",
  task: "Aufgabe",
  follow_up: "Follow-up",
  onsite: "Vor-Ort",
  remote: "Remote",
  system: "System",
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return "gerade eben"
  if (m < 60) return `vor ${m} Min.`
  const h = Math.floor(m / 60)
  if (h < 24) return `vor ${h} Std.`
  const d = Math.floor(h / 24)
  if (d === 1) return "gestern"
  return `vor ${d} Tagen`
}

const dotColors = ["bg-primary", "bg-chart-3", "bg-chart-2", "bg-chart-4", "bg-chart-5"]

export function AktivitaetCard() {
  const [items, setItems] = useState<Activity[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiClient
      .get("/api/backoffice/crm/activities/latest?limit=5")
      .then((r) => setItems(r.data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <div className="flex items-center justify-between">
        <h3 className="font-heading text-sm font-bold text-foreground">Letzte Aktivität</h3>
        <Link href="/crm/customers" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
          CRM →
        </Link>
      </div>

      {loading ? (
        <div className="mt-4 flex flex-col gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="flex gap-3 animate-pulse">
              <span className="mt-1 h-2 w-2 rounded-full bg-border" />
              <div className="flex-1 space-y-1">
                <div className="h-3 w-3/4 rounded bg-border" />
                <div className="h-2.5 w-1/3 rounded bg-border" />
              </div>
            </div>
          ))}
        </div>
      ) : items.length === 0 ? (
        <p className="mt-4 text-sm text-muted-foreground">Keine Aktivitäten vorhanden.</p>
      ) : (
        <ul className="mt-4 flex flex-col gap-4">
          {items.map((item, i) => (
            <li key={item.id} className="flex gap-3">
              <span className="relative mt-1 flex flex-col items-center">
                <span className={`h-2 w-2 shrink-0 rounded-full ${dotColors[i % dotColors.length]}`} />
                {i < items.length - 1 && (
                  <span className="absolute top-3 h-[calc(100%+0.25rem)] w-px bg-border" />
                )}
              </span>
              <div className="leading-tight">
                <p className="text-sm text-foreground">
                  {activityLabels[item.type] ?? item.type}
                  {item.customer_name ? ` – ${item.customer_name}` : ""}
                </p>
                {item.description && (
                  <p className="mt-0.5 truncate text-xs text-muted-foreground max-w-[180px]">{item.description}</p>
                )}
                <p className="mt-0.5 text-xs text-muted-foreground/70">{timeAgo(item.occurred_at ?? item.created_at)}</p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

const quickLinks = [
  { label: "CRM", icon: Users, href: "/crm" },
  { label: "Pipeline", icon: KanbanSquare, href: "/crm/pipeline" },
  { label: "Rechnungen", icon: FileText, href: "/invoices" },
  { label: "Projekte", icon: FolderKanban, href: "/projects" },
  { label: "Finanzen", icon: Wallet, href: "/finance" },
  { label: "Zeiterfassung", icon: Clock, href: "/time" },
  { label: "Support", icon: Headphones, href: "/support" },
  { label: "HR", icon: UserCog, href: "/hr" },
  { label: "Wissen", icon: BookOpen, href: "/knowledge" },
  { label: "Admin", icon: Settings, href: "/admin" },
]

const PRIO_COLOR: Record<string, string> = {
  urgent: "text-red-500",
  high: "text-orange-500",
  medium: "text-blue-500",
  low: "text-muted-foreground",
}
const PRIO_LABEL: Record<string, string> = {
  urgent: "Dringend", high: "Hoch", medium: "Mittel", low: "Niedrig",
}

export function TicketsCard() {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    supportService.list({ status: "open", limit: 5 })
      .then(data => setTickets(Array.isArray(data) ? data : (data as { items?: Ticket[] }).items ?? []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const urgentCount = tickets.filter(t => t.priority === "urgent" || t.priority === "high").length

  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <div className="flex items-center justify-between">
        <h3 className="font-heading text-sm font-bold text-foreground">Offene Tickets</h3>
        <Link href="/support" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
          Alle →
        </Link>
      </div>

      {loading ? (
        <div className="mt-4 space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-4 rounded bg-border animate-pulse" />
          ))}
        </div>
      ) : tickets.length === 0 ? (
        <p className="mt-4 text-sm text-muted-foreground">Keine offenen Tickets.</p>
      ) : (
        <>
          {urgentCount > 0 && (
            <p className="mt-3 text-xs font-medium text-red-500">{urgentCount} dringend/hoch priorisiert</p>
          )}
          <ul className="mt-3 space-y-2.5">
            {tickets.slice(0, 4).map(t => (
              <li key={t.id}>
                <Link
                  href={`/support/${t.id}`}
                  className="flex items-start gap-2 hover:text-primary transition-colors group"
                >
                  <span className={`mt-0.5 text-xs font-semibold shrink-0 ${PRIO_COLOR[t.priority] ?? "text-muted-foreground"}`}>
                    {PRIO_LABEL[t.priority] ?? t.priority}
                  </span>
                  <span className="text-sm text-foreground group-hover:text-primary truncate leading-tight">
                    {t.title}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  )
}

export function SchnellzugriffCard() {
  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <h3 className="font-heading text-sm font-bold text-foreground">Schnellzugriff</h3>
      <ul className="mt-4 grid grid-cols-2 gap-0.5">
        {quickLinks.map((link) => {
          const Icon = link.icon
          return (
            <li key={link.label}>
              <Link
                href={link.href}
                className="group flex items-center gap-2 rounded-lg px-2.5 py-2 text-sm text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
              >
                <Icon className="h-4 w-4 shrink-0" />
                <span className="truncate text-xs">{link.label}</span>
                <ArrowRight className="ml-auto h-3 w-3 opacity-0 transition-opacity group-hover:opacity-60 shrink-0" />
              </Link>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
