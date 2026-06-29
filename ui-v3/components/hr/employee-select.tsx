"use client"

import { useEffect, useState } from "react"
import { hrService } from "@/lib/hr/service"
import type { Employee } from "@/lib/hr/types"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface Props {
  id?: string
  label?: string
  value: string
  onChange: (employeeId: string) => void
  disabled?: boolean
}

function employeeLabel(e: Employee): string {
  const nr = e.workmate_id ?? e.employee_code
  const name = `${e.first_name} ${e.last_name}`
  return nr ? `${nr} — ${name}` : name
}

export function EmployeeSelect({ id = "employee-select", label = "Mitarbeiter", value, onChange, disabled }: Props) {
  const [employees, setEmployees] = useState<Employee[]>([])

  useEffect(() => {
    hrService.listEmployees({ limit: 500 }).catch(() => []).then(setEmployees)
  }, [])

  const selected = employees.find(e => e.id === value)

  return (
    <div className="space-y-1.5">
      <Label htmlFor={id}>{label}</Label>
      <Select value={value} onValueChange={onChange} disabled={disabled || employees.length === 0}>
        <SelectTrigger id={id}>
          <SelectValue placeholder={employees.length === 0 ? "Lädt…" : "Mitarbeiter wählen"}>
            {selected ? employeeLabel(selected) : undefined}
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          {employees.map((e) => (
            <SelectItem key={e.id} value={e.id}>
              {employeeLabel(e)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}
