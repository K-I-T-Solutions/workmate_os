"use client"

import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { timeTrackingService } from "@/lib/time-tracking/service"
import { projectService } from "@/lib/projects/service"
import { crmService } from "@/lib/crm/service"
import type { BillableEntry } from "@/lib/time-tracking/types"
import type { Project } from "@/lib/projects/types"
import type { Customer } from "@/lib/crm/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select"
import {
  Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog"
import { ReceiptIcon } from "lucide-react"

function fmt(n: number) {
  return new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR" }).format(n)
}

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("de-DE")
}

function mostCommonRate(entries: BillableEntry[]): number {
  const rates = entries
    .map(e => e.hourly_rate)
    .filter((r): r is number => r !== null && r !== undefined)
  if (rates.length === 0) return 79
  const freq: Record<number, number> = {}
  for (const r of rates) freq[r] = (freq[r] ?? 0) + 1
  return Number(Object.entries(freq).sort((a, b) => b[1] - a[1])[0][0])
}

export function TimeBilling() {
  const router = useRouter()

  const [entries, setEntries] = useState<BillableEntry[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [customers, setCustomers] = useState<Customer[]>([])
  const [loading, setLoading] = useState(true)

  const [filterProject, setFilterProject] = useState<string>("")
  const [filterEmployee, setFilterEmployee] = useState<string>("")

  const [selected, setSelected] = useState<Set<string>>(new Set())

  const [dialogOpen, setDialogOpen] = useState(false)
  const [dialogCustomerId, setDialogCustomerId] = useState("")
  const [dialogRate, setDialogRate] = useState("79")
  const [dialogGroupByTask, setDialogGroupByTask] = useState(false)
  const [dialogNotes, setDialogNotes] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [successMsg, setSuccessMsg] = useState<{ id: string; invoice_number: string } | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const params: { project_id?: string; employee_id?: string } = {}
      if (filterProject) params.project_id = filterProject
      if (filterEmployee) params.employee_id = filterEmployee

      const [res, projs, custs] = await Promise.all([
        timeTrackingService.getBillableUninvoiced(params),
        projectService.list().catch(() => [] as Project[]),
        crmService.getCustomers({ limit: 500 }).catch(() => [] as Customer[]),
      ])
      setEntries(res.entries)
      setProjects(projs)
      setCustomers(Array.isArray(custs) ? custs : (custs as unknown as { items?: Customer[] }).items ?? [])
      setSelected(new Set())
    } finally {
      setLoading(false)
    }
  }, [filterProject, filterEmployee])

  useEffect(() => { load() }, [load])

  const allSelected = entries.length > 0 && selected.size === entries.length

  function toggleAll() {
    if (allSelected) {
      setSelected(new Set())
    } else {
      setSelected(new Set(entries.map(e => e.id)))
    }
  }

  function toggleOne(id: string) {
    setSelected(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const selectedEntries = entries.filter(e => selected.has(e.id))
  const selectedHours = selectedEntries.reduce((s, e) => s + e.duration_hours, 0)
  const selectedAmount = selectedEntries.reduce((s, e) => s + (e.amount ?? e.duration_hours * (e.hourly_rate ?? 0)), 0)

  function openDialog() {
    const defaultRate = mostCommonRate(selectedEntries)
    setDialogRate(String(defaultRate))
    setDialogCustomerId("")
    setDialogGroupByTask(false)
    setDialogNotes("")
    setSuccessMsg(null)
    setDialogOpen(true)
  }

  async function handleCreateInvoice() {
    if (!dialogCustomerId) return
    setSubmitting(true)
    try {
      const result = await timeTrackingService.createInvoiceFromEntries({
        time_entry_ids: Array.from(selected),
        customer_id: dialogCustomerId,
        hourly_rate: parseFloat(dialogRate) || 79,
        group_by_task_type: dialogGroupByTask,
        notes: dialogNotes || undefined,
      })
      setSuccessMsg(result)
      load()
    } finally {
      setSubmitting(false)
    }
  }

  const employeeNames = Array.from(new Set(entries.map(e => e.employee_name))).sort()

  return (
    <div className="space-y-6 px-8 py-6">
      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <Select value={filterProject || "__all__"} onValueChange={v => setFilterProject(!v || v === "__all__" ? "" : v)}>
          <SelectTrigger className="w-52">
            <SelectValue placeholder="Alle Projekte" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="__all__">Alle Projekte</SelectItem>
            {projects.map(p => (
              <SelectItem key={p.id} value={p.id}>{p.title}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        {employeeNames.length > 1 && (
          <Select value={filterEmployee || "__all__"} onValueChange={v => setFilterEmployee(!v || v === "__all__" ? "" : v)}>
            <SelectTrigger className="w-52">
              <SelectValue placeholder="Alle Mitarbeiter" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="__all__">Alle Mitarbeiter</SelectItem>
              {employeeNames.map(name => (
                <SelectItem key={name} value={name}>{name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </div>

      {loading ? (
        <div className="py-16 text-center text-sm text-muted-foreground">Laden…</div>
      ) : entries.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-3 rounded-xl border bg-card py-20 text-center">
          <ReceiptIcon className="h-10 w-10 text-muted-foreground/40" />
          <p className="text-sm font-medium text-muted-foreground">Keine offenen billable Stunden</p>
          <p className="text-xs text-muted-foreground">Alle abrechenbaren Einträge wurden bereits abgerechnet.</p>
        </div>
      ) : (
        <>
          {/* Table */}
          <div className="rounded-lg border overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="w-10 px-4 py-2.5 text-left">
                    <input
                      type="checkbox"
                      checked={allSelected}
                      onChange={toggleAll}
                      className="h-4 w-4 rounded border-border accent-primary"
                    />
                  </th>
                  <th className="px-3 py-2.5 text-left text-xs font-medium text-muted-foreground">Datum</th>
                  <th className="px-3 py-2.5 text-left text-xs font-medium text-muted-foreground">Mitarbeiter</th>
                  <th className="px-3 py-2.5 text-left text-xs font-medium text-muted-foreground">Projekt</th>
                  <th className="px-3 py-2.5 text-left text-xs font-medium text-muted-foreground">Tätigkeit</th>
                  <th className="px-3 py-2.5 text-left text-xs font-medium text-muted-foreground max-w-xs">Notiz</th>
                  <th className="px-3 py-2.5 text-right text-xs font-medium text-muted-foreground">Stunden</th>
                  <th className="px-3 py-2.5 text-right text-xs font-medium text-muted-foreground">Stundensatz</th>
                  <th className="px-3 py-2.5 text-right text-xs font-medium text-muted-foreground">Betrag</th>
                </tr>
              </thead>
              <tbody className="divide-y bg-card">
                {entries.map(e => (
                  <tr
                    key={e.id}
                    className={`transition-colors hover:bg-muted/30 cursor-pointer ${selected.has(e.id) ? "bg-primary/5" : ""}`}
                    onClick={() => toggleOne(e.id)}
                  >
                    <td className="px-4 py-2.5" onClick={ev => ev.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={selected.has(e.id)}
                        onChange={() => toggleOne(e.id)}
                        className="h-4 w-4 rounded border-border accent-primary"
                      />
                    </td>
                    <td className="px-3 py-2.5 whitespace-nowrap text-muted-foreground">{fmtDate(e.date)}</td>
                    <td className="px-3 py-2.5 whitespace-nowrap">{e.employee_name}</td>
                    <td className="px-3 py-2.5 whitespace-nowrap text-muted-foreground">{e.project_name ?? "–"}</td>
                    <td className="px-3 py-2.5 whitespace-nowrap text-muted-foreground">{e.task_type ?? "–"}</td>
                    <td className="px-3 py-2.5 max-w-xs truncate text-muted-foreground" title={e.note ?? undefined}>{e.note ?? "–"}</td>
                    <td className="px-3 py-2.5 text-right tabular-nums font-medium">{e.duration_hours.toFixed(2)}</td>
                    <td className="px-3 py-2.5 text-right tabular-nums text-muted-foreground">
                      {e.hourly_rate !== null ? fmt(e.hourly_rate) : "–"}
                    </td>
                    <td className="px-3 py-2.5 text-right tabular-nums font-medium">
                      {e.amount !== null ? fmt(e.amount) : "–"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Summary + action */}
          <div className="flex flex-wrap items-center justify-between gap-4 rounded-lg border bg-card px-5 py-4">
            <div className="flex items-center gap-6 text-sm">
              <div>
                <span className="text-muted-foreground">Ausgewählt: </span>
                <span className="font-semibold">{selected.size} Einträge</span>
              </div>
              <div>
                <span className="text-muted-foreground">Stunden: </span>
                <span className="font-semibold tabular-nums">{selectedHours.toFixed(2)}h</span>
              </div>
              <div>
                <span className="text-muted-foreground">Betrag: </span>
                <span className="font-semibold tabular-nums text-primary">{fmt(selectedAmount)}</span>
              </div>
            </div>
            <Button
              disabled={selected.size === 0}
              onClick={openDialog}
            >
              <ReceiptIcon className="mr-2 h-4 w-4" />
              Rechnung erstellen
            </Button>
          </div>
        </>
      )}

      {/* Create invoice dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Rechnung aus Zeiteinträgen erstellen</DialogTitle>
          </DialogHeader>

          {successMsg ? (
            <div className="space-y-4 py-2">
              <div className="rounded-lg border border-green-200 bg-green-50 p-4 text-sm text-green-800">
                <p className="font-medium">Rechnung erstellt</p>
                <p className="mt-1">Rechnungsnummer: <span className="font-mono">{successMsg.invoice_number}</span></p>
              </div>
              <DialogFooter className="gap-2">
                <Button variant="outline" onClick={() => setDialogOpen(false)}>Schließen</Button>
                <Button onClick={() => router.push(`/invoices/${successMsg.id}`)}>
                  Rechnung öffnen
                </Button>
              </DialogFooter>
            </div>
          ) : (
            <div className="space-y-4 py-2">
              <div className="rounded-lg border bg-muted/40 px-4 py-3 text-sm text-muted-foreground">
                {selected.size} Einträge · {selectedHours.toFixed(2)}h · {fmt(selectedAmount)}
              </div>

              <div className="grid gap-1.5">
                <Label>Kunde *</Label>
                <Select value={dialogCustomerId} onValueChange={v => v && setDialogCustomerId(v)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Kunde auswählen…" />
                  </SelectTrigger>
                  <SelectContent>
                    {customers.map(c => (
                      <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-1.5">
                <Label>Stundensatz (€)</Label>
                <Input
                  type="number"
                  min="0"
                  step="0.01"
                  value={dialogRate}
                  onChange={e => setDialogRate(e.target.value)}
                  placeholder="79"
                />
              </div>

              <div className="grid gap-1.5">
                <Label>Gruppierung</Label>
                <div className="flex gap-1 rounded-lg border bg-muted p-1 w-fit">
                  <button
                    type="button"
                    onClick={() => setDialogGroupByTask(false)}
                    className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                      !dialogGroupByTask ? "bg-card text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    Gesamtposition
                  </button>
                  <button
                    type="button"
                    onClick={() => setDialogGroupByTask(true)}
                    className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                      dialogGroupByTask ? "bg-card text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    Pro Tätigkeit
                  </button>
                </div>
              </div>

              <div className="grid gap-1.5">
                <Label>Notiz <span className="text-muted-foreground font-normal">(optional)</span></Label>
                <Textarea
                  value={dialogNotes}
                  onChange={e => setDialogNotes(e.target.value)}
                  rows={3}
                  placeholder="Interne oder externe Anmerkung zur Rechnung…"
                />
              </div>

              <DialogFooter className="gap-2">
                <Button variant="outline" onClick={() => setDialogOpen(false)} disabled={submitting}>
                  Abbrechen
                </Button>
                <Button
                  onClick={handleCreateInvoice}
                  disabled={submitting || !dialogCustomerId}
                >
                  {submitting ? "Erstelle…" : "Rechnung erstellen"}
                </Button>
              </DialogFooter>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
