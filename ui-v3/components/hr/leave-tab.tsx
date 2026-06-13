"use client"

import { useEffect, useState } from "react"
import { hrService } from "@/lib/hr/service"
import type { LeaveRequest, LeaveStatistics, LeaveType, LeaveStatus, Employee } from "@/lib/hr/types"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { Input } from "@/components/ui/input"
import { CheckIcon, XIcon } from "lucide-react"

const LEAVE_TYPE_LABELS: Record<LeaveType, string> = {
  vacation: "Urlaub", sick: "Krank", parental: "Elternzeit", other: "Sonstiges",
}
const LEAVE_STATUS_LABELS: Record<LeaveStatus, string> = {
  pending: "Ausstehend", approved: "Genehmigt", rejected: "Abgelehnt", cancelled: "Storniert",
}
const STATUS_COLOR: Record<LeaveStatus, string> = {
  pending: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  approved: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  cancelled: "bg-muted text-muted-foreground",
}

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("de-DE")
}

export function LeaveTab({ stats }: { stats: LeaveStatistics | null }) {
  const [requests, setRequests] = useState<LeaveRequest[]>([])
  const [employees, setEmployees] = useState<Employee[]>([])
  const [loading, setLoading] = useState(true)
  const [filterStatus, setFilterStatus] = useState("all")
  const [filterType, setFilterType] = useState("all")
  const [rejectId, setRejectId] = useState<string | null>(null)
  const [rejectReason, setRejectReason] = useState("")
  const [processing, setProcessing] = useState<string | null>(null)

  const employeeMap = Object.fromEntries(
    employees.map(e => [e.id, `${e.first_name} ${e.last_name}`])
  )

  async function load() {
    setLoading(true)
    try {
      const params: Record<string, string> = {}
      if (filterStatus !== "all") params.status = filterStatus
      if (filterType !== "all") params.leave_type = filterType
      const data = await hrService.listLeaveRequests(params as Parameters<typeof hrService.listLeaveRequests>[0])
      setRequests(data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    hrService.listEmployees({ limit: 200 }).then(setEmployees).catch(() => {})
  }, [])

  useEffect(() => { load() }, [filterStatus, filterType])

  async function handleApprove(id: string) {
    setProcessing(id)
    try {
      await hrService.approveLeave(id)
      load()
    } finally {
      setProcessing(null)
    }
  }

  async function handleReject() {
    if (!rejectId) return
    setProcessing(rejectId)
    try {
      await hrService.rejectLeave(rejectId, rejectReason)
      setRejectId(null)
      setRejectReason("")
      load()
    } finally {
      setProcessing(null)
    }
  }

  return (
    <div className="space-y-4">
      {/* Stats */}
      {stats && (
        <div className="grid gap-3 sm:grid-cols-4">
          {[
            { label: "Gesamt", value: stats.total_requests },
            { label: "Ausstehend", value: stats.pending_requests },
            { label: "Genehmigt", value: stats.approved_requests },
            { label: "Abgelehnt", value: stats.rejected_requests },
          ].map(s => (
            <div key={s.label} className="rounded-lg border bg-card p-4">
              <p className="text-xs text-muted-foreground">{s.label}</p>
              <p className="mt-1 text-2xl font-semibold">{s.value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Filter */}
      <div className="flex gap-2">
        <Select value={filterStatus} onValueChange={v => v && setFilterStatus(v)}>
          <SelectTrigger className="w-44"><SelectValue placeholder="Status" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle Status</SelectItem>
            {Object.entries(LEAVE_STATUS_LABELS).map(([v, l]) => <SelectItem key={v} value={v}>{l}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={filterType} onValueChange={v => v && setFilterType(v)}>
          <SelectTrigger className="w-44"><SelectValue placeholder="Abwesenheitsart" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle Arten</SelectItem>
            {Object.entries(LEAVE_TYPE_LABELS).map(([v, l]) => <SelectItem key={v} value={v}>{l}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      {loading ? (
        <div className="py-12 text-center text-sm text-muted-foreground">Laden…</div>
      ) : requests.length === 0 ? (
        <div className="rounded-lg border border-dashed p-12 text-center text-sm text-muted-foreground">
          Keine Abwesenheitsanträge gefunden.
        </div>
      ) : (
        <div className="rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/40">
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Mitarbeiter</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Typ</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Zeitraum</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Tage</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Grund</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Status</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Aktionen</th>
              </tr>
            </thead>
            <tbody>
              {requests.map(req => (
                <tr key={req.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                  <td className="px-4 py-3">
                    <span className="font-medium">{employeeMap[req.employee_id] ?? "–"}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="font-medium">{LEAVE_TYPE_LABELS[req.leave_type as LeaveType] ?? req.leave_type}</span>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {fmtDate(req.start_date)} – {fmtDate(req.end_date)}
                  </td>
                  <td className="px-4 py-3 font-medium">{req.total_days}</td>
                  <td className="px-4 py-3 text-muted-foreground max-w-48 truncate">{req.reason ?? "–"}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLOR[req.status as LeaveStatus] ?? "bg-muted"}`}>
                      {LEAVE_STATUS_LABELS[req.status as LeaveStatus] ?? req.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {req.status === "pending" && (
                      <div className="flex gap-1">
                        <Button
                          size="icon" variant="ghost"
                          className="h-7 w-7 text-green-600 hover:bg-green-50 dark:hover:bg-green-950"
                          disabled={processing === req.id}
                          onClick={() => handleApprove(req.id)}
                          title="Genehmigen"
                        >
                          <CheckIcon className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          size="icon" variant="ghost"
                          className="h-7 w-7 text-destructive hover:bg-destructive/10"
                          disabled={processing === req.id}
                          onClick={() => { setRejectId(req.id); setRejectReason("") }}
                          title="Ablehnen"
                        >
                          <XIcon className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <AlertDialog open={!!rejectId} onOpenChange={open => !open && setRejectId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Antrag ablehnen</AlertDialogTitle>
            <AlertDialogDescription>Bitte gib einen Ablehnungsgrund an.</AlertDialogDescription>
          </AlertDialogHeader>
          <div className="px-1 pb-2">
            <Input
              value={rejectReason}
              onChange={e => setRejectReason(e.target.value)}
              placeholder="Ablehnungsgrund…"
            />
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleReject}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              disabled={!rejectReason.trim()}
            >
              Ablehnen
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
