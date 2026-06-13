"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { usePageTitle } from "@/lib/page-title-context"
import { invoiceService } from "@/lib/invoices/service"
import type { Invoice, Payment, InvoiceStatus } from "@/lib/invoices/types"
import { Button } from "@/components/ui/button"
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select"
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table"
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog"
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { ArrowLeftIcon, PencilIcon, Trash2Icon, DownloadIcon, PlusIcon, MailIcon, CheckCircleIcon } from "lucide-react"

const STATUS_LABELS: Record<InvoiceStatus, string> = {
  draft: "Entwurf",
  sent: "Versendet",
  paid: "Bezahlt",
  partial: "Teilbezahlt",
  overdue: "Überfällig",
  cancelled: "Storniert",
}

const STATUS_COLOR: Record<InvoiceStatus, string> = {
  draft: "bg-muted text-muted-foreground",
  sent: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  paid: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  partial: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  overdue: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  cancelled: "bg-muted text-muted-foreground",
}

const DOC_TYPE_LABELS: Record<string, string> = {
  invoice: "Rechnung",
  quote: "Angebot",
  credit_note: "Gutschrift",
  order_confirmation: "Auftragsbestätigung",
}

const PAYMENT_METHOD_LABELS: Record<string, string> = {
  cash: "Bar",
  bank_transfer: "Überweisung",
  credit_card: "Kreditkarte",
  debit_card: "EC-Karte",
  paypal: "PayPal",
  sepa: "SEPA",
  other: "Sonstige",
}

function fmt(amount: string | null | undefined) {
  if (!amount) return "–"
  return new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR" }).format(parseFloat(amount))
}

function fmtDate(date: string | null | undefined) {
  if (!date) return "–"
  return new Date(date).toLocaleDateString("de-DE")
}

function PaymentModal({
  invoiceId,
  onSaved,
  onClose,
}: {
  invoiceId: string
  onSaved: () => void
  onClose: () => void
}) {
  const [amount, setAmount] = useState("")
  const [date, setDate] = useState(new Date().toISOString().substring(0, 10))
  const [method, setMethod] = useState("bank_transfer")
  const [reference, setReference] = useState("")
  const [saving, setSaving] = useState(false)

  async function handleSave() {
    if (!amount) return
    setSaving(true)
    try {
      await invoiceService.addPayment(invoiceId, {
        amount,
        payment_date: date || undefined,
        method,
        reference: reference || undefined,
      })
      onSaved()
      onClose()
    } finally {
      setSaving(false)
    }
  }

  return (
    <Dialog open onOpenChange={open => !open && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Zahlung erfassen</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-2">
          <div className="grid gap-1.5">
            <Label>Betrag (EUR)*</Label>
            <Input type="number" min="0" step="0.01" value={amount} onChange={e => setAmount(e.target.value)} placeholder="0,00" />
          </div>
          <div className="grid gap-1.5">
            <Label>Datum</Label>
            <Input type="date" value={date} onChange={e => setDate(e.target.value)} />
          </div>
          <div className="grid gap-1.5">
            <Label>Zahlungsart</Label>
            <Select value={method} onValueChange={v => v && setMethod(v)}>
              <SelectTrigger>
                <span data-slot="select-value">
                  {PAYMENT_METHOD_LABELS[method] ?? method}
                </span>
              </SelectTrigger>
              <SelectContent>
                {Object.entries(PAYMENT_METHOD_LABELS).map(([v, l]) => (
                  <SelectItem key={v} value={v}>{l}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-1.5">
            <Label>Referenz</Label>
            <Input value={reference} onChange={e => setReference(e.target.value)} placeholder="Verwendungszweck o. ä." />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Abbrechen</Button>
          <Button onClick={handleSave} disabled={saving || !amount}>
            {saving ? "Speichern…" : "Speichern"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

function SendEmailModal({
  invoiceId,
  defaultEmail,
  onSent,
  onClose,
}: {
  invoiceId: string
  defaultEmail: string | null
  onSent: () => void
  onClose: () => void
}) {
  const [toEmail, setToEmail] = useState(defaultEmail ?? "")
  const [ccEmail, setCcEmail] = useState("")
  const [message, setMessage] = useState("")
  const [sending, setSending] = useState(false)
  const [sent, setSent] = useState(false)

  async function handleSend() {
    if (!toEmail) return
    setSending(true)
    try {
      await invoiceService.sendEmail(invoiceId, {
        to_email: toEmail.trim(),
        cc_email: ccEmail.trim() || undefined,
        message: message.trim() || undefined,
      })
      setSent(true)
      setTimeout(() => { onSent(); onClose() }, 1200)
    } finally {
      setSending(false)
    }
  }

  return (
    <Dialog open onOpenChange={open => !open && onClose()}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Rechnung per E-Mail senden</DialogTitle>
        </DialogHeader>
        {sent ? (
          <div className="flex flex-col items-center gap-3 py-8 text-center">
            <CheckCircleIcon className="h-10 w-10 text-green-500" />
            <p className="text-sm font-medium text-foreground">Rechnung erfolgreich gesendet!</p>
          </div>
        ) : (
          <div className="space-y-4 py-2">
            <div className="grid gap-1.5">
              <Label>An *</Label>
              <Input
                type="email"
                value={toEmail}
                onChange={e => setToEmail(e.target.value)}
                placeholder="empfaenger@beispiel.de"
              />
            </div>
            <div className="grid gap-1.5">
              <Label>CC</Label>
              <Input
                type="email"
                value={ccEmail}
                onChange={e => setCcEmail(e.target.value)}
                placeholder="kopie@beispiel.de"
              />
            </div>
            <div className="grid gap-1.5">
              <Label>Nachricht (optional)</Label>
              <Textarea
                value={message}
                onChange={e => setMessage(e.target.value)}
                placeholder="Sehr geehrte Damen und Herren, anbei erhalten Sie…"
                rows={4}
              />
            </div>
          </div>
        )}
        {!sent && (
          <DialogFooter>
            <Button variant="outline" onClick={onClose}>Abbrechen</Button>
            <Button onClick={handleSend} disabled={sending || !toEmail}>
              <MailIcon className="mr-2 h-4 w-4" />
              {sending ? "Senden…" : "Senden"}
            </Button>
          </DialogFooter>
        )}
      </DialogContent>
    </Dialog>
  )
}

export function InvoiceDetail({ id }: { id: string }) {
  const router = useRouter()
  const [invoice, setInvoice] = useState<Invoice | null>(null)
  const [payments, setPayments] = useState<Payment[]>([])
  const [loading, setLoading] = useState(true)
  const [showPaymentModal, setShowPaymentModal] = useState(false)
  const [showEmailModal, setShowEmailModal] = useState(false)
  const [showDelete, setShowDelete] = useState(false)
  const [updatingStatus, setUpdatingStatus] = useState(false)
  usePageTitle(invoice?.invoice_number)

  async function load() {
    setLoading(true)
    try {
      const [inv, pmts] = await Promise.all([
        invoiceService.get(id),
        invoiceService.getPayments(id),
      ])
      setInvoice(inv)
      setPayments(pmts)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [id])

  async function handleStatusChange(status: string) {
    if (!invoice) return
    setUpdatingStatus(true)
    try {
      const updated = await invoiceService.updateStatus(id, status as InvoiceStatus)
      setInvoice(updated)
    } finally {
      setUpdatingStatus(false)
    }
  }

  async function handleDelete() {
    await invoiceService.delete(id)
    router.push("/invoices")
  }

  if (loading) {
    return <div className="flex items-center justify-center py-24 text-sm text-muted-foreground">Laden…</div>
  }
  if (!invoice) {
    return <div className="flex items-center justify-center py-24 text-sm text-destructive">Rechnung nicht gefunden.</div>
  }

  const paidTotal = payments.reduce((s, p) => s + parseFloat(p.amount), 0)
  const remaining = parseFloat(invoice.total) - paidTotal

  return (
    <div className="space-y-6 px-8 py-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.push("/invoices")}>
          <ArrowLeftIcon className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <h1 className="text-xl font-semibold">{invoice.invoice_number}</h1>
          <p className="text-sm text-muted-foreground">
            {DOC_TYPE_LABELS[invoice.document_type]} · {invoice.customer.name}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select
            value={invoice.status}
            onValueChange={v => v && handleStatusChange(v)}
            disabled={updatingStatus}
          >
            <SelectTrigger className="w-40">
              <span data-slot="select-value" className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLOR[invoice.status]}`}>
                {STATUS_LABELS[invoice.status]}
              </span>
            </SelectTrigger>
            <SelectContent>
              {Object.entries(STATUS_LABELS).map(([v, l]) => (
                <SelectItem key={v} value={v}>{l}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowEmailModal(true)}
            title="Per E-Mail senden"
          >
            <MailIcon className="mr-2 h-4 w-4" />
            Senden
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={() => invoiceService.downloadPdf(id, `${invoice.invoice_number}.pdf`)}
            title="PDF herunterladen"
          >
            <DownloadIcon className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="icon" onClick={() => router.push(`/invoices/${id}/edit`)}>
            <PencilIcon className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="text-destructive hover:text-destructive hover:bg-destructive/10"
            onClick={() => setShowDelete(true)}
          >
            <Trash2Icon className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Meta */}
      <div className="grid grid-cols-2 gap-4 rounded-lg border bg-card p-4 sm:grid-cols-4">
        <div>
          <p className="text-xs text-muted-foreground">Rechnungsdatum</p>
          <p className="mt-0.5 text-sm font-medium">{fmtDate(invoice.issued_date)}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Fälligkeitsdatum</p>
          <p className="mt-0.5 text-sm font-medium">{fmtDate(invoice.due_date)}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Netto</p>
          <p className="mt-0.5 text-sm font-medium">{fmt(invoice.subtotal)}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">MwSt.</p>
          <p className="mt-0.5 text-sm font-medium">{fmt(invoice.tax_amount)}</p>
        </div>
      </div>

      {/* Line items */}
      <div>
        <h2 className="mb-2 text-sm font-medium text-muted-foreground">Positionen</h2>
        <div className="rounded-lg border overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-8">#</TableHead>
                <TableHead>Beschreibung</TableHead>
                <TableHead className="text-right">Menge</TableHead>
                <TableHead className="text-right">Einheit</TableHead>
                <TableHead className="text-right">Einzelpreis</TableHead>
                <TableHead className="text-right">Rabatt</TableHead>
                <TableHead className="text-right">MwSt.</TableHead>
                <TableHead className="text-right">Gesamt</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {invoice.line_items.map(li => (
                <TableRow key={li.id}>
                  <TableCell className="text-muted-foreground text-sm">{li.position}</TableCell>
                  <TableCell>{li.description}</TableCell>
                  <TableCell className="text-right text-sm">{li.quantity}</TableCell>
                  <TableCell className="text-right text-sm text-muted-foreground">{li.unit}</TableCell>
                  <TableCell className="text-right text-sm">{fmt(li.unit_price)}</TableCell>
                  <TableCell className="text-right text-sm">
                    {parseFloat(li.discount_percent) > 0 ? `${li.discount_percent}%` : "–"}
                  </TableCell>
                  <TableCell className="text-right text-sm">{li.tax_rate}%</TableCell>
                  <TableCell className="text-right font-medium">{fmt(li.total)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        <div className="mt-3 flex justify-end">
          <div className="w-64 space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Netto</span>
              <span>{fmt(invoice.subtotal)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">MwSt.</span>
              <span>{fmt(invoice.tax_amount)}</span>
            </div>
            <div className="flex justify-between border-t pt-1 font-semibold">
              <span>Gesamt</span>
              <span>{fmt(invoice.total)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Notes / Terms */}
      {(invoice.notes || invoice.terms) && (
        <div className="grid gap-4 sm:grid-cols-2">
          {invoice.notes && (
            <div>
              <p className="mb-1 text-xs font-medium text-muted-foreground">Anmerkungen</p>
              <p className="rounded-lg border bg-muted/30 p-3 text-sm whitespace-pre-wrap">{invoice.notes}</p>
            </div>
          )}
          {invoice.terms && (
            <div>
              <p className="mb-1 text-xs font-medium text-muted-foreground">Zahlungsbedingungen</p>
              <p className="rounded-lg border bg-muted/30 p-3 text-sm whitespace-pre-wrap">{invoice.terms}</p>
            </div>
          )}
        </div>
      )}

      {/* Payments */}
      <div>
        <div className="mb-2 flex items-center justify-between">
          <h2 className="text-sm font-medium text-muted-foreground">
            Zahlungen
            {payments.length > 0 && (
              <span className="ml-2 text-foreground">
                {fmt(String(paidTotal))} von {fmt(invoice.total)}
                {remaining > 0 && (
                  <span className="text-orange-600"> · {fmt(String(remaining))} offen</span>
                )}
              </span>
            )}
          </h2>
          <Button variant="outline" size="sm" onClick={() => setShowPaymentModal(true)}>
            <PlusIcon className="mr-1.5 h-3.5 w-3.5" />
            Zahlung erfassen
          </Button>
        </div>
        {payments.length === 0 ? (
          <p className="text-sm text-muted-foreground">Noch keine Zahlungen erfasst.</p>
        ) : (
          <div className="rounded-lg border overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Datum</TableHead>
                  <TableHead>Zahlungsart</TableHead>
                  <TableHead>Referenz</TableHead>
                  <TableHead className="text-right">Betrag</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {payments.map(p => (
                  <TableRow key={p.id}>
                    <TableCell className="text-sm">{fmtDate(p.payment_date)}</TableCell>
                    <TableCell className="text-sm">{PAYMENT_METHOD_LABELS[p.method] ?? p.method}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">{p.reference ?? "–"}</TableCell>
                    <TableCell className="text-right font-medium">{fmt(p.amount)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </div>

      {showPaymentModal && (
        <PaymentModal
          invoiceId={id}
          onSaved={load}
          onClose={() => setShowPaymentModal(false)}
        />
      )}

      {showEmailModal && (
        <SendEmailModal
          invoiceId={id}
          defaultEmail={invoice.customer.email}
          onSent={() => handleStatusChange("sent")}
          onClose={() => setShowEmailModal(false)}
        />
      )}

      <AlertDialog open={showDelete} onOpenChange={setShowDelete}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Rechnung löschen?</AlertDialogTitle>
            <AlertDialogDescription>
              {invoice.invoice_number} wird unwiderruflich gelöscht.
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
