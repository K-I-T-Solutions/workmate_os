"use client"

import { useState } from "react"
import { financeService } from "@/lib/finance/service"
import type { BankAccount, BankAccountCreate, AccountType } from "@/lib/finance/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { PlusIcon, Trash2Icon, PencilIcon } from "lucide-react"

const ACCOUNT_TYPES: { value: AccountType; label: string }[] = [
  { value: "checking", label: "Girokonto" },
  { value: "savings", label: "Sparkonto" },
  { value: "credit", label: "Kreditkarte" },
  { value: "cash", label: "Bargeld" },
]

function fmt(n: number) {
  return new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR" }).format(n)
}

function AccountForm({ initial, onSave, onClose }: {
  initial?: BankAccount
  onSave: () => void
  onClose: () => void
}) {
  const [accountName, setAccountName] = useState(initial?.account_name ?? "")
  const [iban, setIban] = useState(initial?.iban ?? "")
  const [bic, setBic] = useState(initial?.bic ?? "")
  const [bankName, setBankName] = useState(initial?.bank_name ?? "")
  const [accountHolder, setAccountHolder] = useState(initial?.account_holder ?? "")
  const [type, setType] = useState<AccountType>(initial?.account_type ?? "checking")
  const [balance, setBalance] = useState(initial ? String(parseFloat(initial.balance || "0")) : "0")
  const [note, setNote] = useState(initial?.note ?? "")
  const [saving, setSaving] = useState(false)

  async function handleSave() {
    if (!accountName.trim()) return
    setSaving(true)
    try {
      const payload: BankAccountCreate = {
        account_name: accountName.trim(),
        account_type: type,
        iban: iban.trim() || null,
        bic: bic.trim() || null,
        bank_name: bankName.trim() || null,
        account_holder: accountHolder.trim() || null,
        note: note.trim() || null,
        balance: parseFloat(balance) || 0,
      }
      if (initial) {
        await financeService.updateAccount(initial.id, payload)
      } else {
        await financeService.createAccount(payload)
      }
      onSave()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-1.5">
        <Label>Kontobezeichnung *</Label>
        <Input value={accountName} onChange={e => setAccountName(e.target.value)} placeholder="Geschäftskonto N26" />
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="grid gap-1.5">
          <Label>Kontoart</Label>
          <Select value={type} onValueChange={v => v && setType(v as AccountType)}>
            <SelectTrigger>
              <span data-slot="select-value">
                {ACCOUNT_TYPES.find(t => t.value === type)?.label ?? type}
              </span>
            </SelectTrigger>
            <SelectContent>{ACCOUNT_TYPES.map(t => <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>)}</SelectContent>
          </Select>
        </div>
        <div className="grid gap-1.5">
          <Label>Anfangssaldo (€)</Label>
          <Input type="number" step="0.01" value={balance} onChange={e => setBalance(e.target.value)} />
        </div>
        <div className="grid gap-1.5">
          <Label>IBAN</Label>
          <Input value={iban} onChange={e => setIban(e.target.value)} placeholder="DE00 0000 0000 0000 0000 00" />
        </div>
        <div className="grid gap-1.5">
          <Label>BIC</Label>
          <Input value={bic} onChange={e => setBic(e.target.value)} placeholder="SSKMDEMMXXX" />
        </div>
        <div className="grid gap-1.5">
          <Label>Bank</Label>
          <Input value={bankName} onChange={e => setBankName(e.target.value)} placeholder="Sparkasse München" />
        </div>
        <div className="grid gap-1.5">
          <Label>Kontoinhaber</Label>
          <Input value={accountHolder} onChange={e => setAccountHolder(e.target.value)} placeholder="Max Mustermann" />
        </div>
      </div>
      <div className="grid gap-1.5">
        <Label>Notiz</Label>
        <Input value={note} onChange={e => setNote(e.target.value)} placeholder="Interne Anmerkungen…" />
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="outline" onClick={onClose}>Abbrechen</Button>
        <Button onClick={handleSave} disabled={saving || !accountName.trim()}>
          {saving ? "Speichern…" : initial ? "Speichern" : "Konto anlegen"}
        </Button>
      </div>
    </div>
  )
}

export function AccountsTab({ accounts, onRefresh }: { accounts: BankAccount[]; onRefresh: () => void }) {
  const [showForm, setShowForm] = useState(false)
  const [editAccount, setEditAccount] = useState<BankAccount | null>(null)
  const [deleteId, setDeleteId] = useState<string | null>(null)

  async function handleDelete() {
    if (!deleteId) return
    await financeService.deleteAccount(deleteId)
    setDeleteId(null)
    onRefresh()
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button size="sm" onClick={() => { setEditAccount(null); setShowForm(true) }}>
          <PlusIcon className="mr-2 h-4 w-4" />
          Konto hinzufügen
        </Button>
      </div>

      {accounts.length === 0 ? (
        <div className="rounded-lg border border-dashed p-12 text-center text-sm text-muted-foreground">
          Noch keine Konten angelegt.
        </div>
      ) : (
        <div className="space-y-2">
          {accounts.map(acc => (
            <div key={acc.id} className="group flex items-center justify-between rounded-lg border bg-card px-4 py-3">
              <div>
                <p className="font-medium">{acc.account_name}</p>
                <p className="text-xs text-muted-foreground">
                  {ACCOUNT_TYPES.find(t => t.value === acc.account_type)?.label}
                  {acc.bank_name && ` · ${acc.bank_name}`}
                  {acc.iban && ` · ${acc.iban}`}
                </p>
              </div>
              <div className="flex items-center gap-3">
                {!acc.is_active && (
                  <span className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">Inaktiv</span>
                )}
                <p className={`text-lg font-semibold tabular-nums ${parseFloat(acc.balance) < 0 ? "text-destructive" : ""}`}>
                  {fmt(parseFloat(acc.balance || "0"))}
                </p>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button variant="ghost" size="icon" onClick={() => { setEditAccount(acc); setShowForm(true) }}>
                    <PencilIcon className="h-3.5 w-3.5" />
                  </Button>
                  <Button variant="ghost" size="icon" className="text-destructive hover:bg-destructive/10"
                    onClick={() => setDeleteId(acc.id)}>
                    <Trash2Icon className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Dialog open={showForm} onOpenChange={open => !open && setShowForm(false)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editAccount ? "Konto bearbeiten" : "Neues Konto"}</DialogTitle>
          </DialogHeader>
          <AccountForm
            initial={editAccount ?? undefined}
            onSave={() => { setShowForm(false); onRefresh() }}
            onClose={() => setShowForm(false)}
          />
        </DialogContent>
      </Dialog>

      <AlertDialog open={!!deleteId} onOpenChange={open => !open && setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Konto löschen?</AlertDialogTitle>
            <AlertDialogDescription>Das Konto wird unwiderruflich gelöscht.</AlertDialogDescription>
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
