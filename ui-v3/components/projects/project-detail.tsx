"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { usePageTitle } from "@/lib/page-title-context"
import { projectService } from "@/lib/projects/service"
import { crmService } from "@/lib/crm/service"
import { timeTrackingService } from "@/lib/time-tracking/service"
import type { Project } from "@/lib/projects/types"
import type { Customer } from "@/lib/crm/types"
import type { TimeEntry } from "@/lib/time-tracking/types"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger } from "@/components/ui/select"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { ArrowLeftIcon, PencilIcon, Trash2Icon, CalendarIcon, UserIcon, ClockIcon } from "lucide-react"

const STATUS_LABELS: Record<string, string> = {
  planning: "Planung",
  active: "Aktiv",
  on_hold: "Pausiert",
  completed: "Abgeschlossen",
  cancelled: "Abgebrochen",
}

const STATUS_COLOR: Record<string, string> = {
  planning: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  active: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  on_hold: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  completed: "bg-muted text-muted-foreground",
  cancelled: "bg-muted text-muted-foreground",
}

function fmtDate(d: string | null | undefined) {
  if (!d) return "–"
  return new Date(d).toLocaleDateString("de-DE")
}

function fmtMin(min: number) {
  const h = Math.floor(min / 60)
  const m = min % 60
  return h > 0 ? `${h}h${m > 0 ? ` ${m}min` : ""}` : `${m}min`
}

export function ProjectDetail({ id }: { id: string }) {
  const router = useRouter()
  const [project, setProject] = useState<Project | null>(null)
  const [customer, setCustomer] = useState<Customer | null>(null)
  const [timeEntries, setTimeEntries] = useState<TimeEntry[]>([])
  const [loadingTime, setLoadingTime] = useState(true)
  const [loading, setLoading] = useState(true)
  const [showDelete, setShowDelete] = useState(false)
  const [updatingStatus, setUpdatingStatus] = useState(false)
  usePageTitle(project?.title)

  useEffect(() => {
    projectService.get(id)
      .then(p => {
        setProject(p)
        if (p.customer_id) {
          crmService.getCustomer(p.customer_id).then(setCustomer).catch(() => {})
        }
      })
      .finally(() => setLoading(false))

    timeTrackingService.list({ project_id: id, limit: 200 })
      .then(data => setTimeEntries(Array.isArray(data) ? data : []))
      .catch(() => {})
      .finally(() => setLoadingTime(false))
  }, [id])

  async function handleStatusChange(status: string) {
    if (!project) return
    setUpdatingStatus(true)
    try {
      const updated = await projectService.update(id, { status })
      setProject(updated)
    } finally {
      setUpdatingStatus(false)
    }
  }

  async function handleDelete() {
    await projectService.delete(id)
    router.push("/projects")
  }

  const totalMin = timeEntries.reduce((s, e) => s + (e.duration_minutes ?? 0), 0)
  const billableMin = timeEntries.filter(e => e.billable).reduce((s, e) => s + (e.duration_minutes ?? 0), 0)
  const completedEntries = timeEntries.filter(e => e.end_time).slice(0, 8)

  if (loading) {
    return <div className="flex items-center justify-center py-24 text-sm text-muted-foreground">Laden…</div>
  }
  if (!project) {
    return <div className="flex items-center justify-center py-24 text-sm text-destructive">Projekt nicht gefunden.</div>
  }

  return (
    <div className="space-y-6 px-8 py-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.push("/projects")}>
          <ArrowLeftIcon className="h-4 w-4" />
        </Button>
        <div className="flex-1 min-w-0">
          <h1 className="truncate text-xl font-semibold">{project.title}</h1>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <Select value={project.status} onValueChange={v => v && handleStatusChange(v)} disabled={updatingStatus}>
            <SelectTrigger className="w-40">
              <span data-slot="select-value" className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLOR[project.status] ?? "bg-muted text-muted-foreground"}`}>
                {STATUS_LABELS[project.status] ?? project.status}
              </span>
            </SelectTrigger>
            <SelectContent>
              {Object.entries(STATUS_LABELS).map(([v, l]) => (
                <SelectItem key={v} value={v}>{l}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button variant="outline" size="icon" onClick={() => router.push(`/projects/${id}/edit`)}>
            <PencilIcon className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="text-destructive hover:text-destructive hover:bg-destructive/10"
            onClick={() => setShowDelete(true)}
          >
            <Trash2Icon className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Meta */}
      <div className="grid grid-cols-2 gap-4 rounded-lg border bg-card p-4 sm:grid-cols-3">
        <div className="flex items-start gap-2">
          <CalendarIcon className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
          <div>
            <p className="text-xs text-muted-foreground">Zeitraum</p>
            <p className="mt-0.5 text-sm font-medium">
              {fmtDate(project.start_date)} → {fmtDate(project.end_date)}
            </p>
          </div>
        </div>
        <div className="flex items-start gap-2">
          <CalendarIcon className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
          <div>
            <p className="text-xs text-muted-foreground">Erstellt am</p>
            <p className="mt-0.5 text-sm font-medium">{fmtDate(project.created_at)}</p>
          </div>
        </div>
        {project.customer_id && (
          <div className="flex items-start gap-2">
            <UserIcon className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
            <div>
              <p className="text-xs text-muted-foreground">Kunde</p>
              <button
                onClick={() => router.push(`/crm/customers/${project.customer_id}`)}
                className="mt-0.5 text-sm font-medium text-primary hover:underline"
              >
                {customer ? customer.name : "Laden…"}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Description */}
      {project.description && (
        <div>
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">Beschreibung</h2>
          <p className="rounded-lg border bg-card p-4 text-sm whitespace-pre-wrap">{project.description}</p>
        </div>
      )}

      {/* Time tracking */}
      <div className="rounded-lg border bg-card">
        <div className="flex items-center gap-2 border-b px-4 py-3">
          <ClockIcon className="h-4 w-4 text-muted-foreground" />
          <h2 className="text-sm font-medium">Zeiterfassung</h2>
          {!loadingTime && totalMin > 0 && (
            <span className="ml-auto text-sm font-semibold">{fmtMin(totalMin)} gesamt</span>
          )}
        </div>

        {loadingTime ? (
          <div className="py-8 text-center text-sm text-muted-foreground">Laden…</div>
        ) : totalMin === 0 ? (
          <div className="py-8 text-center text-sm text-muted-foreground">
            Noch keine Zeiteinträge für dieses Projekt.
          </div>
        ) : (
          <>
            {/* Summary */}
            <div className="grid grid-cols-3 divide-x border-b">
              {[
                { label: "Gesamt", value: fmtMin(totalMin) },
                { label: "Abrechenbar", value: fmtMin(billableMin), highlight: true },
                { label: "Einträge", value: String(timeEntries.length) },
              ].map(s => (
                <div key={s.label} className="px-4 py-3">
                  <p className="text-xs text-muted-foreground">{s.label}</p>
                  <p className={`mt-0.5 text-lg font-semibold ${s.highlight ? "text-primary" : ""}`}>{s.value}</p>
                </div>
              ))}
            </div>

            {/* Entry list */}
            <div className="divide-y">
              {completedEntries.map(e => (
                <div key={e.id} className="flex items-center gap-3 px-4 py-2.5">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm truncate">{e.note || e.task_type || "–"}</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(e.start_time).toLocaleDateString("de-DE")}
                      {e.task_type ? ` · ${e.task_type}` : ""}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0 text-xs text-muted-foreground">
                    {e.billable && <span className="rounded-full bg-primary/10 px-1.5 py-0.5 text-primary">€</span>}
                    {e.is_approved && <span className="text-green-600">✓</span>}
                    <span className="font-medium text-foreground tabular-nums">
                      {e.duration_minutes ? fmtMin(e.duration_minutes) : "läuft"}
                    </span>
                  </div>
                </div>
              ))}
              {timeEntries.length > 8 && (
                <div className="px-4 py-2 text-xs text-muted-foreground">
                  + {timeEntries.length - 8} weitere Einträge
                </div>
              )}
            </div>
          </>
        )}
      </div>

      <AlertDialog open={showDelete} onOpenChange={setShowDelete}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Projekt löschen?</AlertDialogTitle>
            <AlertDialogDescription>
              „{project.title}" wird unwiderruflich gelöscht.
            </AlertDialogDescription>
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
