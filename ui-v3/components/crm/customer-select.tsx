"use client"

import { Combobox } from "@base-ui/react/combobox"
import { CheckIcon, ChevronDownIcon } from "lucide-react"
import { cn } from "@/lib/utils"
import type { Customer } from "@/lib/crm/types"

type CustomerOption = { value: string; label: string }

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
  const options: CustomerOption[] = customers.map(c => ({ value: c.id, label: c.name }))
  const selected = value ? (options.find(o => o.value === value) ?? null) : null

  return (
    <Combobox.Root<CustomerOption>
      value={selected}
      onValueChange={v => onChange(v?.value ?? "")}
      isItemEqualToValue={(a, b) => a.value === b.value}
      disabled={disabled}
    >
      <Combobox.InputGroup
        className={cn(
          "flex h-8 w-full items-center rounded-lg border border-input bg-transparent text-sm transition-colors",
          "focus-within:border-ring focus-within:ring-3 focus-within:ring-ring/50",
          "dark:bg-input/30",
          disabled && "cursor-not-allowed opacity-50",
          className,
        )}
      >
        <Combobox.Input
          className="min-w-0 flex-1 bg-transparent py-1 pl-2.5 pr-1 outline-none placeholder:text-muted-foreground"
          placeholder={placeholder}
        />
        <Combobox.Trigger className="flex shrink-0 items-center pr-2 text-muted-foreground">
          <ChevronDownIcon className="size-4 pointer-events-none" />
        </Combobox.Trigger>
      </Combobox.InputGroup>

      <Combobox.Portal>
        <Combobox.Positioner sideOffset={4} className="isolate z-50">
          <Combobox.Popup
            className={cn(
              "max-h-64 w-(--anchor-width) min-w-48 overflow-y-auto rounded-lg bg-popover text-popover-foreground shadow-md ring-1 ring-foreground/10",
              "origin-(--transform-origin) duration-100",
              "data-open:animate-in data-open:fade-in-0 data-open:zoom-in-95",
              "data-closed:animate-out data-closed:fade-out-0 data-closed:zoom-out-95",
            )}
          >
            <Combobox.List className="p-1">
              <Combobox.Empty className="py-6 text-center text-sm text-muted-foreground">
                Keine Kunden gefunden.
              </Combobox.Empty>
              {options.map(opt => (
                <Combobox.Item
                  key={opt.value}
                  value={opt}
                  className={cn(
                    "relative flex w-full cursor-default select-none items-center rounded-md py-1.5 pl-2 pr-8 text-sm outline-none",
                    "data-highlighted:bg-accent data-highlighted:text-accent-foreground",
                    "data-disabled:pointer-events-none data-disabled:opacity-50",
                  )}
                >
                  {opt.label}
                  <Combobox.ItemIndicator className="pointer-events-none absolute right-2 flex size-4 items-center justify-center">
                    <CheckIcon className="size-3.5" />
                  </Combobox.ItemIndicator>
                </Combobox.Item>
              ))}
            </Combobox.List>
          </Combobox.Popup>
        </Combobox.Positioner>
      </Combobox.Portal>
    </Combobox.Root>
  )
}
