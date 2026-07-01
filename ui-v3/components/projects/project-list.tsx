"use client"

import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { projectService } from "@/lib/projects/service"
import type { Project } from "@/lib/projects/types"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { Input } from "@/components/ui/input"
import { PlusIcon, Trash2Icon, FolderOpenIcon, CalendarIcon, LayoutGridIcon, GanttChartIcon, SearchIcon } from "lucide-react"
import { ProjectTimeline } from "./project-timeline"
import { useAuth } from "@/components/providers/auth-provider"

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
  cancelled: "bg-muted text-muted-foreground line-through",
}

function fmtDate(d: string | null | undefined) {
  if (!d) return null
  return new Date(d).toLocaleDateString("de-DE")
}

export function ProjectList() {
  const router = useRouter()
  const { hasPermission } = useAuth()
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState("all")
  const [deleteId, setDeleteId] = useState<string | null>(null)
  const [deleteTitle, setDeleteTitle] = useState("")
  const [view, setView] = useState<"grid" | "timeline">("grid")
  const [search, setSearch] = useState("")

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await projectService.list()
      setProjects(data)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const q = search.toLowerCase()
  const filtered = projects
    .filter(p => statusFilter === "all" || p.status === statusFilter)
    .filter(p => !q || p.title.toLowerCase().includes(q) || (p.description ?? "").toLowerCase().includes(q))

  async function handleDelete() {
    if (!deleteId) return
    await projectService.delete(deleteId)
    setDeleteId(null)
    load()
  }

  const counts: Record<string, number> = {}
  for (const p of projects) {
    counts[p.status] = (counts[p.status] ?? 0) + 1
  }

  return (
    <div className="space-y-6 px-8 py-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Projekte</h1>
          <p className="text-sm text-muted-foreground">{projects.length} Projekte gesamt</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex gap-0.5 rounded-lg border bg-muted p-1">
            <button
              onClick={() => setView("grid")}
              className={`rounded p-1.5 transition-colors ${view === "grid" ? "bg-card shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"}`}
              title="Kacheln"
            >
              <LayoutGridIcon className="h-4 w-4" />
            </button>
            <button
              onClick={() => setView("timeline")}
              className={`rounded p-1.5 transition-colors ${view === "timeline" ? "bg-card shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"}`}
              title="Timeline"
            >
              <GanttChartIcon className="h-4 w-4" />
            </button>
          </div>
          {hasPermission("backoffice.projects.write") && (
            <Button onClick={() => router.push("/projects/new")}>
              <PlusIcon className="mr-2 h-4 w-4" />
              Neu
            </Button>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          { key: "active", label: "Aktiv" },
          { key: "planning", label: "Planung" },
          { key: "on_hold", label: "Pausiert" },
          { key: "completed", label: "Abgeschlossen" },
        ].map(s => (
          <button
            key={s.key}
            onClick={() => setStatusFilter(v => v === s.key ? "all" : s.key)}
            className={`rounded-lg border p-4 text-left transition-colors hover:bg-muted/50 ${statusFilter === s.key ? "border-primary bg-primary/5" : "bg-card"}`}
          >
            <p className="text-xs text-muted-foreground">{s.label}</p>
            <p className="mt-1 text-2xl font-semibold">{counts[s.key] ?? 0}</p>
          </button>
        ))}
      </div>

      {/* Filter */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-xs">
          <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
          <Input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Projekt suchen…"
            className="pl-9"
          />
        </div>
        <Select value={statusFilter} onValueChange={v => v && setStatusFilter(v)}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle Status</SelectItem>
            {Object.entries(STATUS_LABELS).map(([v, l]) => (
              <SelectItem key={v} value={v}>{l}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        {search && (
          <span className="text-xs text-muted-foreground">
            {filtered.length} von {projects.length}
          </span>
        )}
      </div>

      {/* List */}
      {loading ? (
        <div className="flex items-center justify-center py-24 text-sm text-muted-foreground">Laden…</div>
      ) : view === "timeline" ? (
        <ProjectTimeline projects={filtered} />
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-3 py-24 text-muted-foreground">
          <FolderOpenIcon className="h-10 w-10 opacity-30" />
          <span className="text-sm">Keine Projekte gefunden.</span>
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map(project => (
            <div
              key={project.id}
              onClick={() => router.push(`/projects/${project.id}`)}
              className="group relative cursor-pointer rounded-xl border bg-card p-5 transition-shadow hover:shadow-md"
            >
              {/* Delete button */}
              {hasPermission("backoffice.projects.delete") && (
                <button
                  onClick={e => {
                    e.stopPropagation()
                    setDeleteId(project.id)
                    setDeleteTitle(project.title)
                  }}
                  className="absolute right-3 top-3 rounded p-1 opacity-0 transition-opacity group-hover:opacity-100 hover:bg-destructive/10 hover:text-destructive text-muted-foreground"
                >
                  <Trash2Icon className="h-3.5 w-3.5" />
                </button>
              )}

              {/* Status badge */}
              <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLOR[project.status] ?? "bg-muted text-muted-foreground"}`}>
                {STATUS_LABELS[project.status] ?? project.status}
              </span>

              <h3 className="mt-3 font-medium leading-snug">{project.title}</h3>

              {project.description && (
                <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">{project.description}</p>
              )}

              {(project.start_date || project.end_date) && (
                <div className="mt-3 flex items-center gap-1.5 text-xs text-muted-foreground">
                  <CalendarIcon className="h-3.5 w-3.5" />
                  {fmtDate(project.start_date) ?? "–"}
                  {" → "}
                  {fmtDate(project.end_date) ?? "offen"}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <AlertDialog open={!!deleteId} onOpenChange={open => !open && setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Projekt löschen?</AlertDialogTitle>
            <AlertDialogDescription>
              „{deleteTitle}" wird unwiderruflich gelöscht.
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
