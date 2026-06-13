"use client"

import { useEffect, useState } from "react"
import { hrService } from "@/lib/hr/service"
import type { JobPosting, Application, ApplicationStatus, JobStatus } from "@/lib/hr/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { PlusIcon, Trash2Icon, ChevronDownIcon, ChevronUpIcon } from "lucide-react"

const JOB_STATUS_LABELS: Record<JobStatus, string> = {
  draft: "Entwurf", open: "Offen", closed: "Geschlossen", archived: "Archiviert",
}
const JOB_STATUS_COLOR: Record<JobStatus, string> = {
  draft: "bg-muted text-muted-foreground",
  open: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  closed: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  archived: "bg-muted text-muted-foreground",
}
const APP_STATUS_LABELS: Record<ApplicationStatus, string> = {
  new: "Neu", screening: "Sichtung", interview: "Interview",
  offer: "Angebot", hired: "Eingestellt", rejected: "Abgelehnt",
}
const APP_STATUS_COLOR: Record<ApplicationStatus, string> = {
  new: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  screening: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  interview: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  offer: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  hired: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
}

function fmtDate(d: string | null) {
  if (!d) return "–"
  return new Date(d).toLocaleDateString("de-DE")
}

function NewJobForm({ onSave, onClose }: { onSave: () => void; onClose: () => void }) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [requirements, setRequirements] = useState("")
  const [location, setLocation] = useState("")
  const [remote, setRemote] = useState(false)
  const [employmentType, setEmploymentType] = useState("fulltime")
  const [deadline, setDeadline] = useState("")
  const [status, setStatus] = useState<JobStatus>("draft")
  const [saving, setSaving] = useState(false)

  async function handleSave() {
    if (!title.trim()) return
    setSaving(true)
    try {
      await hrService.createJob({
        title: title.trim(),
        description: description.trim() || null,
        requirements: requirements.trim() || null,
        location: location.trim() || null,
        remote,
        employment_type: employmentType,
        deadline: deadline || null,
        status,
      })
      onSave()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-1.5">
        <Label>Stellentitel *</Label>
        <Input value={title} onChange={e => setTitle(e.target.value)} placeholder="Frontend Developer (m/w/d)" />
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="grid gap-1.5">
          <Label>Anstellungsart</Label>
          <Select value={employmentType} onValueChange={v => v && setEmploymentType(v)}>
            <SelectTrigger>
              <span data-slot="select-value">
                {([["fulltime","Vollzeit"],["parttime","Teilzeit"],["freelancer","Freelancer"],["intern","Praktikum"]] as [string,string][]).find(([v]) => v === employmentType)?.[1] ?? employmentType}
              </span>
            </SelectTrigger>
            <SelectContent>
              {[["fulltime","Vollzeit"],["parttime","Teilzeit"],["freelancer","Freelancer"],["intern","Praktikum"]].map(([v,l]) =>
                <SelectItem key={v} value={v}>{l}</SelectItem>
              )}
            </SelectContent>
          </Select>
        </div>
        <div className="grid gap-1.5">
          <Label>Status</Label>
          <Select value={status} onValueChange={v => v && setStatus(v as JobStatus)}>
            <SelectTrigger>
              <span data-slot="select-value">
                {JOB_STATUS_LABELS[status] ?? status}
              </span>
            </SelectTrigger>
            <SelectContent>
              {Object.entries(JOB_STATUS_LABELS).map(([v, l]) => <SelectItem key={v} value={v}>{l}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
        <div className="grid gap-1.5">
          <Label>Ort</Label>
          <Input value={location} onChange={e => setLocation(e.target.value)} placeholder="Koblenz / Remote" />
        </div>
        <div className="grid gap-1.5">
          <Label>Bewerbungsschluss</Label>
          <Input type="date" value={deadline} onChange={e => setDeadline(e.target.value)} />
        </div>
      </div>
      <div className="flex items-center gap-2">
        <input type="checkbox" id="remote" checked={remote} onChange={e => setRemote(e.target.checked)} className="h-4 w-4" />
        <label htmlFor="remote" className="text-sm">Remote möglich</label>
      </div>
      <div className="grid gap-1.5">
        <Label>Beschreibung</Label>
        <Textarea value={description} onChange={e => setDescription(e.target.value)} rows={4} placeholder="Stellenbeschreibung…" />
      </div>
      <div className="grid gap-1.5">
        <Label>Anforderungen</Label>
        <Textarea value={requirements} onChange={e => setRequirements(e.target.value)} rows={3} placeholder="Anforderungen und Skills…" />
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="outline" onClick={onClose}>Abbrechen</Button>
        <Button onClick={handleSave} disabled={saving || !title.trim()}>
          {saving ? "Anlegen…" : "Stelle anlegen"}
        </Button>
      </div>
    </div>
  )
}

function ApplicationRow({ app, onStatusChange }: { app: Application; onStatusChange: () => void }) {
  async function update(status: string) {
    await hrService.updateApplication(app.id, { status })
    onStatusChange()
  }

  return (
    <tr className="border-b last:border-0 hover:bg-muted/30 transition-colors">
      <td className="px-4 py-3">
        <p className="font-medium">{app.first_name} {app.last_name}</p>
        <p className="text-xs text-muted-foreground">{app.email}</p>
      </td>
      <td className="px-4 py-3 text-muted-foreground">{fmtDate(app.created_at)}</td>
      <td className="px-4 py-3">
        {app.rating != null && (
          <span className="text-sm font-medium">{app.rating}/5</span>
        )}
      </td>
      <td className="px-4 py-3">
        <Select value={app.status} onValueChange={v => v && update(v)}>
          <SelectTrigger className="h-7 w-36 text-xs px-2">
            <span data-slot="select-value" className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${APP_STATUS_COLOR[app.status] ?? "bg-muted"}`}>
              {APP_STATUS_LABELS[app.status] ?? app.status}
            </span>
          </SelectTrigger>
          <SelectContent>
            {Object.entries(APP_STATUS_LABELS).map(([v, l]) => (
              <SelectItem key={v} value={v}>
                <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${APP_STATUS_COLOR[v as ApplicationStatus] ?? "bg-muted"}`}>{l}</span>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </td>
    </tr>
  )
}

function JobCard({ job, onRefresh }: { job: JobPosting; onRefresh: () => void }) {
  const [expanded, setExpanded] = useState(false)
  const [applications, setApplications] = useState<Application[]>([])
  const [loadingApps, setLoadingApps] = useState(false)
  const [deleteId, setDeleteId] = useState<string | null>(null)

  async function loadApplications() {
    if (applications.length > 0) return
    setLoadingApps(true)
    try {
      const data = await hrService.listApplications({ job_posting_id: job.id })
      setApplications(data)
    } finally {
      setLoadingApps(false)
    }
  }

  function toggle() {
    setExpanded(v => !v)
    if (!expanded) loadApplications()
  }

  async function handleDelete() {
    await hrService.deleteJob(job.id)
    setDeleteId(null)
    onRefresh()
  }

  async function handleStatusChange(status: string) {
    await hrService.updateJob(job.id, { status: status as JobStatus })
    onRefresh()
  }

  return (
    <div className="rounded-lg border bg-card">
      <div className="flex items-center justify-between p-4">
        <div className="flex items-center gap-3 min-w-0">
          <button onClick={toggle} className="text-muted-foreground hover:text-foreground">
            {expanded ? <ChevronUpIcon className="h-4 w-4" /> : <ChevronDownIcon className="h-4 w-4" />}
          </button>
          <div className="min-w-0">
            <p className="font-medium truncate">{job.title}</p>
            <p className="text-xs text-muted-foreground">
              {job.location ?? "–"}
              {job.remote && " · Remote"}
              {job.deadline && ` · Bis ${fmtDate(job.deadline)}`}
              {` · ${job.application_count} Bewerbung${job.application_count === 1 ? "" : "en"}`}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <Select value={job.status} onValueChange={v => v && handleStatusChange(v)}>
            <SelectTrigger className="h-7 w-36 text-xs px-2">
              <span data-slot="select-value" className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${JOB_STATUS_COLOR[job.status] ?? "bg-muted"}`}>
                {JOB_STATUS_LABELS[job.status] ?? job.status}
              </span>
            </SelectTrigger>
            <SelectContent>
              {Object.entries(JOB_STATUS_LABELS).map(([v, l]) => (
                <SelectItem key={v} value={v}>
                  <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${JOB_STATUS_COLOR[v as JobStatus] ?? "bg-muted"}`}>{l}</span>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive hover:bg-destructive/10" onClick={() => setDeleteId(job.id)}>
            <Trash2Icon className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>

      {expanded && (
        <div className="border-t px-4 py-3">
          {loadingApps ? (
            <p className="text-sm text-muted-foreground py-4 text-center">Laden…</p>
          ) : applications.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4 text-center">Keine Bewerbungen.</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="pb-2 text-left font-medium text-muted-foreground">Bewerber</th>
                  <th className="pb-2 text-left font-medium text-muted-foreground">Eingegangen</th>
                  <th className="pb-2 text-left font-medium text-muted-foreground">Bewertung</th>
                  <th className="pb-2 text-left font-medium text-muted-foreground">Status</th>
                </tr>
              </thead>
              <tbody>
                {applications.map(app => (
                  <ApplicationRow
                    key={app.id}
                    app={app}
                    onStatusChange={() => {
                      setApplications(prev => prev.map(a => a.id === app.id ? { ...a, status: app.status } : a))
                      hrService.listApplications({ job_posting_id: job.id }).then(setApplications)
                    }}
                  />
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      <AlertDialog open={!!deleteId} onOpenChange={open => !open && setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Stelle löschen?</AlertDialogTitle>
            <AlertDialogDescription>„{job.title}" wird unwiderruflich gelöscht.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">Löschen</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

export function RecruitingTab() {
  const [jobs, setJobs] = useState<JobPosting[]>([])
  const [loading, setLoading] = useState(true)
  const [filterStatus, setFilterStatus] = useState("all")
  const [showForm, setShowForm] = useState(false)

  async function load() {
    setLoading(true)
    try {
      const params: Record<string, string> = {}
      if (filterStatus !== "all") params.status = filterStatus
      const data = await hrService.listJobs(params as Parameters<typeof hrService.listJobs>[0])
      setJobs(data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [filterStatus])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <Select value={filterStatus} onValueChange={v => v && setFilterStatus(v)}>
          <SelectTrigger className="w-44"><SelectValue placeholder="Status" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle Status</SelectItem>
            {Object.entries(JOB_STATUS_LABELS).map(([v, l]) => <SelectItem key={v} value={v}>{l}</SelectItem>)}
          </SelectContent>
        </Select>
        <Button size="sm" onClick={() => setShowForm(true)}>
          <PlusIcon className="mr-2 h-4 w-4" />
          Stelle anlegen
        </Button>
      </div>

      {loading ? (
        <div className="py-12 text-center text-sm text-muted-foreground">Laden…</div>
      ) : jobs.length === 0 ? (
        <div className="rounded-lg border border-dashed p-12 text-center text-sm text-muted-foreground">
          Keine Stellenausschreibungen gefunden.
        </div>
      ) : (
        <div className="space-y-2">
          {jobs.map(job => (
            <JobCard key={job.id} job={job} onRefresh={load} />
          ))}
        </div>
      )}

      <Dialog open={showForm} onOpenChange={open => !open && setShowForm(false)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Neue Stelle</DialogTitle>
          </DialogHeader>
          <NewJobForm
            onSave={() => { setShowForm(false); load() }}
            onClose={() => setShowForm(false)}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}
