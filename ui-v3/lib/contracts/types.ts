export type ContractType = "maintenance" | "managed_service" | "subscription" | "hosting" | "license" | "other"
export type ContractStatus = "draft" | "active" | "paused" | "cancelled" | "expired"
export type BillingInterval = "monthly" | "quarterly" | "semiannual" | "yearly"

export interface ContractItem {
  id?: string
  product_id?: string | null
  position?: number
  description: string
  quantity: number | string
  unit: string
  unit_price: number | string
  tax_rate: number | string
  discount_percent?: number | string
  net_amount?: number | string
}

export interface Contract {
  id: string
  contract_number: string
  title: string
  description: string | null
  contract_type: ContractType
  status: ContractStatus
  customer_id: string
  customer_name: string | null
  start_date: string
  end_date: string | null
  auto_renew: boolean
  renewal_months: number
  notice_period_days: number
  billing_interval: BillingInterval
  next_billing_date: string | null
  last_billed_date: string | null
  payment_terms_days: number
  included_hours: number | string | null
  notes: string | null
  net_amount_per_period: number | string
  monthly_recurring_revenue: number | string
  items: ContractItem[]
  created_at: string
  updated_at: string
}

export interface ContractCreate {
  title: string
  description?: string | null
  contract_type: ContractType
  customer_id: string
  start_date: string
  end_date?: string | null
  auto_renew: boolean
  renewal_months?: number
  notice_period_days: number
  billing_interval: BillingInterval
  payment_terms_days?: number
  included_hours?: number | null
  notes?: string | null
  status: ContractStatus
  next_billing_date?: string | null
  items: ContractItem[]
}

export type ContractUpdate = Partial<Omit<ContractCreate, "customer_id" | "start_date">>

export interface ContractListResponse {
  items: Contract[]
  total: number
  skip: number
  limit: number
}

export interface ContractStats {
  active_contracts: number
  monthly_recurring_revenue: number | string
  annual_recurring_revenue: number | string
  due_for_billing: number
  notice_deadlines_30d: number
}

export interface BillingRunResult {
  run_date: string
  invoices_created: {
    contract_number: string
    invoice_id: string
    invoice_number: string
    period_start: string
    period_end: string
    total: string
  }[]
  contracts_renewed: string[]
  contracts_expired: string[]
  errors: { contract_number: string; error: string }[]
  notice_deadlines: {
    contract_id: string
    contract_number: string
    title: string
    customer_name: string | null
    end_date: string
    notice_deadline: string
    auto_renew: boolean
  }[]
}

export interface ContractInvoiceBrief {
  id: string
  invoice_number: string
  status: string
  issued_date: string | null
  total: number | string
}
