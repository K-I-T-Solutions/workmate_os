"use client"

import { useEffect, useState } from "react"
import { financeService } from "@/lib/finance/service"
import type { BankAccount, BankTransaction, BankTransactionCreate, TransactionType, ReconciliationStatus } from "@/lib/finance/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { PlusIcon, Trash2Icon } from "lucide-react"

const TX_TYPES: { value: TransactionType; label: string }[] = [
  { value: "income", label: "Einnahme" },
  { value: "expense", label: "Ausgabe" },
  { value: "transfer", label: "Transfer" },
  { value: "fee", label: "Gebühr" },
  { value: "interest", label: "Zinsen" },
]
const RECON_STATUS: { value: ReconciliationStatus; label: string }[] = [
  { value: "unmatched", label: "Offen" },
  { value: "matched", label: "Zugeordnet" },
  { value: "confirmed", label: "Bestätigt" },
  { value: "ignored", label: "Ignoriert" },
]
const RECON_COLOR: Record<ReconciliationStatus, string> = {
  unmatched: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  matched: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  confirmed: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  ignored: "bg-muted text-muted-foreground",
}
const TX_COLOR: Record<TransactionType, string> = {
  income: "text-green-600",
  expense: "text-destructive",
  transfer: "text-blue-600",
  fee: "text-orange-600",
  interest: "text-purple-600",
}

function fmt(n: number) {
  return new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR" }).format(n)
}
function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("de-DE")
}

function NewTransactionForm({ accounts, onSave, onClose }: {
  accounts: BankAccount[]
  onSave: () => void
  onClose: () => void
}) {
  const [accountId, setAccountId] = useState(accounts[0]?.id ?? "")
  const [type, setType] = useState<TransactionType>("income")
  const [amount, setAmount] = useState("")
  const [purpose, setPurpose] = useState("")
  const [counterpartyName, setCounterpartyName] = useState("")
  const [counterpartyIban, setCounterpartyIban] = useState("")
  const [reference, setReference] = useState("")
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10))
  const [saving, setSaving] = useState(false)

  async function handleSave() {
    if (!accountId || !amount) return
    setSaving(true)
    try {
      const payload: BankTransactionCreate = {
        account_id: accountId,
        transaction_type: type,
        amount: parseFloat(amount),
        purpose: purpose.trim() || null,
        counterparty_name: counterpartyName.trim() || null,
        counterparty_iban: counterpartyIban.trim() || null,
        reference: reference.trim() || null,
        transaction_date: date,
      }
      await financeService.createTransaction(payload)
      onSave()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="grid gap-1.5">
          <Label>Konto *</Label>
          <Select value={accountId} onValueChange={v => v && setAccountId(v)}>
            <SelectTrigger>
              <span data-slot="select-value" className={accountId ? "" : "text-muted-foreground"}>
                {accountId ? (accounts.find(a => a.id === accountId)?.account_name ?? "…") : "Konto wählen"}
              </span>
            </SelectTrigger>
            <SelectContent>{accounts.map(a => <SelectItem key={a.id} value={a.id}>{a.account_name}</SelectItem>)}</SelectContent>
          </Select>
        </div>
        <div className="grid gap-1.5">
          <Label>Typ</Label>
          <Select value={type} onValueChange={v => v && setType(v as TransactionType)}>
            <SelectTrigger>
              <span data-slot="select-value">
                {TX_TYPES.find(t => t.value === type)?.label ?? type}
              </span>
            </SelectTrigger>
            <SelectContent>{TX_TYPES.map(t => <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>)}</SelectContent>
          </Select>
        </div>
        <div className="grid gap-1.5">
          <Label>Betrag (€) *</Label>
          <Input type="number" step="0.01" value={amount} onChange={e => setAmount(e.target.value)} placeholder="0,00" />
        </div>
        <div className="grid gap-1.5">
          <Label>Datum *</Label>
          <Input type="date" value={date} onChange={e => setDate(e.target.value)} />
        </div>
        <div className="grid gap-1.5">
          <Label>Zahlungspartner</Label>
          <Input value={counterpartyName} onChange={e => setCounterpartyName(e.target.value)} placeholder="Mustermann GmbH" />
        </div>
        <div className="grid gap-1.5">
          <Label>Partner-IBAN</Label>
          <Input value={counterpartyIban} onChange={e => setCounterpartyIban(e.target.value)} placeholder="DE00 …" />
        </div>
      </div>
      <div className="grid gap-1.5">
        <Label>Verwendungszweck</Label>
        <Input value={purpose} onChange={e => setPurpose(e.target.value)} placeholder="Rechnung 2024-001…" />
      </div>
      <div className="grid gap-1.5">
        <Label>Referenz</Label>
        <Input value={reference} onChange={e => setReference(e.target.value)} placeholder="Transaktions-ID der Bank…" />
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="outline" onClick={onClose}>Abbrechen</Button>
        <Button onClick={handleSave} disabled={saving || !accountId || !amount}>
          {saving ? "Buchen…" : "Buchung anlegen"}
        </Button>
      </div>
    </div>
  )
}

export function TransactionsTab({ accounts }: { accounts: BankAccount[] }) {
  const [transactions, setTransactions] = useState<BankTransaction[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [deleteId, setDeleteId] = useState<string | null>(null)
  const [filterAccount, setFilterAccount] = useState("all")
  const [filterStatus, setFilterStatus] = useState("all")

  async function load() {
    setLoading(true)
    try {
      const params: Record<string, string> = {}
      if (filterAccount !== "all") params.account_id = filterAccount
      if (filterStatus !== "all") params.reconciliation_status = filterStatus
      const data = await financeService.listTransactions(params as Parameters<typeof financeService.listTransactions>[0])
      setTransactions(data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [filterAccount, filterStatus])

  async function handleDelete() {
    if (!deleteId) return
    await financeService.deleteTransaction(deleteId)
    setDeleteId(null)
    load()
  }

  async function handleReconStatus(tx: BankTransaction, status: ReconciliationStatus) {
    await financeService.updateTransaction(tx.id, { reconciliation_status: status })
    load()
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="flex gap-2">
          <Select value={filterAccount} onValueChange={v => v && setFilterAccount(v)}>
            <SelectTrigger className="w-44"><SelectValue placeholder="Alle Konten" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Alle Konten</SelectItem>
              {accounts.map(a => <SelectItem key={a.id} value={a.id}>{a.account_name}</SelectItem>)}
            </SelectContent>
          </Select>
          <Select value={filterStatus} onValueChange={v => v && setFilterStatus(v)}>
            <SelectTrigger className="w-40"><SelectValue placeholder="Status" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Alle Status</SelectItem>
              {RECON_STATUS.map(s => <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
        <Button size="sm" onClick={() => setShowForm(true)}>
          <PlusIcon className="mr-2 h-4 w-4" />
          Buchung anlegen
        </Button>
      </div>

      {loading ? (
        <div className="py-12 text-center text-sm text-muted-foreground">Laden…</div>
      ) : transactions.length === 0 ? (
        <div className="rounded-lg border border-dashed p-12 text-center text-sm text-muted-foreground">
          Keine Buchungen gefunden.
        </div>
      ) : (
        <div className="rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/40">
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Datum</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Verwendungszweck</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Typ</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Status</th>
                <th className="px-4 py-3 text-right font-medium text-muted-foreground">Betrag</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {transactions.map(tx => (
                <tr key={tx.id} className="group border-b last:border-0 hover:bg-muted/30 transition-colors">
                  <td className="px-4 py-3 text-muted-foreground">{fmtDate(tx.transaction_date)}</td>
                  <td className="px-4 py-3">
                    <p className="font-medium">{tx.purpose ?? tx.counterparty_name ?? "–"}</p>
                    {tx.counterparty_name && tx.purpose && (
                      <p className="text-xs text-muted-foreground">{tx.counterparty_name}</p>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs font-medium ${TX_COLOR[tx.transaction_type]}`}>
                      {TX_TYPES.find(t => t.value === tx.transaction_type)?.label}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <Select value={tx.reconciliation_status} onValueChange={v => v && handleReconStatus(tx, v as ReconciliationStatus)}>
                      <SelectTrigger className="h-7 w-36 text-xs px-2">
                        <span data-slot="select-value" className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${RECON_COLOR[tx.reconciliation_status] ?? "bg-muted"}`}>
                          {RECON_STATUS.find(s => s.value === tx.reconciliation_status)?.label ?? tx.reconciliation_status}
                        </span>
                      </SelectTrigger>
                      <SelectContent>
                        {RECON_STATUS.map(s => (
                          <SelectItem key={s.value} value={s.value}>
                            <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${RECON_COLOR[s.value]}`}>
                              {s.label}
                            </span>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </td>
                  <td className={`px-4 py-3 text-right font-semibold tabular-nums ${TX_COLOR[tx.transaction_type]}`}>
                    {tx.transaction_type === "expense" || tx.transaction_type === "fee" ? "-" : "+"}
                    {fmt(Math.abs(parseFloat(tx.amount || "0")))}
                  </td>
                  <td className="px-4 py-3">
                    <Button
                      variant="ghost" size="icon"
                      className="h-7 w-7 opacity-0 group-hover:opacity-100 text-destructive hover:bg-destructive/10 transition-opacity"
                      onClick={() => setDeleteId(tx.id)}
                    >
                      <Trash2Icon className="h-3.5 w-3.5" />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Dialog open={showForm} onOpenChange={open => !open && setShowForm(false)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Neue Buchung</DialogTitle>
          </DialogHeader>
          <NewTransactionForm
            accounts={accounts}
            onSave={() => { setShowForm(false); load() }}
            onClose={() => setShowForm(false)}
          />
        </DialogContent>
      </Dialog>

      <AlertDialog open={!!deleteId} onOpenChange={open => !open && setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Buchung löschen?</AlertDialogTitle>
            <AlertDialogDescription>Diese Buchung wird unwiderruflich gelöscht.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">Löschen</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
