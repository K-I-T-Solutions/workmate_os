/**
 * Composable für Invoice Compliance Logic (GoBD, HGB, AO)
 *
 * Handles:
 * - Invoice Immutability (§238 HGB)
 * - Allowed Status Transitions (State Machine)
 * - Field Locking
 */
import { computed, type Ref } from 'vue'
import type { Invoice } from '../types'

export function useInvoiceCompliance(invoice: Ref<Invoice | null>) {
  /**
   * Check if invoice is locked (immutable)
   * Locked = status >= "sent"
   */
  const isInvoiceLocked = computed(() => {
    if (!invoice.value) return false

    const lockedStatuses = ['sent', 'partial', 'paid', 'overdue', 'cancelled']
    return lockedStatuses.includes(invoice.value.status)
  })

  /**
   * Fields that can ALWAYS be edited (even when locked)
   */
  const alwaysEditableFields = ['notes', 'terms']

  /**
   * Check if a specific field can be edited
   */
  const canEditField = (fieldName: string): boolean => {
    if (!invoice.value) return true

    // Draft invoices can edit everything
    if (invoice.value.status === 'draft') return true

    // Locked invoices can only edit notes and terms
    return alwaysEditableFields.includes(fieldName)
  }

  /**
   * Get allowed status transitions for current invoice
   */
  const getAllowedStatusTransitions = computed(() => {
    if (!invoice.value) return []

    const transitions: Record<string, string[]> = {
      draft: ['sent', 'cancelled'],
      sent: ['partial', 'paid', 'overdue', 'cancelled'],
      partial: ['paid', 'overdue', 'cancelled'],
      overdue: ['partial', 'paid', 'cancelled'],
      paid: ['cancelled'],
      cancelled: []
    }

    return transitions[invoice.value.status] || []
  })

  /**
   * Check if status transition is allowed
   */
  const canTransitionTo = (newStatus: string): boolean => {
    if (!invoice.value) return false

    // Same status is always OK (no-op)
    if (newStatus === invoice.value.status) return true

    return getAllowedStatusTransitions.value.includes(newStatus)
  }

  /**
   * Get warning message for immutable invoice
   */
  const getImmutabilityWarning = (): string => {
    if (!isInvoiceLocked.value) return ''

    return `⚠️ Diese Rechnung ist gesperrt (Status: ${invoice.value?.status}). ` +
           `Nur "Notizen" und "Zahlungsbedingungen" können noch bearbeitet werden. ` +
           `(§238 HGB: Unveränderbarkeit nach Rechnungsstellung)`
  }

  /**
   * Get status label in German
   */
  const getStatusLabel = (status: string): string => {
    const labels: Record<string, string> = {
      draft: 'Entwurf',
      sent: 'Versendet',
      partial: 'Teilweise bezahlt',
      paid: 'Bezahlt',
      overdue: 'Überfällig',
      cancelled: 'Storniert'
    }
    return labels[status] || status
  }

  /**
   * Get status color class
   */
  const getStatusColor = (status: string): string => {
    const colors: Record<string, string> = {
      draft: 'bg-gray-500/20 text-gray-300',
      sent: 'bg-blue-500/20 text-blue-300',
      partial: 'bg-yellow-500/20 text-yellow-300',
      paid: 'bg-green-500/20 text-green-300',
      overdue: 'bg-red-500/20 text-red-300',
      cancelled: 'bg-gray-500/20 text-gray-400'
    }
    return colors[status] || 'bg-gray-500/20 text-gray-300'
  }

  return {
    isInvoiceLocked,
    alwaysEditableFields,
    canEditField,
    getAllowedStatusTransitions,
    canTransitionTo,
    getImmutabilityWarning,
    getStatusLabel,
    getStatusColor
  }
}
