/**
 * Composable für Audit Log Management (GoBD Compliance)
 */
import { ref, computed } from 'vue'
import type { AuditLog, AuditLogListResponse, AuditLogFilters } from '../types/audit'

const API_BASE = '/api/backoffice/invoices'

export function useAuditLogs() {
  const auditLogs = ref<AuditLog[]>([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  /**
   * Fetch audit logs with filters
   */
  const fetchAuditLogs = async (filters: AuditLogFilters = {}) => {
    loading.value = true
    error.value = null

    try {
      const params = new URLSearchParams()
      if (filters.entity_type) params.append('entity_type', filters.entity_type)
      if (filters.entity_id) params.append('entity_id', filters.entity_id)
      if (filters.action) params.append('action', filters.action)
      if (filters.skip !== undefined) params.append('skip', filters.skip.toString())
      if (filters.limit !== undefined) params.append('limit', filters.limit.toString())

      const response = await fetch(`${API_BASE}/audit-logs?${params}`)

      if (!response.ok) {
        throw new Error(`Failed to fetch audit logs: ${response.statusText}`)
      }

      const data: AuditLogListResponse = await response.json()
      auditLogs.value = data.items
      total.value = data.total
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error occurred'
      console.error('Error fetching audit logs:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * Get action label in German
   */
  const getActionLabel = (action: string): string => {
    const labels: Record<string, string> = {
      create: 'Erstellt',
      update: 'Aktualisiert',
      delete: 'Gelöscht',
      status_change: 'Status geändert'
    }
    return labels[action] || action
  }

  /**
   * Get action color class
   */
  const getActionColor = (action: string): string => {
    const colors: Record<string, string> = {
      create: 'text-green-400',
      update: 'text-blue-400',
      delete: 'text-red-400',
      status_change: 'text-yellow-400'
    }
    return colors[action] || 'text-gray-400'
  }

  /**
   * Format timestamp
   */
  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp)
    return new Intl.DateTimeFormat('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(date)
  }

  /**
   * Get changed fields from old/new values
   */
  const getChangedFields = (oldValues: Record<string, any> | null, newValues: Record<string, any> | null): string[] => {
    if (!oldValues || !newValues) return []

    const allKeys = new Set([...Object.keys(oldValues), ...Object.keys(newValues)])
    const changed: string[] = []

    allKeys.forEach(key => {
      if (JSON.stringify(oldValues[key]) !== JSON.stringify(newValues[key])) {
        changed.push(key)
      }
    })

    return changed
  }

  return {
    auditLogs,
    total,
    loading,
    error,
    fetchAuditLogs,
    getActionLabel,
    getActionColor,
    formatTimestamp,
    getChangedFields
  }
}
