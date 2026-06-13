"use client"

import { useEffect, useState, useCallback, useRef } from "react"
import { timeTrackingService } from "@/lib/time-tracking/service"
import { projectService } from "@/lib/projects/service"
import { useAuth } from "@/components/providers/auth-provider"
import type { TimeEntry, TimeTrackingStats } from "@/lib/time-tracking/types"
import type { Project } from "@/lib/projects/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { PlayIcon, SquareIcon, ClockIcon, Trash2Icon, CheckIcon, XIcon } from "lucide-react"

const TASK_TYPES = ["Entwicklung", "Beratung", "Support", "Planung", "Design", "Meeting", "Dokumentation", "Sonstiges"]

function fmtMinutes(min: number | null | undefined) {
  if (!min) return "–"
  const h = Math.floor(min / 60)
  const m = min % 60
  return h > 0 ? `${h}h ${m > 0 ? `${m}min` : ""}`.trim() : `${m}min`
}

function fmtHours(h: number) {
  return `${h.toFixed(1)}h`
}

function fmtDateTime(dt: string) {
  return new Date(dt).toLocaleString("de-DE", { dateStyle: "short", timeStyle: "short" })
}

function fmtDate(dt: string) {
  return new Date(dt).toLocaleDateString("de-DE")
}

function ElapsedTimer({ startTime }: { startTime: string }) {
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => {
    const start = new Date(startTime).getTime()
    const tick = () => setElapsed(Math.floor((Date.now() - start) / 1000))
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [startTime])

  const h = Math.floor(elapsed / 3600)
  const m = Math.floor((elapsed % 3600) / 60)
  const s = elapsed % 60
  return (
    <span className="font-mono text-lg font-semibold tabular-nums text-primary">
      {String(h).padStart(2, "0")}:{String(m).padStart(2, "0")}:{String(s).padStart(2, "0")}
    </span>
  )
}

export function TimeTracker() {
  const { user } = useAuth()
  const [entries, setEntries] = useState<TimeEntry[]>([])
  const [stats, setStats] = useState<TimeTrackingStats | null>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState<TimeEntry | null>(null)

  // New entry state
  const [note, setNote] = useState("")
  const [taskType, setTaskType] = useState("Entwicklung")
  const [projectId, setProjectId] = useState("none")
  const [billable, setBillable] = useState(true)
  const [starting, setStarting] = useState(false)
  const [stopping, setStopping] = useState(false)

  const [deleteId, setDeleteId] = useState<string | null>(null)

  const load = useCallback(async () => {
    const [data, statsData] = await Promise.all([
      timeTrackingService.list({ limit: 50 }),
      timeTrackingService.getStats().catch(() => null),
    ])
    setEntries(data)
    setStats(statsData)
    setRunning(data.find(e => !e.end_time) ?? null)
    setLoading(false)
  }, [])

  useEffect(() => {
    projectService.list().then(setProjects)
    load()
  }, [load])

  async function handleStart() {
    if (!user) return
    setStarting(true)
    try {
      await timeTrackingService.create({
        employee_id: user.sub,
        project_id: projectId === "none" ? null : projectId,
        start_time: new Date().toISOString(),
        note: note || null,
        task_type: taskType || null,
        billable,
      })
      setNote("")
      load()
    } finally {
      setStarting(false)
    }
  }

  async function handleStop() {
    if (!running) return
    setStopping(true)
    try {
      await timeTrackingService.update(running.id, { end_time: new Date().toISOString() })
      load()
    } finally {
      setStopping(false)
    }
  }

  async function handleDelete() {
    if (!deleteId) return
    await timeTrackingService.delete(deleteId)
    setDeleteId(null)
    load()
  }

  const today = new Date().toLocaleDateString("de-DE")
  const todayEntries = entries.filter(e => fmtDate(e.start_time) === today)
  const olderEntries = entries.filter(e => fmtDate(e.start_time) !== today)

  return (
    <div className="space-y-6 px-8 py-6">
      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {[
            { label: "Heute", value: fmtHours(stats.total_hours_today) },
            { label: "Woche", value: fmtHours(stats.total_hours_week) },
            { label: "Monat", value: fmtHours(stats.total_hours_month) },
            { label: "Abrechenbar", value: fmtHours(stats.billable_hours), highlight: true },
          ].map(s => (
            <div key={s.label} className="rounded-lg border bg-card p-4">
              <p className="text-xs text-muted-foreground">{s.label}</p>
              <p className={`mt-1 text-2xl font-semibold ${s.highlight ? "text-primary" : ""}`}>{s.value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Timer */}
      <div className="rounded-xl border bg-card p-5">
        {running ? (
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <p className="text-xs text-muted-foreground mb-1">Läuft seit {fmtDateTime(running.start_time)}</p>
              <ElapsedTimer startTime={running.start_time} />
              {running.note && <p className="mt-1 text-sm text-muted-foreground">{running.note}</p>}
            </div>
            <Button onClick={handleStop} disabled={stopping} variant="destructive" size="sm">
              <SquareIcon className="mr-2 h-4 w-4" />
              {stopping ? "Stoppe…" : "Stoppen"}
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="flex gap-2">
              <Input
                value={note}
                onChange={e => setNote(e.target.value)}
                placeholder="Woran arbeitest du?"
                className="flex-1"
                onKeyDown={e => e.key === "Enter" && !starting && handleStart()}
              />
              <Button onClick={handleStart} disabled={starting} size="sm">
                <PlayIcon className="mr-2 h-4 w-4" />
                {starting ? "Start…" : "Starten"}
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              <Select value={taskType} onValueChange={v => v && setTaskType(v)}>
                <SelectTrigger className="w-44">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {TASK_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                </SelectContent>
              </Select>
              <Select value={projectId} onValueChange={v => v && setProjectId(v)}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Kein Projekt" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Kein Projekt</SelectItem>
                  {projects.map(p => <SelectItem key={p.id} value={p.id}>{p.title}</SelectItem>)}
                </SelectContent>
              </Select>
              <button
                onClick={() => setBillable(v => !v)}
                className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm transition-colors ${billable ? "border-primary bg-primary/10 text-primary" : "border-border text-muted-foreground"}`}
              >
                <CheckIcon className="h-3.5 w-3.5" />
                Abrechenbar
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Entries */}
      {loading ? (
        <div className="flex items-center justify-center py-16 text-sm text-muted-foreground">Laden…</div>
      ) : entries.length === 0 ? (
        <div className="flex flex-col items-center gap-3 py-16 text-muted-foreground">
          <ClockIcon className="h-10 w-10 opacity-30" />
          <p className="text-sm">Noch keine Einträge.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {todayEntries.length > 0 && (
            <EntryGroup label="Heute" entries={todayEntries} projects={projects} onDelete={id => setDeleteId(id)} onRefresh={load} />
          )}
          {olderEntries.length > 0 && (
            <EntryGroup label="Früher" entries={olderEntries} projects={projects} onDelete={id => setDeleteId(id)} onRefresh={load} />
          )}
        </div>
      )}

      <AlertDialog open={!!deleteId} onOpenChange={open => !open && setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Eintrag löschen?</AlertDialogTitle>
            <AlertDialogDescription>Dieser Zeiteintrag wird unwiderruflich gelöscht.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Löschen
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

function EntryGroup({ label, entries, projects, onDelete, onRefresh }: {
  label: string
  entries: TimeEntry[]
  projects: Project[]
  onDelete: (id: string) => void
  onRefresh: () => void
}) {
  const projectMap = Object.fromEntries(projects.map(p => [p.id, p.title]))
  const totalMin = entries.reduce((s, e) => s + (e.duration_minutes ?? 0), 0)

  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-sm font-medium text-muted-foreground">{label}</h2>
        <span className="text-sm text-muted-foreground">{fmtMinutes(totalMin)}</span>
      </div>
      <div className="divide-y rounded-lg border overflow-hidden">
        {entries.map(entry => (
          <EntryRow key={entry.id} entry={entry} projectTitle={entry.project_id ? projectMap[entry.project_id] : null} onDelete={onDelete} onRefresh={onRefresh} />
        ))}
      </div>
    </div>
  )
}

function EntryRow({ entry, projectTitle, onDelete, onRefresh }: {
  entry: TimeEntry
  projectTitle: string | null | undefined
  onDelete: (id: string) => void
  onRefresh: () => void
}) {
  const isRunning = !entry.end_time

  return (
    <div className={`group flex items-center gap-3 bg-card px-4 py-3 ${isRunning ? "bg-primary/5" : ""}`}>
      {isRunning && <span className="h-2 w-2 shrink-0 rounded-full bg-primary animate-pulse" />}
      <div className="flex-1 min-w-0">
        <p className="truncate text-sm font-medium">
          {entry.note || entry.task_type || "–"}
        </p>
        <p className="text-xs text-muted-foreground">
          {entry.task_type && <span className="mr-2">{entry.task_type}</span>}
          {projectTitle && <span className="mr-2">· {projectTitle}</span>}
          {new Date(entry.start_time).toLocaleTimeString("de-DE", { timeStyle: "short" })}
          {entry.end_time && ` – ${new Date(entry.end_time).toLocaleTimeString("de-DE", { timeStyle: "short" })}`}
        </p>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        {entry.billable && (
          <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs text-primary">€</span>
        )}
        {entry.is_approved && (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs text-green-700 dark:bg-green-900 dark:text-green-200">
            <CheckIcon className="inline h-3 w-3" />
          </span>
        )}
        <span className="text-sm font-medium tabular-nums">
          {isRunning ? <ElapsedTimer startTime={entry.start_time} /> : fmtMinutes(entry.duration_minutes)}
        </span>
        <button
          onClick={() => onDelete(entry.id)}
          className="opacity-0 group-hover:opacity-100 rounded p-1 text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-opacity"
        >
          <Trash2Icon className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  )
}
