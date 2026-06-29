"use client"

import { useState } from "react"
import { hrService } from "@/lib/hr/service"
import type { SalaryRecord, Benefit } from "@/lib/hr/types"
import { Button } from "@/components/ui/button"
import { EmployeeSelect } from "./employee-select"

export function CompensationTab() {
  const [employeeId, setEmployeeId] = useState("")
  const [employeeName, setEmployeeName] = useState("")
  const [inputValue, setInputValue] = useState("")
  const [salaryRecords, setSalaryRecords] = useState<SalaryRecord[]>([])
  const [benefits, setBenefits] = useState<Benefit[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    if (!inputValue.trim()) return
    setLoading(true)
    const id = inputValue.trim()
    setEmployeeId(id)
    const [emp, salary, bens] = await Promise.all([
      hrService.getEmployee(id).catch(() => null),
      hrService.getEmployeeSalary(id).catch(() => []),
      hrService.getEmployeeBenefits(id).catch(() => []),
    ])
    if (emp) {
      const nr = emp.workmate_id ?? emp.employee_code
      setEmployeeName(nr ? `${nr} — ${emp.first_name} ${emp.last_name}` : `${emp.first_name} ${emp.last_name}`)
    }
    setSalaryRecords(salary)
    setBenefits(bens)
    setSearched(true)
    setLoading(false)
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
          <div>
            <h2 className="text-sm font-semibold mb-3">Gehaltshistorie — {employeeName || employeeId}</h2>
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

          <div>
            <h2 className="text-sm font-semibold mb-3">Benefits</h2>
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
    </div>
  )
}
