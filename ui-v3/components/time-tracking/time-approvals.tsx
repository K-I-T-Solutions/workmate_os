"use client"

import { useEffect, useState, useCallback } from "react"
import { timeTrackingService } from "@/lib/time-tracking/service"
import { projectService } from "@/lib/projects/service"
import type { TimeEntry } from "@/lib/time-tracking/types"
import type { Project } from "@/lib/projects/types"
import { Button } from "@/components/ui/button"
import { CheckIcon, XIcon, CheckCheckIcon, ClockIcon } from "lucide-react"

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", year: "2-digit" })
}
function fmtTime(d: string) {
  return new Date(d).toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" })
}
function fmtMin(min: number | null | undefined) {
  if (!min) return "–"
  const h = Math.floor(min / 60)
  const m = min % 60
  return h > 0 ? `${h}h${m > 0 ? ` ${m}min` : ""}` : `${m}min`
}

export function TimeApprovals() {
  const [entries, setEntries] = useState<TimeEntry[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [processing, setProcessing] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    setSelected(new Set())
    try {
      const [rawEntries, projs] = await Promise.all([
        timeTrackingService.list({ is_approved: false, limit: 200 }),
        projectService.list().catch(() => [] as Project[]),
      ])
      const pending = rawEntries.filter(e => e.end_time !== null)
      setEntries(pending)
      setProjects(projs)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const projectMap = Object.fromEntries(projects.map(p => [p.id, p.title]))

  function toggleAll() {
    if (selected.size === entries.length) {
      setSelected(new Set())
    } else {
      setSelected(new Set(entries.map(e => e.id)))
    }
  }

  function toggle(id: string) {
    setSelected(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  async function approveSelected() {
    if (selected.size === 0) return
    setProcessing(true)
    try {
      await Promise.all([...selected].map(id => timeTrackingService.approve(id)))
      load()
    } finally {
      setProcessing(false)
    }
  }

  async function approveAll() {
    setProcessing(true)
    try {
      await Promise.all(entries.map(e => timeTrackingService.approve(e.id)))
      load()
    } finally {
      setProcessing(false)
    }
  }

  async function rejectSelected() {
    if (selected.size === 0) return
    setProcessing(true)
    try {
      await Promise.all([...selected].map(id => timeTrackingService.reject(id)))
      load()
    } finally {
      setProcessing(false)
    }
  }

  async function approveOne(id: string) {
    setProcessing(true)
    try {
      await timeTrackingService.approve(id)
      load()
    } finally {
      setProcessing(false)
    }
  }

  async function rejectOne(id: string) {
    setProcessing(true)
    try {
      await timeTrackingService.reject(id)
      load()
    } finally {
      setProcessing(false)
    }
  }

  if (loading) {
    return <div className="py-16 text-center text-sm text-muted-foreground">Laden…</div>
  }

  if (entries.length === 0) {
    return (
      <div className="flex flex-col items-center gap-4 py-24 text-muted-foreground">
        <CheckCheckIcon className="h-10 w-10 opacity-30" />
        <p className="text-sm">Keine ausstehenden Freigaben.</p>
      </div>
    )
  }

  const totalMinPending = entries.reduce((s, e) => s + (e.duration_minutes ?? 0), 0)

  return (
    <div className="space-y-4 px-8 py-6">
      {/* Header / Bulk actions */}
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <p className="text-sm font-medium">
            {entries.length} Eintr{entries.length !== 1 ? "äge" : "ag"} ausstehend
          </p>
          <p className="text-xs text-muted-foreground mt-0.5">
            Gesamt: {(totalMinPending / 60).toFixed(1)}h
          </p>
        </div>
        <div className="flex items-center gap-2">
          {selected.size > 0 && (
            <>
              <span className="text-xs text-muted-foreground">{selected.size} ausgewählt</span>
              <Button
                size="sm"
                variant="outline"
                disabled={processing}
                onClick={rejectSelected}
                className="text-destructive hover:bg-destructive/10 hover:text-destructive border-destructive/30"
              >
                <XIcon className="mr-1.5 h-3.5 w-3.5" />
                Ablehnen
              </Button>
              <Button size="sm" disabled={processing} onClick={approveSelected}>
                <CheckIcon className="mr-1.5 h-3.5 w-3.5" />
                Genehmigen
              </Button>
            </>
          )}
          <Button size="sm" variant="outline" disabled={processing} onClick={approveAll}>
            <CheckCheckIcon className="mr-1.5 h-3.5 w-3.5" />
            Alle genehmigen
          </Button>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-lg border overflow-hidden">
        {/* Column header */}
        <div className="flex items-center gap-3 border-b bg-muted/40 px-4 py-2 text-xs font-medium text-muted-foreground">
          <input
            type="checkbox"
            checked={selected.size === entries.length}
            onChange={toggleAll}
            className="h-3.5 w-3.5 rounded"
          />
          <span className="w-24 shrink-0">Datum</span>
          <span className="w-24 shrink-0">Zeit</span>
          <span className="flex-1">Beschreibung / Projekt</span>
          <span className="w-14 text-right shrink-0">Dauer</span>
          <span className="w-20 shrink-0" />
        </div>

        {entries.map(e => (
          <div
            key={e.id}
            className="flex items-center gap-3 border-b bg-card px-4 py-2.5 last:border-0 hover:bg-muted/20 transition-colors"
          >
            <input
              type="checkbox"
              checked={selected.has(e.id)}
              onChange={() => toggle(e.id)}
              className="h-3.5 w-3.5 rounded"
            />
            <span className="w-24 shrink-0 text-xs tabular-nums">{fmtDate(e.start_time)}</span>
            <span className="w-24 shrink-0 text-xs tabular-nums text-muted-foreground">
              {fmtTime(e.start_time)}{e.end_time ? ` – ${fmtTime(e.end_time)}` : ""}
            </span>
            <div className="flex-1 min-w-0">
              <p className="truncate text-sm">{e.note || e.task_type || "–"}</p>
              {e.project_id && projectMap[e.project_id] && (
                <p className="truncate text-xs text-muted-foreground">{projectMap[e.project_id]}</p>
              )}
            </div>
            <span className="w-14 shrink-0 text-right text-sm font-medium tabular-nums">
              {fmtMin(e.duration_minutes)}
            </span>
            <div className="flex w-20 shrink-0 items-center justify-end gap-1">
              <button
                onClick={() => rejectOne(e.id)}
                disabled={processing}
                className="rounded p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
                title="Ablehnen"
              >
                <XIcon className="h-3.5 w-3.5" />
              </button>
              <button
                onClick={() => approveOne(e.id)}
                disabled={processing}
                className="rounded p-1.5 text-muted-foreground hover:bg-green-500/10 hover:text-green-600 transition-colors"
                title="Genehmigen"
              >
                <CheckIcon className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
