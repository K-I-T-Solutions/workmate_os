"use client"

import { ComboSelect } from "@/components/ui/combo-select"
import type { Project } from "@/lib/projects/types"

interface ProjectSelectProps {
  projects: Project[]
  value: string          // "" oder "none" = kein Projekt
  onChange: (id: string) => void
  placeholder?: string
  allowNone?: boolean    // "Kein Projekt" Option anzeigen
  noneLabel?: string     // Label für den leeren Eintrag
  className?: string
  disabled?: boolean
}

export function ProjectSelect({
  projects,
  value,
  onChange,
  placeholder = "Projekt auswählen…",
  allowNone = true,
  noneLabel = "Kein Projekt",
  className,
  disabled,
}: ProjectSelectProps) {
  const noneOption = { value: "none", label: noneLabel }
  const options = [
    ...(allowNone ? [noneOption] : []),
    ...projects.map(p => ({ value: p.id, label: p.title })),
  ]

  const effectiveValue = value || "none"

  return (
    <ComboSelect
      options={options}
      value={effectiveValue}
      onChange={v => onChange(v === "none" ? "" : v)}
      placeholder={placeholder}
      emptyText="Keine Projekte gefunden."
      className={className}
      disabled={disabled}
    />
  )
}
