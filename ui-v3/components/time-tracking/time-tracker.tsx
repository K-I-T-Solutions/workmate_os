"use client"

import { useEffect, useState, useCallback } from "react"
import { timeTrackingService } from "@/lib/time-tracking/service"
import { projectService } from "@/lib/projects/service"
import { useAuth } from "@/components/providers/auth-provider"
import type { TimeEntry, TimeTrackingStats } from "@/lib/time-tracking/types"
import type { Project } from "@/lib/projects/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { PlayIcon, SquareIcon, ClockIcon, Trash2Icon, CheckIcon, AlertTriangleIcon, AlertCircleIcon, PencilIcon, TimerIcon } from "lucide-react"

// ArbZG §4: Pausen ab 6h Arbeit 30min, ab 9h 45min
// ArbZG §3: Max 8h/Tag, Ausnahme bis 10h wenn Ausgleich
// ArbZG §5: Min 11h Ruhezeit zwischen Arbeitstagen

const TASK_TYPES = ["Entwicklung", "Beratung", "Support", "Planung", "Design", "Meeting", "Dokumentation", "Pause", "Sonstiges"]
const PAUSE_TYPE = "Pause"

// ─── Formatierung ────────────────────────────────────────────

function fmtMinutes(min: number | null | undefined) {
  if (!min) return "–"
  const h = Math.floor(min / 60)
  const m = min % 60
  return h > 0 ? `${h}h ${m > 0 ? `${m}min` : ""}`.trim() : `${m}min`
}

function fmtHours(h: number) {
  return `${h.toFixed(1)}h`
}

function fmtTime(dt: string) {
  return new Date(dt).toLocaleTimeString("de-DE", { timeStyle: "short" })
}

function fmtDayLabel(isoDate: string) {
  const d = new Date(isoDate + "T12:00:00")
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)

  const isoToday = today.toISOString().slice(0, 10)
  const isoYesterday = yesterday.toISOString().slice(0, 10)

  if (isoDate === isoToday) return "Heute"
  if (isoDate === isoYesterday) return "Gestern"

  return d.toLocaleDateString("de-DE", { weekday: "short", day: "2-digit", month: "2-digit", year: "numeric" })
}

// ─── ArbZG Compliance ────────────────────────────────────────

type ComplianceStatus = "ok" | "warn" | "violation"

interface DayCompliance {
  status: ComplianceStatus
  issues: string[]
  netMinutes: number   // Arbeitszeit ohne Pausen
  pauseMinutes: number
  firstStart: string | null
  lastEnd: string | null
}

function checkCompliance(entries: TimeEntry[]): DayCompliance {
  const issues: string[] = []
  const finished = entries.filter(e => e.end_time)

  const pauseEntries = finished.filter(e => e.task_type === PAUSE_TYPE)
  const workEntries = finished.filter(e => e.task_type !== PAUSE_TYPE)

  const pauseMinutes = pauseEntries.reduce((s, e) => s + (e.duration_minutes ?? 0), 0)
  const netMinutes = workEntries.reduce((s, e) => s + (e.duration_minutes ?? 0), 0)
  const netHours = netMinutes / 60

  const allStarts = finished.map(e => new Date(e.start_time).getTime())
  const allEnds = finished.map(e => new Date(e.end_time!).getTime())
  const firstStart = allStarts.length ? new Date(Math.min(...allStarts)).toISOString() : null
  const lastEnd = allEnds.length ? new Date(Math.max(...allEnds)).toISOString() : null

  // ArbZG §3: Über 10h ist Überschreitung
  if (netHours > 10) {
    issues.push("Arbeitszeit über 10h (ArbZG §3)")
  } else if (netHours > 8) {
    issues.push("Arbeitszeit über 8h — Ausgleich erforderlich (ArbZG §3)")
  }

  // ArbZG §4: Pause bei >6h mind. 30min, bei >9h mind. 45min
  if (netHours > 9 && pauseMinutes < 45) {
    issues.push(`Pause zu kurz: ${pauseMinutes}min erfasst, mind. 45min erforderlich (ArbZG §4)`)
  } else if (netHours > 6 && pauseMinutes < 30) {
    issues.push(`Pause zu kurz: ${pauseMinutes}min erfasst, mind. 30min erforderlich (ArbZG §4)`)
  }

  const status: ComplianceStatus =
    issues.some(i => i.includes("über 10h") || i.includes("Pause zu kurz")) ? "violation"
    : issues.length > 0 ? "warn"
    : "ok"

  return { status, issues, netMinutes, pauseMinutes, firstStart, lastEnd }
}

// ─── Timer ───────────────────────────────────────────────────

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

// ─── Hauptkomponente ──────────────────────────────────────────

export function TimeTracker() {
  const { user } = useAuth()
  const [entries, setEntries] = useState<TimeEntry[]>([])
  const [stats, setStats] = useState<TimeTrackingStats | null>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState<TimeEntry | null>(null)

  // Timer-Modus
  const [note, setNote] = useState("")
  const [taskType, setTaskType] = useState("Entwicklung")
  const [projectId, setProjectId] = useState("none")
  const [billable, setBillable] = useState(true)
  const [starting, setStarting] = useState(false)
  const [stopping, setStopping] = useState(false)
  const [deleteId, setDeleteId] = useState<string | null>(null)

  // Manuell-Modus
  const [inputMode, setInputMode] = useState<"timer" | "manual">("timer")
  const todayStr = new Date().toISOString().slice(0, 10)
  const [manualDate, setManualDate] = useState(todayStr)
  const [manualStart, setManualStart] = useState("")
  const [manualEnd, setManualEnd] = useState("")
  const [manualNote, setManualNote] = useState("")
  const [manualTaskType, setManualTaskType] = useState("Entwicklung")
  const [manualProjectId, setManualProjectId] = useState("none")
  const [manualBillable, setManualBillable] = useState(true)
  const [manualSaving, setManualSaving] = useState(false)

  const load = useCallback(async () => {
    const [data, statsData] = await Promise.all([
      timeTrackingService.list({ limit: 200 }),
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

  // Pause-Einträge sollen nie billable sein
  const effectiveBillable = taskType === PAUSE_TYPE ? false : billable

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
        billable: effectiveBillable,
      })
      setNote("")
      load()
    } finally {
      setStarting(false)
    }
  }

  async function handleManualSave() {
    if (!user || !manualStart || !manualEnd) return
    setManualSaving(true)
    try {
      const startISO = new Date(`${manualDate}T${manualStart}`).toISOString()
      const endISO = new Date(`${manualDate}T${manualEnd}`).toISOString()
      await timeTrackingService.create({
        employee_id: user.sub,
        project_id: manualTaskType === PAUSE_TYPE ? null : (manualProjectId === "none" ? null : manualProjectId),
        start_time: startISO,
        end_time: endISO,
        note: manualNote || null,
        task_type: manualTaskType || null,
        billable: manualTaskType === PAUSE_TYPE ? false : manualBillable,
      })
      setManualNote("")
      setManualStart("")
      setManualEnd("")
      load()
    } finally {
      setManualSaving(false)
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

  // Nach Datum gruppieren
  const grouped = groupByDate(entries)

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

      {/* Erfassungs-Widget */}
      <div className="rounded-xl border bg-card p-5">
        {running ? (
          /* Laufender Timer */
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <p className="text-xs text-muted-foreground mb-1">
                {running.task_type === PAUSE_TYPE ? "⏸ Pause läuft seit" : "▶ Läuft seit"} {fmtTime(running.start_time)}
              </p>
              <ElapsedTimer startTime={running.start_time} />
              {running.note && <p className="mt-1 text-sm text-muted-foreground">{running.note}</p>}
            </div>
            <Button onClick={handleStop} disabled={stopping} variant="destructive" size="sm">
              <SquareIcon className="mr-2 h-4 w-4" />
              {stopping ? "Stoppe…" : "Stoppen"}
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Modus-Toggle */}
            <div className="flex gap-1 rounded-lg border bg-muted p-1 w-fit">
              <button
                onClick={() => setInputMode("timer")}
                className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${inputMode === "timer" ? "bg-card text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"}`}
              >
                <TimerIcon className="h-3.5 w-3.5" />
                Timer
              </button>
              <button
                onClick={() => setInputMode("manual")}
                className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${inputMode === "manual" ? "bg-card text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"}`}
              >
                <PencilIcon className="h-3.5 w-3.5" />
                Manuell
              </button>
            </div>

            {inputMode === "timer" ? (
              /* Timer-Modus */
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
                  <Select value={taskType} onValueChange={v => {
                    if (!v) return
                    setTaskType(v)
                    if (v === PAUSE_TYPE) setBillable(false)
                  }}>
                    <SelectTrigger className="w-44">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {TASK_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                    </SelectContent>
                  </Select>
                  {taskType !== PAUSE_TYPE && (
                    <Select value={projectId} onValueChange={v => v && setProjectId(v)}>
                      <SelectTrigger className="w-48">
                        <SelectValue placeholder="Kein Projekt" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">Kein Projekt</SelectItem>
                        {projects.map(p => <SelectItem key={p.id} value={p.id}>{p.title}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  )}
                  {taskType !== PAUSE_TYPE && (
                    <button
                      onClick={() => setBillable(v => !v)}
                      className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm transition-colors ${billable ? "border-primary bg-primary/10 text-primary" : "border-border text-muted-foreground"}`}
                    >
                      <CheckIcon className="h-3.5 w-3.5" />
                      Abrechenbar
                    </button>
                  )}
                </div>
              </div>
            ) : (
              /* Manuell-Modus */
              <div className="space-y-3">
                {/* Datum + Zeiten */}
                <div className="flex flex-wrap gap-2 items-end">
                  <div className="grid gap-1">
                    <label className="text-xs text-muted-foreground">Datum</label>
                    <input
                      type="date"
                      value={manualDate}
                      max={todayStr}
                      onChange={e => setManualDate(e.target.value)}
                      className="h-8 rounded-lg border border-input bg-transparent px-2 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/30"
                    />
                  </div>
                  <div className="grid gap-1">
                    <label className="text-xs text-muted-foreground">Von</label>
                    <input
                      type="time"
                      value={manualStart}
                      onChange={e => setManualStart(e.target.value)}
                      className="h-8 rounded-lg border border-input bg-transparent px-2 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/30"
                    />
                  </div>
                  <div className="grid gap-1">
                    <label className="text-xs text-muted-foreground">Bis</label>
                    <input
                      type="time"
                      value={manualEnd}
                      onChange={e => setManualEnd(e.target.value)}
                      className="h-8 rounded-lg border border-input bg-transparent px-2 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/30"
                    />
                  </div>
                  {manualStart && manualEnd && manualEnd > manualStart && (
                    <span className="text-xs text-muted-foreground pb-1.5">
                      {(() => {
                        const [sh, sm] = manualStart.split(":").map(Number)
                        const [eh, em] = manualEnd.split(":").map(Number)
                        const mins = (eh * 60 + em) - (sh * 60 + sm)
                        return fmtMinutes(mins)
                      })()}
                    </span>
                  )}
                </div>

                {/* Notiz */}
                <Input
                  value={manualNote}
                  onChange={e => setManualNote(e.target.value)}
                  placeholder="Beschreibung (optional)"
                  className="h-8 text-sm"
                />

                {/* Typ + Projekt + Billable + Speichern */}
                <div className="flex flex-wrap gap-2">
                  <Select value={manualTaskType} onValueChange={v => {
                    if (!v) return
                    setManualTaskType(v)
                    if (v === PAUSE_TYPE) setManualBillable(false)
                  }}>
                    <SelectTrigger className="w-44">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {TASK_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                    </SelectContent>
                  </Select>

                  {manualTaskType !== PAUSE_TYPE && (
                    <Select value={manualProjectId} onValueChange={v => v && setManualProjectId(v)}>
                      <SelectTrigger className="w-48">
                        <SelectValue placeholder="Kein Projekt" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">Kein Projekt</SelectItem>
                        {projects.map(p => <SelectItem key={p.id} value={p.id}>{p.title}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  )}

                  {manualTaskType !== PAUSE_TYPE && (
                    <button
                      onClick={() => setManualBillable(v => !v)}
                      className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm transition-colors ${manualBillable ? "border-primary bg-primary/10 text-primary" : "border-border text-muted-foreground"}`}
                    >
                      <CheckIcon className="h-3.5 w-3.5" />
                      Abrechenbar
                    </button>
                  )}

                  <Button
                    onClick={handleManualSave}
                    disabled={manualSaving || !manualStart || !manualEnd || manualEnd <= manualStart}
                    size="sm"
                    className="ml-auto"
                  >
                    {manualSaving ? "Speichern…" : "Erfassen"}
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Einträge nach Tag */}
      {loading ? (
        <div className="flex items-center justify-center py-16 text-sm text-muted-foreground">Laden…</div>
      ) : grouped.length === 0 ? (
        <div className="flex flex-col items-center gap-3 py-16 text-muted-foreground">
          <ClockIcon className="h-10 w-10 opacity-30" />
          <p className="text-sm">Noch keine Einträge.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {grouped.map(({ date, entries: dayEntries }) => (
            <DayGroup
              key={date}
              date={date}
              entries={dayEntries}
              projects={projects}
              onDelete={id => setDeleteId(id)}
              onRefresh={load}
            />
          ))}
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

// ─── Datumsgruppierung ────────────────────────────────────────

function groupByDate(entries: TimeEntry[]): { date: string; entries: TimeEntry[] }[] {
  const map = new Map<string, TimeEntry[]>()
  for (const e of entries) {
    const date = e.start_time.slice(0, 10)
    if (!map.has(date)) map.set(date, [])
    map.get(date)!.push(e)
  }
  return Array.from(map.entries())
    .sort(([a], [b]) => b.localeCompare(a))
    .map(([date, entries]) => ({ date, entries }))
}

// ─── Tagesgruppe mit ArbZG-Check ─────────────────────────────

function DayGroup({ date, entries, projects, onDelete, onRefresh }: {
  date: string
  entries: TimeEntry[]
  projects: Project[]
  onDelete: (id: string) => void
  onRefresh: () => void
}) {
  const compliance = checkCompliance(entries)
  const totalMin = entries.reduce((s, e) => s + (e.duration_minutes ?? 0), 0)

  const sortedEntries = [...entries].sort(
    (a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
  )

  return (
    <div>
      {/* Tages-Header */}
      <div className="mb-2 flex items-center gap-3">
        <span className="text-sm font-medium">{fmtDayLabel(date)}</span>

        {/* ArbZG-Indikator */}
        {compliance.status === "ok" && entries.filter(e => e.end_time).length > 0 && (
          <span className="flex items-center gap-1 rounded-full bg-green-100 px-2 py-0.5 text-xs text-green-700 dark:bg-green-900/40 dark:text-green-300">
            <CheckIcon className="h-3 w-3" /> Konform
          </span>
        )}
        {compliance.status === "warn" && (
          <span title={compliance.issues.join("\n")} className="flex items-center gap-1 rounded-full bg-yellow-100 px-2 py-0.5 text-xs text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300 cursor-help">
            <AlertTriangleIcon className="h-3 w-3" /> Hinweis
          </span>
        )}
        {compliance.status === "violation" && (
          <span title={compliance.issues.join("\n")} className="flex items-center gap-1 rounded-full bg-red-100 px-2 py-0.5 text-xs text-red-700 dark:bg-red-900/40 dark:text-red-300 cursor-help">
            <AlertCircleIcon className="h-3 w-3" /> Verstoß
          </span>
        )}

        <span className="ml-auto text-sm text-muted-foreground tabular-nums">
          {fmtMinutes(compliance.netMinutes)}
          {compliance.pauseMinutes > 0 && (
            <span className="ml-1 text-xs text-muted-foreground/70">+ {fmtMinutes(compliance.pauseMinutes)} Pause</span>
          )}
        </span>
      </div>

      {/* Compliance-Hinweise */}
      {compliance.issues.length > 0 && (
        <div className={`mb-2 rounded-lg px-3 py-2 text-xs space-y-0.5 ${
          compliance.status === "violation"
            ? "bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-400"
            : "bg-yellow-50 text-yellow-700 dark:bg-yellow-950/40 dark:text-yellow-400"
        }`}>
          {compliance.issues.map((issue, i) => (
            <p key={i}>⚠ {issue}</p>
          ))}
        </div>
      )}

      {/* Einträge */}
      <div className="divide-y rounded-lg border overflow-hidden">
        {sortedEntries.map(entry => (
          <EntryRow
            key={entry.id}
            entry={entry}
            projects={projects}
            onDelete={onDelete}
            onRefresh={onRefresh}
          />
        ))}
      </div>
    </div>
  )
}

// ─── Einzelne Zeile mit Edit-Modus ────────────────────────────

function toLocalDatetimeValue(iso: string) {
  // "2026-07-01T08:30:00Z" → "2026-07-01T08:30" (für datetime-local Input)
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, "0")
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function EntryRow({ entry, projects, onDelete, onRefresh }: {
  entry: TimeEntry
  projects: Project[]
  onDelete: (id: string) => void
  onRefresh: () => void
}) {
  const isRunning = !entry.end_time
  const isPause = entry.task_type === PAUSE_TYPE

  const [editing, setEditing] = useState(false)
  const [saving, setSaving] = useState(false)

  // Edit-Felder
  const [editNote, setEditNote] = useState("")
  const [editTaskType, setEditTaskType] = useState("")
  const [editProjectId, setEditProjectId] = useState("none")
  const [editBillable, setEditBillable] = useState(true)
  const [editStart, setEditStart] = useState("")
  const [editEnd, setEditEnd] = useState("")

  function startEdit() {
    setEditNote(entry.note ?? "")
    setEditTaskType(entry.task_type ?? "Sonstiges")
    setEditProjectId(entry.project_id ?? "none")
    setEditBillable(entry.billable)
    setEditStart(toLocalDatetimeValue(entry.start_time))
    setEditEnd(entry.end_time ? toLocalDatetimeValue(entry.end_time) : "")
    setEditing(true)
  }

  async function saveEdit() {
    setSaving(true)
    try {
      await timeTrackingService.update(entry.id, {
        note: editNote || null,
        task_type: editTaskType || null,
        project_id: editTaskType === PAUSE_TYPE ? null : (editProjectId === "none" ? null : editProjectId),
        billable: editTaskType === PAUSE_TYPE ? false : editBillable,
        start_time: editStart ? new Date(editStart).toISOString() : undefined,
        end_time: editEnd ? new Date(editEnd).toISOString() : null,
      })
      setEditing(false)
      onRefresh()
    } finally {
      setSaving(false)
    }
  }

  const projectTitle = entry.project_id
    ? projects.find(p => p.id === entry.project_id)?.title ?? null
    : null

  // ── Edit-Modus ──
  if (editing) {
    return (
      <div className="bg-card px-4 py-3 space-y-3">
        {/* Zeitfelder */}
        <div className="flex flex-wrap gap-2 items-center">
          <div className="grid gap-1">
            <label className="text-xs text-muted-foreground">Start</label>
            <input
              type="datetime-local"
              value={editStart}
              onChange={e => setEditStart(e.target.value)}
              className="h-8 rounded-lg border border-input bg-transparent px-2 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/30"
            />
          </div>
          <div className="grid gap-1">
            <label className="text-xs text-muted-foreground">Ende</label>
            <input
              type="datetime-local"
              value={editEnd}
              onChange={e => setEditEnd(e.target.value)}
              className="h-8 rounded-lg border border-input bg-transparent px-2 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/30"
            />
          </div>
        </div>

        {/* Notiz */}
        <Input
          value={editNote}
          onChange={e => setEditNote(e.target.value)}
          placeholder="Notiz"
          className="h-8 text-sm"
        />

        {/* Tasktyp + Projekt + Billable */}
        <div className="flex flex-wrap gap-2">
          <Select value={editTaskType} onValueChange={v => {
            if (!v) return
            setEditTaskType(v)
            if (v === PAUSE_TYPE) setEditBillable(false)
          }}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {TASK_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
            </SelectContent>
          </Select>

          {editTaskType !== PAUSE_TYPE && (
            <Select value={editProjectId} onValueChange={v => v && setEditProjectId(v)}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Kein Projekt" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">Kein Projekt</SelectItem>
                {projects.map(p => <SelectItem key={p.id} value={p.id}>{p.title}</SelectItem>)}
              </SelectContent>
            </Select>
          )}

          {editTaskType !== PAUSE_TYPE && (
            <button
              onClick={() => setEditBillable(v => !v)}
              className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm transition-colors ${editBillable ? "border-primary bg-primary/10 text-primary" : "border-border text-muted-foreground"}`}
            >
              <CheckIcon className="h-3.5 w-3.5" />
              Abrechenbar
            </button>
          )}
        </div>

        {/* Aktionen */}
        <div className="flex gap-2">
          <Button size="sm" onClick={saveEdit} disabled={saving}>
            {saving ? "Speichern…" : "Speichern"}
          </Button>
          <Button size="sm" variant="outline" onClick={() => setEditing(false)} disabled={saving}>
            Abbrechen
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => { setEditing(false); onDelete(entry.id) }}
            className="ml-auto text-destructive hover:bg-destructive/10 hover:text-destructive"
            disabled={saving}
          >
            <Trash2Icon className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>
    )
  }

  // ── Anzeigemodus ──
  return (
    <div
      onClick={startEdit}
      className={`group flex cursor-pointer items-center gap-3 px-4 py-3 transition-colors hover:bg-muted/40 ${
        isRunning ? "bg-primary/5" : isPause ? "bg-muted/30" : "bg-card"
      }`}
    >
      {isRunning && <span className="h-2 w-2 shrink-0 rounded-full bg-primary animate-pulse" />}
      {isPause && !isRunning && <span className="h-2 w-2 shrink-0 rounded-full bg-muted-foreground/40" />}

      {/* Zeitspanne */}
      <span className="shrink-0 font-mono text-xs text-muted-foreground tabular-nums w-24">
        {fmtTime(entry.start_time)}
        {entry.end_time ? ` – ${fmtTime(entry.end_time)}` : " – läuft"}
      </span>

      {/* Inhalt */}
      <div className="flex-1 min-w-0">
        <p className={`truncate text-sm ${isPause ? "text-muted-foreground italic" : "font-medium"}`}>
          {entry.note || entry.task_type || "–"}
        </p>
        {projectTitle && (
          <p className="text-xs text-muted-foreground truncate">{projectTitle}</p>
        )}
      </div>

      {/* Badges + Dauer */}
      <div className="flex items-center gap-2 shrink-0">
        {entry.billable && !isPause && (
          <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs text-primary">€</span>
        )}
        {entry.is_approved && (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs text-green-700 dark:bg-green-900 dark:text-green-200">
            <CheckIcon className="inline h-3 w-3" />
          </span>
        )}
        <span className={`text-sm tabular-nums ${isPause ? "text-muted-foreground" : "font-medium"}`}>
          {isRunning ? <ElapsedTimer startTime={entry.start_time} /> : fmtMinutes(entry.duration_minutes)}
        </span>
      </div>
    </div>
  )
}
