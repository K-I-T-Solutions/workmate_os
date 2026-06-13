"use client"

import { useEffect, useState } from "react"
import { hrService } from "@/lib/hr/service"
import { adminService } from "@/lib/admin/service"
import type { Employee, LeaveRequest, LeaveRequestCreate, LeaveType, LeaveStatus } from "@/lib/hr/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { PlusIcon, XCircleIcon } from "lucide-react"

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

function diffDays(start: string, end: string): number {
  const ms = new Date(end).getTime() - new Date(start).getTime()
  return Math.max(1, Math.round(ms / 86400000) + 1)
}

function BalanceCards({ requests, vacationTotal }: { requests: LeaveRequest[]; vacationTotal: number }) {
  const year = new Date().getFullYear()
  const thisYear = requests.filter(r => new Date(r.start_date).getFullYear() === year)
  const vacationUsed = thisYear
    .filter(r => r.leave_type === "vacation" && r.status === "approved")
    .reduce((s, r) => s + r.total_days, 0)
  const pending = thisYear.filter(r => r.status === "pending").length
  const VACATION_TOTAL = vacationTotal
  const pct = Math.min(100, Math.round((vacationUsed / VACATION_TOTAL) * 100))

  return (
    <div className="grid gap-4 sm:grid-cols-3">
      <div className="rounded-xl border bg-card p-4">
        <div className="mb-2 flex items-center justify-between">
          <span className="text-sm font-medium">Urlaubstage {year}</span>
          <span className="text-sm">
            <span className="font-semibold">{vacationUsed}</span>
            <span className="text-muted-foreground"> / {VACATION_TOTAL}</span>
          </span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-muted">
          <div
            className={`h-full rounded-full ${pct >= 90 ? "bg-red-500" : pct >= 70 ? "bg-amber-500" : "bg-primary"}`}
            style={{ width: `${pct}%` }}
          />
        </div>
        <p className="mt-1.5 text-xs text-muted-foreground">{VACATION_TOTAL - vacationUsed} Tage verbleibend</p>
      </div>
      <div className="rounded-xl border bg-card p-4">
        <p className="text-sm font-medium">Verbleibend {year}</p>
        <p className="mt-2 text-2xl font-semibold">{VACATION_TOTAL - vacationUsed}</p>
        <p className="mt-0.5 text-xs text-muted-foreground">Urlaubstage verfügbar</p>
      </div>
      <div className="rounded-xl border bg-card p-4">
        <p className="text-sm font-medium">Ausstehend</p>
        <p className="mt-2 text-2xl font-semibold">{pending}</p>
        <p className="mt-0.5 text-xs text-muted-foreground">Anträge warten auf Genehmigung</p>
      </div>
    </div>
  )
}

function NewLeaveForm({
  employee,
  onSave,
  onClose,
}: {
  employee: Employee
  onSave: () => void
  onClose: () => void
}) {
  const [leaveType, setLeaveType] = useState<LeaveType>("vacation")
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [reason, setReason] = useState("")
  const [saving, setSaving] = useState(false)

  const totalDays = startDate && endDate ? diffDays(startDate, endDate) : 0

  async function handleSave() {
    if (!startDate || !endDate) return
    setSaving(true)
    try {
      const payload: LeaveRequestCreate = {
        employee_id: employee.id,
        leave_type: leaveType,
        start_date: startDate,
        end_date: endDate,
        total_days: totalDays,
        reason: reason.trim() || null,
      }
      await hrService.createLeaveRequest(payload)
      onSave()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="grid gap-1.5 sm:col-span-2">
          <Label>Art der Abwesenheit</Label>
          <Select value={leaveType} onValueChange={v => v && setLeaveType(v as LeaveType)}>
            <SelectTrigger>
              <span data-slot="select-value">
                {LEAVE_TYPE_LABELS[leaveType]}
              </span>
            </SelectTrigger>
            <SelectContent>
              {(Object.entries(LEAVE_TYPE_LABELS) as [LeaveType, string][]).map(([v, l]) => (
                <SelectItem key={v} value={v}>{l}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="grid gap-1.5">
          <Label>Von *</Label>
          <Input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
        </div>
        <div className="grid gap-1.5">
          <Label>Bis *</Label>
          <Input type="date" value={endDate} min={startDate} onChange={e => setEndDate(e.target.value)} />
        </div>
        {totalDays > 0 && (
          <p className="sm:col-span-2 text-sm text-muted-foreground">
            {totalDays} Arbeitstag{totalDays !== 1 ? "e" : ""}
          </p>
        )}
        <div className="grid gap-1.5 sm:col-span-2">
          <Label>Grund (optional)</Label>
          <Input value={reason} onChange={e => setReason(e.target.value)} placeholder="Begründung…" />
        </div>
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="outline" onClick={onClose}>Abbrechen</Button>
        <Button onClick={handleSave} disabled={saving || !startDate || !endDate}>
          {saving ? "Einreichen…" : "Antrag einreichen"}
        </Button>
      </div>
    </div>
  )
}

export function MyLeave() {
  const [employee, setEmployee] = useState<Employee | null>(null)
  const [requests, setRequests] = useState<LeaveRequest[]>([])
  const [vacationTotal, setVacationTotal] = useState(30)
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [filterType, setFilterType] = useState("all")
  const [cancelId, setCancelId] = useState<string | null>(null)
  const [cancelling, setCancelling] = useState(false)

  async function load(emp?: Employee | null) {
    const e = emp ?? employee
    if (!e) return
    const leaves = await hrService.listLeaveRequests({ employee_id: e.id })
    setRequests(leaves)
  }

  useEffect(() => {
    async function init() {
      setLoading(true)
      try {
        const [emp, settings] = await Promise.all([
          hrService.getMyEmployee(),
          adminService.getSettings().catch(() => null),
        ])
        if (settings?.vacation_days_per_year) setVacationTotal(settings.vacation_days_per_year)
        setEmployee(emp)
        if (emp) {
          const leaves = await hrService.listLeaveRequests({ employee_id: emp.id })
          setRequests(leaves)
        }
      } finally {
        setLoading(false)
      }
    }
    init()
  }, [])

  async function handleCancel() {
    if (!cancelId) return
    setCancelling(true)
    try {
      await hrService.cancelLeaveRequest(cancelId)
      setCancelId(null)
      load()
    } finally {
      setCancelling(false)
    }
  }

  const filtered = filterType === "all"
    ? requests
    : requests.filter(r => r.leave_type === filterType)

  if (loading) {
    return <div className="px-8 py-16 text-center text-sm text-muted-foreground">Laden…</div>
  }

  if (!employee) {
    return (
      <div className="px-8 py-16 text-center">
        <p className="text-sm text-muted-foreground">
          Kein Mitarbeiterprofil gefunden. Bitte wenden Sie sich an den Administrator.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6 px-8 py-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Meine Abwesenheiten</h1>
          <p className="text-sm text-muted-foreground mt-0.5">{employee.first_name} {employee.last_name}</p>
        </div>
        <Button size="sm" onClick={() => setShowForm(true)}>
          <PlusIcon className="mr-2 h-4 w-4" />
          Neuer Antrag
        </Button>
      </div>

      <BalanceCards requests={requests} vacationTotal={vacationTotal} />

      {/* Filter */}
      <div className="flex gap-2 flex-wrap">
        {[{ value: "all", label: "Alle" }, ...Object.entries(LEAVE_TYPE_LABELS).map(([v, l]) => ({ value: v, label: l }))].map(f => (
          <button
            key={f.value}
            onClick={() => setFilterType(f.value)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              filterType === f.value
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:text-foreground"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="rounded-lg border border-dashed p-12 text-center text-sm text-muted-foreground">
          Keine Abwesenheitsanträge vorhanden.
        </div>
      ) : (
        <div className="rounded-lg border overflow-hidden">
          {filtered.map(req => (
            <div key={req.id} className="flex items-center gap-3 border-b last:border-0 px-4 py-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-medium">{LEAVE_TYPE_LABELS[req.leave_type]}</span>
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${LEAVE_STATUS_COLOR[req.status]}`}>
                    {LEAVE_STATUS_LABELS[req.status]}
                  </span>
                  <span className="text-xs text-muted-foreground">{req.total_days} Tag{req.total_days !== 1 ? "e" : ""}</span>
                </div>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  {fmtDate(req.start_date)} – {fmtDate(req.end_date)}
                </p>
                {req.reason && (
                  <p className="mt-0.5 text-xs text-muted-foreground">{req.reason}</p>
                )}
                {req.rejection_reason && (
                  <p className="mt-0.5 text-xs text-red-500">{req.rejection_reason}</p>
                )}
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <p className="text-xs text-muted-foreground">{fmtDate(req.created_at)}</p>
                {req.status === "pending" && (
                  <button
                    onClick={() => setCancelId(req.id)}
                    className="rounded p-1 text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
                    title="Stornieren"
                  >
                    <XCircleIcon className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <AlertDialog open={!!cancelId} onOpenChange={open => !open && setCancelId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Antrag stornieren?</AlertDialogTitle>
            <AlertDialogDescription>
              Der Abwesenheitsantrag wird storniert und kann nicht rückgängig gemacht werden.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={cancelling}>Abbrechen</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleCancel}
              disabled={cancelling}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {cancelling ? "Storniere…" : "Stornieren"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <Dialog open={showForm} onOpenChange={open => !open && setShowForm(false)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Neuer Abwesenheitsantrag</DialogTitle>
          </DialogHeader>
          <NewLeaveForm
            employee={employee}
            onSave={() => { setShowForm(false); load() }}
            onClose={() => setShowForm(false)}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}
