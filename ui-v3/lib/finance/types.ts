export type AccountType = "checking" | "savings" | "credit" | "cash"
export type TransactionType = "income" | "expense" | "transfer" | "fee" | "interest"
export type ReconciliationStatus = "unmatched" | "matched" | "confirmed" | "ignored"
export type ExpenseCategory = "travel" | "material" | "software" | "hardware" | "consulting" | "marketing" | "office" | "training" | "other"

export interface BankAccount {
  id: string
  account_name: string
  account_type: AccountType
  iban: string | null
  bic: string | null
  bank_name: string | null
  account_holder: string | null
  balance: string
  is_active: boolean
  note: string | null
  created_at: string
  updated_at: string
}

export interface BankAccountCreate {
  account_name: string
  account_type?: AccountType
  iban?: string | null
  bic?: string | null
  bank_name?: string | null
  account_holder?: string | null
  is_active?: boolean
  note?: string | null
  balance?: number | string
}

export interface BankAccountUpdate extends Partial<BankAccountCreate> {}

export interface BankTransaction {
  id: string
  account_id: string
  transaction_date: string
  value_date: string | null
  amount: string
  transaction_type: TransactionType
  counterparty_name: string | null
  counterparty_iban: string | null
  purpose: string | null
  reference: string | null
  reconciliation_status: ReconciliationStatus
  reconciliation_note: string | null
  reconciled_at: string | null
  matched_payment_id: string | null
  matched_expense_id: string | null
  created_at: string
  updated_at: string
}

export interface BankTransactionCreate {
  account_id: string
  transaction_date: string
  value_date?: string | null
  amount: number | string
  transaction_type: TransactionType
  counterparty_name?: string | null
  counterparty_iban?: string | null
  purpose?: string | null
  reference?: string | null
}

export interface BankTransactionUpdate {
  transaction_type?: TransactionType
  amount?: number | string
  purpose?: string | null
  reference?: string | null
  transaction_date?: string
  reconciliation_status?: ReconciliationStatus
}

export interface Expense {
  id: string
  title: string
  category: ExpenseCategory
  amount: string
  description: string
  receipt_path: string | null
  note: string | null
  is_billable: boolean
  project_id: string | null
  invoice_id: string | null
  created_at: string
  updated_at: string
}

export interface ExpenseCreate {
  title: string
  category: ExpenseCategory
  amount: number | string
  description: string
  receipt_path?: string | null
  note?: string | null
  is_billable?: boolean
  project_id?: string | null
  invoice_id?: string | null
}

export interface ExpenseUpdate extends Partial<ExpenseCreate> {}

export interface ExpenseKpi {
  total: string
  by_category: Record<string, string>
}

export interface TransactionListParams {
  account_id?: string
  reconciliation_status?: ReconciliationStatus
  from_date?: string
  to_date?: string
  limit?: number
  offset?: number
}

export interface ExpenseListParams {
  title?: string
  category?: ExpenseCategory
  project_id?: string
  invoice_id?: string
  from_date?: string
  to_date?: string
  limit?: number
  offset?: number
}
