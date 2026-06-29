"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { invoiceService } from "@/lib/invoices/service"
import { crmService } from "@/lib/crm/service"
import { productsService } from "@/lib/products/service"
import type { Invoice, InvoiceLineItemInput, DocumentType } from "@/lib/invoices/types"
import type { Customer } from "@/lib/crm/types"
import type { Product } from "@/lib/products/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select"
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table"
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
} from "@/components/ui/dialog"
import { ArrowLeftIcon, PlusIcon, Trash2Icon, BookOpenIcon } from "lucide-react"

const DOC_TYPES: { value: DocumentType; label: string }[] = [
  { value: "invoice", label: "Rechnung" },
  { value: "quote", label: "Angebot" },
  { value: "credit_note", label: "Gutschrift" },
  { value: "order_confirmation", label: "Auftragsbestätigung" },
]

function uid() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36)
}

type LineItemRow = Omit<InvoiceLineItemInput, "position"> & { _key: string }

function emptyLine(): LineItemRow {
  return {
    _key: uid(),
    description: "",
    quantity: "1",
    unit: "Std.",
    unit_price: "0",
    tax_rate: "19",
    discount_percent: "0",
  }
}

function calcLine(row: LineItemRow) {
  const qty = parseFloat(row.quantity) || 0
  const price = parseFloat(row.unit_price) || 0
  const disc = parseFloat(row.discount_percent) || 0
  const tax = parseFloat(row.tax_rate) || 0
  const subtotal = qty * price
  const discountAmt = subtotal * (disc / 100)
  const net = subtotal - discountAmt
  const taxAmt = net * (tax / 100)
  return { net, taxAmt, total: net + taxAmt }
}

function toPayloadLines(rows: LineItemRow[]): InvoiceLineItemInput[] {
  return rows.map((r, i) => ({
    position: i + 1,
    description: r.description,
    quantity: r.quantity,
    unit: r.unit,
    unit_price: r.unit_price,
    tax_rate: r.tax_rate,
    discount_percent: r.discount_percent,
  }))
}

interface Props {
  initial?: Invoice
  invoiceId?: string
}

function fmt(n: number) {
  return new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR" }).format(n)
}

function ProductPickerDialog({
  open,
  onOpenChange,
  onSelect,
}: {
  open: boolean
  onOpenChange: (v: boolean) => void
  onSelect: (p: Product) => void
}) {
  const [products, setProducts] = useState<Product[]>([])
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!open) return
    setLoading(true)
    productsService.list({ limit: 500 })
      .then(setProducts)
      .finally(() => setLoading(false))
  }, [open])

  const filtered = products.filter(
    p => p.is_active && (
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      (p.description ?? "").toLowerCase().includes(search.toLowerCase()) ||
      (p.sku ?? "").toLowerCase().includes(search.toLowerCase())
    )
  )

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Produkt aus Katalog wählen</DialogTitle>
        </DialogHeader>
        <Input
          placeholder="Suchen…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="mt-1"
          autoFocus
        />
        <div className="mt-2 max-h-80 overflow-y-auto space-y-1">
          {loading ? (
            <p className="py-4 text-center text-sm text-muted-foreground">Laden…</p>
          ) : filtered.length === 0 ? (
            <p className="py-4 text-center text-sm text-muted-foreground">Keine Produkte gefunden</p>
          ) : (
            filtered.map(p => (
              <button
                key={p.id}
                onClick={() => { onSelect(p); onOpenChange(false) }}
                className="w-full text-left rounded-md px-3 py-2.5 hover:bg-accent transition-colors"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">{p.name}</p>
                    {p.description && (
                      <p className="text-xs text-muted-foreground truncate">{p.description}</p>
                    )}
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-sm font-medium">
                      {new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR" }).format(
                        typeof p.unit_price === "string" ? parseFloat(p.unit_price) : p.unit_price
                      )}
                    </p>
                    <p className="text-xs text-muted-foreground">{p.unit}</p>
                  </div>
                </div>
              </button>
            ))
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}

export function InvoiceForm({ initial, invoiceId }: Props) {
  const router = useRouter()
  const isEdit = !!invoiceId
  const [customers, setCustomers] = useState<Customer[]>([])
  const [pickerOpen, setPickerOpen] = useState(false)

  const [customerId, setCustomerId] = useState(initial?.customer_id ?? "")
  const [docType, setDocType] = useState<DocumentType>(initial?.document_type ?? "invoice")
  const [issuedDate, setIssuedDate] = useState(
    initial?.issued_date?.substring(0, 10) ?? new Date().toISOString().substring(0, 10)
  )
  const [dueDate, setDueDate] = useState(initial?.due_date?.substring(0, 10) ?? "")
  const [notes, setNotes] = useState(initial?.notes ?? "")
  const [terms, setTerms] = useState(initial?.terms ?? "")
  const [lines, setLines] = useState<LineItemRow[]>(
    initial?.line_items.length
      ? initial.line_items.map(li => ({
          _key: uid(),
          description: li.description,
          quantity: li.quantity,
          unit: li.unit,
          unit_price: li.unit_price,
          tax_rate: li.tax_rate,
          discount_percent: li.discount_percent,
        }))
      : [emptyLine()]
  )
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    crmService.getCustomers({ limit: 500 }).then(setCustomers)
  }, [])

  function updateLine(key: string, field: keyof Omit<LineItemRow, "_key">, value: string) {
    setLines(prev => prev.map(l => l._key === key ? { ...l, [field]: value } : l))
  }

  function addLine() {
    setLines(prev => [...prev, emptyLine()])
  }

  function addProductLine(p: Product) {
    setLines(prev => [...prev, {
      _key: uid(),
      description: p.name + (p.description ? ` — ${p.description}` : ""),
      quantity: "1",
      unit: p.unit ?? "Stk.",
      unit_price: String(p.unit_price),
      tax_rate: String(p.default_tax_rate ?? "19"),
      discount_percent: "0",
    }])
  }

  function removeLine(key: string) {
    setLines(prev => prev.filter(l => l._key !== key))
  }

  const totals = lines.reduce(
    (acc, l) => {
      const c = calcLine(l)
      return { net: acc.net + c.net, tax: acc.tax + c.taxAmt, total: acc.total + c.total }
    },
    { net: 0, tax: 0, total: 0 }
  )

  async function handleSave() {
    if (!customerId) return
    setSaving(true)
    try {
      const payload = {
        customer_id: customerId,
        document_type: docType,
        issued_date: issuedDate || undefined,
        due_date: dueDate || undefined,
        notes: notes || undefined,
        terms: terms || undefined,
        line_items: toPayloadLines(lines),
      }
      let saved: Invoice
      if (isEdit && invoiceId) {
        saved = await invoiceService.update(invoiceId, payload)
      } else {
        saved = await invoiceService.create(payload)
      }
      router.push(`/invoices/${saved.id}`)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-6 px-8 py-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ArrowLeftIcon className="h-4 w-4" />
        </Button>
        <h1 className="text-xl font-semibold">
          {isEdit ? "Rechnung bearbeiten" : "Neue Rechnung"}
        </h1>
      </div>

      {/* Allgemein */}
      <div className="rounded-lg border bg-card p-4">
        <h2 className="mb-4 text-sm font-medium text-muted-foreground">Allgemein</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div className="lg:col-span-2 grid gap-1.5">
            <Label>Kunde *</Label>
            <Select value={customerId} onValueChange={v => v && setCustomerId(v)}>
              <SelectTrigger>
                <span data-slot="select-value" className={customerId ? "" : "text-muted-foreground"}>
                  {customerId ? (customers.find(c => c.id === customerId)?.name ?? "…") : "Kunde auswählen…"}
                </span>
              </SelectTrigger>
              <SelectContent>
                {customers.map(c => (
                  <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-1.5">
            <Label>Dokumenttyp</Label>
            <Select value={docType} onValueChange={v => setDocType(v as DocumentType)}>
              <SelectTrigger>
                <span data-slot="select-value">
                  {DOC_TYPES.find(t => t.value === docType)?.label ?? docType}
                </span>
              </SelectTrigger>
              <SelectContent>
                {DOC_TYPES.map(t => (
                  <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-1.5">
            <Label>Rechnungsdatum</Label>
            <Input type="date" value={issuedDate} onChange={e => setIssuedDate(e.target.value)} />
          </div>
          <div className="grid gap-1.5">
            <Label>Fälligkeitsdatum</Label>
            <Input type="date" value={dueDate} onChange={e => setDueDate(e.target.value)} />
          </div>
        </div>
      </div>

      {/* Positionen */}
      <div className="rounded-lg border bg-card">
        <div className="flex items-center justify-between px-4 py-3 border-b">
          <h2 className="text-sm font-medium text-muted-foreground">Positionen</h2>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => setPickerOpen(true)}>
              <BookOpenIcon className="mr-1.5 h-3.5 w-3.5" />
              Aus Katalog
            </Button>
            <Button variant="outline" size="sm" onClick={addLine}>
              <PlusIcon className="mr-1.5 h-3.5 w-3.5" />
              Position hinzufügen
            </Button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="min-w-[240px]">Beschreibung</TableHead>
                <TableHead className="w-24 text-right">Menge</TableHead>
                <TableHead className="w-24 text-right">Einheit</TableHead>
                <TableHead className="w-28 text-right">Preis (€)</TableHead>
                <TableHead className="w-20 text-right">Rabatt %</TableHead>
                <TableHead className="w-20 text-right">MwSt. %</TableHead>
                <TableHead className="w-28 text-right">Gesamt</TableHead>
                <TableHead className="w-8" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {lines.map(line => {
                const c = calcLine(line)
                return (
                  <TableRow key={line._key}>
                    <TableCell>
                      <Input
                        value={line.description}
                        onChange={e => updateLine(line._key, "description", e.target.value)}
                        placeholder="Leistungsbeschreibung"
                        className="border-0 shadow-none focus-visible:ring-0 px-0"
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        type="number" min="0" step="0.01"
                        value={line.quantity}
                        onChange={e => updateLine(line._key, "quantity", e.target.value)}
                        className="border-0 shadow-none focus-visible:ring-0 text-right px-0"
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        value={line.unit}
                        onChange={e => updateLine(line._key, "unit", e.target.value)}
                        className="border-0 shadow-none focus-visible:ring-0 text-right px-0"
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        type="number" min="0" step="0.01"
                        value={line.unit_price}
                        onChange={e => updateLine(line._key, "unit_price", e.target.value)}
                        className="border-0 shadow-none focus-visible:ring-0 text-right px-0"
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        type="number" min="0" max="100" step="0.1"
                        value={line.discount_percent}
                        onChange={e => updateLine(line._key, "discount_percent", e.target.value)}
                        className="border-0 shadow-none focus-visible:ring-0 text-right px-0"
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        type="number" min="0" max="100" step="0.1"
                        value={line.tax_rate}
                        onChange={e => updateLine(line._key, "tax_rate", e.target.value)}
                        className="border-0 shadow-none focus-visible:ring-0 text-right px-0"
                      />
                    </TableCell>
                    <TableCell className="text-right font-medium text-sm">
                      {fmt(c.total)}
                    </TableCell>
                    <TableCell>
                      <button
                        onClick={() => removeLine(line._key)}
                        className="p-1 rounded hover:bg-destructive/10 hover:text-destructive text-muted-foreground"
                      >
                        <Trash2Icon className="h-4 w-4" />
                      </button>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </div>
        <div className="flex justify-end p-4 border-t">
          <div className="w-56 space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Netto</span>
              <span>{fmt(totals.net)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">MwSt.</span>
              <span>{fmt(totals.tax)}</span>
            </div>
            <div className="flex justify-between border-t pt-1 font-semibold">
              <span>Gesamt</span>
              <span>{fmt(totals.total)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Notizen / Bedingungen */}
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="grid gap-1.5">
          <Label>Anmerkungen</Label>
          <Textarea
            value={notes}
            onChange={e => setNotes(e.target.value)}
            rows={4}
            placeholder="Interne oder externe Notizen…"
          />
        </div>
        <div className="grid gap-1.5">
          <Label>Zahlungsbedingungen</Label>
          <Textarea
            value={terms}
            onChange={e => setTerms(e.target.value)}
            rows={4}
            placeholder="z. B. Zahlbar innerhalb 14 Tagen…"
          />
        </div>
      </div>

      {/* Aktionen */}
      <div className="flex justify-end gap-3">
        <Button variant="outline" onClick={() => router.back()}>Abbrechen</Button>
        <Button onClick={handleSave} disabled={saving || !customerId || lines.length === 0}>
          {saving ? "Speichern…" : isEdit ? "Änderungen speichern" : "Rechnung erstellen"}
        </Button>
      </div>

      <ProductPickerDialog
        open={pickerOpen}
        onOpenChange={setPickerOpen}
        onSelect={addProductLine}
      />
    </div>
  )
}
