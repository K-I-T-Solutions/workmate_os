"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { usePageTitle } from "@/lib/page-title-context"
import { contractsService } from "@/lib/contracts/service"
import type { BillingRunResult, Contract, ContractInvoiceBrief } from "@/lib/contracts/types"
import {
  CONTRACT_STATUS_COLOR, CONTRACT_STATUS_LABELS, CONTRACT_TYPE_LABELS, INTERVAL_LABELS, fmtDate, fmtEur,
} from "@/lib/contracts/labels"
import { ContractFormDialog } from "@/components/contracts/contract-form-dialog"
import { BillingResultView } from "@/components/contracts/contracts-dashboard"
import { useAuth } from "@/components/providers/auth-provider"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { ArrowLeftIcon, PencilIcon, PlayIcon, BanIcon } from "lucide-react"

export function ContractDetailView({ id }: { id: string }) {
  const router = useRouter()
  const { hasPermission } = useAuth()
  const [contract, setContract] = useState<Contract | null>(null)
  const [invoices, setInvoices] = useState<ContractInvoiceBrief[]>([])
  const [loading, setLoading] = useState(true)
  const [editOpen, setEditOpen] = useState(false)
  const [cancelOpen, setCancelOpen] = useState(false)
  const [cancelDate, setCancelDate] = useState("")
  const [cancelReason, setCancelReason] = useState("")
  const [billing, setBilling] = useState(false)
  const [billResult, setBillResult] = useState<BillingRunResult | null>(null)
  usePageTitle(contract?.title)

  const canWrite = hasPermission("backoffice.contracts.write")

  async function load() {
    const [c, inv] = await Promise.all([
      contractsService.get(id).catch(() => null),
      contractsService.invoices(id).catch(() => []),
    ])
    setContract(c)
    setInvoices(inv)
    setLoading(false)
  }

  useEffect(() => { load() }, [id])

  function openCancel() {
    if (!contract) return
    // Vorschlag: frühestmögliches Ende = heute + Kündigungsfrist, mindestens Vertragsende
    const earliest = new Date(Date.now() + contract.notice_period_days * 86_400_000)
    const end = contract.end_date && new Date(contract.end_date) > earliest ? contract.end_date : earliest.toISOString().slice(0, 10)
    setCancelDate(end)
    setCancelReason("")
    setCancelOpen(true)
  }

  async function handleCancel() {
    if (!cancelDate) return
    setContract(await contractsService.cancel(id, cancelDate, cancelReason || undefined))
    setCancelOpen(false)
  }

  async function handleBillNow() {
    setBilling(true)
    try {
      setBillResult(await contractsService.billNow(id))
      load()
    } finally {
      setBilling(false)
    }
  }

  if (loading) return <div className="flex items-center justify-center py-24 text-sm text-muted-foreground">Laden…</div>
  if (!contract) return <div className="flex items-center justify-center py-24 text-sm text-destructive">Vertrag nicht gefunden.</div>

  const due = contract.next_billing_date && new Date(contract.next_billing_date) <= new Date()
  const noticeDeadline = contract.end_date
    ? new Date(new Date(contract.end_date).getTime() - contract.notice_period_days * 86_400_000).toISOString().slice(0, 10)
    : null

  return (
    <div className="space-y-6 px-8 py-6">
      <div className="flex items-start gap-3">
        <Button variant="ghost" size="icon" className="mt-0.5 shrink-0" onClick={() => router.push("/contracts")}>
          <ArrowLeftIcon className="h-4 w-4" />
        </Button>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-xs text-muted-foreground">{contract.contract_number}</span>
            <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${CONTRACT_STATUS_COLOR[contract.status]}`}>
              {CONTRACT_STATUS_LABELS[contract.status]}
            </span>
            <span className="text-sm text-muted-foreground">{CONTRACT_TYPE_LABELS[contract.contract_type]}</span>
          </div>
          <h1 className="mt-1 text-xl font-semibold">{contract.title}</h1>
          <Link href={`/crm/customers/${contract.customer_id}`} className="text-sm text-primary hover:underline">
            {contract.customer_name}
          </Link>
        </div>
        {canWrite && (
          <div className="flex shrink-0 gap-2">
            {due && ["active", "cancelled"].includes(contract.status) && (
              <Button variant="outline" onClick={handleBillNow} disabled={billing}>
                <PlayIcon className="mr-2 h-3.5 w-3.5" /> {billing ? "Läuft…" : "Jetzt abrechnen"}
              </Button>
            )}
            {contract.status === "active" && (
              <Button variant="outline" onClick={openCancel}>
                <BanIcon className="mr-2 h-3.5 w-3.5" /> Kündigen
              </Button>
            )}
            <Button variant="outline" onClick={() => setEditOpen(true)}>
              <PencilIcon className="mr-2 h-3.5 w-3.5" /> Bearbeiten
            </Button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3 rounded-lg border bg-card p-4 text-sm sm:grid-cols-4">
        {[
          { label: "Laufzeit", value: `${fmtDate(contract.start_date)} – ${contract.end_date ? fmtDate(contract.end_date) : "unbefristet"}` },
          { label: "Abrechnung", value: `${INTERVAL_LABELS[contract.billing_interval]}, ${contract.payment_terms_days} Tage Ziel` },
          { label: "Nächste Rechnung", value: fmtDate(contract.next_billing_date) },
          { label: "Zuletzt abgerechnet", value: fmtDate(contract.last_billed_date) },
          { label: "Netto / Zeitraum", value: fmtEur(contract.net_amount_per_period) },
          { label: "MRR", value: fmtEur(contract.monthly_recurring_revenue) },
          { label: "Verlängerung", value: contract.auto_renew ? `automatisch um ${contract.renewal_months} Monate` : "keine" },
          { label: "Kündigungsfrist", value: noticeDeadline ? `${contract.notice_period_days} Tage (bis ${fmtDate(noticeDeadline)})` : `${contract.notice_period_days} Tage` },
        ].map(m => (
          <div key={m.label}>
            <p className="text-xs text-muted-foreground">{m.label}</p>
            <p className="mt-0.5 font-medium">{m.value}</p>
          </div>
        ))}
        {contract.included_hours && (
          <div>
            <p className="text-xs text-muted-foreground">Inklusiv-Stunden</p>
            <p className="mt-0.5 font-medium">{parseFloat(String(contract.included_hours))} h / Zeitraum</p>
          </div>
        )}
      </div>

      <div>
        <h2 className="mb-2 text-sm font-medium text-muted-foreground">Positionen</h2>
        <div className="overflow-hidden rounded-lg border">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-4 py-2.5 text-left font-medium text-muted-foreground">Leistung</th>
                <th className="px-4 py-2.5 text-right font-medium text-muted-foreground">Menge</th>
                <th className="px-4 py-2.5 text-right font-medium text-muted-foreground">Einzelpreis</th>
                <th className="px-4 py-2.5 text-right font-medium text-muted-foreground">MwSt.</th>
                <th className="px-4 py-2.5 text-right font-medium text-muted-foreground">Netto</th>
              </tr>
            </thead>
            <tbody className="divide-y bg-card">
              {contract.items.map(i => (
                <tr key={i.id}>
                  <td className="px-4 py-2.5">{i.description}</td>
                  <td className="px-4 py-2.5 text-right tabular-nums">{parseFloat(String(i.quantity)).toLocaleString("de-DE")} {i.unit}</td>
                  <td className="px-4 py-2.5 text-right tabular-nums">{fmtEur(i.unit_price)}</td>
                  <td className="px-4 py-2.5 text-right tabular-nums">{parseFloat(String(i.tax_rate))} %</td>
                  <td className="px-4 py-2.5 text-right tabular-nums font-medium">{fmtEur(i.net_amount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {contract.notes && (
        <div>
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">Notizen</h2>
          <p className="whitespace-pre-wrap rounded-lg border bg-card p-4 text-sm">{contract.notes}</p>
        </div>
      )}

      <div>
        <h2 className="mb-2 text-sm font-medium text-muted-foreground">Rechnungen aus diesem Vertrag</h2>
        {invoices.length === 0 ? (
          <p className="text-sm text-muted-foreground">Noch keine Rechnungen.</p>
        ) : (
          <div className="overflow-hidden rounded-lg border">
            <table className="w-full text-sm">
              <tbody className="divide-y bg-card">
                {invoices.map(i => (
                  <tr key={i.id} className="cursor-pointer hover:bg-muted/30" onClick={() => router.push(`/invoices/${i.id}`)}>
                    <td className="px-4 py-2.5 font-mono text-xs">{i.invoice_number}</td>
                    <td className="px-4 py-2.5 text-muted-foreground">{fmtDate(i.issued_date)}</td>
                    <td className="px-4 py-2.5">{i.status === "draft" ? "Entwurf" : i.status}</td>
                    <td className="px-4 py-2.5 text-right tabular-nums">{fmtEur(i.total)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <ContractFormDialog open={editOpen} onClose={() => setEditOpen(false)} onSaved={setContract} contract={contract} />

      <Dialog open={cancelOpen} onOpenChange={setCancelOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader><DialogTitle>Vertrag kündigen</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Der Vertrag wird bis zum Vertragsende weiter abgerechnet und verlängert sich nicht mehr automatisch.
            </p>
            <div className="space-y-1.5">
              <Label htmlFor="cancel-date">Vertragsende (letzter Leistungstag)</Label>
              <Input id="cancel-date" type="date" value={cancelDate} onChange={e => setCancelDate(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="cancel-reason">Grund (optional)</Label>
              <Textarea id="cancel-reason" rows={2} value={cancelReason} onChange={e => setCancelReason(e.target.value)} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCancelOpen(false)}>Abbrechen</Button>
            <Button variant="destructive" onClick={handleCancel} disabled={!cancelDate}>Kündigen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={!!billResult} onOpenChange={v => { if (!v) setBillResult(null) }}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader><DialogTitle>Abrechnung</DialogTitle></DialogHeader>
          {billResult && <BillingResultView result={billResult} />}
          <DialogFooter><Button onClick={() => setBillResult(null)}>Schließen</Button></DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
