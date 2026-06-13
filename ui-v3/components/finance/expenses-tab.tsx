"use client"

import { useEffect, useState } from "react"
import { financeService } from "@/lib/finance/service"
import type { Expense, ExpenseCreate, ExpenseCategory } from "@/lib/finance/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { PlusIcon, Trash2Icon, PencilIcon, CheckCircle2Icon, CircleIcon } from "lucide-react"

const CATEGORIES: { value: ExpenseCategory; label: string }[] = [
  { value: "travel", label: "Reise" },
  { value: "material", label: "Material" },
  { value: "software", label: "Software" },
  { value: "hardware", label: "Hardware" },
  { value: "consulting", label: "Beratung" },
  { value: "marketing", label: "Marketing" },
  { value: "office", label: "Büro" },
  { value: "training", label: "Training" },
  { value: "other", label: "Sonstiges" },
]

function fmt(n: number) {
  return new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR" }).format(n)
}
function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("de-DE")
}

function ExpenseForm({ initial, onSave, onClose }: {
  initial?: Expense
  onSave: () => void
  onClose: () => void
}) {
  const [title, setTitle] = useState(initial?.title ?? "")
  const [amount, setAmount] = useState(initial ? String(parseFloat(initial.amount || "0")) : "")
  const [category, setCategory] = useState<ExpenseCategory>(initial?.category ?? "other")
  const [description, setDescription] = useState(initial?.description ?? "")
  const [note, setNote] = useState(initial?.note ?? "")
  const [billable, setBillable] = useState(initial?.is_billable ?? true)
  const [saving, setSaving] = useState(false)

  async function handleSave() {
    if (!title.trim() || !amount) return
    setSaving(true)
    try {
      const payload: ExpenseCreate = {
        title: title.trim(),
        amount: parseFloat(amount),
        category,
        description: description.trim(),
        note: note.trim() || null,
        is_billable: billable,
      }
      if (initial) {
        await financeService.updateExpense(initial.id, payload)
      } else {
        await financeService.createExpense(payload)
      }
      onSave()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-1.5">
        <Label>Titel *</Label>
        <Input value={title} onChange={e => setTitle(e.target.value)} placeholder="Bahnticket München…" />
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="grid gap-1.5">
          <Label>Betrag (€) *</Label>
          <Input type="number" step="0.01" value={amount} onChange={e => setAmount(e.target.value)} placeholder="0,00" />
        </div>
        <div className="grid gap-1.5">
          <Label>Kategorie</Label>
          <Select value={category} onValueChange={v => v && setCategory(v as ExpenseCategory)}>
            <SelectTrigger>
              <span data-slot="select-value">
                {CATEGORIES.find(c => c.value === category)?.label ?? category}
              </span>
            </SelectTrigger>
            <SelectContent>{CATEGORIES.map(c => <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>)}</SelectContent>
          </Select>
        </div>
      </div>
      <div className="grid gap-1.5">
        <Label>Beschreibung</Label>
        <Textarea value={description} onChange={e => setDescription(e.target.value)} rows={3} placeholder="Details zur Ausgabe…" />
      </div>
      <div className="grid gap-1.5">
        <Label>Notiz</Label>
        <Input value={note} onChange={e => setNote(e.target.value)} placeholder="Interne Anmerkungen…" />
      </div>
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => setBillable(v => !v)}
          className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
        >
          {billable
            ? <CheckCircle2Icon className="h-4 w-4 text-primary" />
            : <CircleIcon className="h-4 w-4" />}
          An Kunden weiterberechenbar
        </button>
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="outline" onClick={onClose}>Abbrechen</Button>
        <Button onClick={handleSave} disabled={saving || !title.trim() || !amount}>
          {saving ? "Speichern…" : initial ? "Speichern" : "Ausgabe anlegen"}
        </Button>
      </div>
    </div>
  )
}

export function ExpensesTab({ onKpiRefresh }: { onKpiRefresh: () => void }) {
  const [expenses, setExpenses] = useState<Expense[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editExpense, setEditExpense] = useState<Expense | null>(null)
  const [deleteId, setDeleteId] = useState<string | null>(null)
  const [filterCategory, setFilterCategory] = useState("all")
  const [search, setSearch] = useState("")

  async function load() {
    setLoading(true)
    try {
      const params: Record<string, string> = {}
      if (filterCategory !== "all") params.category = filterCategory
      if (search.trim()) params.title = search.trim()
      const data = await financeService.listExpenses(params as Parameters<typeof financeService.listExpenses>[0])
      setExpenses(data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [filterCategory, search])

  async function handleDelete() {
    if (!deleteId) return
    await financeService.deleteExpense(deleteId)
    setDeleteId(null)
    load()
    onKpiRefresh()
  }

  const total = expenses.reduce((s, e) => s + parseFloat(e.amount || "0"), 0)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="flex gap-2">
          <Input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Suchen…"
            className="w-48"
          />
          <Select value={filterCategory} onValueChange={v => v && setFilterCategory(v)}>
            <SelectTrigger className="w-44"><SelectValue placeholder="Kategorie" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Alle Kategorien</SelectItem>
              {CATEGORIES.map(c => <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
        <div className="flex items-center gap-4">
          {expenses.length > 0 && (
            <span className="text-sm text-muted-foreground">
              Gesamt: <span className="font-semibold text-foreground">{fmt(total)}</span>
            </span>
          )}
          <Button size="sm" onClick={() => { setEditExpense(null); setShowForm(true) }}>
            <PlusIcon className="mr-2 h-4 w-4" />
            Ausgabe anlegen
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="py-12 text-center text-sm text-muted-foreground">Laden…</div>
      ) : expenses.length === 0 ? (
        <div className="rounded-lg border border-dashed p-12 text-center text-sm text-muted-foreground">
          Keine Ausgaben gefunden.
        </div>
      ) : (
        <div className="rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/40">
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Erstellt</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Titel</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Kategorie</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Berechenbar</th>
                <th className="px-4 py-3 text-right font-medium text-muted-foreground">Betrag</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {expenses.map(exp => (
                <tr key={exp.id} className="group border-b last:border-0 hover:bg-muted/30 transition-colors">
                  <td className="px-4 py-3 text-muted-foreground">{fmtDate(exp.created_at)}</td>
                  <td className="px-4 py-3">
                    <p className="font-medium">{exp.title}</p>
                    {exp.description && <p className="text-xs text-muted-foreground truncate max-w-48">{exp.description}</p>}
                  </td>
                  <td className="px-4 py-3">
                    <span className="rounded-full bg-muted px-2 py-0.5 text-xs">
                      {CATEGORIES.find(c => c.value === exp.category)?.label ?? exp.category}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {exp.is_billable
                      ? <CheckCircle2Icon className="h-4 w-4 text-green-600" />
                      : <CircleIcon className="h-4 w-4 text-muted-foreground" />}
                  </td>
                  <td className="px-4 py-3 text-right font-semibold tabular-nums text-destructive">
                    {fmt(parseFloat(exp.amount || "0"))}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Button
                        variant="ghost" size="icon" className="h-7 w-7"
                        onClick={() => { setEditExpense(exp); setShowForm(true) }}
                      >
                        <PencilIcon className="h-3.5 w-3.5" />
                      </Button>
                      <Button
                        variant="ghost" size="icon" className="h-7 w-7 text-destructive hover:bg-destructive/10"
                        onClick={() => setDeleteId(exp.id)}
                      >
                        <Trash2Icon className="h-3.5 w-3.5" />
                      </Button>
                    </div>
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
            <DialogTitle>{editExpense ? "Ausgabe bearbeiten" : "Neue Ausgabe"}</DialogTitle>
          </DialogHeader>
          <ExpenseForm
            initial={editExpense ?? undefined}
            onSave={() => { setShowForm(false); load(); onKpiRefresh() }}
            onClose={() => setShowForm(false)}
          />
        </DialogContent>
      </Dialog>

      <AlertDialog open={!!deleteId} onOpenChange={open => !open && setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Ausgabe löschen?</AlertDialogTitle>
            <AlertDialogDescription>Diese Ausgabe wird unwiderruflich gelöscht.</AlertDialogDescription>
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
