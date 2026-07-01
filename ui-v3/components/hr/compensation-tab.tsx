"use client"

import { useState } from "react"
import { hrService } from "@/lib/hr/service"
import { apiClient } from "@/lib/api/client"
import type { SalaryRecord, Benefit } from "@/lib/hr/types"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { EmployeeSelect } from "./employee-select"
import { useAuth } from "@/components/providers/auth-provider"

// ---------- lokale Helpers ----------

async function postSalary(employeeId: string, payload: object) {
  const { data } = await apiClient.post(`/api/hr/compensation/employees/${employeeId}/salary`, payload)
  return data
}

async function postBonus(employeeId: string, payload: object) {
  const { data } = await apiClient.post(`/api/hr/compensation/employees/${employeeId}/bonuses`, payload)
  return data
}

async function postBenefit(employeeId: string, payload: object) {
  const { data } = await apiClient.post(`/api/hr/compensation/employees/${employeeId}/benefits`, payload)
  return data
}

async function getBonuses(employeeId: string) {
  const { data } = await apiClient.get(`/api/hr/compensation/employees/${employeeId}/bonuses`)
  return Array.isArray(data) ? data : ((data as { items?: unknown[] }).items ?? [])
}

// ---------- Dialog: Gehalt anlegen ----------

function AddSalaryDialog({
  open,
  employeeId,
  onClose,
  onSaved,
}: {
  open: boolean
  employeeId: string
  onClose: () => void
  onSaved: () => void
}) {
  const [amount, setAmount] = useState("")
  const [effectiveDate, setEffectiveDate] = useState("")
  const [compType, setCompType] = useState("base_salary")
  const [notes, setNotes] = useState("")
  const [saving, setSaving] = useState(false)

  function reset() { setAmount(""); setEffectiveDate(""); setCompType("base_salary"); setNotes("") }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!amount || !effectiveDate) return
    setSaving(true)
    await postSalary(employeeId, {
      amount: parseFloat(amount),
      effective_date: effectiveDate,
      compensation_type: compType,
      ...(notes.trim() ? { notes: notes.trim() } : {}),
    }).catch(() => null)
    setSaving(false)
    reset()
    onClose()
    onSaved()
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) { reset(); onClose() } }}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Gehalt anlegen</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div className="space-y-1.5">
            <Label htmlFor="sal-amount">Betrag (€) *</Label>
            <Input id="sal-amount" type="number" min="0" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} required />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="sal-date">Gültig ab *</Label>
            <Input id="sal-date" type="date" value={effectiveDate} onChange={(e) => setEffectiveDate(e.target.value)} required />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="sal-type">Art</Label>
            <select
              id="sal-type"
              value={compType}
              onChange={(e) => setCompType(e.target.value)}
              className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              <option value="base_salary">Grundgehalt</option>
              <option value="bonus">Bonus</option>
              <option value="allowance">Zulage</option>
            </select>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="sal-notes">Notizen</Label>
            <textarea
              id="sal-notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => { reset(); onClose() }}>Abbrechen</Button>
            <Button type="submit" disabled={saving || !amount || !effectiveDate}>
              {saving ? "Speichern…" : "Erstellen"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// ---------- Dialog: Bonus anlegen ----------

function AddBonusDialog({
  open,
  employeeId,
  onClose,
  onSaved,
}: {
  open: boolean
  employeeId: string
  onClose: () => void
  onSaved: () => void
}) {
  const [amount, setAmount] = useState("")
  const [bonusType, setBonusType] = useState("Jahresbonus")
  const [paymentDate, setPaymentDate] = useState("")
  const [description, setDescription] = useState("")
  const [saving, setSaving] = useState(false)

  function reset() { setAmount(""); setBonusType("Jahresbonus"); setPaymentDate(""); setDescription("") }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!amount || !paymentDate) return
    setSaving(true)
    await postBonus(employeeId, {
      amount: parseFloat(amount),
      bonus_type: bonusType,
      payment_date: paymentDate,
      ...(description.trim() ? { description: description.trim() } : {}),
    }).catch(() => null)
    setSaving(false)
    reset()
    onClose()
    onSaved()
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) { reset(); onClose() } }}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Bonus anlegen</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div className="space-y-1.5">
            <Label htmlFor="bon-amount">Betrag (€) *</Label>
            <Input id="bon-amount" type="number" min="0" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} required />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="bon-type">Art</Label>
            <select
              id="bon-type"
              value={bonusType}
              onChange={(e) => setBonusType(e.target.value)}
              className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              <option value="Jahresbonus">Jahresbonus</option>
              <option value="Projektbonus">Projektbonus</option>
              <option value="Sonderzahlung">Sonderzahlung</option>
            </select>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="bon-date">Auszahlungsdatum *</Label>
            <Input id="bon-date" type="date" value={paymentDate} onChange={(e) => setPaymentDate(e.target.value)} required />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="bon-desc">Beschreibung</Label>
            <textarea
              id="bon-desc"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => { reset(); onClose() }}>Abbrechen</Button>
            <Button type="submit" disabled={saving || !amount || !paymentDate}>
              {saving ? "Speichern…" : "Erstellen"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// ---------- Dialog: Benefit anlegen ----------

function AddBenefitDialog({
  open,
  employeeId,
  onClose,
  onSaved,
}: {
  open: boolean
  employeeId: string
  onClose: () => void
  onSaved: () => void
}) {
  const [benefitType, setBenefitType] = useState("health_insurance")
  const [description, setDescription] = useState("")
  const [value, setValue] = useState("")
  const [startDate, setStartDate] = useState("")
  const [saving, setSaving] = useState(false)

  function reset() { setBenefitType("health_insurance"); setDescription(""); setValue(""); setStartDate("") }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!startDate) return
    setSaving(true)
    await postBenefit(employeeId, {
      benefit_type: benefitType,
      start_date: startDate,
      ...(description.trim() ? { description: description.trim() } : {}),
      ...(value ? { value: parseFloat(value) } : {}),
    }).catch(() => null)
    setSaving(false)
    reset()
    onClose()
    onSaved()
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) { reset(); onClose() } }}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Benefit anlegen</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div className="space-y-1.5">
            <Label htmlFor="ben-type">Art</Label>
            <select
              id="ben-type"
              value={benefitType}
              onChange={(e) => setBenefitType(e.target.value)}
              className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              <option value="health_insurance">Krankenversicherung</option>
              <option value="gym">Fitnessstudio</option>
              <option value="meal_voucher">Essensgutschein</option>
              <option value="transport">Fahrtkosten</option>
              <option value="phone">Diensthandy</option>
              <option value="home_office">Home Office</option>
              <option value="other">Sonstiges</option>
            </select>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="ben-desc">Beschreibung</Label>
            <textarea
              id="ben-desc"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="ben-value">Wert (€)</Label>
              <Input id="ben-value" type="number" min="0" step="0.01" value={value} onChange={(e) => setValue(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="ben-start">Ab Datum *</Label>
              <Input id="ben-start" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} required />
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => { reset(); onClose() }}>Abbrechen</Button>
            <Button type="submit" disabled={saving || !startDate}>
              {saving ? "Speichern…" : "Erstellen"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// ---------- Haupt-Komponente ----------

export function CompensationTab() {
  const { hasPermission } = useAuth()
  const [employeeId, setEmployeeId] = useState("")
  const [employeeName, setEmployeeName] = useState("")
  const [inputValue, setInputValue] = useState("")
  const [salaryRecords, setSalaryRecords] = useState<SalaryRecord[]>([])
  const [bonuses, setBonuses] = useState<{ id: string; amount: number; bonus_type: string; payment_date: string; description?: string }[]>([])
  const [benefits, setBenefits] = useState<Benefit[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  const [salaryDialogOpen, setSalaryDialogOpen] = useState(false)
  const [bonusDialogOpen, setBonusDialogOpen] = useState(false)
  const [benefitDialogOpen, setBenefitDialogOpen] = useState(false)

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    if (!inputValue.trim()) return
    setLoading(true)
    const id = inputValue.trim()
    setEmployeeId(id)
    const [emp, salary, bens, boni] = await Promise.all([
      hrService.getEmployee(id).catch(() => null),
      hrService.getEmployeeSalary(id).catch(() => []),
      hrService.getEmployeeBenefits(id).catch(() => []),
      getBonuses(id).catch(() => []),
    ])
    if (emp) {
      const nr = emp.workmate_id ?? emp.employee_code
      setEmployeeName(nr ? `${nr} — ${emp.first_name} ${emp.last_name}` : `${emp.first_name} ${emp.last_name}`)
    }
    setSalaryRecords(salary)
    setBenefits(bens)
    setBonuses(boni as typeof bonuses)
    setSearched(true)
    setLoading(false)
  }

  async function reloadSalary() {
    const salary = await hrService.getEmployeeSalary(employeeId).catch(() => [])
    setSalaryRecords(salary)
  }

  async function reloadBonuses() {
    const boni = await getBonuses(employeeId).catch(() => [])
    setBonuses(boni as typeof bonuses)
  }

  async function reloadBenefits() {
    const bens = await hrService.getEmployeeBenefits(employeeId).catch(() => [])
    setBenefits(bens)
  }

  return (
    <div className="space-y-6">
      <div className="rounded-lg border bg-muted/30 p-4">
        <p className="text-sm text-muted-foreground">
          Gehaltsdaten sind vertraulich. Mitarbeiter auswählen um Details zu sehen.
        </p>
      </div>

      <form onSubmit={handleSearch} className="flex items-end gap-3 max-w-sm">
        <div className="flex-1">
          <EmployeeSelect
            id="comp-emp"
            label="Mitarbeiter"
            value={inputValue}
            onChange={setInputValue}
            disabled={loading}
          />
        </div>
        <Button type="submit" disabled={loading || !inputValue.trim()}>
          {loading ? "Lädt…" : "Anzeigen"}
        </Button>
      </form>

      {searched && !loading && (
        <div className="space-y-6">
          {/* Gehaltshistorie */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold">Gehaltshistorie — {employeeName || employeeId}</h2>
              {hasPermission("hr.manage") && <Button size="sm" variant="outline" onClick={() => setSalaryDialogOpen(true)}>+ Gehalt</Button>}
            </div>
            {salaryRecords.length === 0 ? (
              <p className="py-4 text-center text-sm text-muted-foreground">Keine Gehaltsdaten vorhanden.</p>
            ) : (
              <div className="rounded-lg border overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Gültig ab</th>
                      <th className="text-right px-4 py-3 font-medium text-muted-foreground">Betrag</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Notizen</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {salaryRecords.map((r) => (
                      <tr key={r.id} className="hover:bg-muted/30">
                        <td className="px-4 py-3">{new Date(r.effective_date).toLocaleDateString("de-DE")}</td>
                        <td className="px-4 py-3 text-right">
                          {new Intl.NumberFormat("de-DE", { style: "currency", currency: r.currency || "EUR" }).format(
                            parseFloat(String(r.amount || "0")),
                          )}
                        </td>
                        <td className="px-4 py-3 text-muted-foreground">{r.notes ?? "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Boni */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold">Boni</h2>
              {hasPermission("hr.manage") && <Button size="sm" variant="outline" onClick={() => setBonusDialogOpen(true)}>+ Bonus</Button>}
            </div>
            {bonuses.length === 0 ? (
              <p className="py-4 text-center text-sm text-muted-foreground">Keine Boni erfasst.</p>
            ) : (
              <div className="rounded-lg border overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Art</th>
                      <th className="text-right px-4 py-3 font-medium text-muted-foreground">Betrag</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Auszahlung</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Beschreibung</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {bonuses.map((b) => (
                      <tr key={b.id} className="hover:bg-muted/30">
                        <td className="px-4 py-3 font-medium">{b.bonus_type}</td>
                        <td className="px-4 py-3 text-right">
                          {new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR" }).format(Number(b.amount))}
                        </td>
                        <td className="px-4 py-3">{b.payment_date ? new Date(b.payment_date).toLocaleDateString("de-DE") : "—"}</td>
                        <td className="px-4 py-3 text-muted-foreground">{b.description ?? "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Benefits */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold">Benefits</h2>
              {hasPermission("hr.manage") && <Button size="sm" variant="outline" onClick={() => setBenefitDialogOpen(true)}>+ Benefit</Button>}
            </div>
            {benefits.length === 0 ? (
              <p className="py-4 text-center text-sm text-muted-foreground">Keine Benefits erfasst.</p>
            ) : (
              <div className="rounded-lg border overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Art</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Beschreibung</th>
                      <th className="text-right px-4 py-3 font-medium text-muted-foreground">Wert</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Von</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Bis</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {benefits.map((b) => (
                      <tr key={b.id} className="hover:bg-muted/30">
                        <td className="px-4 py-3 font-medium">{b.benefit_type}</td>
                        <td className="px-4 py-3 text-muted-foreground">{b.description ?? "—"}</td>
                        <td className="px-4 py-3 text-right">{b.value != null ? String(b.value) : "—"}</td>
                        <td className="px-4 py-3">{b.start_date ? new Date(b.start_date).toLocaleDateString("de-DE") : "—"}</td>
                        <td className="px-4 py-3">{b.end_date ? new Date(b.end_date).toLocaleDateString("de-DE") : "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      <AddSalaryDialog
        open={salaryDialogOpen}
        employeeId={employeeId}
        onClose={() => setSalaryDialogOpen(false)}
        onSaved={reloadSalary}
      />
      <AddBonusDialog
        open={bonusDialogOpen}
        employeeId={employeeId}
        onClose={() => setBonusDialogOpen(false)}
        onSaved={reloadBonuses}
      />
      <AddBenefitDialog
        open={benefitDialogOpen}
        employeeId={employeeId}
        onClose={() => setBenefitDialogOpen(false)}
        onSaved={reloadBenefits}
      />
    </div>
  )
}
