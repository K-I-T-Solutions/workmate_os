/**
 * SevDesk Integration Types
 */

// ============================================================================
// CONFIG
// ============================================================================

export interface SevDeskConfig {
  id: string;
  configured: boolean;
  auto_sync_enabled: boolean;
  sync_invoices: boolean;
  sync_bank_accounts: boolean;
  sync_transactions: boolean;
  last_sync_at?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SevDeskConfigRequest {
  api_token: string;
  auto_sync_enabled?: boolean;
  sync_invoices?: boolean;
  sync_bank_accounts?: boolean;
  sync_transactions?: boolean;
}

export interface SevDeskConfigResponse {
  success: boolean;
  message: string;
  config_id?: string;
}

// ============================================================================
// TEST CONNECTION
// ============================================================================

export interface SevDeskConnectionTestResponse {
  success: boolean;
  check_accounts: number;
  invoices: number;
  contacts: number;
  transactions: number;
  message: string;
}

// ============================================================================
// INVOICE SYNC
// ============================================================================

export interface SevDeskSyncInvoiceRequest {
  invoice_id: string;
}

export interface SevDeskSyncInvoiceResponse {
  success: boolean;
  invoice_id: string;
  sevdesk_invoice_id?: string;
  message: string;
  synced_at?: string;
}

// ============================================================================
// PAYMENT SYNC
// ============================================================================

export interface SevDeskSyncPaymentsRequest {
  invoice_id?: string;
  sync_all?: boolean;
}

export interface SevDeskPaymentDetail {
  invoice_id: string;
  invoice_number: string;
  sevdesk_invoice_id: string;
  sevdesk_paid_amount: number;
  workmate_paid_amount: number;
  payment_created: boolean;
  payment_id?: string;
  payment_amount?: number;
  new_invoice_status?: string;
}

export interface SevDeskSyncPaymentsResponse {
  success: boolean;
  total_invoices_checked: number;
  payments_created: number;
  payments_updated: number;
  invoices_status_updated: number;
  details: SevDeskPaymentDetail[];
  errors: string[];
}

// ============================================================================
// BANK ACCOUNT SYNC
// ============================================================================

export interface SevDeskSyncBankAccountRequest {
  bank_account_id: string;
}

export interface SevDeskSyncBankAccountResponse {
  success: boolean;
  bank_account_id: string;
  sevdesk_check_account_id?: string;
  message: string;
  synced_at?: string;
}

// ============================================================================
// TRANSACTION SYNC
// ============================================================================

export interface SevDeskSyncTransactionsRequest {
  check_account_id?: string;
  limit?: number;
}

export interface SevDeskSyncTransactionsResponse {
  success: boolean;
  total: number;
  imported: number;
  skipped: number;
  errors: string[];
}

// ============================================================================
// SYNC HISTORY
// ============================================================================

export interface SevDeskSyncHistory {
  id: string;
  sync_type: 'invoice' | 'payment' | 'bank_account' | 'transaction';
  direction: 'push_to_sevdesk' | 'pull_from_sevdesk';
  status: 'success' | 'failed' | 'partial';
  records_processed: number;
  records_success: number;
  records_failed: number;
  error_message?: string;
  started_at: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface SevDeskSyncHistoryListResponse {
  items: SevDeskSyncHistory[];
  total: number;
}

// ============================================================================
// UI STATE
// ============================================================================

export interface SevDeskState {
  config: SevDeskConfig | null;
  isConfigured: boolean;
  isLoading: boolean;
  isSyncing: boolean;
  lastSyncTime?: string;
  syncHistory: SevDeskSyncHistory[];
}

export type SevDeskSyncType = 'invoice' | 'payment' | 'bank_account' | 'transaction';
export type SevDeskSyncDirection = 'push' | 'pull';
export type SevDeskSyncStatus = 'success' | 'failed' | 'partial';
