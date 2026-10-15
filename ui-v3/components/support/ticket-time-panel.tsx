"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { timeTrackingService } from "@/lib/time-tracking/service"
import type { TicketTimeSummary } from "@/lib/time-tracking/types"
import type { Employee } from "@/lib/hr/types"
import { useAuth } from "@/components/providers/auth-provider"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ClockIcon, ReceiptIcon } from "lucide-react"

function todayIso() {
  return new Date().toISOString().slice(0, 10)
}

function fmtHours(minutes: number | null) {
  return ((minutes ?? 0) / 60).toFixed(2).replace(".", ",")
}

export function TicketTimePanel({ ticketId, employees }: { ticketId: string; employees: Employee[] }) {
  const { user, hasPermission } = useAuth()
  const [summary, setSummary] = useState<TicketTimeSummary | null>(null)
  const [employeeId, setEmployeeId] = useState("")
  const [day, setDay] = useState(todayIso())
  const [start, setStart] = useState("09:00")
  const [minutes, setMinutes] = useState("30")
  const [note, setNote] = useState("")
  const [billable, setBillable] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const canBook = hasPermission("backoffice.time_tracking.write")

  async function load() {
    setSummary(await timeTrackingService.listForTicket(ticketId).catch(() => null))
  }

  useEffect(() => { load() }, [ticketId])

  // Eigenen Mitarbeiter vorauswählen
  useEffect(() => {
    if (employeeId || !user) return
    const me = employees.find(e => e.email?.toLowerCase() === user.email?.toLowerCase())
    if (me) setEmployeeId(me.id)
  }, [employees, user, employeeId])

  async function handleBook(e: React.FormEvent) {
    e.preventDefault()
    const mins = parseInt(minutes, 10)
    if (!employeeId || !mins || mins <= 0) return
    setSaving(true)
    setError(null)
    try {
      const startDate = new Date(`${day}T${start}:00`)
      const endDate = new Date(startDate.getTime() + mins * 60_000)
      await timeTrackingService.create({
        employee_id: employeeId,
        ticket_id: ticketId,
        start_time: startDate.toISOString(),
        end_time: endDate.toISOString(),
        note: note.trim() || null,
        task_type: "support",
        billable,
      })
      setNote("")
      load()
    } catch {
      setError("Zeit konnte nicht gebucht werden.")
    } finally {
      setSaving(false)
    }
  }

  const employeeName = (id: string) => {
    const e = employees.find(x => x.id === id)
    return e ? `${e.first_name} ${e.last_name}` : "…"
  }

  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="flex items-center gap-1.5 text-sm font-medium text-muted-foreground">
          <ClockIcon className="h-3.5 w-3.5" />
          Zeiten
          {summary && summary.items.length > 0 && (
            <span className="ml-1 font-normal">
              · {summary.total_hours.toFixed(2).replace(".", ",")} h gesamt
              {summary.unbilled_hours > 0 && ` · ${summary.unbilled_hours.toFixed(2).replace(".", ",")} h offen`}
            </span>
          )}
        </h2>
        {summary && summary.unbilled_hours > 0 && hasPermission("backoffice.time_tracking.write") && (
          <Link href="/time?tab=billing" className="flex items-center gap-1 text-xs text-primary hover:underline">
            <ReceiptIcon className="h-3.5 w-3.5" /> Abrechnen
          </Link>
        )}
      </div>

      {summary && summary.items.length > 0 && (
        <div className="mb-3 overflow-hidden rounded-lg border">
          <table className="w-full text-sm">
            <tbody className="divide-y bg-card">
              {summary.items.map(e => (
                <tr key={e.id}>
                  <td className="px-3 py-2 whitespace-nowrap text-muted-foreground">
                    {new Date(e.start_time).toLocaleDateString("de-DE")}
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap">{employeeName(e.employee_id)}</td>
                  <td className="px-3 py-2 text-muted-foreground truncate max-w-xs">{e.note ?? "–"}</td>
                  <td className="px-3 py-2 text-right tabular-nums">{fmtHours(e.duration_minutes)} h</td>
                  <td className="px-3 py-2 text-right text-xs">
                    {e.is_invoiced ? (
                      <span className="text-green-700 dark:text-green-400">abgerechnet</span>
                    ) : e.billable ? (
                      <span className="text-muted-foreground">offen</span>
                    ) : (
                      <span className="text-muted-foreground">intern</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {canBook && (
        <form onSubmit={handleBook} className="grid grid-cols-2 gap-3 rounded-lg border bg-card p-4 sm:grid-cols-6">
          <div className="col-span-2 space-y-1.5">
            <Label htmlFor="tt-emp">Mitarbeiter</Label>
            <select
              id="tt-emp"
              value={employeeId}
              onChange={e => setEmployeeId(e.target.value)}
              className="flex h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm dark:bg-input/30"
              required
            >
              <option value="">Auswählen…</option>
              {employees.map(e => (
                <option key={e.id} value={e.id}>{e.first_name} {e.last_name}</option>
              ))}
            </select>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="tt-day">Datum</Label>
            <Input id="tt-day" type="date" value={day} onChange={e => setDay(e.target.value)} required />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="tt-start">Beginn</Label>
            <Input id="tt-start" type="time" value={start} onChange={e => setStart(e.target.value)} required />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="tt-min">Minuten</Label>
            <Input id="tt-min" type="number" min="1" step="5" value={minutes} onChange={e => setMinutes(e.target.value)} required />
          </div>
          <div className="flex items-end pb-1.5">
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={billable} onChange={e => setBillable(e.target.checked)} className="h-4 w-4 accent-primary" />
              Abrechenbar
            </label>
          </div>
          <div className="col-span-2 space-y-1.5 sm:col-span-5">
            <Label htmlFor="tt-note">Tätigkeit</Label>
            <Input id="tt-note" value={note} onChange={e => setNote(e.target.value)} placeholder="z.B. Fernwartung Druckertreiber" />
          </div>
          <div className="flex items-end">
            <Button type="submit" size="sm" className="w-full" disabled={saving || !employeeId}>
              {saving ? "Buche…" : "Buchen"}
            </Button>
          </div>
          {error && <p className="col-span-full text-sm text-destructive">{error}</p>}
        </form>
      )}
    </div>
  )
}
