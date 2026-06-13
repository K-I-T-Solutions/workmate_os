"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { hrService } from "@/lib/hr/service"
import { adminService } from "@/lib/admin/service"
import type { Employee, LeaveRequest, EmployeeUpdate, EmployeeStatus, EmploymentType, LeaveType, LeaveStatus } from "@/lib/hr/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  AlertDialog, AlertDialogContent, AlertDialogHeader,
  AlertDialogTitle, AlertDialogFooter, AlertDialogCancel,
} from "@/components/ui/alert-dialog"
import { timeTrackingService } from "@/lib/time-tracking/service"
import type { TimeEntry } from "@/lib/time-tracking/types"
import {
  ArrowLeftIcon, CheckIcon, XIcon, MailIcon, PhoneIcon,
  BuildingIcon, CalendarIcon, BadgeIcon, KeyRoundIcon, ClockIcon, FolderOpenIcon,
} from "lucide-react"
import { DocumentsTab } from "@/components/documents/documents-dashboard"

const STATUS_LABELS: Record<EmployeeStatus, string> = {
  active: "Aktiv", inactive: "Inaktiv", on_leave: "Abwesend", terminated: "Ausgeschieden",
}
const STATUS_COLOR: Record<EmployeeStatus, string> = {
  active: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  inactive: "bg-muted text-muted-foreground",
  on_leave: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  terminated: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
}
const EMPLOYMENT_TYPES = [
  { value: "fulltime", label: "Vollzeit" }, { value: "parttime", label: "Teilzeit" },
  { value: "freelancer", label: "Freelancer" }, { value: "intern", label: "Praktikant" },
  { value: "minijob", label: "Minijob" },
]
const GENDER_LABELS: Record<string, string> = {
  male: "Männlich", female: "Weiblich", other: "Divers", prefer_not_to_say: "Keine Angabe",
}
const LEAVE_TYPE_LABELS: Record<LeaveType, string> = {
  vacation: "Urlaub", sick: "Krank", parental: "Elternzeit", other: "Sonstig",
}
const LEAVE_STATUS_LABELS: Record<LeaveStatus, string> = {
  pending: "Ausstehend", approved: "Genehmigt", rejected: "Abgelehnt", cancelled: "Storniert",
}
const LEAVE_STATUS_COLOR: Record<LeaveStatus, string> = {
  pending: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  approved: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  cancelled: "bg-muted text-muted-foreground",
}

function fmtDate(d: string | null) {
  if (!d) return "–"
  return new Date(d).toLocaleDateString("de-DE")
}

function initials(emp: Employee) {
  return `${emp.first_name[0] ?? ""}${emp.last_name[0] ?? ""}`.toUpperCase()
}

function LeaveBalanceCards({ requests, vacationTotal }: { requests: LeaveRequest[]; vacationTotal: number }) {
  const year = new Date().getFullYear()
  const thisYear = requests.filter(r => new Date(r.start_date).getFullYear() === year)
  const vacationUsed = thisYear
    .filter(r => r.leave_type === "vacation" && r.status === "approved")
    .reduce((s, r) => s + r.total_days, 0)
  const sickDays = thisYear
    .filter(r => r.leave_type === "sick")
    .reduce((s, r) => s + r.total_days, 0)
  const pct = Math.min(100, Math.round((vacationUsed / vacationTotal) * 100))

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <div className="rounded-lg border bg-card p-4">
        <div className="mb-2 flex items-center justify-between">
          <span className="text-sm font-medium">Urlaubstage {year}</span>
          <span className="text-sm">
            <span className="font-semibold">{vacationUsed}</span>
            <span className="text-muted-foreground"> / {vacationTotal}</span>
          </span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-muted">
          <div
            className={`h-full rounded-full transition-all ${pct >= 90 ? "bg-red-500" : pct >= 70 ? "bg-amber-500" : "bg-primary"}`}
            style={{ width: `${pct}%` }}
          />
        </div>
        <p className="mt-1.5 text-xs text-muted-foreground">{vacationTotal - vacationUsed} Tage verbleibend</p>
      </div>
      <div className="rounded-lg border bg-card p-4">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Kranktage {year}</span>
          <span className="text-sm font-semibold">{sickDays}</span>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">Tage krank gemeldet</p>
      </div>
    </div>
  )
}

function ÜbersichtTab({ employee }: { employee: Employee }) {
  const rows: { label: string; value: string; icon?: React.ElementType }[] = [
    { label: "E-Mail", value: employee.email, icon: MailIcon },
    { label: "Telefon", value: employee.phone ?? "–", icon: PhoneIcon },
    { label: "Abteilung", value: employee.department?.name ?? "–", icon: BuildingIcon },
    { label: "Rolle", value: employee.role?.name ?? "–", icon: BadgeIcon },
    { label: "Einstellungsdatum", value: fmtDate(employee.hire_date), icon: CalendarIcon },
    { label: "Geburtsdatum", value: fmtDate(employee.birth_date), icon: CalendarIcon },
    { label: "Anstellungsart", value: EMPLOYMENT_TYPES.find(t => t.value === employee.employment_type)?.label ?? "–" },
    { label: "Geschlecht", value: employee.gender ? (GENDER_LABELS[employee.gender] ?? employee.gender) : "–" },
    { label: "Mitarbeiternummer", value: employee.employee_code ?? "–" },
    { label: "Workmate-ID", value: employee.workmate_id ?? "–", icon: KeyRoundIcon },
  ]

  if (employee.termination_date) {
    rows.push({ label: "Austrittsdatum", value: fmtDate(employee.termination_date) })
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-2 sm:grid-cols-2">
        {rows.map(row => (
          <div key={row.label} className="flex items-start gap-3 rounded-lg border bg-card px-4 py-3">
            {row.icon && <row.icon className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />}
            <div className="min-w-0">
              <p className="text-xs text-muted-foreground">{row.label}</p>
              <p className="mt-0.5 text-sm font-medium truncate">{row.value}</p>
            </div>
          </div>
        ))}
      </div>

      {employee.bio && (
        <div className="rounded-lg border bg-card p-4">
          <p className="text-xs text-muted-foreground mb-1">Bio</p>
          <p className="text-sm whitespace-pre-wrap">{employee.bio}</p>
        </div>
      )}
    </div>
  )
}

function UrlaubsantraegeTab({
  requests,
  onApprove,
  onReject,
}: {
  requests: LeaveRequest[]
  onApprove: (id: string) => Promise<void>
  onReject: (id: string, reason: string) => Promise<void>
}) {
  const [rejectTarget, setRejectTarget] = useState<string | null>(null)
  const [rejectReason, setRejectReason] = useState("")
  const [processing, setProcessing] = useState<string | null>(null)

  async function doApprove(id: string) {
    setProcessing(id)
    try { await onApprove(id) } finally { setProcessing(null) }
  }

  async function doReject() {
    if (!rejectTarget) return
    setProcessing(rejectTarget)
    try {
      await onReject(rejectTarget, rejectReason)
      setRejectTarget(null)
      setRejectReason("")
    } finally {
      setProcessing(null)
    }
  }

  return (
    <div className="space-y-4">
      <LeaveBalanceCards requests={requests} vacationTotal={30} />

      {requests.length === 0 ? (
        <div className="rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground">
          Keine Abwesenheitsanträge vorhanden.
        </div>
      ) : (
        <div className="rounded-lg border overflow-hidden">
          {requests.map(req => (
            <div key={req.id} className="flex items-center gap-3 border-b last:border-0 px-4 py-3 hover:bg-muted/20">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{LEAVE_TYPE_LABELS[req.leave_type]}</span>
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${LEAVE_STATUS_COLOR[req.status]}`}>
                    {LEAVE_STATUS_LABELS[req.status]}
                  </span>
                </div>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  {fmtDate(req.start_date)} – {fmtDate(req.end_date)} · {req.total_days} Tag{req.total_days !== 1 ? "e" : ""}
                </p>
                {req.reason && <p className="mt-0.5 text-xs text-muted-foreground truncate max-w-xs">{req.reason}</p>}
              </div>
              {req.status === "pending" && (
                <div className="flex gap-1 shrink-0">
                  <button
                    onClick={() => doApprove(req.id)}
                    disabled={processing === req.id}
                    className="rounded p-1.5 text-green-600 hover:bg-green-50 dark:hover:bg-green-950 disabled:opacity-40"
                  >
                    <CheckIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => setRejectTarget(req.id)}
                    disabled={processing === req.id}
                    className="rounded p-1.5 text-red-600 hover:bg-red-50 dark:hover:bg-red-950 disabled:opacity-40"
                  >
                    <XIcon className="h-4 w-4" />
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <AlertDialog open={!!rejectTarget} onOpenChange={open => !open && setRejectTarget(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Antrag ablehnen</AlertDialogTitle>
          </AlertDialogHeader>
          <div className="py-2">
            <Label className="text-sm">Ablehnungsgrund</Label>
            <Textarea
              value={rejectReason}
              onChange={e => setRejectReason(e.target.value)}
              placeholder="Bitte Grund angeben…"
              className="mt-1.5"
              rows={3}
            />
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <Button variant="destructive" onClick={doReject} disabled={!rejectReason.trim() || !!processing}>
              Ablehnen
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

function BearbeitenTab({
  employee,
  departments,
  roles,
  onSave,
}: {
  employee: Employee
  departments: { id: string; name: string }[]
  roles: { id: string; name: string }[]
  onSave: (data: EmployeeUpdate) => Promise<void>
}) {
  const [form, setForm] = useState<EmployeeUpdate>({
    first_name: employee.first_name,
    last_name: employee.last_name,
    email: employee.email,
    phone: employee.phone ?? "",
    birth_date: employee.birth_date ?? "",
    hire_date: employee.hire_date ?? "",
    employment_type: employee.employment_type ?? "fulltime",
    status: employee.status ?? "active",
    department_id: employee.department_id ?? "",
    role_id: employee.role_id ?? "",
    employee_code: employee.employee_code ?? "",
    workmate_id: employee.workmate_id ?? "",
    bio: employee.bio ?? "",
    photo_url: employee.photo_url ?? "",
    termination_date: employee.termination_date ?? "",
  })
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  function set(key: keyof EmployeeUpdate, value: string | null) {
    setForm(f => ({ ...f, [key]: value || null }))
  }

  async function handleSave() {
    setSaving(true)
    try {
      await onSave(form)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="grid gap-1.5">
          <Label>Vorname *</Label>
          <Input value={form.first_name ?? ""} onChange={e => set("first_name", e.target.value)} />
        </div>
        <div className="grid gap-1.5">
          <Label>Nachname *</Label>
          <Input value={form.last_name ?? ""} onChange={e => set("last_name", e.target.value)} />
        </div>
        <div className="grid gap-1.5 sm:col-span-2">
          <Label>E-Mail *</Label>
          <Input type="email" value={form.email ?? ""} onChange={e => set("email", e.target.value)} />
        </div>
        <div className="grid gap-1.5">
          <Label>Telefon</Label>
          <Input value={form.phone ?? ""} onChange={e => set("phone", e.target.value)} />
        </div>
        <div className="grid gap-1.5">
          <Label>Geburtsdatum</Label>
          <Input type="date" value={form.birth_date ?? ""} onChange={e => set("birth_date", e.target.value)} />
        </div>
        <div className="grid gap-1.5">
          <Label>Anstellungsart</Label>
          <Select value={form.employment_type ?? ""} onValueChange={v => v && set("employment_type", v)}>
            <SelectTrigger>
              <span data-slot="select-value">
                {EMPLOYMENT_TYPES.find(t => t.value === form.employment_type)?.label ?? "–"}
              </span>
            </SelectTrigger>
            <SelectContent>
              {EMPLOYMENT_TYPES.map(t => <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
        <div className="grid gap-1.5">
          <Label>Status</Label>
          <Select value={form.status ?? ""} onValueChange={v => v && set("status", v)}>
            <SelectTrigger>
              <span data-slot="select-value">
                {STATUS_LABELS[form.status as EmployeeStatus] ?? form.status ?? "–"}
              </span>
            </SelectTrigger>
            <SelectContent>
              {Object.entries(STATUS_LABELS).map(([v, l]) => <SelectItem key={v} value={v}>{l}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
        <div className="grid gap-1.5">
          <Label>Einstellungsdatum</Label>
          <Input type="date" value={form.hire_date ?? ""} onChange={e => set("hire_date", e.target.value)} />
        </div>
        <div className="grid gap-1.5">
          <Label>Austrittsdatum</Label>
          <Input type="date" value={form.termination_date ?? ""} onChange={e => set("termination_date", e.target.value)} />
        </div>
        <div className="grid gap-1.5">
          <Label>Abteilung</Label>
          <Select value={form.department_id ?? "none"} onValueChange={v => set("department_id", v === "none" ? null : v)}>
            <SelectTrigger>
              <span data-slot="select-value" className={form.department_id ? "" : "text-muted-foreground"}>
                {form.department_id ? (departments.find(d => d.id === form.department_id)?.name ?? "…") : "Keine"}
              </span>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">Keine</SelectItem>
              {departments.map(d => <SelectItem key={d.id} value={d.id}>{d.name}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
        <div className="grid gap-1.5">
          <Label>Rolle</Label>
          <Select value={form.role_id ?? "none"} onValueChange={v => set("role_id", v === "none" ? null : v)}>
            <SelectTrigger>
              <span data-slot="select-value" className={form.role_id ? "" : "text-muted-foreground"}>
                {form.role_id ? (roles.find(r => r.id === form.role_id)?.name ?? "…") : "Keine"}
              </span>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">Keine</SelectItem>
              {roles.map(r => <SelectItem key={r.id} value={r.id}>{r.name}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
        <div className="grid gap-1.5">
          <Label>Mitarbeiternummer</Label>
          <Input value={form.employee_code ?? ""} onChange={e => set("employee_code", e.target.value)} />
        </div>
        <div className="grid gap-1.5">
          <Label>Workmate-ID</Label>
          <Input value={form.workmate_id ?? ""} onChange={e => set("workmate_id", e.target.value)} />
        </div>
        <div className="grid gap-1.5">
          <Label>Foto-URL</Label>
          <Input value={form.photo_url ?? ""} onChange={e => set("photo_url", e.target.value)} placeholder="https://…" />
        </div>
        <div className="grid gap-1.5 sm:col-span-2">
          <Label>Bio</Label>
          <Textarea
            value={form.bio ?? ""}
            onChange={e => set("bio", e.target.value)}
            placeholder="Kurzbeschreibung des Mitarbeiters…"
            rows={3}
          />
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Button onClick={handleSave} disabled={saving}>
          {saving ? "Speichern…" : "Änderungen speichern"}
        </Button>
        {saved && <span className="text-sm text-green-600 dark:text-green-400">Gespeichert.</span>}
      </div>
    </div>
  )
}

function fmtMin(min: number) {
  const h = Math.floor(min / 60)
  const m = min % 60
  return h > 0 ? `${h}h${m > 0 ? ` ${m}min` : ""}` : `${m}min`
}

function ZeiterfassungTab({ employeeId }: { employeeId: string }) {
  const [entries, setEntries] = useState<TimeEntry[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    timeTrackingService.list({ employee_id: employeeId, limit: 200 })
      .then(data => setEntries(Array.isArray(data) ? data : []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [employeeId])

  const totalMin = entries.reduce((s, e) => s + (e.duration_minutes ?? 0), 0)
  const billableMin = entries.filter(e => e.billable).reduce((s, e) => s + (e.duration_minutes ?? 0), 0)
  const thisMonth = entries.filter(e => {
    const d = new Date(e.start_time)
    const now = new Date()
    return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()
  })
  const thisMonthMin = thisMonth.reduce((s, e) => s + (e.duration_minutes ?? 0), 0)

  if (loading) return <div className="py-12 text-center text-sm text-muted-foreground">Laden…</div>

  if (entries.length === 0) {
    return (
      <div className="rounded-lg border border-dashed p-12 text-center">
        <ClockIcon className="mx-auto h-8 w-8 text-muted-foreground/30 mb-3" />
        <p className="text-sm text-muted-foreground">Keine Zeiteinträge vorhanden.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-lg border bg-card p-4">
          <p className="text-xs text-muted-foreground">Gesamt</p>
          <p className="mt-1 text-2xl font-semibold">{fmtMin(totalMin)}</p>
          <p className="mt-0.5 text-xs text-muted-foreground">{entries.length} Einträge</p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <p className="text-xs text-muted-foreground">Abrechenbar</p>
          <p className="mt-1 text-2xl font-semibold text-primary">{fmtMin(billableMin)}</p>
          <p className="mt-0.5 text-xs text-muted-foreground">
            {totalMin ? `${Math.round(billableMin / totalMin * 100)}%` : "–"}
          </p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <p className="text-xs text-muted-foreground">Dieser Monat</p>
          <p className="mt-1 text-2xl font-semibold">{fmtMin(thisMonthMin)}</p>
          <p className="mt-0.5 text-xs text-muted-foreground">{thisMonth.length} Einträge</p>
        </div>
      </div>
      <div className="rounded-lg border overflow-hidden">
        {entries.slice(0, 20).map(e => (
          <div key={e.id} className="flex items-center gap-3 border-b last:border-0 bg-card px-4 py-2.5">
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
        {entries.length > 20 && (
          <div className="px-4 py-2 text-xs text-muted-foreground bg-muted/30">
            + {entries.length - 20} weitere Einträge
          </div>
        )}
      </div>
    </div>
  )
}

type Tab = "overview" | "leave" | "time" | "documents" | "edit"
const TABS: { id: Tab; label: string }[] = [
  { id: "overview", label: "Übersicht" },
  { id: "leave", label: "Urlaubsanträge" },
  { id: "time", label: "Zeiterfassung" },
  { id: "documents", label: "Dokumente" },
  { id: "edit", label: "Bearbeiten" },
]

export function EmployeeDetail({ id }: { id: string }) {
  const router = useRouter()
  const [employee, setEmployee] = useState<Employee | null>(null)
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([])
  const [departments, setDepartments] = useState<{ id: string; name: string }[]>([])
  const [roles, setRoles] = useState<{ id: string; name: string }[]>([])
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState<Tab>("overview")

  async function load() {
    setLoading(true)
    try {
      const [emp, leaves, depts, rls] = await Promise.all([
        hrService.getEmployee(id),
        hrService.listLeaveRequests({ employee_id: id }),
        adminService.listDepartments(),
        adminService.listRoles(),
      ])
      setEmployee(emp)
      setLeaveRequests(leaves)
      setDepartments(depts)
      setRoles(rls)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [id])

  async function handleApprove(leaveId: string) {
    const updated = await hrService.approveLeave(leaveId)
    setLeaveRequests(prev => prev.map(r => r.id === updated.id ? updated : r))
  }

  async function handleReject(leaveId: string, reason: string) {
    const updated = await hrService.rejectLeave(leaveId, reason)
    setLeaveRequests(prev => prev.map(r => r.id === updated.id ? updated : r))
  }

  async function handleSave(data: EmployeeUpdate) {
    const updated = await hrService.updateEmployee(id, data)
    setEmployee(updated)
  }

  if (loading) {
    return <div className="px-8 py-16 text-center text-sm text-muted-foreground">Laden…</div>
  }
  if (!employee) {
    return <div className="px-8 py-16 text-center text-sm text-destructive">Mitarbeiter nicht gefunden.</div>
  }

  const fullName = `${employee.first_name} ${employee.last_name}`
  const empType = EMPLOYMENT_TYPES.find(t => t.value === employee.employment_type)?.label

  return (
    <div className="space-y-6 px-8 py-6">
      {/* Back */}
      <button
        onClick={() => router.back()}
        className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeftIcon className="h-4 w-4" />
        Zurück
      </button>

      {/* Header */}
      <div className="flex items-start gap-4">
        {employee.photo_url ? (
          <img src={employee.photo_url} alt="" className="h-16 w-16 rounded-full object-cover shrink-0" />
        ) : (
          <div className="h-16 w-16 rounded-full bg-muted flex items-center justify-center text-lg font-semibold shrink-0">
            {initials(employee)}
          </div>
        )}
        <div className="min-w-0">
          <h1 className="text-xl font-semibold">{fullName}</h1>
          <div className="mt-1 flex flex-wrap items-center gap-2">
            {employee.status && (
              <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_COLOR[employee.status]}`}>
                {STATUS_LABELS[employee.status]}
              </span>
            )}
            {empType && (
              <span className="rounded-full bg-muted px-2.5 py-0.5 text-xs">{empType}</span>
            )}
            {employee.department?.name && (
              <span className="text-sm text-muted-foreground">{employee.department.name}</span>
            )}
          </div>
          <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
            <span>{employee.email}</span>
            {employee.hire_date && <span>Seit {fmtDate(employee.hire_date)}</span>}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b">
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px ${
              tab === t.id
                ? "border-primary text-foreground"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {t.label}
            {t.id === "leave" && leaveRequests.filter(r => r.status === "pending").length > 0 && (
              <span className="ml-1.5 rounded-full bg-amber-500 px-1.5 py-0.5 text-[10px] text-white">
                {leaveRequests.filter(r => r.status === "pending").length}
              </span>
            )}
          </button>
        ))}
      </div>

      {tab === "overview" && <ÜbersichtTab employee={employee} />}
      {tab === "leave" && (
        <UrlaubsantraegeTab
          requests={leaveRequests}
          onApprove={handleApprove}
          onReject={handleReject}
        />
      )}
      {tab === "time" && <ZeiterfassungTab employeeId={employee.id} />}
      {tab === "documents" && (
        <div className="p-6">
          <DocumentsTab ownerId={employee.id} />
        </div>
      )}
      {tab === "edit" && (
        <BearbeitenTab
          employee={employee}
          departments={departments}
          roles={roles}
          onSave={handleSave}
        />
      )}
    </div>
  )
}
