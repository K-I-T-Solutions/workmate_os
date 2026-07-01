"use client"

import { useState, useEffect } from "react"
import { productsService } from "@/lib/products/service"
import type { Product, ProductCreate, ProductType } from "@/lib/products/types"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useAuth } from "@/components/providers/auth-provider"

type Tab = "products"
const TABS: { id: Tab; label: string }[] = [{ id: "products", label: "Produkte" }]

const PRODUCT_TYPE_LABELS: Record<ProductType, string> = {
  service: "Dienstleistung",
  product: "Produkt",
  license: "Lizenz",
  subscription: "Abo",
}

const TAX_RATES = [
  { value: 0, label: "0 %" },
  { value: 7, label: "7 %" },
  { value: 19, label: "19 %" },
]

function formatPrice(value: number | string, currency = "EUR"): string {
  const n = parseFloat(String(value) || "0")
  return new Intl.NumberFormat("de-DE", { style: "currency", currency }).format(n)
}

function StatusBadge({ active }: { active: boolean }) {
  return active ? (
    <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
      Aktiv
    </span>
  ) : (
    <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300">
      Inaktiv
    </span>
  )
}

function CreateDialog({
  open,
  onClose,
  onCreated,
}: {
  open: boolean
  onClose: () => void
  onCreated: (p: Product) => void
}) {
  const [name, setName] = useState("")
  const [sku, setSku] = useState("")
  const [description, setDescription] = useState("")
  const [productType, setProductType] = useState<ProductType>("service")
  const [unitPrice, setUnitPrice] = useState("")
  const [unit, setUnit] = useState("")
  const [taxRate, setTaxRate] = useState(19)
  const [saving, setSaving] = useState(false)

  function reset() {
    setName(""); setSku(""); setDescription(""); setProductType("service")
    setUnitPrice(""); setUnit(""); setTaxRate(19)
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) return
    setSaving(true)
    const payload: ProductCreate = {
      name: name.trim(),
      product_type: productType,
      unit_price: parseFloat(unitPrice || "0"),
      tax_rate: taxRate,
      ...(sku.trim() ? { sku: sku.trim() } : {}),
      ...(description.trim() ? { description: description.trim() } : {}),
      ...(unit.trim() ? { unit: unit.trim() } : {}),
    }
    const created = await productsService.create(payload).catch(() => null)
    setSaving(false)
    if (created) { onCreated(created); reset(); onClose() }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) { reset(); onClose() } }}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Neues Produkt</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2 space-y-1.5">
              <Label htmlFor="p-name">Name *</Label>
              <Input id="p-name" value={name} onChange={(e) => setName(e.target.value)} required />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="p-sku">SKU / Artikelnummer</Label>
              <Input id="p-sku" value={sku} onChange={(e) => setSku(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="p-type">Typ *</Label>
              <select
                id="p-type"
                value={productType}
                onChange={(e) => setProductType(e.target.value as ProductType)}
                className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              >
                {(Object.entries(PRODUCT_TYPE_LABELS) as [ProductType, string][]).map(([k, v]) => (
                  <option key={k} value={k}>{v}</option>
                ))}
              </select>
            </div>
            <div className="col-span-2 space-y-1.5">
              <Label htmlFor="p-desc">Beschreibung</Label>
              <Input id="p-desc" value={description} onChange={(e) => setDescription(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="p-price">Preis (netto) *</Label>
              <Input id="p-price" type="number" step="0.01" min="0" value={unitPrice} onChange={(e) => setUnitPrice(e.target.value)} required />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="p-unit">Einheit</Label>
              <Input id="p-unit" placeholder="z.B. Stunde, Stück" value={unit} onChange={(e) => setUnit(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="p-tax">Mehrwertsteuer</Label>
              <select
                id="p-tax"
                value={taxRate}
                onChange={(e) => setTaxRate(Number(e.target.value))}
                className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              >
                {TAX_RATES.map((r) => (
                  <option key={r.value} value={r.value}>{r.label}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => { reset(); onClose() }}>Abbrechen</Button>
            <Button type="submit" disabled={saving || !name.trim()}>
              {saving ? "Speichern…" : "Erstellen"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export function ProductsDashboard() {
  const { hasPermission } = useAuth()
  const [tab, setTab] = useState<Tab>("products")
  const [products, setProducts] = useState<Product[]>([])
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)

  function load(q?: string) {
    setLoading(true)
    productsService.list({ search: q || undefined }).then(setProducts).catch(() => {}).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  useEffect(() => {
    const t = setTimeout(() => load(search), 300)
    return () => clearTimeout(t)
  }, [search])

  async function handleDelete(id: string) {
    await productsService.remove(id).catch(() => {})
    setProducts((prev) => prev.filter((p) => p.id !== id))
  }

  function handleCreated(p: Product) {
    setProducts((prev) => [p, ...prev])
  }

  return (
    <div className="space-y-6 px-8 py-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Produkte &amp; Leistungen</h1>
        {hasPermission("backoffice.products.write") && (
          <Button onClick={() => setDialogOpen(true)}>Neues Produkt</Button>
        )}
      </div>

      <div className="flex gap-1 border-b">
        {TABS.map((t) => (
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
          </button>
        ))}
      </div>

      {tab === "products" && (
        <div className="space-y-4">
          <Input
            placeholder="Suche nach Name, SKU…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="max-w-sm"
          />

          {loading && <p className="text-sm text-muted-foreground">Lädt...</p>}

          {!loading && products.length === 0 && (
            <p className="py-8 text-center text-sm text-muted-foreground">Keine Einträge vorhanden.</p>
          )}

          {!loading && products.length > 0 && (
            <div className="rounded-lg border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="text-left px-4 py-3 font-medium text-muted-foreground">Name</th>
                    <th className="text-left px-4 py-3 font-medium text-muted-foreground">SKU</th>
                    <th className="text-left px-4 py-3 font-medium text-muted-foreground">Typ</th>
                    <th className="text-right px-4 py-3 font-medium text-muted-foreground">Preis</th>
                    <th className="text-right px-4 py-3 font-medium text-muted-foreground">MwSt.</th>
                    <th className="text-left px-4 py-3 font-medium text-muted-foreground">Einheit</th>
                    <th className="text-left px-4 py-3 font-medium text-muted-foreground">Status</th>
                    <th className="px-4 py-3" />
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {products.map((p) => (
                    <tr key={p.id} className="hover:bg-muted/30">
                      <td className="px-4 py-3 font-medium">{p.name}</td>
                      <td className="px-4 py-3 text-muted-foreground">{p.sku ?? "—"}</td>
                      <td className="px-4 py-3">{PRODUCT_TYPE_LABELS[p.product_type]}</td>
                      <td className="px-4 py-3 text-right">{formatPrice(p.unit_price, p.currency)}</td>
                      <td className="px-4 py-3 text-right">{parseFloat(String(p.tax_rate || "0"))} %</td>
                      <td className="px-4 py-3 text-muted-foreground">{p.unit ?? "—"}</td>
                      <td className="px-4 py-3"><StatusBadge active={p.is_active} /></td>
                      <td className="px-4 py-3 text-right">
                        {hasPermission("backoffice.products.delete") && (
                          <Button
                            size="sm"
                            variant="ghost"
                            className="text-destructive hover:text-destructive hover:bg-destructive/10"
                            onClick={() => handleDelete(p.id)}
                          >
                            Löschen
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      <CreateDialog open={dialogOpen} onClose={() => setDialogOpen(false)} onCreated={handleCreated} />
    </div>
  )
}
