"use client"

import { useEffect, useState } from "react"
import { contractsService } from "@/lib/contracts/service"
import { crmService } from "@/lib/crm/service"
import type { Contract, ContractCreate, ContractItem, ContractType, BillingInterval, ContractStatus } from "@/lib/contracts/types"
import type { Customer } from "@/lib/crm/types"
import { CONTRACT_TYPE_LABELS, INTERVAL_LABELS, fmtEur } from "@/lib/contracts/labels"
import { CustomerSelect } from "@/components/crm/customer-select"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { PlusIcon, Trash2Icon } from "lucide-react"

const SELECT_CLS = "flex h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm dark:bg-input/30"

const EMPTY_ITEM: ContractItem = { description: "", quantity: 1, unit: "Monat", unit_price: "", tax_rate: 19 }

function today() {
  return new Date().toISOString().slice(0, 10)
}

/** Anlegen oder Bearbeiten eines Vertrags inkl. Positionen. */
export function ContractFormDialog({
  open,
  onClose,
  onSaved,
  contract,
  defaultCustomerId,
}: {
  open: boolean
  onClose: () => void
  onSaved: (c: Contract) => void
  contract?: Contract | null
  defaultCustomerId?: string
}) {
  const editing = !!contract
  const [customers, setCustomers] = useState<Customer[]>([])
  const [title, setTitle] = useState("")
  const [customerId, setCustomerId] = useState("")
  const [type, setType] = useState<ContractType>("maintenance")
  const [status, setStatus] = useState<ContractStatus>("active")
  const [startDate, setStartDate] = useState(today())
  const [endDate, setEndDate] = useState("")
  const [billingInterval, setBillingInterval] = useState<BillingInterval>("monthly")
  const [autoRenew, setAutoRenew] = useState(true)
  const [noticeDays, setNoticeDays] = useState("90")
  const [includedHours, setIncludedHours] = useState("")
  const [items, setItems] = useState<ContractItem[]>([{ ...EMPTY_ITEM }])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!open) return
    crmService.getCustomers({ limit: 500 }).then(c => setCustomers(Array.isArray(c) ? c : [])).catch(() => {})
    setError(null)
    if (contract) {
      setTitle(contract.title)
      setCustomerId(contract.customer_id)
      setType(contract.contract_type)
      setStatus(contract.status)
      setStartDate(contract.start_date)
      setEndDate(contract.end_date ?? "")
      setBillingInterval(contract.billing_interval)
      setAutoRenew(contract.auto_renew)
      setNoticeDays(String(contract.notice_period_days))
      setIncludedHours(contract.included_hours ? String(contract.included_hours) : "")
      setItems(contract.items.length ? contract.items.map(i => ({ ...i })) : [{ ...EMPTY_ITEM }])
    } else {
      setTitle(""); setCustomerId(defaultCustomerId ?? ""); setType("maintenance"); setStatus("active")
      setStartDate(today()); setEndDate(""); setBillingInterval("monthly"); setAutoRenew(true)
      setNoticeDays("90"); setIncludedHours(""); setItems([{ ...EMPTY_ITEM }])
    }
  }, [open, contract, defaultCustomerId])

  function updateItem(idx: number, patch: Partial<ContractItem>) {
    setItems(prev => prev.map((it, i) => (i === idx ? { ...it, ...patch } : it)))
  }

  const validItems = items.filter(i => i.description.trim() && String(i.unit_price) !== "")
  const netPerPeriod = validItems.reduce(
    (s, i) => s + (parseFloat(String(i.quantity)) || 0) * (parseFloat(String(i.unit_price)) || 0),
    0,
  )

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim() || !customerId || validItems.length === 0) return
    setSaving(true)
    setError(null)
    const payloadItems = validItems.map(i => ({
      description: i.description.trim(),
      quantity: parseFloat(String(i.quantity)) || 1,
      unit: i.unit || "Monat",
      unit_price: parseFloat(String(i.unit_price)) || 0,
      tax_rate: parseFloat(String(i.tax_rate)) || 0,
      discount_percent: parseFloat(String(i.discount_percent ?? 0)) || 0,
      product_id: i.product_id ?? null,
    }))
    try {
      let saved: Contract
      if (editing && contract) {
        saved = await contractsService.update(contract.id, {
          title: title.trim(),
          contract_type: type,
          status,
          end_date: endDate || null,
          billing_interval: billingInterval,
          auto_renew: autoRenew,
          notice_period_days: parseInt(noticeDays, 10) || 0,
          included_hours: includedHours ? parseFloat(includedHours) : null,
          items: payloadItems,
        })
      } else {
        const payload: ContractCreate = {
          title: title.trim(),
          contract_type: type,
          customer_id: customerId,
          status,
          start_date: startDate,
          end_date: endDate || null,
          billing_interval: billingInterval,
          auto_renew: autoRenew,
          notice_period_days: parseInt(noticeDays, 10) || 0,
          included_hours: includedHours ? parseFloat(includedHours) : null,
          items: payloadItems,
        }
        saved = await contractsService.create(payload)
      }
      onSaved(saved)
      onClose()
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
      setError(typeof detail === "string" ? detail : "Speichern fehlgeschlagen.")
    } finally {
      setSaving(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={v => { if (!v) onClose() }}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{editing ? `Vertrag ${contract?.contract_number} bearbeiten` : "Neuer Vertrag"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="mt-2 space-y-5">
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="col-span-2 space-y-1.5">
              <Label htmlFor="c-title">Bezeichnung *</Label>
              <Input id="c-title" value={title} onChange={e => setTitle(e.target.value)} placeholder="z.B. Wartung Server & Netzwerk" required />
            </div>
            <div className="col-span-2 space-y-1.5">
              <Label>Kunde *</Label>
              <CustomerSelect customers={customers} value={customerId} onChange={setCustomerId} disabled={editing} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="c-type">Art</Label>
              <select id="c-type" value={type} onChange={e => setType(e.target.value as ContractType)} className={SELECT_CLS}>
                {Object.entries(CONTRACT_TYPE_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="c-status">Status</Label>
              <select id="c-status" value={status} onChange={e => setStatus(e.target.value as ContractStatus)} className={SELECT_CLS}>
                <option value="draft">Entwurf</option>
                <option value="active">Aktiv</option>
                <option value="paused">Pausiert</option>
              </select>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="c-interval">Abrechnung</Label>
              <select id="c-interval" value={billingInterval} onChange={e => setBillingInterval(e.target.value as BillingInterval)} className={SELECT_CLS}>
                {Object.entries(INTERVAL_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="c-hours">Inklusiv-Std./Zeitraum</Label>
              <Input id="c-hours" type="number" min="0" step="0.5" value={includedHours} onChange={e => setIncludedHours(e.target.value)} placeholder="—" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="c-start">Beginn *</Label>
              <Input id="c-start" type="date" value={startDate} onChange={e => setStartDate(e.target.value)} disabled={editing} required />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="c-end">Ende</Label>
              <Input id="c-end" type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="c-notice">Kündigungsfrist (Tage)</Label>
              <Input id="c-notice" type="number" min="0" value={noticeDays} onChange={e => setNoticeDays(e.target.value)} />
            </div>
            <div className="flex items-end pb-1.5">
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={autoRenew} onChange={e => setAutoRenew(e.target.checked)} className="h-4 w-4 accent-primary" />
                Verlängert sich automatisch
              </label>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>Positionen pro Abrechnungszeitraum *</Label>
              <span className="text-sm text-muted-foreground">Netto/Zeitraum: <span className="font-medium text-foreground">{fmtEur(netPerPeriod)}</span></span>
            </div>
            <div className="space-y-2">
              {items.map((it, idx) => (
                <div key={idx} className="grid grid-cols-12 gap-2">
                  <Input className="col-span-5" placeholder="Leistung" value={it.description} onChange={e => updateItem(idx, { description: e.target.value })} />
                  <Input className="col-span-1" type="number" min="0.01" step="0.01" value={it.quantity} onChange={e => updateItem(idx, { quantity: e.target.value })} title="Menge" />
                  <Input className="col-span-2" placeholder="Einheit" value={it.unit} onChange={e => updateItem(idx, { unit: e.target.value })} />
                  <Input className="col-span-2" type="number" min="0" step="0.01" placeholder="Preis netto" value={it.unit_price} onChange={e => updateItem(idx, { unit_price: e.target.value })} />
                  <select className={`col-span-1 ${SELECT_CLS}`} value={String(parseFloat(String(it.tax_rate)))} onChange={e => updateItem(idx, { tax_rate: e.target.value })} title="MwSt.">
                    <option value="19">19 %</option>
                    <option value="7">7 %</option>
                    <option value="0">0 %</option>
                  </select>
                  <Button type="button" variant="ghost" size="icon" className="col-span-1 text-muted-foreground" onClick={() => setItems(prev => prev.length > 1 ? prev.filter((_, i) => i !== idx) : prev)}>
                    <Trash2Icon className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
            <Button type="button" variant="outline" size="sm" onClick={() => setItems(prev => [...prev, { ...EMPTY_ITEM }])}>
              <PlusIcon className="mr-1 h-3.5 w-3.5" /> Position
            </Button>
          </div>

          {error && <p className="text-sm text-destructive">{error}</p>}

          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={onClose}>Abbrechen</Button>
            <Button type="submit" disabled={saving || !title.trim() || !customerId || validItems.length === 0}>
              {saving ? "Speichern…" : editing ? "Speichern" : "Vertrag anlegen"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
