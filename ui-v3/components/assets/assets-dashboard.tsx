"use client"

import { useEffect, useState } from "react"
import { assetsService } from "@/lib/assets/service"
import { crmService } from "@/lib/crm/service"
import type { AssetPayload, AssetStatus, AssetType, CustomerAsset, ExpiringItem, LicensePayload, LicenseType, SoftwareLicense } from "@/lib/assets/types"
import type { Customer } from "@/lib/crm/types"
import { fmtDate } from "@/lib/contracts/labels"
import { CustomerSelect } from "@/components/crm/customer-select"
import { useAuth } from "@/components/providers/auth-provider"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { AlertTriangleIcon } from "lucide-react"

type Tab = "devices" | "licenses" | "expiring"

const SELECT_CLS = "flex h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm dark:bg-input/30"

export const ASSET_TYPE_LABELS: Record<AssetType, string> = {
  workstation: "Arbeitsplatz-PC", laptop: "Notebook", server: "Server", network: "Netzwerk",
  storage: "Speicher/NAS", printer: "Drucker", phone: "Telefon", mobile: "Smartphone/Tablet",
  peripheral: "Peripherie", other: "Sonstiges",
}
const ASSET_STATUS_LABELS: Record<AssetStatus, string> = {
  active: "In Betrieb", in_repair: "In Reparatur", in_stock: "Auf Lager", retired: "Ausgemustert",
}
const LICENSE_TYPE_LABELS: Record<LicenseType, string> = {
  subscription: "Abo", perpetual: "Kauflizenz", volume: "Volumenlizenz", oem: "OEM",
}

function daysUntil(d: string | null) {
  if (!d) return null
  return Math.ceil((new Date(d).getTime() - Date.now()) / 86_400_000)
}

function ExpiryBadge({ date }: { date: string | null }) {
  const days = daysUntil(date)
  if (date === null || days === null) return <span className="text-muted-foreground">—</span>
  const cls = days < 0 ? "text-destructive" : days <= 30 ? "text-orange-600 dark:text-orange-400" : "text-muted-foreground"
  return <span className={cls}>{fmtDate(date)}{days < 0 ? " (abgelaufen)" : days <= 30 ? ` (${days} T.)` : ""}</span>
}

function Field({ label, children, wide }: { label: string; children: React.ReactNode; wide?: boolean }) {
  return (
    <div className={`space-y-1.5 ${wide ? "col-span-2" : ""}`}>
      <Label>{label}</Label>
      {children}
    </div>
  )
}

function errorText(err: unknown) {
  const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
  return typeof detail === "string" ? detail : "Speichern fehlgeschlagen."
}

// ─── Gerät anlegen/bearbeiten ────────────────────────────────

function AssetDialog({
  open, onClose, onSaved, asset, customers,
}: {
  open: boolean; onClose: () => void; onSaved: () => void; asset: CustomerAsset | null; customers: Customer[]
}) {
  const [form, setForm] = useState<AssetPayload>({})
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!open) return
    setError(null)
    setForm(asset ? { ...asset } : { asset_type: "workstation", status: "active" })
  }, [open, asset])

  const set = (k: keyof AssetPayload) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value || null }))

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.name || !form.customer_id) return
    setSaving(true)
    setError(null)
    try {
      const { customer_id, ...rest } = form
      if (asset) await assetsService.update(asset.id, rest)
      else await assetsService.create({ ...rest, customer_id })
      onSaved()
      onClose()
    } catch (err) {
      setError(errorText(err))
    } finally {
      setSaving(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={v => { if (!v) onClose() }}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader><DialogTitle>{asset ? `${asset.asset_tag} bearbeiten` : "Neues Gerät"}</DialogTitle></DialogHeader>
        <form onSubmit={handleSubmit} className="mt-2 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Field label="Bezeichnung *"><Input value={form.name ?? ""} onChange={set("name")} required placeholder="z.B. Empfang-PC" /></Field>
            <Field label="Kunde *">
              <CustomerSelect customers={customers} value={form.customer_id ?? ""} onChange={v => setForm(f => ({ ...f, customer_id: v }))} disabled={!!asset} />
            </Field>
            <Field label="Typ">
              <select value={form.asset_type ?? "workstation"} onChange={set("asset_type")} className={SELECT_CLS}>
                {Object.entries(ASSET_TYPE_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </Field>
            <Field label="Status">
              <select value={form.status ?? "active"} onChange={set("status")} className={SELECT_CLS}>
                {Object.entries(ASSET_STATUS_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </Field>
            <Field label="Hersteller"><Input value={form.manufacturer ?? ""} onChange={set("manufacturer")} /></Field>
            <Field label="Modell"><Input value={form.model ?? ""} onChange={set("model")} /></Field>
            <Field label="Seriennummer"><Input value={form.serial_number ?? ""} onChange={set("serial_number")} /></Field>
            <Field label="Standort"><Input value={form.location ?? ""} onChange={set("location")} /></Field>
            <Field label="Hostname"><Input value={form.hostname ?? ""} onChange={set("hostname")} /></Field>
            <Field label="IP-Adresse"><Input value={form.ip_address ?? ""} onChange={set("ip_address")} /></Field>
            <Field label="Betriebssystem"><Input value={form.operating_system ?? ""} onChange={set("operating_system")} /></Field>
            <Field label="MAC-Adresse"><Input value={form.mac_address ?? ""} onChange={set("mac_address")} /></Field>
            <Field label="Kaufdatum"><Input type="date" value={form.purchase_date ?? ""} onChange={set("purchase_date")} /></Field>
            <Field label="Garantie bis"><Input type="date" value={form.warranty_until ?? ""} onChange={set("warranty_until")} /></Field>
            <Field label="Notizen" wide><Textarea rows={2} value={form.notes ?? ""} onChange={set("notes")} /></Field>
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={onClose}>Abbrechen</Button>
            <Button type="submit" disabled={saving || !form.name || !form.customer_id}>{saving ? "Speichern…" : "Speichern"}</Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// ─── Lizenz anlegen/bearbeiten ───────────────────────────────

function LicenseDialog({
  open, onClose, onSaved, license, customers,
}: {
  open: boolean; onClose: () => void; onSaved: () => void; license: SoftwareLicense | null; customers: Customer[]
}) {
  const [form, setForm] = useState<LicensePayload>({})
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!open) return
    setError(null)
    setForm(license ? { ...license } : { license_type: "subscription", seats: 1, auto_renew: false })
  }, [open, license])

  const set = (k: keyof LicensePayload) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value || null }))

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.product_name || !form.customer_id) return
    setSaving(true)
    setError(null)
    try {
      const { customer_id, ...rest } = form
      const payload = { ...rest, seats: Number(form.seats) || 1, seats_used: form.seats_used ? Number(form.seats_used) : null }
      if (license) await assetsService.updateLicense(license.id, payload)
      else await assetsService.createLicense({ ...payload, customer_id })
      onSaved()
      onClose()
    } catch (err) {
      setError(errorText(err))
    } finally {
      setSaving(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={v => { if (!v) onClose() }}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader><DialogTitle>{license ? "Lizenz bearbeiten" : "Neue Lizenz"}</DialogTitle></DialogHeader>
        <form onSubmit={handleSubmit} className="mt-2 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Field label="Produkt *"><Input value={form.product_name ?? ""} onChange={set("product_name")} required placeholder="z.B. Microsoft 365 Business Standard" /></Field>
            <Field label="Kunde *">
              <CustomerSelect customers={customers} value={form.customer_id ?? ""} onChange={v => setForm(f => ({ ...f, customer_id: v }))} disabled={!!license} />
            </Field>
            <Field label="Hersteller"><Input value={form.vendor ?? ""} onChange={set("vendor")} /></Field>
            <Field label="Lizenzart">
              <select value={form.license_type ?? "subscription"} onChange={set("license_type")} className={SELECT_CLS}>
                {Object.entries(LICENSE_TYPE_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </Field>
            <Field label="Plätze"><Input type="number" min="1" value={form.seats ?? 1} onChange={set("seats")} /></Field>
            <Field label="Davon genutzt"><Input type="number" min="0" value={form.seats_used ?? ""} onChange={set("seats_used")} /></Field>
            <Field label="Gültig ab"><Input type="date" value={form.valid_from ?? ""} onChange={set("valid_from")} /></Field>
            <Field label="Gültig bis"><Input type="date" value={form.valid_until ?? ""} onChange={set("valid_until")} /></Field>
            <Field label="Einkauf / Zeitraum (€)"><Input type="number" min="0" step="0.01" value={form.cost_price ?? ""} onChange={set("cost_price")} /></Field>
            <Field label="Verkauf / Zeitraum (€)"><Input type="number" min="0" step="0.01" value={form.sale_price ?? ""} onChange={set("sale_price")} /></Field>
            <Field label="Lizenzschlüssel" wide><Input value={form.license_key ?? ""} onChange={set("license_key")} className="font-mono" autoComplete="off" /></Field>
            <div className="col-span-2">
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={!!form.auto_renew} onChange={e => setForm(f => ({ ...f, auto_renew: e.target.checked }))} className="h-4 w-4 accent-primary" />
                Verlängert sich automatisch
              </label>
            </div>
            <Field label="Notizen" wide><Textarea rows={2} value={form.notes ?? ""} onChange={set("notes")} /></Field>
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={onClose}>Abbrechen</Button>
            <Button type="submit" disabled={saving || !form.product_name || !form.customer_id}>{saving ? "Speichern…" : "Speichern"}</Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// ─── Übersicht ───────────────────────────────────────────────

export function AssetsDashboard() {
  const { hasPermission } = useAuth()
  const [tab, setTab] = useState<Tab>("devices")
  const [customers, setCustomers] = useState<Customer[]>([])
  const [customerFilter, setCustomerFilter] = useState("")
  const [search, setSearch] = useState("")
  const [assets, setAssets] = useState<CustomerAsset[]>([])
  const [licenses, setLicenses] = useState<SoftwareLicense[]>([])
  const [expiring, setExpiring] = useState<ExpiringItem[]>([])
  const [loading, setLoading] = useState(true)
  const [assetDialog, setAssetDialog] = useState<{ open: boolean; asset: CustomerAsset | null }>({ open: false, asset: null })
  const [licenseDialog, setLicenseDialog] = useState<{ open: boolean; license: SoftwareLicense | null }>({ open: false, license: null })

  const canWrite = hasPermission("backoffice.assets.write")

  useEffect(() => {
    crmService.getCustomers({ limit: 500 }).then(c => setCustomers(Array.isArray(c) ? c : [])).catch(() => {})
    assetsService.expiring(60).then(setExpiring).catch(() => {})
  }, [])

  function load() {
    setLoading(true)
    const params = { customer_id: customerFilter || undefined, search: search || undefined, limit: 200 }
    const req = tab === "licenses"
      ? assetsService.listLicenses(params).then(r => setLicenses(r.items))
      : tab === "devices"
        ? assetsService.list(params).then(r => setAssets(r.items))
        : assetsService.expiring(60).then(setExpiring)
    req.catch(() => {}).finally(() => setLoading(false))
  }

  useEffect(() => {
    const t = setTimeout(load, search ? 300 : 0)
    return () => clearTimeout(t)
  }, [tab, customerFilter, search])

  const TABS: { id: Tab; label: string }[] = [
    { id: "devices", label: "Geräte" },
    { id: "licenses", label: "Lizenzen" },
    { id: "expiring", label: `Läuft ab${expiring.length ? ` (${expiring.length})` : ""}` },
  ]

  return (
    <div className="space-y-6 px-8 py-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Kunden-Assets</h1>
        {canWrite && tab === "devices" && <Button onClick={() => setAssetDialog({ open: true, asset: null })}>Neues Gerät</Button>}
        {canWrite && tab === "licenses" && <Button onClick={() => setLicenseDialog({ open: true, license: null })}>Neue Lizenz</Button>}
      </div>

      <div className="flex gap-1 border-b">
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`-mb-px border-b-2 px-4 py-2 text-sm font-medium transition-colors ${tab === t.id ? "border-primary text-foreground" : "border-transparent text-muted-foreground hover:text-foreground"}`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab !== "expiring" && (
        <div className="flex flex-wrap items-center gap-3">
          <Input placeholder={tab === "devices" ? "Suche nach Name, Seriennr., Hostname, IP…" : "Suche nach Produkt, Hersteller…"} value={search} onChange={e => setSearch(e.target.value)} className="max-w-sm" />
          <div className="w-64">
            <CustomerSelect customers={[{ id: "", name: "Alle Kunden" } as Customer, ...customers]} value={customerFilter} onChange={setCustomerFilter} placeholder="Alle Kunden" />
          </div>
        </div>
      )}

      {loading && <p className="text-sm text-muted-foreground">Lädt…</p>}

      {!loading && tab === "devices" && (
        assets.length === 0 ? <p className="py-8 text-center text-sm text-muted-foreground">Keine Geräte erfasst.</p> : (
          <div className="overflow-hidden rounded-lg border">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>
                  {["Tag", "Gerät", "Kunde", "Seriennr. / Host", "Vertrag", "Garantie", "Status"].map(h => (
                    <th key={h} className="px-4 py-3 text-left font-medium text-muted-foreground">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y">
                {assets.map(a => (
                  <tr key={a.id} className={canWrite ? "cursor-pointer hover:bg-muted/30" : ""} onClick={() => canWrite && setAssetDialog({ open: true, asset: a })}>
                    <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{a.asset_tag}</td>
                    <td className="px-4 py-3">
                      <p className="font-medium">{a.name}</p>
                      <p className="text-xs text-muted-foreground">{ASSET_TYPE_LABELS[a.asset_type]}{a.manufacturer ? ` · ${a.manufacturer} ${a.model ?? ""}` : ""}</p>
                    </td>
                    <td className="px-4 py-3">{a.customer_name}</td>
                    <td className="px-4 py-3 text-muted-foreground">
                      <p>{a.serial_number ?? "—"}</p>
                      {(a.hostname || a.ip_address) && <p className="text-xs">{[a.hostname, a.ip_address].filter(Boolean).join(" · ")}</p>}
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{a.contract_number ?? "—"}</td>
                    <td className="px-4 py-3"><ExpiryBadge date={a.warranty_until} /></td>
                    <td className="px-4 py-3 text-muted-foreground">{ASSET_STATUS_LABELS[a.status]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}

      {!loading && tab === "licenses" && (
        licenses.length === 0 ? <p className="py-8 text-center text-sm text-muted-foreground">Keine Lizenzen erfasst.</p> : (
          <div className="overflow-hidden rounded-lg border">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>
                  {["Produkt", "Kunde", "Art", "Plätze", "Gültig bis", "Verlängerung"].map(h => (
                    <th key={h} className="px-4 py-3 text-left font-medium text-muted-foreground">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y">
                {licenses.map(l => (
                  <tr key={l.id} className={canWrite ? "cursor-pointer hover:bg-muted/30" : ""} onClick={() => canWrite && setLicenseDialog({ open: true, license: l })}>
                    <td className="px-4 py-3">
                      <p className="font-medium">{l.product_name}</p>
                      <p className="text-xs text-muted-foreground">{l.vendor ?? ""}{l.asset_name ? ` · ${l.asset_name}` : ""}</p>
                    </td>
                    <td className="px-4 py-3">{l.customer_name}</td>
                    <td className="px-4 py-3 text-muted-foreground">{LICENSE_TYPE_LABELS[l.license_type]}</td>
                    <td className="px-4 py-3 tabular-nums">{l.seats_used != null ? `${l.seats_used} / ${l.seats}` : l.seats}</td>
                    <td className="px-4 py-3"><ExpiryBadge date={l.valid_until} /></td>
                    <td className="px-4 py-3 text-muted-foreground">{l.auto_renew ? "automatisch" : "manuell"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}

      {!loading && tab === "expiring" && (
        expiring.length === 0 ? <p className="py-8 text-center text-sm text-muted-foreground">In den nächsten 60 Tagen läuft nichts ab.</p> : (
          <div className="overflow-hidden rounded-lg border">
            <table className="w-full text-sm">
              <tbody className="divide-y bg-card">
                {expiring.map(i => (
                  <tr key={`${i.kind}-${i.id}`}>
                    <td className="px-4 py-3">
                      <AlertTriangleIcon className={`h-4 w-4 ${i.days_left <= 14 ? "text-destructive" : "text-orange-500"}`} />
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">{i.kind === "warranty" ? "Garantie" : "Lizenz"}</td>
                    <td className="px-4 py-3 font-medium">{i.name}</td>
                    <td className="px-4 py-3">{i.customer_name}</td>
                    <td className="px-4 py-3 tabular-nums">{fmtDate(i.expires_on)}</td>
                    <td className="px-4 py-3 text-muted-foreground">noch {i.days_left} Tage{i.auto_renew ? " · verlängert automatisch" : ""}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}

      <AssetDialog open={assetDialog.open} asset={assetDialog.asset} customers={customers} onClose={() => setAssetDialog({ open: false, asset: null })} onSaved={load} />
      <LicenseDialog open={licenseDialog.open} license={licenseDialog.license} customers={customers} onClose={() => setLicenseDialog({ open: false, license: null })} onSaved={load} />
    </div>
  )
}
