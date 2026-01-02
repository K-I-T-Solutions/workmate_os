/**
 * Audit Log Types für GoBD Compliance
 */

export interface AuditLog {
  id: string
  entity_type: 'Invoice' | 'Payment' | 'Expense' | 'InvoiceLineItem'
  entity_id: string
  action: 'create' | 'update' | 'delete' | 'status_change'
  old_values: Record<string, any> | null
  new_values: Record<string, any> | null
  user_id: string | null
  timestamp: string
  ip_address: string | null
}

export interface AuditLogListResponse {
  items: AuditLog[]
  total: number
  skip: number
  limit: number
}

export interface AuditLogFilters {
  entity_type?: string
  entity_id?: string
  action?: string
  skip?: number
  limit?: number
}
