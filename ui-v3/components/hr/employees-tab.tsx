"use client"

import { useEffect, useState } from "react"
import { hrService } from "@/lib/hr/service"
import type { Employee, EmployeeStatus, EmployeeStatistics } from "@/lib/hr/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { useRouter } from "next/navigation"
import { PlusIcon, UserIcon } from "lucide-react"

const STATUS_LABELS: Record<EmployeeStatus, string> = {
  active: "Aktiv", inactive: "Inaktiv", on_leave: "Abwesend", terminated: "Ausgeschieden",
}
const STATUS_COLOR: Record<EmployeeStatus, string> = {
  active: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  inactive: "bg-muted text-muted-foreground",
  on_leave: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  terminated: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
}
const EMPLOYMENT_TYPES = [
  { value: "fulltime", label: "Vollzeit" },
  { value: "parttime", label: "Teilzeit" },
  { value: "freelancer", label: "Freelancer" },
  { value: "intern", label: "Praktikant" },
  { value: "minijob", label: "Minijob" },
]

function fmtDate(d: string | null) {
  if (!d) return "–"
  return new Date(d).toLocaleDateString("de-DE")
}

function initials(emp: Employee) {
  return `${emp.first_name[0] ?? ""}${emp.last_name[0] ?? ""}`.toUpperCase()
}

function NewEmployeeForm({ onSave, onClose }: { onSave: () => void; onClose: () => void }) {
  const [firstName, setFirstName] = useState("")
  const [lastName, setLastName] = useState("")
  const [email, setEmail] = useState("")
  const [phone, setPhone] = useState("")
  const [employmentType, setEmploymentType] = useState("fulltime")
  const [hireDate, setHireDate] = useState(new Date().toISOString().slice(0, 10))
  const [saving, setSaving] = useState(false)

  async function handleSave() {
    if (!firstName.trim() || !lastName.trim() || !email.trim()) return
    setSaving(true)
    try {
      await hrService.createEmployee({
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        email: email.trim(),
        phone: phone.trim() || null,
        employment_type: employmentType as "fulltime",
        hire_date: hireDate || null,
        status: "active",
      })
      onSave()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="grid gap-1.5">
          <Label>Vorname *</Label>
          <Input value={firstName} onChange={e => setFirstName(e.target.value)} placeholder="Max" />
        </div>
        <div className="grid gap-1.5">
          <Label>Nachname *</Label>
          <Input value={lastName} onChange={e => setLastName(e.target.value)} placeholder="Mustermann" />
        </div>
        <div className="grid gap-1.5 sm:col-span-2">
          <Label>E-Mail *</Label>
          <Input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="max@firma.de" />
        </div>
        <div className="grid gap-1.5">
          <Label>Telefon</Label>
          <Input value={phone} onChange={e => setPhone(e.target.value)} placeholder="+49 …" />
        </div>
        <div className="grid gap-1.5">
          <Label>Anstellungsart</Label>
          <Select value={employmentType} onValueChange={v => v && setEmploymentType(v)}>
            <SelectTrigger>
              <span data-slot="select-value">
                {EMPLOYMENT_TYPES.find(t => t.value === employmentType)?.label ?? employmentType}
              </span>
            </SelectTrigger>
            <SelectContent>{EMPLOYMENT_TYPES.map(t => <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>)}</SelectContent>
          </Select>
        </div>
        <div className="grid gap-1.5">
          <Label>Einstellungsdatum</Label>
          <Input type="date" value={hireDate} onChange={e => setHireDate(e.target.value)} />
        </div>
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="outline" onClick={onClose}>Abbrechen</Button>
        <Button onClick={handleSave} disabled={saving || !firstName.trim() || !lastName.trim() || !email.trim()}>
          {saving ? "Anlegen…" : "Mitarbeiter anlegen"}
        </Button>
      </div>
    </div>
  )
}

export function EmployeesTab({ stats }: { stats: EmployeeStatistics | null }) {
  const router = useRouter()
  const [employees, setEmployees] = useState<Employee[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [filterStatus, setFilterStatus] = useState("all")
  const [showForm, setShowForm] = useState(false)

  async function load() {
    setLoading(true)
    try {
      const params: Record<string, string> = { limit: "200" }
      if (search.trim()) params.search = search.trim()
      if (filterStatus !== "all") params.status = filterStatus
      const data = await hrService.listEmployees(params as Parameters<typeof hrService.listEmployees>[0])
      setEmployees(data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [search, filterStatus])

  return (
    <div className="space-y-4">
      {/* Stats */}
      {stats && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { label: "Gesamt", value: stats.total_employees },
            { label: "Aktiv", value: stats.active_employees },
            ...Object.entries(stats.by_employment_type).slice(0, 2).map(([k, v]) => ({
              label: EMPLOYMENT_TYPES.find(t => t.value === k)?.label ?? k,
              value: v,
            })),
          ].map(s => (
            <div key={s.label} className="rounded-lg border bg-card p-4">
              <p className="text-xs text-muted-foreground">{s.label}</p>
              <p className="mt-1 text-2xl font-semibold">{s.value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Toolbar */}
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="flex gap-2">
          <Input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Suchen…"
            className="w-56"
          />
          <Select value={filterStatus} onValueChange={v => v && setFilterStatus(v)}>
            <SelectTrigger className="w-40"><SelectValue placeholder="Status" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Alle Status</SelectItem>
              {Object.entries(STATUS_LABELS).map(([v, l]) => <SelectItem key={v} value={v}>{l}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
        <Button size="sm" onClick={() => setShowForm(true)}>
          <PlusIcon className="mr-2 h-4 w-4" />
          Mitarbeiter anlegen
        </Button>
      </div>

      {loading ? (
        <div className="py-12 text-center text-sm text-muted-foreground">Laden…</div>
      ) : employees.length === 0 ? (
        <div className="rounded-lg border border-dashed p-12 text-center text-sm text-muted-foreground">
          Keine Mitarbeiter gefunden.
        </div>
      ) : (
        <div className="rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/40">
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Name</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">E-Mail</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Abteilung</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Anstellungsart</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Einstellung</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Status</th>
              </tr>
            </thead>
            <tbody>
              {employees.map(emp => (
                <tr
                  key={emp.id}
                  className="border-b last:border-0 hover:bg-muted/30 transition-colors cursor-pointer"
                  onClick={() => router.push(`/hr/employees/${emp.id}`)}
                >
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      {emp.photo_url ? (
                        <img src={emp.photo_url} alt="" className="h-8 w-8 rounded-full object-cover" />
                      ) : (
                        <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center text-xs font-medium">
                          {initials(emp)}
                        </div>
                      )}
                      <div>
                        <p className="font-medium">{emp.first_name} {emp.last_name}</p>
                        {emp.employee_code && <p className="text-xs text-muted-foreground">{emp.employee_code}</p>}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">{emp.email}</td>
                  <td className="px-4 py-3">{emp.department?.name ?? "–"}</td>
                  <td className="px-4 py-3">
                    {EMPLOYMENT_TYPES.find(t => t.value === emp.employment_type)?.label ?? emp.employment_type ?? "–"}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">{fmtDate(emp.hire_date)}</td>
                  <td className="px-4 py-3">
                    {emp.status ? (
                      <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLOR[emp.status as EmployeeStatus] ?? "bg-muted"}`}>
                        {STATUS_LABELS[emp.status as EmployeeStatus] ?? emp.status}
                      </span>
                    ) : "–"}
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
            <DialogTitle>Neuer Mitarbeiter</DialogTitle>
          </DialogHeader>
          <NewEmployeeForm
            onSave={() => { setShowForm(false); load() }}
            onClose={() => setShowForm(false)}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}
