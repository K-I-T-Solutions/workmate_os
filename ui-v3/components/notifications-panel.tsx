"use client"

import { useEffect, useState, useRef, useCallback } from "react"
import { useRouter } from "next/navigation"
import { invoiceService } from "@/lib/invoices/service"
import { supportService } from "@/lib/support/service"
import { hrService } from "@/lib/hr/service"
import type { Invoice } from "@/lib/invoices/types"
import type { Ticket } from "@/lib/support/types"
import type { LeaveRequest } from "@/lib/hr/types"
import { Bell, FileText, MessageSquare, CalendarClock, ChevronRight, CheckCheck } from "lucide-react"

interface Notification {
  id: string
  type: "invoice" | "ticket" | "leave"
  title: string
  subtitle: string
  href: string
  severity: "warning" | "error" | "info"
}

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit" })
}

const SEVERITY_DOT: Record<Notification["severity"], string> = {
  error: "bg-red-500",
  warning: "bg-amber-500",
  info: "bg-blue-500",
}

const TYPE_ICON: Record<Notification["type"], React.ReactNode> = {
  invoice: <FileText className="h-4 w-4" />,
  ticket: <MessageSquare className="h-4 w-4" />,
  leave: <CalendarClock className="h-4 w-4" />,
}

const TYPE_BG: Record<Notification["type"], string> = {
  invoice: "bg-emerald-500/15 text-emerald-500",
  ticket: "bg-orange-500/15 text-orange-500",
  leave: "bg-blue-500/15 text-blue-500",
}

function buildNotifications(
  invoices: Invoice[],
  tickets: Ticket[],
  leaves: LeaveRequest[],
): Notification[] {
  const out: Notification[] = []

  for (const inv of invoices.slice(0, 5)) {
    out.push({
      id: `inv-${inv.id}`,
      type: "invoice",
      title: `Rechnung ${inv.invoice_number} überfällig`,
      subtitle: `${inv.customer?.name ?? ""} · ${inv.due_date ? fmtDate(inv.due_date) : ""}`,
      href: `/invoices/${inv.id}`,
      severity: "error",
    })
  }

  for (const t of tickets.filter(t => t.sla_breached).slice(0, 5)) {
    out.push({
      id: `t-sla-${t.id}`,
      type: "ticket",
      title: `SLA verletzt: ${t.ticket_number}`,
      subtitle: t.title.slice(0, 60),
      href: `/support/${t.id}`,
      severity: "error",
    })
  }

  for (const t of tickets.filter(t => !t.sla_breached && t.priority === "urgent").slice(0, 3)) {
    out.push({
      id: `t-urg-${t.id}`,
      type: "ticket",
      title: `Dringendes Ticket: ${t.ticket_number}`,
      subtitle: t.title.slice(0, 60),
      href: `/support/${t.id}`,
      severity: "warning",
    })
  }

  for (const lr of leaves.slice(0, 5)) {
    out.push({
      id: `lr-${lr.id}`,
      type: "leave",
      title: "Urlaubsantrag ausstehend",
      subtitle: `${lr.start_date ? fmtDate(lr.start_date) : ""} – ${lr.end_date ? fmtDate(lr.end_date) : ""} · ${lr.total_days}d`,
      href: "/hr",
      severity: "info",
    })
  }

  return out
}

export function NotificationsPanel() {
  const [open, setOpen] = useState(false)
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(false)
  const [loaded, setLoaded] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const router = useRouter()

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener("mousedown", handleClick)
    return () => document.removeEventListener("mousedown", handleClick)
  }, [])

  const loadNotifications = useCallback(async () => {
    if (loaded) return
    setLoading(true)
    try {
      const [invRes, tickRes, leaveRes] = await Promise.all([
        invoiceService.list({ status: "overdue", limit: 20 }).catch(() => ({ items: [] as Invoice[] })),
        supportService.list({ limit: 100 }).catch(() => ({ items: [] as Ticket[] })),
        hrService.listLeaveRequests({ status: "pending" }).catch(() => [] as LeaveRequest[]),
      ])
      const invs = invRes.items ?? []
      const ticks = tickRes.items ?? []
      const leaves = Array.isArray(leaveRes) ? leaveRes : []
      setNotifications(buildNotifications(invs, ticks, leaves))
      setLoaded(true)
    } finally {
      setLoading(false)
    }
  }, [loaded])

  function handleOpen() {
    setOpen(v => {
      if (!v) loadNotifications()
      return !v
    })
  }

  function navigate(href: string) {
    setOpen(false)
    router.push(href)
  }

  const count = notifications.length
  const hasError = notifications.some(n => n.severity === "error")

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={handleOpen}
        className="relative flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
        title="Benachrichtigungen"
      >
        <Bell className="h-[18px] w-[18px]" />
        {count > 0 && (
          <span className={`absolute right-1 top-1 flex h-4 w-4 items-center justify-center rounded-full text-[9px] font-bold text-white ${hasError ? "bg-red-500" : "bg-amber-500"}`}>
            {count > 9 ? "9+" : count}
          </span>
        )}
        {count === 0 && loaded && (
          <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-green-500" />
        )}
        {!loaded && (
          <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-primary" />
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-10 z-50 w-80 rounded-xl border border-border bg-card shadow-lg overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-border px-4 py-3">
            <span className="text-sm font-semibold">Benachrichtigungen</span>
            {count > 0 && (
              <span className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
                {count}
              </span>
            )}
          </div>

          {/* Content */}
          <div className="max-h-[60vh] overflow-y-auto">
            {loading ? (
              <div className="flex items-center justify-center py-10 text-sm text-muted-foreground">
                Laden…
              </div>
            ) : notifications.length === 0 ? (
              <div className="flex flex-col items-center gap-3 py-10 text-muted-foreground">
                <CheckCheck className="h-8 w-8 opacity-30" />
                <p className="text-sm">Alles in Ordnung!</p>
              </div>
            ) : (
              <ul className="divide-y divide-border">
                {notifications.map(n => (
                  <li key={n.id}>
                    <button
                      type="button"
                      onClick={() => navigate(n.href)}
                      className="flex w-full items-start gap-3 px-4 py-3 text-left hover:bg-muted/50 transition-colors"
                    >
                      {/* Icon */}
                      <div className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg ${TYPE_BG[n.type]}`}>
                        {TYPE_ICON[n.type]}
                      </div>
                      {/* Text */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-1.5">
                          <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${SEVERITY_DOT[n.severity]}`} />
                          <p className="truncate text-xs font-medium text-foreground">{n.title}</p>
                        </div>
                        <p className="mt-0.5 truncate text-[11px] text-muted-foreground">{n.subtitle}</p>
                      </div>
                      <ChevronRight className="h-3.5 w-3.5 shrink-0 mt-1.5 text-muted-foreground/40" />
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Footer */}
          {count > 0 && (
            <div className="border-t border-border p-2">
              <button
                type="button"
                onClick={() => { setOpen(false); router.push("/support") }}
                className="w-full rounded-lg px-3 py-2 text-xs text-muted-foreground hover:bg-muted transition-colors text-center"
              >
                Alle Support-Tickets anzeigen →
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
