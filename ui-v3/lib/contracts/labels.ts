import type { BillingInterval, ContractStatus, ContractType } from "./types"

export const CONTRACT_TYPE_LABELS: Record<ContractType, string> = {
  maintenance: "Wartungsvertrag",
  managed_service: "Managed Service",
  subscription: "Abo",
  hosting: "Hosting",
  license: "Lizenz",
  other: "Sonstiges",
}

export const CONTRACT_STATUS_LABELS: Record<ContractStatus, string> = {
  draft: "Entwurf",
  active: "Aktiv",
  paused: "Pausiert",
  cancelled: "Gekündigt",
  expired: "Beendet",
}

export const CONTRACT_STATUS_COLOR: Record<ContractStatus, string> = {
  draft: "bg-muted text-muted-foreground",
  active: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  paused: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  cancelled: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  expired: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
}

export const INTERVAL_LABELS: Record<BillingInterval, string> = {
  monthly: "monatlich",
  quarterly: "quartalsweise",
  semiannual: "halbjährlich",
  yearly: "jährlich",
}

export function fmtEur(value: number | string | null | undefined): string {
  return new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR" }).format(parseFloat(String(value ?? 0)) || 0)
}

export function fmtDate(value: string | null | undefined): string {
  return value ? new Date(value).toLocaleDateString("de-DE") : "—"
}
