"use client"

import { useEffect, useState, useCallback } from "react"
import { timeTrackingService } from "@/lib/time-tracking/service"
import { projectService } from "@/lib/projects/service"
import { crmService } from "@/lib/crm/service"
import type { TimeEntry, TimeTrackingStats } from "@/lib/time-tracking/types"
import type { Project } from "@/lib/projects/types"
import type { Customer } from "@/lib/crm/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { DownloadIcon } from "lucide-react"

type Period = "today" | "week" | "month" | "custom"

const pad = (n: number) => String(n).padStart(2, "0")
const fmtDate = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`

function getDefaultRange(period: Period): { start: string; end: string } {
  const now = new Date()
  const today = fmtDate(now)
  if (period === "today") return { start: today, end: today }
  if (period === "week") {
    const day = now.getDay()
    const mon = new Date(now)
    mon.setDate(now.getDate() - (day === 0 ? 6 : day - 1))
    const sun = new Date(mon)
    sun.setDate(mon.getDate() + 6)
    return { start: fmtDate(mon), end: fmtDate(sun) }
  }
  if (period === "month") {
    const start = new Date(now.getFullYear(), now.getMonth(), 1)
    const end = new Date(now.getFullYear(), now.getMonth() + 1, 0)
    return { start: fmtDate(start), end: fmtDate(end) }
  }
  return { start: fmtDate(new Date(now.getFullYear(), now.getMonth(), 1)), end: today }
}

function fmtMin(min: number | null | undefined) {
  if (!min) return "–"
  const h = Math.floor(min / 60)
  const m = min % 60
  return h > 0 ? `${h}h${m > 0 ? ` ${m}min` : ""}` : `${m}min`
}

function HoursBarList({ items, color = "bg-primary" }: {
  items: { label: string; hours: number }[]
  color?: string
}) {
  if (items.length === 0) return <p className="text-sm text-muted-foreground">Keine Daten.</p>
  const max = Math.max(...items.map(i => i.hours), 0.01)
  return (
    <ul className="space-y-2.5">
      {items.map(item => (
        <li key={item.label} className="flex items-center gap-3">
          <span className="w-36 shrink-0 truncate text-xs text-muted-foreground" title={item.label}>
            {item.label || "Unbekannt"}
          </span>
          <div className="flex-1 h-1.5 rounded-full bg-muted overflow-hidden">
            <div
              className={`h-full rounded-full ${color}`}
              style={{ width: `${Math.round((item.hours / max) * 100)}%` }}
            />
          </div>
          <span className="w-14 shrink-0 text-right text-xs font-medium tabular-nums">
            {item.hours.toFixed(1)}h
          </span>
        </li>
      ))}
    </ul>
  )
}

function exportCsv(entries: TimeEntry[], projectMap: Record<string, string>) {
  const q = (s: string) => `"${s.replace(/"/g, '""')}"`
  const fmtD = (d: string) => new Date(d).toLocaleDateString("de-DE")
  const fmtT = (d: string) => new Date(d).toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" })

  const header = ["Datum", "Von", "Bis", "Minuten", "Tätigkeitstyp", "Projekt", "Notiz", "Abrechenbar", "Stundensatz"].join(";")
  const rows = entries.map(e => [
    fmtD(e.start_time),
    fmtT(e.start_time),
    e.end_time ? fmtT(e.end_time) : "",
    e.duration_minutes ?? "",
    q(e.task_type ?? ""),
    q(e.project_id ? (projectMap[e.project_id] ?? "") : ""),
    q(e.note ?? ""),
    e.billable ? "Ja" : "Nein",
    e.hourly_rate ?? "",
  ].join(";"))

  const csv = "﻿" + [header, ...rows].join("\r\n")
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = `zeitbericht-${new Date().toISOString().slice(0, 10)}.csv`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const PERIODS: { id: Period; label: string }[] = [
  { id: "today", label: "Heute" },
  { id: "week", label: "Diese Woche" },
  { id: "month", label: "Dieser Monat" },
  { id: "custom", label: "Benutzerdefiniert" },
]

export function TimeReports() {
  const [period, setPeriod] = useState<Period>("month")
  const [range, setRange] = useState(getDefaultRange("month"))
  const [entries, setEntries] = useState<TimeEntry[]>([])
  const [allStats, setAllStats] = useState<TimeTrackingStats | null>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [customers, setCustomers] = useState<Customer[]>([])
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(false)

  const projectMap = Object.fromEntries(projects.map(p => [p.id, p.title]))

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [ents, stats, projs, custs] = await Promise.all([
        timeTrackingService.list({ start_date: range.start, end_date: range.end, limit: 500 }),
        timeTrackingService.getStats().catch(() => null),
        projectService.list().catch(() => []),
        crmService.getCustomers({ limit: 500 }).catch(() => [] as Customer[]),
      ])
      setEntries(ents)
      setAllStats(stats)
      setProjects(projs)
      setCustomers(Array.isArray(custs) ? custs : (custs as unknown as { items?: Customer[] }).items ?? [])
    } finally {
      setLoading(false)
    }
  }, [range.start, range.end])

  useEffect(() => { load() }, [load])

  function selectPeriod(p: Period) {
    setPeriod(p)
    if (p !== "custom") setRange(getDefaultRange(p))
  }

  // Compute stats from filtered entries
  const totalMin = entries.reduce((s, e) => s + (e.duration_minutes ?? 0), 0)
  const billableMin = entries.filter(e => e.billable).reduce((s, e) => s + (e.duration_minutes ?? 0), 0)
  const nonBillableMin = totalMin - billableMin

  // Hours by project from filtered entries
  const byProject = Object.entries(
    entries.reduce<Record<string, number>>((acc, e) => {
      if (!e.project_id) return acc
      const title = projectMap[e.project_id] ?? e.project_id
      acc[title] = (acc[title] ?? 0) + (e.duration_minutes ?? 0) / 60
      return acc
    }, {})
  ).map(([label, hours]) => ({ label, hours })).sort((a, b) => b.hours - a.hours)

  // Hours by task type from filtered entries
  const byType = Object.entries(
    entries.reduce<Record<string, number>>((acc, e) => {
      const type = e.task_type ?? "Sonstiges"
      acc[type] = (acc[type] ?? 0) + (e.duration_minutes ?? 0) / 60
      return acc
    }, {})
  ).map(([label, hours]) => ({ label, hours })).sort((a, b) => b.hours - a.hours)

  const approvalPending = entries.filter(e => !e.is_approved && e.end_time).length

  // Hours by customer (project → customer_id → customer name)
  const customerMap = Object.fromEntries(customers.map(c => [c.id, c.name]))
  const byCustomer = Object.entries(
    entries.reduce<Record<string, number>>((acc, e) => {
      if (!e.project_id) return acc
      const proj = projects.find(p => p.id === e.project_id)
      if (!proj?.customer_id) return acc
      const name = customerMap[proj.customer_id] ?? proj.customer_id
      acc[name] = (acc[name] ?? 0) + (e.duration_minutes ?? 0) / 60
      return acc
    }, {})
  ).map(([label, hours]) => ({ label, hours })).sort((a, b) => b.hours - a.hours)

  return (
    <div className="space-y-6 px-8 py-6">
      {/* Period selector */}
      <div className="flex flex-wrap items-center gap-2">
        <div className="flex gap-1 rounded-lg border bg-muted p-1">
          {PERIODS.map(p => (
            <button
              key={p.id}
              onClick={() => selectPeriod(p.id)}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                period === p.id ? "bg-card text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>

        {period === "custom" && (
          <div className="flex items-center gap-2">
            <Input
              type="date"
              value={range.start}
              onChange={e => setRange(r => ({ ...r, start: e.target.value }))}
              className="w-36 text-sm"
            />
            <span className="text-xs text-muted-foreground">bis</span>
            <Input
              type="date"
              value={range.end}
              onChange={e => setRange(r => ({ ...r, end: e.target.value }))}
              className="w-36 text-sm"
            />
          </div>
        )}

        <Button
          variant="outline"
          size="sm"
          className="ml-auto"
          disabled={exporting || entries.length === 0}
          onClick={() => {
            setExporting(true)
            exportCsv(entries, projectMap)
            setExporting(false)
          }}
        >
          <DownloadIcon className="mr-2 h-4 w-4" />
          {exporting ? "Exportiere…" : "CSV-Export"}
        </Button>
      </div>

      {loading ? (
        <div className="py-12 text-center text-sm text-muted-foreground">Laden…</div>
      ) : (
        <>
          {/* Summary stats */}
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { label: "Gesamt", value: `${(totalMin / 60).toFixed(1)}h`, sub: `${entries.length} Einträge` },
              { label: "Abrechenbar", value: `${(billableMin / 60).toFixed(1)}h`, sub: totalMin ? `${Math.round(billableMin / totalMin * 100)}%` : "–", highlight: true },
              { label: "Nicht abrechenbar", value: `${(nonBillableMin / 60).toFixed(1)}h`, sub: "" },
              { label: "Genehmigung ausstehend", value: String(approvalPending), sub: "nicht genehmigt" },
            ].map(s => (
              <div key={s.label} className="rounded-lg border bg-card p-4">
                <p className="text-xs text-muted-foreground">{s.label}</p>
                <p className={`mt-1 text-2xl font-semibold ${s.highlight ? "text-primary" : ""}`}>{s.value}</p>
                {s.sub && <p className="mt-0.5 text-xs text-muted-foreground">{s.sub}</p>}
              </div>
            ))}
          </div>

          {/* Charts row */}
          <div className={`grid gap-6 ${byCustomer.length > 0 ? "lg:grid-cols-3" : "lg:grid-cols-2"}`}>
            <div className="rounded-xl border bg-card p-5">
              <h3 className="mb-4 text-sm font-semibold">Stunden nach Projekt</h3>
              {byProject.length === 0 ? (
                <p className="text-sm text-muted-foreground">Keine Projektzeiten im Zeitraum.</p>
              ) : (
                <HoursBarList items={byProject} color="bg-primary" />
              )}
            </div>
            <div className="rounded-xl border bg-card p-5">
              <h3 className="mb-4 text-sm font-semibold">Stunden nach Tätigkeitstyp</h3>
              <HoursBarList items={byType} color="bg-chart-3" />
            </div>
            {byCustomer.length > 0 && (
              <div className="rounded-xl border bg-card p-5">
                <h3 className="mb-4 text-sm font-semibold">Stunden je Kunde</h3>
                <HoursBarList items={byCustomer} color="bg-chart-2" />
              </div>
            )}
          </div>

          {/* All-time stats from API */}
          {allStats && (allStats.hours_by_project.length > 0 || allStats.hours_by_task_type.length > 0) && (
            <div className="rounded-xl border bg-card p-5">
              <h3 className="mb-1 text-sm font-semibold">Gesamtstatistik</h3>
              <p className="mb-4 text-xs text-muted-foreground">Heute {allStats.total_hours_today.toFixed(1)}h · Woche {allStats.total_hours_week.toFixed(1)}h · Monat {allStats.total_hours_month.toFixed(1)}h</p>
              <div className="grid gap-6 lg:grid-cols-2">
                <div>
                  <p className="mb-3 text-xs font-medium text-muted-foreground uppercase tracking-wide">Nach Projekt (gesamt)</p>
                  <HoursBarList
                    items={allStats.hours_by_project.map(i => ({ label: i.project_title, hours: i.hours }))}
                    color="bg-chart-2"
                  />
                </div>
                <div>
                  <p className="mb-3 text-xs font-medium text-muted-foreground uppercase tracking-wide">Nach Tätigkeitstyp (gesamt)</p>
                  <HoursBarList
                    items={allStats.hours_by_task_type.map(i => ({ label: i.task_type ?? "Sonstiges", hours: i.hours }))}
                    color="bg-chart-4"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Entry list */}
          {entries.length > 0 && (
            <div>
              <h3 className="mb-3 text-sm font-semibold text-muted-foreground">{entries.length} Einträge im Zeitraum</h3>
              <div className="divide-y rounded-lg border overflow-hidden">
                {entries.map(e => (
                  <div key={e.id} className="flex items-center gap-3 bg-card px-4 py-2.5">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm truncate">{e.note || e.task_type || "–"}</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(e.start_time).toLocaleDateString("de-DE")}
                        {e.project_id && projectMap[e.project_id] ? ` · ${projectMap[e.project_id]}` : ""}
                        {e.task_type ? ` · ${e.task_type}` : ""}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 shrink-0 text-xs text-muted-foreground">
                      {e.billable && <span className="rounded-full bg-primary/10 px-1.5 py-0.5 text-primary">€</span>}
                      {e.is_approved && <span className="text-green-600">✓</span>}
                      <span className="font-medium text-foreground tabular-nums">{fmtMin(e.duration_minutes)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
