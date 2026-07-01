"use client"

import { ComboSelect } from "@/components/ui/combo-select"
import type { Customer } from "@/lib/crm/types"

interface CustomerSelectProps {
  customers: Customer[]
  value: string
  onChange: (id: string) => void
  placeholder?: string
  className?: string
  disabled?: boolean
}

export function CustomerSelect({
  customers,
  value,
  onChange,
  placeholder = "Kunde auswählen…",
  className,
  disabled,
}: CustomerSelectProps) {
  return (
    <ComboSelect
      options={customers.map(c => ({ value: c.id, label: c.name }))}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      emptyText="Keine Kunden gefunden."
      className={className}
      disabled={disabled}
    />
  )
}
