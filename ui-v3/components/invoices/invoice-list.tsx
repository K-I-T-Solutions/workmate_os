"use client"

import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { invoiceService } from "@/lib/invoices/service"
import type { Invoice, InvoiceStatus } from "@/lib/invoices/types"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table"
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select"
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Input } from "@/components/ui/input"
import { PlusIcon, Trash2Icon, FileTextIcon, DownloadIcon, SearchIcon } from "lucide-react"
import { useAuth } from "@/components/providers/auth-provider"

const STATUS_LABELS: Record<InvoiceStatus, string> = {
  draft: "Entwurf",
  sent: "Versendet",
  paid: "Bezahlt",
  partial: "Teilbezahlt",
  overdue: "Überfällig",
  cancelled: "Storniert",
}

const STATUS_VARIANT: Record<InvoiceStatus, "default" | "secondary" | "destructive" | "outline"> = {
  draft: "secondary",
  sent: "default",
  paid: "default",
  partial: "default",
  overdue: "destructive",
  cancelled: "outline",
}

const STATUS_COLOR: Record<InvoiceStatus, string> = {
  draft: "bg-muted text-muted-foreground",
  sent: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  paid: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  partial: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  overdue: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  cancelled: "bg-muted text-muted-foreground line-through",
}

const DOC_TYPE_LABELS: Record<string, string> = {
  invoice: "Rechnung",
  quote: "Angebot",
  credit_note: "Gutschrift",
  order_confirmation: "Auftragsbestätigung",
}

function fmt(amount: string | null | undefined) {
  if (!amount) return "–"
  return new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR" }).format(
    parseFloat(amount)
  )
}

function fmtDate(date: string | null | undefined) {
  if (!date) return "–"
  return new Date(date).toLocaleDateString("de-DE")
}

export function InvoiceList() {
  const router = useRouter()
  const { hasPermission } = useAuth()
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [deleteId, setDeleteId] = useState<string | null>(null)
  const [deleteNum, setDeleteNum] = useState<string>("")
  const [exporting, setExporting] = useState(false)
  const [search, setSearch] = useState("")

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await invoiceService.list({
        status: statusFilter === "all" ? undefined : statusFilter,
        limit: 100,
      })
      setInvoices(res.items)
      setTotal(res.total)
    } finally {
      setLoading(false)
    }
  }, [statusFilter])

  useEffect(() => { load() }, [load])

  async function handleDelete() {
    if (!deleteId) return
    await invoiceService.delete(deleteId)
    setDeleteId(null)
    load()
  }

  async function handleDatevExport() {
    setExporting(true)
    try {
      await invoiceService.exportDatevCsv(
        statusFilter !== "all" ? { status: statusFilter } : undefined
      )
    } finally {
      setExporting(false)
    }
  }

  const q = search.toLowerCase()
  const displayed = q
    ? invoices.filter(i =>
        i.invoice_number.toLowerCase().includes(q) ||
        i.customer.name.toLowerCase().includes(q)
      )
    : invoices

  const totalRevenue = invoices
    .filter(i => i.status === "paid" || i.status === "partial")
    .reduce((s, i) => s + parseFloat(i.total), 0)

  const totalOpen = invoices
    .filter(i => i.status === "sent" || i.status === "overdue")
    .reduce((s, i) => s + parseFloat(i.total), 0)

  return (
    <div className="space-y-6 px-8 py-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Rechnungen</h1>
          <p className="text-sm text-muted-foreground">{total} Dokumente</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleDatevExport} disabled={exporting}>
            <DownloadIcon className="mr-2 h-4 w-4" />
            {exporting ? "Exportiere…" : "DATEV-Export"}
          </Button>
          {hasPermission("backoffice.invoices.write") && (
            <Button onClick={() => router.push("/invoices/new")}>
              <PlusIcon className="mr-2 h-4 w-4" />
              Neu
            </Button>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { label: "Bezahlt", value: totalRevenue, color: "text-green-600" },
          { label: "Offen", value: totalOpen, color: "text-blue-600" },
          {
            label: "Überfällig",
            value: invoices.filter(i => i.status === "overdue").reduce((s, i) => s + parseFloat(i.total), 0),
            color: "text-red-600",
          },
          {
            label: "Entwürfe",
            value: invoices.filter(i => i.status === "draft").length,
            color: "text-muted-foreground",
            isCount: true,
          },
        ].map(s => (
          <div key={s.label} className="rounded-lg border bg-card p-4">
            <p className="text-xs text-muted-foreground">{s.label}</p>
            <p className={`mt-1 text-lg font-semibold ${s.color}`}>
              {s.isCount ? `${s.value} Stk.` : fmt(String(s.value))}
            </p>
          </div>
        ))}
      </div>

      {/* Filter */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-xs">
          <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
          <Input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Nummer oder Kunde…"
            className="pl-9"
          />
        </div>
        <Select value={statusFilter} onValueChange={v => v && setStatusFilter(v)}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle Status</SelectItem>
            {Object.entries(STATUS_LABELS).map(([v, l]) => (
              <SelectItem key={v} value={v}>{l}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        {search && (
          <span className="text-xs text-muted-foreground">
            {displayed.length} von {invoices.length}
          </span>
        )}
      </div>

      {/* Table */}
      {loading ? (
        <div className="flex items-center justify-center py-24 text-sm text-muted-foreground">
          Laden…
        </div>
      ) : displayed.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-3 py-24 text-muted-foreground">
          <FileTextIcon className="h-10 w-10 opacity-30" />
          <span className="text-sm">Keine Rechnungen gefunden.</span>
        </div>
      ) : (
        <div className="rounded-lg border overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nummer</TableHead>
                <TableHead>Typ</TableHead>
                <TableHead>Kunde</TableHead>
                <TableHead>Datum</TableHead>
                <TableHead>Fällig</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Betrag</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {displayed.map(inv => (
                <TableRow
                  key={inv.id}
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => router.push(`/invoices/${inv.id}`)}
                >
                  <TableCell className="font-mono text-sm">{inv.invoice_number}</TableCell>
                  <TableCell className="text-muted-foreground text-sm">
                    {DOC_TYPE_LABELS[inv.document_type] ?? inv.document_type}
                  </TableCell>
                  <TableCell>{inv.customer.name}</TableCell>
                  <TableCell className="text-sm">{fmtDate(inv.issued_date)}</TableCell>
                  <TableCell className="text-sm">{fmtDate(inv.due_date)}</TableCell>
                  <TableCell>
                    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLOR[inv.status]}`}>
                      {STATUS_LABELS[inv.status]}
                    </span>
                  </TableCell>
                  <TableCell className="text-right font-medium">{fmt(inv.total)}</TableCell>
                  <TableCell>
                    {hasPermission("backoffice.invoices.delete") && (
                      <button
                        onClick={e => {
                          e.stopPropagation()
                          setDeleteId(inv.id)
                          setDeleteNum(inv.invoice_number)
                        }}
                        className="p-1 rounded hover:bg-destructive/10 hover:text-destructive text-muted-foreground transition-colors"
                      >
                        <Trash2Icon className="h-4 w-4" />
                      </button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Delete dialog */}
      <AlertDialog open={!!deleteId} onOpenChange={open => !open && setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Rechnung löschen?</AlertDialogTitle>
            <AlertDialogDescription>
              {deleteNum} wird unwiderruflich gelöscht.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Löschen
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
