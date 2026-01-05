/**
 * Banking Module Types
 *
 * Typen für Bank-Konten, Transaktionen, CSV-Import und PSD2-Integration
 */

export type AccountType = 'checking' | 'savings' | 'credit_card' | 'other';
export type ConnectionType = 'manual' | 'csv_import' | 'fints' | 'psd2_api';
export type TransactionType = 'income' | 'expense' | 'transfer';
export type ReconciliationStatus = 'unreconciled' | 'reconciled' | 'partial';

export interface BankAccount {
  id: string;
  account_number?: string;
  iban?: string;
  account_name: string;
  bank_name: string;
  bic?: string; // Backend uses 'bic' not 'bic_swift'
  bic_swift?: string; // Keep for compatibility
  account_holder?: string;
  currency?: string;
  account_type: AccountType;
  connection_type?: ConnectionType;
  balance?: string | number; // Backend uses 'balance' not 'current_balance'
  current_balance?: number; // Keep for compatibility
  is_active?: boolean;
  note?: string;
  last_sync?: string;
  created_at: string;
  updated_at?: string;
}

export interface BankTransaction {
  id: string;
  account_id: string;
  transaction_date: string;
  value_date?: string;
  amount: number;
  currency: string;
  transaction_type: TransactionType;
  counterparty_name?: string;
  counterparty_iban?: string;
  purpose?: string;
  reference?: string;
  reconciliation_status: ReconciliationStatus;
  reconciled_invoice_id?: string;
  import_source?: string;
  created_at: string;
  updated_at?: string;
}

export interface BankAccountCreate {
  account_number?: string;
  iban?: string;
  account_name: string;
  bank_name: string;
  bic_swift?: string;
  currency: string;
  account_type: AccountType;
  connection_type: ConnectionType;
  current_balance?: number;
}

export interface BankTransactionCreate {
  account_id: string;
  transaction_date: string;
  value_date?: string;
  amount: number;
  currency?: string;
  transaction_type: TransactionType;
  counterparty_name?: string;
  counterparty_iban?: string;
  purpose?: string;
  reference?: string;
}

export interface CsvImportResponse {
  success: boolean;
  bank_format?: string;
  total?: number;
  imported?: number;
  skipped?: number;
  reconciled?: number;
  errors?: string[];
  message?: string;
}

export interface PSD2ConsentRequest {
  client_id: string;
  redirect_uri: string;
  scope?: string;
}

export interface PSD2ConsentResponse {
  authorization_url: string;
  state: string;
}

export interface PSD2TokenRequest {
  client_id: string;
  authorization_code: string;
  redirect_uri: string;
}

export interface PSD2TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token?: string;
  scope?: string;
}

export interface BankAccountsStats {
  total_accounts: number;
  total_balance: number;
  by_type: Record<AccountType, number>;
  by_connection: Record<ConnectionType, number>;
}

export interface TransactionStats {
  total_transactions: number;
  total_income: number;
  total_expenses: number;
  net_balance: number;
  reconciled_count: number;
  unreconciled_count: number;
}
