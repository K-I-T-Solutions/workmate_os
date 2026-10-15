"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { contractsService } from "@/lib/contracts/service"
import type { BillingRunResult, Contract, ContractStats } from "@/lib/contracts/types"
import {
  CONTRACT_STATUS_COLOR, CONTRACT_STATUS_LABELS, CONTRACT_TYPE_LABELS, INTERVAL_LABELS, fmtDate, fmtEur,
} from "@/lib/contracts/labels"
import { ContractFormDialog } from "@/components/contracts/contract-form-dialog"
import { useAuth } from "@/components/providers/auth-provider"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { PlayIcon } from "lucide-react"

const STATUS_FILTERS = [
  { value: "", label: "Alle" },
  { value: "active", label: "Aktiv" },
  { value: "cancelled", label: "Gekündigt" },
  { value: "paused", label: "Pausiert" },
  { value: "draft", label: "Entwurf" },
  { value: "expired", label: "Beendet" },
]

function Kpi({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-lg border bg-card p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-xl font-semibold tabular-nums">{value}</p>
      {hint && <p className="mt-0.5 text-xs text-muted-foreground">{hint}</p>}
    </div>
  )
}

export function BillingResultView({ result }: { result: BillingRunResult }) {
  return (
    <div className="space-y-3 text-sm">
      {result.invoices_created.length === 0 ? (
        <p className="text-muted-foreground">Keine fälligen Zeiträume – es wurden keine Rechnungen erzeugt.</p>
      ) : (
        <div>
          <p className="mb-2 font-medium">{result.invoices_created.length} Rechnungsentwürfe erstellt:</p>
          <ul className="space-y-1">
            {result.invoices_created.map(i => (
              <li key={i.invoice_id} className="flex justify-between gap-2">
                <Link href={`/invoices/${i.invoice_id}`} className="font-mono text-primary hover:underline">{i.invoice_number}</Link>
                <span className="text-muted-foreground">{i.contract_number} · {fmtDate(i.period_start)}–{fmtDate(i.period_end)}</span>
                <span className="tabular-nums">{fmtEur(i.total)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      {result.contracts_renewed.length > 0 && <p>Verlängert: {result.contracts_renewed.join(", ")}</p>}
      {result.contracts_expired.length > 0 && <p>Beendet: {result.contracts_expired.join(", ")}</p>}
      {result.errors.length > 0 && (
        <div className="rounded-md border border-destructive/40 bg-destructive/5 p-3 text-destructive">
          {result.errors.map(e => <p key={e.contract_number}>{e.contract_number}: {e.error}</p>)}
        </div>
      )}
      <p className="text-xs text-muted-foreground">Die Rechnungen sind Entwürfe – bitte prüfen und unter „Rechnungen“ versenden.</p>
    </div>
  )
}

export function ContractsDashboard() {
  const router = useRouter()
  const { hasPermission } = useAuth()
  const [contracts, setContracts] = useState<Contract[]>([])
  const [stats, setStats] = useState<ContractStats | null>(null)
  const [statusFilter, setStatusFilter] = useState("")
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(true)
  const [formOpen, setFormOpen] = useState(false)
  const [running, setRunning] = useState(false)
  const [runResult, setRunResult] = useState<BillingRunResult | null>(null)

  const canWrite = hasPermission("backoffice.contracts.write")

  function load() {
    setLoading(true)
    Promise.all([
      contractsService.list({ status: statusFilter || undefined, search: search || undefined, limit: 200 }),
      contractsService.stats(),
    ])
      .then(([list, s]) => { setContracts(list.items); setStats(s) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    const t = setTimeout(load, search ? 300 : 0)
    return () => clearTimeout(t)
  }, [statusFilter, search])

  async function handleRunBilling() {
    setRunning(true)
    try {
      setRunResult(await contractsService.runBilling())
      load()
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="space-y-6 px-8 py-6">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-xl font-semibold">Verträge &amp; Abos</h1>
        {canWrite && (
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleRunBilling} disabled={running}>
              <PlayIcon className="mr-2 h-3.5 w-3.5" />
              {running ? "Läuft…" : "Fällige abrechnen"}
            </Button>
            <Button onClick={() => setFormOpen(true)}>Neuer Vertrag</Button>
          </div>
        )}
      </div>

      {stats && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Kpi label="Aktive Verträge" value={String(stats.active_contracts)} />
          <Kpi label="Monatl. wiederkehrend (MRR)" value={fmtEur(stats.monthly_recurring_revenue)} hint={`${fmtEur(stats.annual_recurring_revenue)} / Jahr`} />
          <Kpi label="Fällig zur Abrechnung" value={String(stats.due_for_billing)} />
          <Kpi label="Kündigungsfrist < 30 Tage" value={String(stats.notice_deadlines_30d)} />
        </div>
      )}

      <div className="flex flex-wrap items-center gap-3">
        <Input placeholder="Suche nach Titel, Nummer, Kunde…" value={search} onChange={e => setSearch(e.target.value)} className="max-w-sm" />
        <div className="flex gap-1 rounded-lg border bg-muted p-1">
          {STATUS_FILTERS.map(f => (
            <button
              key={f.value}
              onClick={() => setStatusFilter(f.value)}
              className={`rounded-md px-3 py-1 text-xs font-medium transition-colors ${statusFilter === f.value ? "bg-card text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"}`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {loading && <p className="text-sm text-muted-foreground">Lädt…</p>}
      {!loading && contracts.length === 0 && (
        <p className="py-8 text-center text-sm text-muted-foreground">Keine Verträge vorhanden.</p>
      )}
      {!loading && contracts.length > 0 && (
        <div className="overflow-hidden rounded-lg border">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Nummer</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Vertrag</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Kunde</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Abrechnung</th>
                <th className="px-4 py-3 text-right font-medium text-muted-foreground">Netto/Zeitraum</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Nächste Rechnung</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {contracts.map(c => (
                <tr key={c.id} className="cursor-pointer hover:bg-muted/30" onClick={() => router.push(`/contracts/${c.id}`)}>
                  <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{c.contract_number}</td>
                  <td className="px-4 py-3">
                    <p className="font-medium">{c.title}</p>
                    <p className="text-xs text-muted-foreground">{CONTRACT_TYPE_LABELS[c.contract_type]}</p>
                  </td>
                  <td className="px-4 py-3">{c.customer_name ?? "—"}</td>
                  <td className="px-4 py-3 text-muted-foreground">{INTERVAL_LABELS[c.billing_interval]}</td>
                  <td className="px-4 py-3 text-right tabular-nums">{fmtEur(c.net_amount_per_period)}</td>
                  <td className="px-4 py-3 text-muted-foreground">{fmtDate(c.next_billing_date)}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${CONTRACT_STATUS_COLOR[c.status]}`}>
                      {CONTRACT_STATUS_LABELS[c.status]}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <ContractFormDialog
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSaved={c => router.push(`/contracts/${c.id}`)}
      />

      <Dialog open={!!runResult} onOpenChange={v => { if (!v) setRunResult(null) }}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader><DialogTitle>Abrechnungslauf</DialogTitle></DialogHeader>
          {runResult && <BillingResultView result={runResult} />}
          <DialogFooter>
            <Button onClick={() => setRunResult(null)}>Schließen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
